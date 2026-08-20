import os
import re
import subprocess
import threading
import uuid
from datetime import datetime
from decimal import Decimal

from django.conf import settings
from django.db import connection
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.core.cache import cache
from django.utils import timezone

from .models import BackupLog

from django.views.decorators.csrf import csrf_exempt

import threading
import uuid



from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import threading
import uuid
import os
import subprocess
from django.db import connection
from django.http import JsonResponse, HttpResponseNotAllowed
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.cache import cache
from django.utils import timezone

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
 
def run_mysql_restore9(filepath):
    params = get_db_params()
    cmd = ['mysql', '-h', params['host'], '-P', str(params['port']), '-u', params['user'], f'-p{params["password"]}', params['name']]
    try:
        with open(filepath, 'r', encoding='utf8', errors='ignore') as f:
            subprocess.run(cmd, stdin=f, check=True, timeout=3600)  # 1 hour
        return True
    except subprocess.TimeoutExpired:
        print("Restore timed out after 1 hour")
        return False
    except Exception as e:
        print(f"Restore error: {e}")
        return False
    
def run_mysql_restore2(filepath):
    params = get_db_params()
    cmd = ['mysql', '-h', params['host'], '-P', str(params['port']), '-u', params['user'], f'-p{params["password"]}', params['name']]
    try:
        with open(filepath, 'r', encoding='utf8', errors='ignore') as f:
            subprocess.run(cmd, stdin=f, check=True, timeout=3600)  # 1 hour timeout
        return True
    except subprocess.TimeoutExpired:
        print("Restore timed out after 1 hour")
        return False
    except Exception as e:
        print(f"Restore error: {e}")
        return False    

def run_mysql_restore1(filepath, target_db=None):
    params = get_db_params()
    db_name = target_db if target_db else params['name']
    cmd = [
        'mysql',
        '-h', params['host'],
        '-P', str(params['port']),
        '-u', params['user'],
        f'-p{params["password"]}',
        db_name,
    ]
    try:
        with open(filepath, 'r', encoding='utf8', errors='ignore') as f:
            subprocess.run(cmd, stdin=f, check=True, capture_output=True)
        return True
    except:
        return False

