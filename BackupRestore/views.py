import os
import re
import subprocess
import threading
import uuid
import tempfile
from datetime import datetime

from django.conf import settings
from django.db import connection
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.core.cache import cache
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import BackupLog

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def get_db_params():
    db = settings.DATABASES['default']
    return {
        'name': db['NAME'],
        'user': db['USER'],
        'password': db['PASSWORD'],
        'host': db.get('HOST', '127.0.0.1'),
        'port': db.get('PORT', '3306'),
    }

def log_action(user, action, result, table_name=None, backup_file=None, details=None, request=None):
    from django.contrib.auth.models import User
    if isinstance(user, int):
        try:
            user = User.objects.get(id=user)
        except User.DoesNotExist:
            user = None
    ip = request.META.get('REMOTE_ADDR') if request else None
    BackupLog.objects.create(
        user=user,
        action=action,
        result=result,
        table_name=table_name,
        backup_file=backup_file,
        details=details,
        ip_address=ip,
    )

def extract_table_name(filepath):
    with open(filepath, 'r', encoding='utf8', errors='ignore') as f:
        for line in f:
            m = re.search(r'CREATE TABLE `([^`]+)`', line)
            if m:
                return m.group(1)
    return None

def extract_constraint_names(filepath):
    constraints = []
    with open(filepath, 'r', encoding='utf8', errors='ignore') as f:
        content = f.read()
        constraints = re.findall(r'CONSTRAINT\s+`([^`]+)`\s+FOREIGN KEY', content, re.IGNORECASE)
    return constraints

def drop_conflicting_constraints(constraint_names):
    with connection.cursor() as cursor:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        for cname in constraint_names:
            cursor.execute("""
                SELECT TABLE_NAME FROM information_schema.TABLE_CONSTRAINTS
                WHERE CONSTRAINT_SCHEMA = DATABASE() AND CONSTRAINT_NAME = %s
            """, [cname])
            row = cursor.fetchone()
            if row:
                table = row[0]
                cursor.execute(f"ALTER TABLE `{table}` DROP FOREIGN KEY `{cname}`;")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

