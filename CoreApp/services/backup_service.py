# CoreApp/services/backup_service.py
import os
import subprocess
from datetime import datetime
from django.conf import settings
from django.core.files import File
from ..models import DatabaseBackup

class DatabaseBackupService:
    """Service to handle MySQL database backups"""
    
    def __init__(self, user=None):
        self.user = user
        self.db_name = settings.DATABASES['default']['NAME']
        self.db_user = settings.DATABASES['default']['USER']
        self.db_password = settings.DATABASES['default']['PASSWORD']
        self.db_host = settings.DATABASES['default'].get('HOST', 'localhost')
        self.db_port = settings.DATABASES['default'].get('PORT', '3306')
        
        # Backup directory
        self.backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def get_backup_filename(self, tables=None):
        """Generate backup filename"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if tables:
            table_str = '_'.join(tables[:3])  # Max 3 table names
            return f"backup_{table_str}_{timestamp}.sql"
        return f"backup_full_{timestamp}.sql"
    
    def backup_specific_tables(self, tables):
        """Backup specific tables"""
        backup = None
        try:
            # Create backup record
            backup = DatabaseBackup.objects.create(
                backup_name=f"Backup of {', '.join(tables)}",
                status='RUNNING',
                created_by=self.user
            )
            
            # Build mysqldump command
            cmd = [
                'mysqldump',
                f'--host={self.db_host}',
                f'--port={self.db_port}',
                f'--user={self.db_user}',
                f'--password={self.db_password}',
                self.db_name,
            ]
            cmd.extend(tables)
            
            # Add options
            cmd.append('--single-transaction')
            cmd.append('--routines')
            cmd.append('--triggers')
            
            # Output file
            filename = self.get_backup_filename(tables)
            filepath = os.path.join(self.backup_dir, filename)
            cmd.append(f'--result-file={filepath}')
            
            # Run command
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Backup successful
                backup.status = 'COMPLETED'
                backup.backup_name = filename
                backup.backup_completed = datetime.now()
                backup.tables_backup = ', '.join(tables)
                
                # Get file size
                if os.path.exists(filepath):
                    backup.file_size = os.path.getsize(filepath)
                    
                    # Save file to Django's FileField
                    with open(filepath, 'rb') as f:
                        backup.backup_file.save(filename, File(f), save=False)
                
                backup.save()
                return {'success': True, 'backup': backup, 'filepath': filepath}
            else:
                raise Exception(result.stderr)
                
        except Exception as e:
            if backup:
                backup.status = 'FAILED'
                backup.notes = str(e)
                backup.save()
            return {'success': False, 'error': str(e)}
    
    def backup_all_tables(self):
        """Backup entire database"""
        return self.backup_specific_tables([])  # Empty list = all tables
    
    def backup_app_tables(self, app_name):
        """Backup all tables for a specific app"""
        from django.apps import apps
        app_config = apps.get_app_config(app_name)
        tables = []
        
        for model in app_config.get_models():
            tables.append(model._meta.db_table)
        
        return self.backup_specific_tables(tables)
    
    def list_backups(self):
        """List all backup files"""
        backups = []
        for file in os.listdir(self.backup_dir):
            if file.endswith('.sql'):
                filepath = os.path.join(self.backup_dir, file)
                backups.append({
                    'name': file,
                    'size': os.path.getsize(filepath),
                    'size_mb': round(os.path.getsize(filepath) / (1024 * 1024), 2),
                    'modified': datetime.fromtimestamp(os.path.getmtime(filepath))
                })
        return sorted(backups, key=lambda x: x['modified'], reverse=True)
    
    def restore_backup(self, backup_file):
        """Restore database from backup file"""
        try:
            cmd = [
                'mysql',
                f'--host={self.db_host}',
                f'--port={self.db_port}',
                f'--user={self.db_user}',
                f'--password={self.db_password}',
                self.db_name,
                f'--execute=source {backup_file}'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {'success': True, 'message': 'Restore completed'}
            else:
                return {'success': False, 'error': result.stderr}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
# CoreApp/services/backup_service.py - Add restore method

import subprocess
import os
from django.conf import settings
from django.core.files import File

class DatabaseBackupService:
    # ... existing code ...
    
    def restore_backup(self, backup_file_path):
        """Restore database from backup file"""
        try:
            # Build mysql command to restore
            cmd = [
                'mysql',
                f'--host={self.db_host}',
                f'--port={self.db_port}',
                f'--user={self.db_user}',
                f'--password={self.db_password}',
                self.db_name,
                f'--execute=source {backup_file_path}'
            ]
            
            # Run command
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)  # 5 minute timeout
            
            if result.returncode == 0:
                return {'success': True, 'message': 'Database restored successfully'}
            else:
                error_msg = result.stderr if result.stderr else result.stdout
                return {'success': False, 'error': error_msg}
                
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Restore operation timed out (5 minutes)'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def restore_from_backup_record(self, backup_record):
        """Restore from a DatabaseBackup record"""
        if not backup_record.backup_file:
            return {'success': False, 'error': 'Backup file not found'}
        
        return self.restore_backup(backup_record.backup_file.path)