def _create_temp_database():
    ts = timezone.now().strftime('%Y%m%d_%H%M%S')
    temp_db_name = f"CredDb_temp_{ts}"
    with connection.cursor() as cursor:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{temp_db_name}`")
    return temp_db_name

def _get_tables_in_database(db_name):
    with connection.cursor() as cursor:
        cursor.execute("SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA = %s", [db_name])
        return [row[0] for row in cursor.fetchall()]

def _table_exists_in_production(table_name):
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM information_schema.TABLES WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s", [table_name])
        return cursor.fetchone()[0] > 0

# ----------------------------------------------------------------------
# Direct restore (background job for large restores)
# ----------------------------------------------------------------------
restore_jobs = {}

def _run_restore_job(job_id, filepath, table_name, user):
    try:
        print(f"[RESTORE] Job {job_id} started")

        # Pre‑restore backup (optional)
        pre_backup = create_pre_restore_backup(table_name)
        print(f"[RESTORE] Pre-restore backup: {pre_backup}")

        # Drop conflicting constraints
        constraints = extract_constraint_names(filepath)
        drop_conflicting_constraints(constraints)

        # Restore using mysql (backup file will DROP and CREATE the table)
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


def _run_restore_job14(job_id, filepath, table_name, user_id):
    try:
        # Optionally create a pre‑restore backup
        pre_backup = create_pre_restore_backup(table_name)
        print(f"[RESTORE] Pre-restore backup: {pre_backup}")

        # Drop any conflicting constraints (optional, but safe)
        constraints = extract_constraint_names(filepath)
        drop_conflicting_constraints(constraints)

        # Restore using mysql (the backup file will drop and recreate the table)
        success = run_mysql_restore(filepath)
        if success:
            restore_jobs[job_id] = {'status': 'SUCCESS', 'pre_backup': pre_backup}
            log_action(user_id, 'RESTORE', 'SUCCESS', table_name=table_name, backup_file=os.path.basename(filepath))
        else:
            restore_jobs[job_id] = {'status': 'FAILED', 'error': 'MySQL restore command failed'}
            log_action(...)
    except Exception as e:
        restore_jobs[job_id] = {'status': 'FAILED', 'error': str(e)}
        log_action(...)
        
def _run_restore_job9(job_id, filepath, table_name, user_id):
    try:
        # Optionally create a pre‑restore backup
        pre_backup = create_pre_restore_backup(table_name)
        print(f"[RESTORE] Pre-restore backup: {pre_backup}")

        # Drop any conflicting constraints (optional, but safe)
        constraints = extract_constraint_names(filepath)
        drop_conflicting_constraints(constraints)

        # Restore using mysql (the backup file will drop and recreate the table)
        success = run_mysql_restore(filepath)
        if success:
            restore_jobs[job_id] = {'status': 'SUCCESS', 'pre_backup': pre_backup}
            log_action(user_id, 'RESTORE', 'SUCCESS', table_name=table_name, backup_file=os.path.basename(filepath))
        else:
            restore_jobs[job_id] = {'status': 'FAILED', 'error': 'MySQL restore command failed'}
            log_action(...)
    except Exception as e:
        restore_jobs[job_id] = {'status': 'FAILED', 'error': str(e)}
        log_action(...)



@csrf_exempt
@require_http_methods(["POST"])
def restore_start(request):
    try:
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

        # Start background thread – pass the user object
        thread = threading.Thread(
            target=_run_restore_job,
            args=(job_id, filepath, table_name, request.user)
        )
        thread.start()

        return JsonResponse({'job_id': job_id})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
    
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

@csrf_exempt
@require_http_methods(["GET"])
def restore_status(request, job_id):
    # No authentication check – public endpoint
    job = restore_jobs.get(job_id)
    if not job:
        return JsonResponse({'status': 'NOT_FOUND'}, status=404)
    return JsonResponse(job)

def restore_status23(request, job_id):
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    job = restore_jobs.get(job_id)
    if not job:
        return JsonResponse({'status': 'NOT_FOUND'}, status=404)
    return JsonResponse(job)

def restore_status1(request, job_id):
    job = restore_jobs.get(job_id)
    if not job:
        return JsonResponse({'status': 'NOT_FOUND'}, status=404)
    return JsonResponse(job)

# ----------------------------------------------------------------------
# Safe restore (two-step with progress bars)
# ----------------------------------------------------------------------
safe_restore_jobs = {}
copy_jobs = {}

def _run_safe_restore(job_id, filepath, filename, user_id):
    try:
        update_safe_restore_progress(job_id, 'CREATING_TEMP_DB', 5)
        temp_db = _create_temp_database()
        safe_restore_jobs[job_id]['temp_db'] = temp_db
        update_safe_restore_progress(job_id, 'RESTORING_BACKUP', 20)
        success = run_mysql_restore(filepath, target_db=temp_db)
        if not success:
            raise Exception("MySQL restore to temp database failed")
        update_safe_restore_progress(job_id, 'COMPLETED', 100)
        log_action(user_id, 'SAFE_RESTORE_PREP', 'SUCCESS', backup_file=filename, details=f"Temp DB: {temp_db}")
    except Exception as e:
        update_safe_restore_progress(job_id, 'FAILED', None, error=str(e))
        log_action(user_id, 'SAFE_RESTORE_PREP', 'FAILURE', backup_file=filename, details=str(e))

def update_safe_restore_progress(job_id, status, percent, error=None):
    safe_restore_jobs[job_id] = {
        'status': status,
        'percent': percent,
        'error': error,
        'temp_db': safe_restore_jobs.get(job_id, {}).get('temp_db')
    }

@staff_member_required
def safe_restore_start(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({'error': 'Not authenticated'}, status=403)
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    filename = request.POST.get('backup_file')
    if not filename:
        return JsonResponse({'error': 'No file specified'}, status=400)
    filepath = os.path.join(settings.BACKUP_DIR, filename)
    if not os.path.exists(filepath):
        return JsonResponse({'error': 'File not found'}, status=404)
    job_id = str(uuid.uuid4())
    safe_restore_jobs[job_id] = {'status': 'STARTING', 'percent': 0}
    thread = threading.Thread(target=_run_safe_restore, args=(job_id, filepath, filename, request.user.id))
    thread.start()
    return JsonResponse({'job_id': job_id})


@staff_member_required
def restore_manual_upload(request):
    """Alternative restore by uploading a backup file (not from list)"""
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    sql_file = request.FILES.get('sql_file')
    if not sql_file:
        messages.error(request, "No file uploaded.")
        return redirect('BackupRestore:backup_panel')
    # Save uploaded file temporarily
    temp_path = os.path.join(settings.BACKUP_DIR, 'upload_temp.sql')
    with open(temp_path, 'wb+') as dest:
        for chunk in sql_file.chunks():
            dest.write(chunk)
    # Then treat it as a normal restore (we need the filename)
    # For simplicity, we move it to backups with a timestamp name
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    new_name = f"uploaded_{timestamp}.sql"
    new_path = os.path.join(settings.BACKUP_DIR, new_name)
    os.rename(temp_path, new_path)
    # Now redirect to restore action with that file
    return redirect(f"?backup_file={new_name}")  # simple, but implement proper GET handling

@staff_member_required
def backup_logs(request):
    logs = BackupLog.objects.all()[:100]
    return render(request, 'BackupRestore/backup_logs.html', {'logs': logs})


@staff_member_required
def restore_from_file(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    filename = request.POST.get('backup_file')
    if not filename:
        messages.error(request, "No backup file specified.")
        return redirect('BackupRestore:backup_panel')
    filepath = os.path.join(settings.BACKUP_DIR, filename)
    if not os.path.exists(filepath):
        messages.error(request, "Backup file not found.")
        return redirect('BackupRestore:backup_panel')

    params = get_db_connection_params()
    cmd = [
        'mysql',
        '-h', params['host'],
        '-P', str(params['port']),
        '-u', params['user'],
        f'-p{params["password"]}',
        params['name'],
    ]
    try:
        with open(filepath, 'r') as f:
            subprocess.run(cmd, stdin=f, check=True)
        messages.success(request, f"Database restored from {filename}")
    except subprocess.CalledProcessError as e:
        messages.error(request, f"Restore failed: {e}")
    return redirect('BackupRestore:backup_panel')


@staff_member_required
def download_backup(request, filename):
    filepath = os.path.join(settings.BACKUP_DIR, filename)
    if not os.path.exists(filepath):
        messages.error(request, "File not found.")
        return redirect('BackupRestore:backup_panel')
    with open(filepath, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/sql')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@staff_member_required
def safe_restore_status(request, job_id):
    job = safe_restore_jobs.get(job_id)
    if not job:
        return JsonResponse({'status': 'NOT_FOUND'}, status=404)
    return JsonResponse(job)

@staff_member_required
def safe_restore_step2(request):
    job_id = request.GET.get('job_id')
    if not job_id:
        messages.error(request, "No job ID provided.")
        return redirect('BackupRestore:backup_panel')
    job = safe_restore_jobs.get(job_id)
    if not job or job.get('status') != 'COMPLETED':
        messages.error(request, "Restore preparation not completed. Please start over.")
        return redirect('BackupRestore:backup_panel')
    temp_db = job.get('temp_db')
    if not temp_db:
        messages.error(request, "Temporary database not found.")
        return redirect('BackupRestore:backup_panel')
    with connection.cursor() as cursor:
        cursor.execute("SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA = %s", [temp_db])
        temp_tables = [row[0] for row in cursor.fetchall()]
    table_status = []
    for tbl in temp_tables:
        exists_in_prod = _table_exists_in_production(tbl)
        table_status.append({
            'name': tbl,
            'exists': exists_in_prod,
            'will_replace': not exists_in_prod,
        })
    context = {
        'filename': os.path.basename(job.get('backup_file', 'unknown')),
        'tables': table_status,
        'temp_db': temp_db,
        'job_id': job_id,
    }
    return render(request, 'BackupRestore/safe_restore_select_tables.html', context)

def _run_copy_tables(job_id, temp_db, selected_tables, replace_tables, drop_temp_db, user_id, filename):
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
    if drop_temp_db == 'on':
        with connection.cursor() as cursor:
            cursor.execute(f"DROP DATABASE IF EXISTS `{temp_db}`")
    copy_jobs[job_id]['status'] = 'COMPLETED'
    copy_jobs[job_id]['percent'] = 100
    copy_jobs[job_id]['success_tables'] = success
    copy_jobs[job_id]['failed_tables'] = failed
    log_action(user_id, 'SAFE_RESTORE_COPY', 'SUCCESS' if not failed else 'PARTIAL',
               details=f"File: {filename}, Tables copied: {success}, Failed: {failed}")

@staff_member_required
def safe_restore_copy_start(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    selected_tables = request.POST.getlist('selected_tables')
    replace_tables = request.POST.getlist('replace_table')
    drop_temp_db = request.POST.get('drop_temp_db', 'off')
    temp_db = request.POST.get('temp_db')
    job_id = request.POST.get('job_id')
    filename = request.POST.get('filename')
    if not selected_tables or not temp_db:
        return JsonResponse({'error': 'Missing parameters'}, status=400)
    copy_job_id = str(uuid.uuid4())
    copy_jobs[copy_job_id] = {'status': 'RUNNING', 'percent': 0, 'current_table': ''}
    thread = threading.Thread(
        target=_run_copy_tables,
        args=(copy_job_id, temp_db, selected_tables, replace_tables, drop_temp_db, request.user.id, filename)
    )
    thread.start()
    return JsonResponse({'copy_job_id': copy_job_id})

@staff_member_required
def copy_status(request, copy_job_id):
    job = copy_jobs.get(copy_job_id)
    if not job:
        return JsonResponse({'status': 'NOT_FOUND'}, status=404)
    return JsonResponse(job)

# ----------------------------------------------------------------------
# Backup views (synchronous, fast)
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
def safe_restore_step1(request):
    """Step 1: Accept backup file, create temp DB, restore backup into it."""
    filename = request.GET.get('file')
    if not filename:
        messages.error(request, "No backup file specified.")
        return redirect('BackupRestore:backup_panel')
    filepath = os.path.join(settings.BACKUP_DIR, filename)
    if not os.path.exists(filepath):
        messages.error(request, "Backup file not found.")
        return redirect('BackupRestore:backup_panel')

    # Store filepath in session for next steps
    request.session['safe_restore_file'] = filepath
    request.session['safe_restore_filename'] = filename

    # Already have a temp DB from previous attempt? Clean it first.
    temp_db = request.session.get('safe_restore_temp_db')
    if temp_db:
        with connection.cursor() as cursor:
            cursor.execute(f"DROP DATABASE IF EXISTS `{temp_db}`")

    # Create new temp database and restore
    temp_db = _create_temp_database()
    try:
        _restore_to_temp_db(filepath, temp_db)
        request.session['safe_restore_temp_db'] = temp_db
        messages.success(request, f"Backup loaded into temporary area. Now select tables to copy.")
        return redirect('BackupRestore:safe_restore_step2')
    except Exception as e:
        messages.error(request, f"Failed to prepare temporary restore: {e}")
        return redirect('BackupRestore:backup_panel')

@staff_member_required
def safe_restore_step2(request):
    """Step 2: Show list of tables from temp DB, allow selection."""
    temp_db = request.session.get('safe_restore_temp_db')
    if not temp_db:
        messages.error(request, "No temporary restore session found. Please start over.")
        return redirect('BackupRestore:backup_panel')

    # Get tables from temp database
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA = %s", [temp_db])
        temp_tables = [row[0] for row in cursor.fetchall()]

    table_status = []
    for tbl in temp_tables:
        exists_in_prod = _table_exists_in_production(tbl)
        table_status.append({
            'name': tbl,
            'exists': exists_in_prod,
            'will_replace': not exists_in_prod,  # new tables auto-checked
        })

    context = {
        'filename': request.session.get('safe_restore_filename'),
        'tables': table_status,
        'temp_db': temp_db,
    }
    return render(request, 'BackupRestore/safe_restore_select_tables.html', context)

@staff_member_required
def safe_restore_copy(request):
    """Step 3: Copy selected tables from temp DB to production."""
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    temp_db = request.session.get('safe_restore_temp_db')
    if not temp_db:
        messages.error(request, "Session expired. Please start over.")
        return redirect('BackupRestore:backup_panel')

    selected_tables = request.POST.getlist('selected_tables')
    replace_checks = request.POST.getlist('replace_table')  # list of table names to replace

    if not selected_tables:
        messages.error(request, "No tables selected.")
        return redirect('BackupRestore:safe_restore_step2')

    success_tables = []
    failed_tables = []
    with connection.cursor() as cursor:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        for table in selected_tables:
            try:
                if table in replace_checks:
                    # Drop existing production table
                    cursor.execute(f"DROP TABLE IF EXISTS `{table}`")
                # Copy table from temp DB to production
                cursor.execute(f"CREATE TABLE `{table}` LIKE `{temp_db}`.`{table}`")
                cursor.execute(f"INSERT INTO `{table}` SELECT * FROM `{temp_db}`.`{table}`")
                success_tables.append(table)
            except Exception as e:
                failed_tables.append(f"{table} ({str(e)})")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

    # Log the action
    log_action(
        request.user, 'SAFE_RESTORE',
        'SUCCESS' if not failed_tables else 'PARTIAL',
        details=f"File: {request.session.get('safe_restore_filename')}, Tables copied: {', '.join(success_tables)}. Failed: {', '.join(failed_tables)}",
        request=request
    )

    # Optionally drop temp database
    if request.POST.get('drop_temp_db') == 'on':
        with connection.cursor() as cursor:
            cursor.execute(f"DROP DATABASE IF EXISTS `{temp_db}`")
        messages.info(request, "Temporary database removed.")
    else:
        messages.info(request, f"Temporary database '{temp_db}' kept. You can manually drop it later.")

    # Clear session variables
    del request.session['safe_restore_temp_db']
    del request.session['safe_restore_file']
    del request.session['safe_restore_filename']

    if failed_tables:
        messages.warning(request, f"Copied {len(success_tables)} tables. Errors: {', '.join(failed_tables)}")
    else:
        messages.success(request, f"Successfully copied {len(success_tables)} tables to your live database.")

    return redirect('BackupRestore:backup_panel')
    
def _run_restore_job_sync(filepath, table_name, user_id):
    import traceback
    try:
        print(f"[RESTORE] Starting restore for table {table_name}")
        pre_backup = create_pre_restore_backup(table_name)
        print(f"[RESTORE] Pre-restore backup created: {pre_backup}")
        
        constraints = extract_constraint_names(filepath)
        if constraints:
            print(f"[RESTORE] Dropping constraints: {constraints}")
            drop_conflicting_constraints(constraints)
        
        with connection.cursor() as cursor:
            cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`;")
        print(f"[RESTORE] Dropped table {table_name}")
        
        success = run_mysql_restore(filepath)
        if success:
            print(f"[RESTORE] Restore completed successfully")
            log_action(user_id, 'RESTORE', 'SUCCESS', table_name=table_name, backup_file=os.path.basename(filepath))
        else:
            raise Exception("MySQL restore command failed")
    except Exception as e:
        print(f"[RESTORE] Failed: {traceback.format_exc()}")
        log_action(user_id, 'RESTORE', 'FAILURE', table_name=table_name, backup_file=os.path.basename(filepath), details=str(e))
        raise
    