def create_pre_restore_backup(table_name):
    params = get_db_params()
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f"pre_restore_{table_name}_{timestamp}.sql"
    backup_path = os.path.join(settings.BACKUP_DIR, backup_file)
    os.makedirs(settings.BACKUP_DIR, exist_ok=True)
    cmd = [
        'mysqldump',
        '-h', params['host'],
        '-P', str(params['port']),
        '-u', params['user'],
        f'-p{params["password"]}',
        '--single-transaction',
        params['name'],
        table_name,
        '-r', backup_path,
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return backup_path
    except:
        return None
    
def run_mysql_restore(filepath, target_db=None):
    params = get_db_params()
    db_name = target_db if target_db else params['name']
    cmd = [
        'mysql',
        '-h', params['host'],
        '-P', str(params['port']),
        '-u', params['user'],
        f'-p{params["password"]}',
        '-f',                      # continue even if errors
        '--binary-mode=1',         # avoid charset issues
        db_name,
    ]
    try:
        with open(filepath, 'r', encoding='utf8', errors='ignore') as f:
            # Run with timeout; capture stdout & stderr
            result = subprocess.run(
                cmd,
                stdin=f,
                capture_output=True,
                text=True,
                timeout=300,        # 5 minutes timeout
            )
        if result.returncode != 0:
            # Print the error for debugging
            error_msg = result.stderr[:500] if result.stderr else "Unknown error"
            print(f"MySQL restore error (code {result.returncode}): {error_msg}")
            return False
        return True
    except subprocess.TimeoutExpired:
        print("Restore timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"Restore exception: {e}")
        return False
    
def run_mysql_restore10(filepath, target_db=None):
    params = get_db_params()
    db_name = target_db if target_db else params['name']
    cmd = [
        'mysql',
        '-h', params['host'],
        '-P', str(params['port']),
        '-u', params['user'],
        f'-p{params["password"]}',
        '-f',  # continue even if errors
        db_name,
    ]
    try:
        with open(filepath, 'r', encoding='utf8', errors='ignore') as f:
            # Use Popen to capture stderr and avoid hanging
            process = subprocess.Popen(cmd, stdin=f, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate(timeout=3600)
            if process.returncode != 0:
                error_msg = stderr.decode('utf8', errors='ignore')[:500]
                print(f"MySQL restore error: {error_msg}")
                return False
            return True
    except subprocess.TimeoutExpired:
        print("Restore timed out after 1 hour")
        process.kill()
        return False
    except Exception as e:
        print(f"Restore error: {e}")
        return False    

def run_mysql_restore9(filepath, target_db=None):
    params = get_db_params()
    db_name = target_db if target_db else params['name']
    cmd = [
        'mysql',
        '-h', params['host'],
        '-P', str(params['port']),
        '-u', params['user'],
        f'-p{params["password"]}',
        '--init-command', 'SET FOREIGN_KEY_CHECKS=0;',
        db_name,
    ]
    try:
        with open(filepath, 'r', encoding='utf8', errors='ignore') as f:
            subprocess.run(cmd, stdin=f, check=True, timeout=3600)
        return True
    except Exception as e:
        print(f"Restore error: {e}")
        return False

def get_table_names_from_backup(filepath):
    tables = set()
    with open(filepath, 'r', encoding='utf8', errors='ignore') as f:
        for line in f:
            m = re.search(r'CREATE TABLE `([^`]+)`', line)
            if m:
                tables.add(m.group(1))
    return list(tables)


# ----------------------------------------------------------------------
# Direct restore (single table, background)
# ----------------------------------------------------------------------
restore_jobs = {}

def _run_restore_job(job_id, filepath, table_name, user):
    try:
        print(f"[RESTORE] Job {job_id} started")
        pre_backup = create_pre_restore_backup(table_name)
        print(f"[RESTORE] Pre-restore backup: {pre_backup}")
        constraints = extract_constraint_names(filepath)
        drop_conflicting_constraints(constraints)
        success = run_mysql_restore(filepath)
        if success:
            restore_jobs[job_id] = {'status': 'SUCCESS', 'pre_backup': pre_backup}
            log_action(user, 'RESTORE', 'SUCCESS', table_name=table_name,
                       backup_file=os.path.basename(filepath))
            print(f"[RESTORE] Job {job_id} SUCCESS")
        else:
            restore_jobs[job_id] = {'status': 'FAILED', 'error': 'MySQL restore command failed'}
            log_action(user, 'RESTORE', 'FAILURE', table_name=table_name,
                       backup_file=os.path.basename(filepath), details='MySQL restore failed')
            print(f"[RESTORE] Job {job_id} FAILED (mysql restore)")
    except Exception as e:
        import traceback
        restore_jobs[job_id] = {'status': 'FAILED', 'error': str(e)}
        log_action(user, 'RESTORE', 'FAILURE', table_name=table_name,
                   backup_file=os.path.basename(filepath), details=str(e))
        print(f"[RESTORE] Job {job_id} FAILED:\n{traceback.format_exc()}")

@csrf_exempt
@require_http_methods(["POST"])
def restore_start(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({'error': 'Authentication required'}, status=403)
    filename = request.POST.get('backup_file')
    if not filename:
        return JsonResponse({'error': 'No backup file specified'}, status=400)
    filepath = os.path.join(settings.BACKUP_DIR, filename)
    if not os.path.exists(filepath):
        return JsonResponse({'error': 'Backup file not found'}, status=404)
    table_name = extract_table_name(filepath)
    if not table_name:
        return JsonResponse({'error': 'Could not determine table name'}, status=400)
    job_id = str(uuid.uuid4())
    restore_jobs[job_id] = {'status': 'RUNNING'}
    thread = threading.Thread(target=_run_restore_job, args=(job_id, filepath, table_name, request.user))
    thread.start()
    return JsonResponse({'job_id': job_id})

@csrf_exempt
@require_http_methods(["GET"])
def restore_status(request, job_id):
    job = restore_jobs.get(job_id)
    if not job:
        return JsonResponse({'status': 'NOT_FOUND'}, status=404)
    return JsonResponse(job)

# ----------------------------------------------------------------------
# Safe restore (2-step, uses temporary tables, no CREATE DATABASE)
# ----------------------------------------------------------------------
def _create_temp_database():
    ts = timezone.now().strftime('%Y%m%d_%H%M%S')
    temp_db_name = f"CredDb_temp_{ts}"
    with connection.cursor() as cursor:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{temp_db_name}`")
    return temp_db_name


def update_safe_restore_progress(job_id, status, percent, error=None):
    safe_restore_jobs[job_id] = {
        'status': status,
        'percent': percent,
        'error': error,
        'temp_db': safe_restore_jobs.get(job_id, {}).get('temp_db')
    }



safe_restore_jobs = {}
copy_jobs = {}

def _run_safe_restore(job_id, filepath, filename, user_id):
    import traceback
    print(f"[DEBUG] _run_safe_restore STARTED for job {job_id}")
    try:
        print("[DEBUG] Updating progress: CREATING_TEMP_DB")
        update_safe_restore_progress(job_id, 'CREATING_TEMP_DB', 5)
        temp_db = _create_temp_database()
        print(f"[DEBUG] Created temp DB: {temp_db}")
        safe_restore_jobs[job_id]['temp_db'] = temp_db

        print("[DEBUG] Updating progress: RESTORING_BACKUP")
        update_safe_restore_progress(job_id, 'RESTORING_BACKUP', 20)

        # Read and clean SQL
        with open(filepath, 'r', encoding='utf8', errors='ignore') as f:
            sql = f.read()
        sql = re.sub(r'^LOCK TABLES.*?;\n', '', sql, flags=re.MULTILINE | re.IGNORECASE)
        sql = re.sub(r'^UNLOCK TABLES.*?;\n', '', sql, flags=re.MULTILINE | re.IGNORECASE)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False, encoding='utf-8') as tmp:
            tmp.write(sql)
            clean_file = tmp.name
        print(f"[DEBUG] Cleaned SQL written to {clean_file}")

        print("[DEBUG] Calling run_mysql_restore...")
        success = run_mysql_restore(clean_file, target_db=temp_db)
        print(f"[DEBUG] run_mysql_restore returned {success}")
        os.unlink(clean_file)

        if not success:
            raise Exception("MySQL restore to temp database failed")

        update_safe_restore_progress(job_id, 'COMPLETED', 100)
        log_action(user_id, 'SAFE_RESTORE_PREP', 'SUCCESS', backup_file=filename, details=f"Temp DB: {temp_db}")
        print("[DEBUG] Safe restore preparation completed successfully")

    except Exception as e:
        print(f"[DEBUG] EXCEPTION: {traceback.format_exc()}")
        update_safe_restore_progress(job_id, 'FAILED', None, error=str(e))
        log_action(user_id, 'SAFE_RESTORE_PREP', 'FAILURE', backup_file=filename, details=str(e))

def _run_safe_restore3(job_id, filepath, filename, user_id):
    import traceback
    debug_file = 'C:/CredSoft/restore_debug.log'
    with open(debug_file, 'a') as log:
        log.write(f"\n=== Job {job_id} started at {timezone.now()} ===\n")
        try:
            update_safe_restore_progress(job_id, 'CREATING_TEMP_DB', 5)
            temp_db = _create_temp_database()
            log.write(f"Created temp DB: {temp_db}\n")
            safe_restore_jobs[job_id]['temp_db'] = temp_db

            update_safe_restore_progress(job_id, 'RESTORING_BACKUP', 20)
            # Remove LOCK/UNLOCK TABLES from the backup file
            with open(filepath, 'r', encoding='utf8', errors='ignore') as f:
                sql = f.read()
            sql = re.sub(r'^LOCK TABLES.*?;\n', '', sql, flags=re.MULTILINE | re.IGNORECASE)
            sql = re.sub(r'^UNLOCK TABLES.*?;\n', '', sql, flags=re.MULTILINE | re.IGNORECASE)

            with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False, encoding='utf-8') as tmp:
                tmp.write(sql)
                clean_file = tmp.name
            log.write(f"Cleaned SQL written to {clean_file}\n")

            success = run_mysql_restore(clean_file, target_db=temp_db)
            log.write(f"MySQL restore returned {success}\n")
            os.unlink(clean_file)

            if not success:
                raise Exception("MySQL restore to temp database failed")

            update_safe_restore_progress(job_id, 'COMPLETED', 100)
            log.write("Safe restore preparation completed successfully\n")
            log_action(user_id, 'SAFE_RESTORE_PREP', 'SUCCESS', backup_file=filename, details=f"Temp DB: {temp_db}")

        except Exception as e:
            log.write(f"EXCEPTION: {traceback.format_exc()}\n")
            update_safe_restore_progress(job_id, 'FAILED', None, error=str(e))
            log_action(user_id, 'SAFE_RESTORE_PREP', 'FAILURE', backup_file=filename, details=str(e))


def _run_safe_restore5(job_id, filepath, filename, user_id):
    try:
        update_safe_restore_progress(job_id, 'CREATING_TEMP_DB', 5)
        temp_db = _create_temp_database()
        safe_restore_jobs[job_id]['temp_db'] = temp_db

        update_safe_restore_progress(job_id, 'RESTORING_BACKUP', 20)
        # Remove LOCK/UNLOCK TABLES from the backup file
        with open(filepath, 'r', encoding='utf8', errors='ignore') as f:
            sql = f.read()
        sql = re.sub(r'^LOCK TABLES.*?;\n', '', sql, flags=re.MULTILINE | re.IGNORECASE)
        sql = re.sub(r'^UNLOCK TABLES.*?;\n', '', sql, flags=re.MULTILINE | re.IGNORECASE)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False, encoding='utf-8') as tmp:
            tmp.write(sql)
            clean_file = tmp.name

        success = run_mysql_restore(clean_file, target_db=temp_db)
        os.unlink(clean_file)

        if not success:
            raise Exception("MySQL restore to temp database failed")

        update_safe_restore_progress(job_id, 'COMPLETED', 100)
        log_action(user_id, 'SAFE_RESTORE_PREP', 'SUCCESS', backup_file=filename, details=f"Temp DB: {temp_db}")

    except Exception as e:
        update_safe_restore_progress(job_id, 'FAILED', None, error=str(e))
        log_action(user_id, 'SAFE_RESTORE_PREP', 'FAILURE', backup_file=filename, details=str(e))

def _run_safe_restore2(job_id, filepath, filename, user_id):
    try:
        update_safe_restore_progress(job_id, 'CREATING_TEMP_DB', 5)
        temp_db = _create_temp_database()
        safe_restore_jobs[job_id]['temp_db'] = temp_db

        update_safe_restore_progress(job_id, 'RESTORING_BACKUP', 20)
        # Remove LOCK/UNLOCK TABLES from the backup file
        with open(filepath, 'r', encoding='utf8', errors='ignore') as f:
            sql = f.read()
        sql = re.sub(r'^LOCK TABLES.*?;\n', '', sql, flags=re.MULTILINE | re.IGNORECASE)
        sql = re.sub(r'^UNLOCK TABLES.*?;\n', '', sql, flags=re.MULTILINE | re.IGNORECASE)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False, encoding='utf-8') as tmp:
            tmp.write(sql)
            clean_file = tmp.name

        success = run_mysql_restore(clean_file, target_db=temp_db)
        os.unlink(clean_file)

        if not success:
            raise Exception("MySQL restore to temp database failed")

        update_safe_restore_progress(job_id, 'COMPLETED', 100)
        log_action(user_id, 'SAFE_RESTORE_PREP', 'SUCCESS', backup_file=filename, details=f"Temp DB: {temp_db}")

    except Exception as e:
        update_safe_restore_progress(job_id, 'FAILED', None, error=str(e))
        log_action(user_id, 'SAFE_RESTORE_PREP', 'FAILURE', backup_file=filename, details=str(e))



def _run_safe_restore1(job_id, filepath, filename, user_id):
    try:
        # Step 1: create temporary tables with unique prefix
        temp_prefix = f"t_{uuid.uuid4().hex[:4]}_"   # e.g., t_a1b2_
    #    temp_prefix = f"temp_{uuid.uuid4().hex[:8]}_"
        mapping = restore_to_temp_tables(filepath, temp_prefix)
        safe_restore_jobs[job_id] = {
            'status': 'TABLES_READY',
            'percent': 50,
            'temp_prefix': temp_prefix,
            'mapping': mapping,
            'filename': filename,
        }
        log_action(user_id, 'SAFE_RESTORE_PREP', 'SUCCESS', backup_file=filename, details=f"Temp prefix: {temp_prefix}")
    except Exception as e:
        safe_restore_jobs[job_id] = {'status': 'FAILED', 'error': str(e)}
        log_action(user_id, 'SAFE_RESTORE_PREP', 'FAILURE', backup_file=filename, details=str(e))

@csrf_exempt
@require_http_methods(["POST"])
def safe_restore_start(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({'error': 'Authentication required'}, status=403)
    filename = request.POST.get('backup_file')
    if not filename:
        return JsonResponse({'error': 'No backup file specified'}, status=400)
    filepath = os.path.join(settings.BACKUP_DIR, filename)
    if not os.path.exists(filepath):
        return JsonResponse({'error': 'Backup file not found'}, status=404)

    job_id = str(uuid.uuid4())
    safe_restore_jobs[job_id] = {'status': 'STARTING', 'percent': 0}
    thread = threading.Thread(target=_run_safe_restore, args=(job_id, filepath, filename, request.user.id))
    thread.start()
    return JsonResponse({'job_id': job_id})

def safe_restore_start1(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({'error': 'Authentication required'}, status=403)
    filename = request.POST.get('backup_file')
    if not filename:
        return JsonResponse({'error': 'No backup file specified'}, status=400)
    filepath = os.path.join(settings.BACKUP_DIR, filename)
    if not os.path.exists(filepath):
        return JsonResponse({'error': 'Backup file not found'}, status=404)
    job_id = str(uuid.uuid4())
    safe_restore_jobs[job_id] = {'status': 'STARTING', 'percent': 0}
    thread = threading.Thread(target=_run_safe_restore, args=(job_id, filepath, filename, request.user.id))
    thread.start()
    return JsonResponse({'job_id': job_id})

@csrf_exempt
@require_http_methods(["GET"])
def safe_restore_status(request, job_id):
    job = safe_restore_jobs.get(job_id)
    if not job:
        return JsonResponse({'status': 'NOT_FOUND'}, status=404)
    return JsonResponse(job)

def safe_restore_step2(request):
    job_id = request.GET.get('job_id')
    if not job_id:
        messages.error(request, "No job ID")
        return redirect('BackupRestore:backup_panel')
    job = safe_restore_jobs.get(job_id)
    if not job or job.get('status') != 'COMPLETED':
        messages.error(request, "Restore preparation not completed")
        return redirect('BackupRestore:backup_panel')
    temp_db = job.get('temp_db')
    if not temp_db:
        messages.error(request, "Temporary database not found")
        return redirect('BackupRestore:backup_panel')

    # Get tables from temp database
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA = %s", [temp_db])
        temp_tables = [row[0] for row in cursor.fetchall()]

    table_status = []
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES;")
        existing_prod = {row[0] for row in cursor.fetchall()}
    for tbl in temp_tables:
        exists = tbl in existing_prod
        table_status.append({
            'name': tbl,
            'exists': exists,
            'will_replace': not exists,
        })

    context = {
        'filename': job.get('backup_file', 'unknown'),
        'tables': table_status,
        'temp_db': temp_db,
        'job_id': job_id,
    }
    return render(request, 'BackupRestore/safe_restore_select_tables.html', context)


def safe_restore_step22(request):
    job_id = request.GET.get('job_id')
    if not job_id:
        messages.error(request, "No job ID")
        return redirect('BackupRestore:backup_panel')
    job = safe_restore_jobs.get(job_id)
    if not job or job.get('status') not in ('TABLES_READY', 'COMPLETED'):
        messages.error(request, "Restore preparation not ready")
        return redirect('BackupRestore:backup_panel')
    temp_prefix = job['temp_prefix']
    mapping = job['mapping']  # original -> temp
    orig_tables = list(mapping.keys())
    table_status = []
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES;")
        existing = {row[0] for row in cursor.fetchall()}
    for orig in orig_tables:
        exists = orig in existing
        table_status.append({
            'name': orig,
            'exists': exists,
            'will_replace': not exists,
        })
    context = {
        'filename': job.get('filename', 'unknown'),
        'tables': table_status,
        'job_id': job_id,
        'temp_prefix': temp_prefix,
    }
    return render(request, 'BackupRestore/safe_restore_select_tables.html', context)

def _run_copy_tables(job_id, temp_db, selected_tables, replace_tables, user_id, filename):
    import traceback
    print(f"[COPY] Job {job_id} started. Tables to copy: {selected_tables}")
    total = len(selected_tables)
    success = []
    failed = []
    with connection.cursor() as cursor:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        for idx, table in enumerate(selected_tables):
            copy_jobs[job_id]['current_table'] = table
            copy_jobs[job_id]['percent'] = int((idx / total) * 100) if total > 0 else 0
            try:
                print(f"[COPY] Processing table {table}...")
                if table in replace_tables:
                    print(f"[COPY] Dropping existing table {table}")
                    cursor.execute(f"DROP TABLE IF EXISTS `{table}`")
                print(f"[COPY] Creating table {table} from temp")
                cursor.execute(f"CREATE TABLE `{table}` LIKE `{temp_db}`.`{table}`")
                print(f"[COPY] Inserting data into {table}")
                cursor.execute(f"INSERT INTO `{table}` SELECT * FROM `{temp_db}`.`{table}`")
                success.append(table)
                print(f"[COPY] Table {table} copied successfully")
            except Exception as e:
                failed.append(f"{table}: {str(e)}")
                print(f"[COPY] Failed on {table}: {e}")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
    copy_jobs[job_id]['status'] = 'COMPLETED'
    copy_jobs[job_id]['percent'] = 100
    copy_jobs[job_id]['success_tables'] = success
    copy_jobs[job_id]['failed_tables'] = failed
    print(f"[COPY] Job {job_id} finished. Success: {success}, Failed: {failed}")
    log_action(user_id, 'SAFE_RESTORE_COPY', 'SUCCESS' if not failed else 'PARTIAL',
               details=f"File: {filename}, Tables copied: {success}, Failed: {failed}")

def _run_copy_tables9(job_id, temp_db, selected_tables, replace_tables, user_id, filename):
    total = len(selected_tables)
    success = []
    failed = []
    with connection.cursor() as cursor:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        for idx, table in enumerate(selected_tables):
            copy_jobs[job_id]['current_table'] = table
            copy_jobs[job_id]['percent'] = int((idx / total) * 100) if total > 0 else 0
            try:
                if table in replace_tables:
                    cursor.execute(f"DROP TABLE IF EXISTS `{table}`")
                cursor.execute(f"CREATE TABLE `{table}` LIKE `{temp_db}`.`{table}`")
                cursor.execute(f"INSERT INTO `{table}` SELECT * FROM `{temp_db}`.`{table}`")
                success.append(table)
            except Exception as e:
                failed.append(f"{table}: {str(e)}")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
    copy_jobs[job_id]['status'] = 'COMPLETED'
    copy_jobs[job_id]['percent'] = 100
    copy_jobs[job_id]['success_tables'] = success
    copy_jobs[job_id]['failed_tables'] = failed
    log_action(user_id, 'SAFE_RESTORE_COPY', 'SUCCESS' if not failed else 'PARTIAL',
               details=f"File: {filename}, Tables copied: {success}, Failed: {failed}")

def _run_copy_tables1(job_id, temp_prefix, selected_tables, replace_tables, user_id, filename):
    total = len(selected_tables)
    success = []
    failed = []
    with connection.cursor() as cursor:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        for idx, table in enumerate(selected_tables):
            copy_jobs[job_id]['current_table'] = table
            copy_jobs[job_id]['percent'] = int((idx / total) * 100) if total > 0 else 0
            temp_table = f"{temp_prefix}{table}"
            try:
                if table in replace_tables:
                    cursor.execute(f"DROP TABLE IF EXISTS `{table}`")
                cursor.execute(f"CREATE TABLE `{table}` LIKE `{temp_table}`")
                cursor.execute(f"INSERT INTO `{table}` SELECT * FROM `{temp_table}`")
                success.append(table)
            except Exception as e:
                failed.append(f"{table}: {str(e)}")
        # Drop all temporary tables with the same prefix
        cursor.execute("SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_NAME LIKE %s", [f"{temp_prefix}%"])
        temp_tables = [row[0] for row in cursor.fetchall()]
        for tt in temp_tables:
            cursor.execute(f"DROP TABLE IF EXISTS `{tt}`")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
    copy_jobs[job_id]['status'] = 'COMPLETED'
    copy_jobs[job_id]['percent'] = 100
    copy_jobs[job_id]['success_tables'] = success
    copy_jobs[job_id]['failed_tables'] = failed
    log_action(user_id, 'SAFE_RESTORE_COPY', 'SUCCESS' if not failed else 'PARTIAL',
               details=f"File: {filename}, Tables copied: {success}, Failed: {failed}")



@csrf_exempt
@require_http_methods(["POST"])
def safe_restore_copy_start(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    selected_tables = request.POST.getlist('selected_tables')
    replace_tables = request.POST.getlist('replace_table')
    temp_db = request.POST.get('temp_db')
    job_id = request.POST.get('job_id')
    filename = request.POST.get('filename')
    if not selected_tables or not temp_db:
        return JsonResponse({'error': 'Missing parameters'}, status=400)
    copy_job_id = str(uuid.uuid4())
    copy_jobs[copy_job_id] = {'status': 'RUNNING', 'percent': 0, 'current_table': ''}
    thread = threading.Thread(target=_run_copy_tables, args=(copy_job_id, temp_db, selected_tables, replace_tables, request.user.id, filename))
    thread.start()
    return JsonResponse({'copy_job_id': copy_job_id})


def safe_restore_copy_start1(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    selected_tables = request.POST.getlist('selected_tables')
    replace_tables = request.POST.getlist('replace_table')
    temp_prefix = request.POST.get('temp_prefix')
    job_id = request.POST.get('job_id')
    filename = request.POST.get('filename')
    if not selected_tables or not temp_prefix:
        return JsonResponse({'error': 'Missing parameters'}, status=400)
    copy_job_id = str(uuid.uuid4())
    copy_jobs[copy_job_id] = {'status': 'RUNNING', 'percent': 0, 'current_table': ''}
    thread = threading.Thread(target=_run_copy_tables,
                              args=(copy_job_id, temp_prefix, selected_tables, replace_tables, request.user.id, filename))
    thread.start()
    return JsonResponse({'copy_job_id': copy_job_id})

@csrf_exempt
@require_http_methods(["GET"])
def copy_status(request, copy_job_id):
    job = copy_jobs.get(copy_job_id)
    if not job:
        return JsonResponse({'status': 'NOT_FOUND'}, status=404)
    return JsonResponse(job)

# ----------------------------------------------------------------------
# Backup views
# ----------------------------------------------------------------------
@staff_member_required
def backup_panel(request):
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES;")
        tables = [row[0] for row in cursor.fetchall()]
    backups = []
    if os.path.exists(settings.BACKUP_DIR):
        for f in os.listdir(settings.BACKUP_DIR):
            if f.endswith('.sql'):
                path = os.path.join(settings.BACKUP_DIR, f)
                stat = os.stat(path)
                backups.append({
                    'filename': f,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime),
                })
        backups.sort(key=lambda x: x['modified'], reverse=True)
    return render(request, 'BackupRestore/backup_panel.html', {'tables': tables, 'backups': backups})

@staff_member_required
def backup_all(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    params = get_db_params()
    ts = timezone.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{params['name']}_full_{ts}.sql"
    filepath = os.path.join(settings.BACKUP_DIR, filename)
    os.makedirs(settings.BACKUP_DIR, exist_ok=True)
    cmd = [
        'mysqldump',
        '-h', params['host'],
        '-P', str(params['port']),
        '-u', params['user'],
        f'-p{params["password"]}',
        '--single-transaction',
        '--routines',
        '--triggers',
        params['name'],
        '-r', filepath,
    ]
    try:
        subprocess.run(cmd, check=True)
        log_action(request.user, 'BACKUP', 'SUCCESS', backup_file=filename, request=request)
        with open(filepath, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/sql')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    except Exception as e:
        log_action(request.user, 'BACKUP', 'FAILURE', backup_file=filename, details=str(e), request=request)
        messages.error(request, f"Backup failed: {e}")
        return redirect('BackupRestore:backup_panel')

@staff_member_required
def backup_table(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    table_name = request.POST.get('table_name')
    if not table_name:
        messages.error(request, "No table selected.")
        return redirect('BackupRestore:backup_panel')
    params = get_db_params()
    ts = timezone.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{table_name}_{ts}.sql"
    filepath = os.path.join(settings.BACKUP_DIR, filename)
    os.makedirs(settings.BACKUP_DIR, exist_ok=True)
    cmd = [
        'mysqldump',
        '-h', params['host'],
        '-P', str(params['port']),
        '-u', params['user'],
        f'-p{params["password"]}',
        params['name'],
        table_name,
        '-r', filepath,
    ]
    try:
        subprocess.run(cmd, check=True)
        log_action(request.user, 'BACKUP', 'SUCCESS', table_name=table_name, backup_file=filename, request=request)
        with open(filepath, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/sql')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    except Exception as e:
        log_action(request.user, 'BACKUP', 'FAILURE', table_name=table_name, details=str(e), request=request)
        messages.error(request, f"Backup failed: {e}")
        return redirect('BackupRestore:backup_panel')
    
@staff_member_required
def cleanup_temp_objects(request):
    """Delete leftover temporary databases and tables from failed restores."""
    with connection.cursor() as cursor:
        # Drop temporary databases (CredDb_temp_*)
        cursor.execute("SHOW DATABASES LIKE 'CredDb_temp_%'")
        temp_dbs = [row[0] for row in cursor.fetchall()]
        for db_name in temp_dbs:
            cursor.execute(f"DROP DATABASE IF EXISTS `{db_name}`")
        
        # Drop temporary tables in the main database that start with 'temp_'
        # Note: underscore is a wildcard, but our tables are named temp_xxxx, so it's fine.
        cursor.execute("SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME LIKE 'temp_%'")
        temp_tables = [row[0] for row in cursor.fetchall()]
        for tbl in temp_tables:
            cursor.execute(f"DROP TABLE IF EXISTS `{tbl}`")
    
    messages.success(request, f"Cleaned up {len(temp_dbs)} temporary database(s) and {len(temp_tables)} temporary table(s).")
    return redirect('BackupRestore:backup_panel')