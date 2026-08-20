# CoreApp/views_backup.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import FileResponse, Http404
from django.utils import timezone
import os
from .models import DatabaseBackup
from .services.backup_service import DatabaseBackupService

@staff_member_required
def backup_dashboard(request):
    """Backup management dashboard"""
    
    service = DatabaseBackupService(request.user)
    backups = DatabaseBackup.objects.all().order_by('-backup_started')[:20]
    backup_files = service.list_backups()
    
    context = {
        'backups': backups,
        'backup_files': backup_files,
        'today': timezone.now(),
    }
    return render(request, 'core/backup_dashboard.html', context)


@staff_member_required
def backup_full(request):
    """Backup entire database"""
    
    if request.method == 'POST':
        service = DatabaseBackupService(request.user)
        result = service.backup_all_tables()
        
        if result['success']:
            messages.success(request, f"Full database backup created successfully!")
        else:
            messages.error(request, f"Backup failed: {result['error']}")
        
        return redirect('core:backup_dashboard')
    
    return redirect('core:backup_dashboard')


@staff_member_required
def backup_app(request, app_name):
    """Backup specific app tables"""
    
    if request.method == 'POST':
        service = DatabaseBackupService(request.user)
        result = service.backup_app_tables(app_name)
        
        if result['success']:
            messages.success(request, f"Backup of {app_name} completed!")
        else:
            messages.error(request, f"Backup failed: {result['error']}")
        
        return redirect('core:backup_dashboard')
    
    return redirect('core:backup_dashboard')


@staff_member_required
def backup_tables(request):
    """Backup selected tables"""
    
    if request.method == 'POST':
        tables = request.POST.getlist('tables')
        
        if not tables:
            messages.error(request, "Please select at least one table")
            return redirect('core:backup_dashboard')
        
        service = DatabaseBackupService(request.user)
        result = service.backup_specific_tables(tables)
        
        if result['success']:
            messages.success(request, f"Backup of {len(tables)} table(s) completed!")
        else:
            messages.error(request, f"Backup failed: {result['error']}")
        
        return redirect('core:backup_dashboard')
    
    return redirect('core:backup_dashboard')


@staff_member_required
def download_backup(request, backup_id):
    """Download a backup file"""
    
    backup = get_object_or_404(DatabaseBackup, id=backup_id)
    
    if not backup.backup_file:
        raise Http404("Backup file not found")
    
    return FileResponse(backup.backup_file, as_attachment=True, filename=backup.backup_name)


@staff_member_required
def delete_backup(request, backup_id):
    """Delete a backup record and file"""
    
    if request.method == 'POST':
        backup = get_object_or_404(DatabaseBackup, id=backup_id)
        
        # Delete the physical file
        if backup.backup_file:
            backup.backup_file.delete()
        
        backup.delete()
        messages.success(request, "Backup deleted successfully")
    
    return redirect('core:backup_dashboard')


@staff_member_required
def restore_backup(request, backup_id):
    """Restore database from backup"""
    
    if request.method == 'POST':
        backup = get_object_or_404(DatabaseBackup, id=backup_id)
        
        if not backup.backup_file:
            messages.error(request, "Backup file not found")
            return redirect('core:backup_dashboard')
        
        service = DatabaseBackupService(request.user)
        result = service.restore_backup(backup.backup_file.path)
        
        if result['success']:
            messages.success(request, "Database restored successfully!")
        else:
            messages.error(request, f"Restore failed: {result['error']}")
        
        return redirect('core:backup_dashboard')
    
    return redirect('core:backup_dashboard')

# CoreApp/views_backup.py - Add restore views

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import FileResponse, Http404
from django.utils import timezone
from django.db import connection
import os
from .models import DatabaseBackup
from .services.backup_service import DatabaseBackupService

# ... existing views ...