def log_action(user, action, result, table_name=None, backup_file=None, details=None, request=None):
    # If user is an ID, retrieve the User object
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

import re
import uuid
import threading
import tempfile
from django.db import connection
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages

# -------------------------------------------------------------
# Helper: extract table names from a backup file
# -------------------------------------------------------------
def get_table_names_from_backup(filepath):
    tables = set()
    with open(filepath, 'r', encoding='utf8', errors='ignore') as f:
        for line in f:
            m = re.search(r'CREATE TABLE `([^`]+)`', line)
            if m:
                tables.add(m.group(1))
    return list(tables)

# -------------------------------------------------------------
# Helper: restore backup into a temporary table prefix
# -------------------------------------------------------------
def restore_to_temp_tables(filepath, temp_prefix):
    """
    Reads the SQL backup file and replaces each occurrence of the original
    table name with a temporary name (prefix + original name), then executes
    the modified SQL. Returns a mapping {original_table: temp_table}.
    """
    with open(filepath, 'r', encoding='utf8', errors='ignore') as f:
        sql = f.read()

    # Find all original table names (from CREATE TABLE statements)
    orig_tables = get_table_names_from_backup(filepath)
    mapping = {}
    for orig in orig_tables:
        temp_name = f"{temp_prefix}{orig}"
        mapping[orig] = temp_name
        # Replace CREATE TABLE `orig` with CREATE TABLE `temp_name`
        sql = re.sub(rf'CREATE TABLE `{re.escape(orig)}`', f'CREATE TABLE `{temp_name}`', sql)
        sql = re.sub(rf'INSERT INTO `{re.escape(orig)}`', f'INSERT INTO `{temp_name}`', sql)
        sql = re.sub(rf'ALTER TABLE `{re.escape(orig)}`', f'ALTER TABLE `{temp_name}`', sql)
        sql = re.sub(rf'DROP TABLE IF EXISTS `{re.escape(orig)}`', f'DROP TABLE IF EXISTS `{temp_name}`', sql)
        # add more patterns as needed

    # Execute the modified SQL using MySQL
    params = get_db_params()
    cmd = [
        'mysql',
        '-h', params['host'],
        '-P', str(params['port']),
        '-u', params['user'],
        f'-p{params["password"]}',
        '--init-command', 'SET FOREIGN_KEY_CHECKS=0;',
        params['name'],
    ]
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as tmp:
        tmp.write(sql)
        tmp_path = tmp.name
    try:
        with open(tmp_path, 'r') as f:
            subprocess.run(cmd, stdin=f, check=True, timeout=3600)
    finally:
        os.unlink(tmp_path)
    return mapping

