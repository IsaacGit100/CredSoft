# CoreApp/urls.py
from django.urls import path
from . import views_batch
from . import views_backup
from . import views

app_name = 'CoreApp'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),  
    path('batch/', views_batch.batch_dashboard, name='batch_dashboard'),
    path('batch/run/<str:process_type>/', views_batch.run_batch_process, name='run_batch_process'),
    path('batch/logs/', views_batch.batch_logs, name='batch_logs'),
    path('batch/logs/<int:process_id>/', views_batch.batch_logs, name='batch_logs_process'),
    path('batch/reset/<int:process_id>/', views_batch.reset_batch_process, name='reset_batch_process'),
    
    path('backup/', views_backup.backup_dashboard, name='backup_dashboard'),
    path('backup/full/', views_backup.backup_full, name='backup_full'),
    path('backup/app/<str:app_name>/', views_backup.backup_app, name='backup_app'),
    path('backup/tables/', views_backup.backup_tables, name='backup_tables'),
    path('backup/download/<int:backup_id>/', views_backup.download_backup, name='download_backup'),
    path('backup/delete/<int:backup_id>/', views_backup.delete_backup, name='delete_backup'),
    path('backup/restore/<int:backup_id>/', views_backup.restore_backup, name='restore_backup'),
    
    
    path('backup/restore/<int:backup_id>/', views_backup.restore_backup, name='restore_backup'),
    path('backup/restore/preview/<int:backup_id>/', views_backup.restore_preview, name='restore_preview'),
    path('backup/restore/upload/', views_backup.restore_upload, name='restore_upload'),
]
    