@staff_member_required
def restore_preview(request, backup_id):
    """Preview backup contents before restoring"""
    
    backup = get_object_or_404(DatabaseBackup, id=backup_id)
    
    if not backup.backup_file:
        messages.error(request, "Backup file not found")
        return redirect('core:backup_dashboard')
    
    # Read first few lines of backup file to preview
    preview_lines = []
    table_list = []
    
    try:
        with open(backup.backup_file.path, 'r', encoding='utf-8', errors='ignore') as f:
            for i, line in enumerate(f):
                if i < 50:  # Read first 50 lines
                    preview_lines.append(line.strip())
                if 'CREATE TABLE' in line:
                    table_name = line.split('CREATE TABLE')[1].split('(')[0].strip().strip('`')
                    if table_name not in table_list:
                        table_list.append(table_name)
                if i > 500:  # Don't read too much
                    break
    except Exception as e:
        preview_lines = [f"Error reading file: {e}"]
    
    context = {
        'backup': backup,
        'preview_lines': preview_lines,
        'table_list': table_list,
        'table_count': len(table_list),
    }
    return render(request, 'core/restore_preview.html', context)


@staff_member_required
def restore_backup(request, backup_id):
    """Restore database from backup"""
    
    if request.method == 'POST':
        backup = get_object_or_404(DatabaseBackup, id=backup_id)
        
        if not backup.backup_file:
            messages.error(request, "Backup file not found")
            return redirect('core:backup_dashboard')
        
        # Confirm option
        confirm = request.POST.get('confirm', '')
        drop_tables = request.POST.get('drop_tables', '') == 'on'
        
        if confirm != 'YES':
            messages.error(request, "Please type 'YES' to confirm restore")
            return redirect('core:restore_preview', backup_id=backup_id)
        
        service = DatabaseBackupService(request.user)
        
        # Optionally drop tables before restore
        if drop_tables:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
                    # Get all tables
                    cursor.execute("SHOW TABLES;")
                    tables = [row[0] for row in cursor.fetchall()]
                    for table in tables:
                        cursor.execute(f"DROP TABLE IF EXISTS `{table}`;")
                    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
                messages.info(request, f"Dropped {len(tables)} existing tables")
            except Exception as e:
                messages.warning(request, f"Error dropping tables: {e}")
        
        # Perform restore
        result = service.restore_backup(backup.backup_file.path)
        
        if result['success']:
            messages.success(request, f"Database restored successfully from '{backup.backup_name}'!")
            
            # Create a restore record
            DatabaseBackup.objects.create(
                backup_name=f"RESTORE_{backup.backup_name}",
                status='COMPLETED',
                created_by=request.user,
                notes=f"Restored from backup: {backup.backup_name}"
            )
        else:
            messages.error(request, f"Restore failed: {result['error']}")
        
        return redirect('core:backup_dashboard')
    
    return redirect('core:backup_dashboard')


@staff_member_required
def restore_upload(request):
    """Upload and restore from a SQL file"""
    
    if request.method == 'POST':
        uploaded_file = request.FILES.get('backup_file')
        confirm = request.POST.get('confirm', '')
        
        if not uploaded_file:
            messages.error(request, "Please select a backup file")
            return redirect('core:backup_dashboard')
        
        if confirm != 'YES':
            messages.error(request, "Please type 'YES' to confirm restore")
            return redirect('core:backup_dashboard')
        
        # Save uploaded file
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        filename = f"uploaded_{timestamp}.sql"
        
        backup = DatabaseBackup.objects.create(
            backup_name=f"Uploaded backup - {uploaded_file.name}",
            status='RUNNING',
            created_by=request.user
        )
        
        backup.backup_file.save(filename, uploaded_file)
        backup.save()
        
        # Perform restore
        service = DatabaseBackupService(request.user)
        result = service.restore_backup(backup.backup_file.path)
        
        if result['success']:
            backup.status = 'COMPLETED'
            backup.backup_completed = timezone.now()
            backup.save()
            messages.success(request, "Database restored successfully from uploaded file!")
        else:
            backup.status = 'FAILED'
            backup.notes = result['error']
            backup.save()
            messages.error(request, f"Restore failed: {result['error']}")
        
        return redirect('core:backup_dashboard')
    
    return redirect('core:backup_dashboard')