# -------------------------------------------------------------
# Step 1: Start safe restore (no database creation)
# -------------------------------------------------------------
safe_restore_jobs = {}  # job_id -> {status, percent, temp_prefix, mapping, ...}

def _run_safe_restore(job_id, filepath, filename, user_id):
    try:
        update_safe_restore_progress(job_id, 'CREATING_TEMP_TABLES', 10)
        temp_prefix = f"temp_{uuid.uuid4().hex[:8]}_"
        mapping = restore_to_temp_tables(filepath, temp_prefix)
        safe_restore_jobs[job_id].update({
            'status': 'TABLES_READY',
            'percent': 50,
            'temp_prefix': temp_prefix,
            'mapping': mapping,
        })
        log_action(user_id, 'SAFE_RESTORE_PREP', 'SUCCESS', backup_file=filename, details=f"Temp prefix: {temp_prefix}")
    except Exception as e:
        safe_restore_jobs[job_id]['status'] = 'FAILED'
        safe_restore_jobs[job_id]['error'] = str(e)
        log_action(user_id, 'SAFE_RESTORE_PREP', 'FAILURE', backup_file=filename, details=str(e))

@csrf_exempt
@require_http_methods(["POST"])
def safe_restore_start(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({'error': 'Authentication required'}, status=403)
    filename = request.POST.get('backup_file')
    if not filename:
        return JsonResponse({'error': 'No file'}, status=400)
    filepath = os.path.join(settings.BACKUP_DIR, filename)
    if not os.path.exists(filepath):
        return JsonResponse({'error': 'File not found'}, status=404)

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

# -------------------------------------------------------------
# Step 2: Show tables available in the temporary store
# -------------------------------------------------------------
def safe_restore_step2(request):
    job_id = request.GET.get('job_id')
    if not job_id:
        messages.error(request, "No job ID")
        return redirect('BackupRestore:backup_panel')
    job = safe_restore_jobs.get(job_id)
    if not job or job['status'] not in ['TABLES_READY', 'COMPLETED']:
        messages.error(request, "Restore preparation not ready")
        return redirect('BackupRestore:backup_panel')
    temp_prefix = job['temp_prefix']
    mapping = job['mapping']  # {original: temp}
    # Get list of original table names
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
            'will_replace': not exists,  # new tables auto-checked
        })
    context = {
        'filename': job.get('backup_file', 'unknown'),
        'tables': table_status,
        'job_id': job_id,
        'temp_prefix': temp_prefix,
    }
    return render(request, 'BackupRestore/safe_restore_select_tables.html', context)

