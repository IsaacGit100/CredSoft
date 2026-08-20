import os
import subprocess
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse, HttpResponseNotAllowed
from django.db import connection
from django.utils import timezone

def get_db_connection_params():
    db = settings.DATABASES['default']
    return {
        'name': db['NAME'],
        'user': db['USER'],
        'password': db['PASSWORD'],
        'host': db.get('HOST', '127.0.0.1'),
        'port': db.get('PORT', '3306'),
    }

@staff_member_required
def backup_panel(request):
    """Display all tables and backup/restore options"""
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES;")
        tables = [row[0] for row in cursor.fetchall()]
    return render(request, 'BackupRestore/backup_panel.html', {'tables': tables})

@staff_member_required
def backup_all(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    params = get_db_connection_params()
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f"{params['name']}_full_{timestamp}.sql"
    backup_path = os.path.join(settings.BACKUP_DIR, backup_file)

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
        '-r', backup_path,
    ]
    try:
        subprocess.run(cmd, check=True)
        with open(backup_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/sql')
            response['Content-Disposition'] = f'attachment; filename="{backup_file}"'
        return response
    except Exception as e:
        messages.error(request, f"Backup failed: {e}")
        return redirect('BackupRestore:backup_panel')








@staff_member_required
def backup_all1(request):
    """Full database backup - POST only"""
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    
    params = get_db_connection_params()
    backup_file = f"{params['name']}_full_{timezone.now().strftime('%Y%m%d_%H%M%S')}.sql"
    backup_path = os.path.join(settings.BASE_DIR, backup_file)

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
        '-r', backup_path,
    ]

    try:
        subprocess.run(cmd, check=True)
        with open(backup_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/sql')
            response['Content-Disposition'] = f'attachment; filename="{backup_file}"'
        os.remove(backup_path)
        return response
    except subprocess.CalledProcessError as e:
        messages.error(request, f"Backup failed: {e}")
    except FileNotFoundError:
        messages.error(request, "mysqldump not found. Please install MySQL client tools.")
    return redirect('backuprestore:backup_panel')


@staff_member_required
def backup_table(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    table_name = request.POST.get('table_name', '').strip()
    if not table_name:
        messages.error(request, "No table selected.")
        return redirect('BackupRestore:backup_panel')
    params = get_db_connection_params()
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f"{table_name}_{timestamp}.sql"
    backup_path = os.path.join(settings.BACKUP_DIR, backup_file)

    os.makedirs(settings.BACKUP_DIR, exist_ok=True)

    cmd = [
        'mysqldump',
        '-h', params['host'],
        '-P', str(params['port']),
        '-u', params['user'],
        f'-p{params["password"]}',
        params['name'],
        table_name,
        '-r', backup_path,
    ]
    try:
        subprocess.run(cmd, check=True)
        with open(backup_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/sql')
            response['Content-Disposition'] = f'attachment; filename="{backup_file}"'
        return response
    except Exception as e:
        messages.error(request, f"Backup failed: {e}")
        return redirect('BackupRestore:backup_panel')


@staff_member_required
def backup_table1(request):
    """Single table backup - POST only"""
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    
    table_name = request.POST.get('table_name', '').strip()
    if not table_name:
        messages.error(request, "No table selected.")
        return redirect('backuprestore:backup_panel')

    params = get_db_connection_params()
    backup_file = f"{table_name}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.sql"
    backup_path = os.path.join(settings.BASE_DIR, backup_file)

    cmd = [
        'mysqldump',
        '-h', params['host'],
        '-P', str(params['port']),
        '-u', params['user'],
        f'-p{params["password"]}',
        params['name'],
        table_name,
        '-r', backup_path,
    ]

    try:
        subprocess.run(cmd, check=True)
        with open(backup_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/sql')
            response['Content-Disposition'] = f'attachment; filename="{backup_file}"'
        os.remove(backup_path)
        return response
    except subprocess.CalledProcessError as e:
        messages.error(request, f"Backup failed: {e}")
    except FileNotFoundError:
        messages.error(request, "mysqldump not found.")
    return redirect('BackupRestore:backup_panel')

@staff_member_required
def restore_table(request):
    """Restore single table from uploaded SQL file - POST only"""
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    table_name = request.POST.get('table_name', '').strip()
    sql_file = request.FILES.get('sql_file')
    if not table_name or not sql_file:
        messages.error(request, "Table name and file are required.")
        return redirect('BackupRestore:backup_panel')

    # Save uploaded file temporarily
    temp_path = os.path.join(settings.BASE_DIR, 'temp_restore.sql')
    with open(temp_path, 'wb+') as dest:
        for chunk in sql_file.chunks():
            dest.write(chunk)

    params = get_db_connection_params()

    # Optional truncation
    if request.POST.get('truncate') == 'on':
        try:
            with connection.cursor() as cursor:
                cursor.execute(f'TRUNCATE TABLE `{table_name}`;')
            messages.warning(request, f"Table `{table_name}` truncated before restore.")
        except Exception as e:
            messages.error(request, f"Truncate failed: {e}")
            os.remove(temp_path)
            return redirect('BackupRestore:backup_panel')

    # Restore using mysql command with stdin
    cmd = [
        'mysql',
        '-h', params['host'],
        '-P', str(params['port']),
        '-u', params['user'],
        f'-p{params["password"]}',
        params['name'],
    ]
    try:
        with open(temp_path, 'r') as f:
            subprocess.run(cmd, stdin=f, check=True)
        messages.success(request, f"Table '{table_name}' restored successfully.")
    except subprocess.CalledProcessError as e:
        messages.error(request, f"Restore failed: {e}")
    except FileNotFoundError:
        messages.error(request, "mysql client not found.")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
    return redirect('BackupRestore:backup_panel')

def list_backup_files():
    backups = []
    if not os.path.exists(settings.BACKUP_DIR):
        return backups
    for filename in os.listdir(settings.BACKUP_DIR):
        if filename.endswith('.sql'):
            filepath = os.path.join(settings.BACKUP_DIR, filename)
            stat = os.stat(filepath)
            # Determine backup type: full or single table
            if '_full_' in filename:
                backup_type = 'Full Database'
            else:
                # Assume first part before underscore is table name
                table_name = filename.split('_')[0]
                backup_type = f'Table: {table_name}'
            backups.append({
                'filename': filename,
                'filepath': filepath,
                'size': stat.st_size,
                'modified': timezone.datetime.fromtimestamp(stat.st_mtime),
                'type': backup_type,
            })
    # Sort by modified date descending
    backups.sort(key=lambda x: x['modified'], reverse=True)
    
    return backups

@staff_member_required
def backup_panel(request):
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES;")
        tables = [row[0] for row in cursor.fetchall()]
    backups = list_backup_files()
    return render(request, 'BackupRestore/backup_panel.html', {'tables': tables, 'backups': backups})


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

import os
import re
import subprocess
from datetime import datetime
from django.conf import settings
from django.db import connection, transaction
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.http import HttpResponseNotAllowed, JsonResponse
from django.core.cache import cache
from django.utils import timezone
from .models import BackupLog

def get_db_connection_params():
    db = settings.DATABASES['default']
    return {
        'name': db['NAME'],
        'user': db['USER'],
        'password': db['PASSWORD'],
        'host': db.get('HOST', '127.0.0.1'),
        'port': db.get('PORT', '3306'),
    }

def log_action(user, action, result, table_name=None, backup_file=None, details=None, request=None):
    ip = None
    if request:
        ip = request.META.get('REMOTE_ADDR')
    BackupLog.objects.create(
        user=user,
        action=action,
        result=result,
        table_name=table_name,
        backup_file=backup_file,
        details=details,
        ip_address=ip,
    )

# ---------- Helper functions (safety and restore) ----------
def _is_valid_sql_backup(filepath):
    if os.path.getsize(filepath) == 0:
        return False
    with open(filepath, 'r') as f:
        content = f.read(2000)
        if 'CREATE TABLE' not in content and 'INSERT INTO' not in content:
            return False
    return True

def _extract_table_name(filepath):
    with open(filepath, 'r') as f:
        for line in f:
            match = re.search(r'CREATE TABLE `([^`]+)`', line)
            if match:
                return match.group(1)
    return None

def _extract_constraint_names(filepath):
    constraints = []
    with open(filepath, 'r') as f:
        content = f.read()
        matches = re.findall(r'CONSTRAINT\s+`([^`]+)`\s+FOREIGN KEY', content, re.IGNORECASE)
        constraints.extend(matches)
    return constraints

def _check_safety_issues(table_name, constraint_names):
    issues = []
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT TABLE_NAME, CONSTRAINT_NAME
            FROM information_schema.KEY_COLUMN_USAGE
            WHERE REFERENCED_TABLE_SCHEMA = DATABASE()
            AND REFERENCED_TABLE_NAME = %s
        """, [table_name])
        refs = cursor.fetchall()
        if refs:
            issues.append(f"Other tables reference '{table_name}': {', '.join([r[0] for r in refs])}")
        for cname in constraint_names:
            cursor.execute("""
                SELECT TABLE_NAME FROM information_schema.TABLE_CONSTRAINTS
                WHERE CONSTRAINT_SCHEMA = DATABASE() AND CONSTRAINT_NAME = %s
            """, [cname])
            row = cursor.fetchone()
            if row:
                issues.append(f"Constraint '{cname}' exists on table '{row[0]}' (will be dropped).")
    return issues

def _drop_constraint_if_exists(constraint_name):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT TABLE_NAME FROM information_schema.TABLE_CONSTRAINTS
            WHERE CONSTRAINT_SCHEMA = DATABASE() AND CONSTRAINT_NAME = %s
        """, [constraint_name])
        row = cursor.fetchone()
        if row:
            table_name = row[0]
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
            cursor.execute(f"ALTER TABLE `{table_name}` DROP FOREIGN KEY `{constraint_name}`;")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
            return True
    return False

def _create_pre_restore_backup(table_name):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"pre_restore_{table_name}_{timestamp}.sql"
    backup_path = os.path.join(settings.BACKUP_DIR, backup_name)
    params = get_db_connection_params()
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
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return backup_path
    except subprocess.CalledProcessError:
        return None

def _run_mysql_restore(filepath):
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
            subprocess.run(cmd, stdin=f, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        return False

def _validate_restore(table_name):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`;")
        count = cursor.fetchone()[0]
        if count > 0:
            return {'success': True, 'message': f'{count} rows'}
        else:
            return {'success': False, 'error': 'Table is empty after restore.'}

def _set_maintenance_mode(enable):
    if enable:
        cache.set('maintenance_mode', True, timeout=None)
    else:
        cache.delete('maintenance_mode')

# ---------- Views ----------
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
    params = get_db_connection_params()
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f"{params['name']}_full_{timestamp}.sql"
    backup_path = os.path.join(settings.BACKUP_DIR, backup_file)
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
        '-r', backup_path,
    ]
    try:
        subprocess.run(cmd, check=True)
        with open(backup_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/sql')
            response['Content-Disposition'] = f'attachment; filename="{backup_file}"'
        log_action(request.user, 'BACKUP', 'SUCCESS', backup_file=backup_file, request=request)
        return response
    except Exception as e:
        log_action(request.user, 'BACKUP', 'FAILURE', details=str(e), request=request)
        messages.error(request, f"Backup failed: {e}")
        return redirect('BackupRestore:backup_panel')

@staff_member_required
def backup_table(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    table_name = request.POST.get('table_name', '').strip()
    if not table_name:
        messages.error(request, "No table selected.")
        return redirect('BackupRestore:backup_panel')
    params = get_db_connection_params()
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f"{table_name}_{timestamp}.sql"
    backup_path = os.path.join(settings.BACKUP_DIR, backup_file)
    os.makedirs(settings.BACKUP_DIR, exist_ok=True)

    cmd = [
        'mysqldump',
        '-h', params['host'],
        '-P', str(params['port']),
        '-u', params['user'],
        f'-p{params["password"]}',
        params['name'],
        table_name,
        '-r', backup_path,
    ]
    try:
        subprocess.run(cmd, check=True)
        with open(backup_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/sql')
            response['Content-Disposition'] = f'attachment; filename="{backup_file}"'
        log_action(request.user, 'BACKUP', 'SUCCESS', table_name=table_name, backup_file=backup_file, request=request)
        return response
    except Exception as e:
        log_action(request.user, 'BACKUP', 'FAILURE', table_name=table_name, details=str(e), request=request)
        messages.error(request, f"Backup failed: {e}")
        return redirect('BackupRestore:backup_panel')

@staff_member_required
def restore_from_file(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    filename = request.POST.get('backup_file')
    dry_run = request.POST.get('dry_run') == 'on'
    force = request.POST.get('force') == 'on'

    if not filename:
        messages.error(request, "No backup file specified.")
        return redirect('BackupRestore:backup_panel')

    filepath = os.path.join(settings.BACKUP_DIR, filename)
    if not os.path.exists(filepath):
        messages.error(request, "Backup file not found.")
        return redirect('BackupRestore:backup_panel')

    # Verify file integrity
    if not _is_valid_sql_backup(filepath):
        messages.error(request, "Backup file is corrupted or empty.")
        log_action(request.user, 'RESTORE', 'FAILURE', backup_file=filename, details="Corrupted backup file", request=request)
        return redirect('BackupRestore:backup_panel')

    # Extract metadata
    table_name = _extract_table_name(filepath)
    if not table_name:
        messages.error(request, "Could not determine target table from backup file.")
        log_action(request.user, 'RESTORE', 'FAILURE', backup_file=filename, details="No table name found", request=request)
        return redirect('BackupRestore:backup_panel')

    constraint_names = _extract_constraint_names(filepath)

    # Safety check
    safety_issues = _check_safety_issues(table_name, constraint_names)
    if safety_issues and not force:
        context = {
            'backup_file': filename,
            'table_name': table_name,
            'safety_issues': safety_issues,
            'constraint_names': constraint_names,
            'dry_run': dry_run,
        }
        return render(request, 'BackupRestore/restore_confirm.html', context)

    # Dry run – no actual changes
    if dry_run:
        log_action(request.user, 'DRY_RUN', 'SUCCESS', table_name=table_name, backup_file=filename,
                   details=f"Would restore {table_name} from {filename}", request=request)
        messages.info(request, f"DRY RUN – Would restore {table_name} from {filename}. No changes made.")
        return redirect('BackupRestore:backup_panel')

    # Pre‑restore backup
    pre_backup_path = _create_pre_restore_backup(table_name)
    if not pre_backup_path:
        log_action(request.user, 'RESTORE', 'FAILURE', table_name=table_name, backup_file=filename,
                   details="Failed to create pre‑restore backup", request=request)
        messages.error(request, "Failed to create pre‑restore backup. Restore aborted.")
        return redirect('BackupRestore:backup_panel')

    # Maintenance mode
    _set_maintenance_mode(True)

    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
                # Drop conflicting constraints
                for cname in constraint_names:
                    _drop_constraint_if_exists(cname)
                # Drop target table (backup will recreate)
                cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`;")
                cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

            # Restore using mysql command
            restore_ok = _run_mysql_restore(filepath)
            if not restore_ok:
                raise Exception("MySQL restore command failed.")

        # Post‑restore validation
        validation = _validate_restore(table_name)
        if validation['success']:
            messages.success(request, f"Restore successful. {validation['message']}")
            log_action(request.user, 'RESTORE', 'SUCCESS', table_name=table_name, backup_file=filename,
                       details=f"Restored {validation['message']}", request=request)
        else:
            messages.error(request, f"Restore completed but validation failed: {validation['error']}")
            log_action(request.user, 'RESTORE', 'FAILURE', table_name=table_name, backup_file=filename,
                       details=validation['error'], request=request)

    except Exception as e:
        messages.error(request, f"Restore failed: {str(e)}")
        log_action(request.user, 'RESTORE', 'FAILURE', table_name=table_name, backup_file=filename,
                   details=str(e), request=request)
    finally:
        _set_maintenance_mode(False)
        cache.clear()

    return redirect('BackupRestore:backup_panel')


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

import threading
from .models import RestoreJob
import uuid

def run_restore(job_id, filepath, table_name, db_params):
    # Actual restore logic (same as before, but update job status)
    try:
        # ... mysql restore command ...
        job.status = 'SUCCESS'
    except Exception as e:
        job.status = 'FAILED'
        job.error_message = str(e)
    finally:
        job.completed_at = timezone.now()
        job.save()

@staff_member_required
def start_restore(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    filename = request.POST.get('backup_file')
    # ... validation ...
    job_id = str(uuid.uuid4())
    job = RestoreJob.objects.create(
        job_id=job_id,
        backup_file=filename,
        created_by=request.user,
        status='PENDING'
    )
    # Start background thread
    thread = threading.Thread(
        target=run_restore,
        args=(job_id, filepath, table_name, get_db_connection_params())
    )
    thread.start()
    return JsonResponse({'job_id': job_id, 'status': 'started'})


def restore_status(request, job_id):
    job = get_object_or_404(RestoreJob, job_id=job_id)
    return JsonResponse({
        'status': job.status,
        'error_message': job.error_message,
        'completed_at': job.completed_at
    })
    
    
    

import tempfile
from django.db import connection, transaction
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from .models import BackupLog

def _create_temp_database():
    """Create a temporary database name with timestamp"""
    ts = timezone.now().strftime('%Y%m%d_%H%M%S')
    temp_db_name = f"CredDb_temp_{ts}"
    with connection.cursor() as cursor:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{temp_db_name}`")
    return temp_db_name

def _restore_to_temp_db(backup_filepath, temp_db_name):
    """Restore the backup file into the temporary database"""
    params = get_db_params()
    cmd = [
        'mysql',
        '-h', params['host'],
        '-P', str(params['port']),
        '-u', params['user'],
        f'-p{params["password"]}',
        temp_db_name,
    ]
    with open(backup_filepath, 'r', encoding='utf8', errors='ignore') as f:
        subprocess.run(cmd, stdin=f, check=True, capture_output=True)
    return True

def _get_tables_in_database(db_name):
    """Return list of table names in the given database"""
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA = %s", [db_name])
        return [row[0] for row in cursor.fetchall()]

def _table_exists_in_production(table_name):
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM information_schema.TABLES WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s", [table_name])
        return cursor.fetchone()[0] > 0

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
    