# -------------------------------------------------------------
# Step 3: Copy selected tables from temp to production
# -------------------------------------------------------------
copy_jobs = {}

def _run_copy_tables(job_id, temp_prefix, selected_tables, replace_tables, user_id, filename):
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
                # Copy structure and data
                cursor.execute(f"CREATE TABLE `{table}` LIKE `{temp_table}`")
                cursor.execute(f"INSERT INTO `{table}` SELECT * FROM `{temp_table}`")
                success.append(table)
            except Exception as e:
                failed.append(f"{table}: {str(e)}")
        # Drop all temp tables with the same prefix
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
    temp_prefix = request.POST.get('temp_prefix')
    job_id = request.POST.get('job_id')
    filename = request.POST.get('filename')
    if not selected_tables or not temp_prefix:
        return JsonResponse({'error': 'Missing parameters'}, status=400)
    copy_job_id = str(uuid.uuid4())
    copy_jobs[copy_job_id] = {'status': 'RUNNING', 'percent': 0, 'current_table': ''}
    thread = threading.Thread(target=_run_copy_tables, args=(copy_job_id, temp_prefix, selected_tables, replace_tables, request.user.id, filename))
    thread.start()
    return JsonResponse({'copy_job_id': copy_job_id})

@csrf_exempt
@require_http_methods(["GET"])
def copy_status(request, copy_job_id):
    job = copy_jobs.get(copy_job_id)
    if not job:
        return JsonResponse({'status': 'NOT_FOUND'}, status=404)
    return JsonResponse(job)