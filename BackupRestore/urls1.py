# Supervisor/urls.py
from django.urls import path
from . import views

app_name = 'BackupRestore'

urlpatterns = [

 #   path('restore/', views.restore_table, name='restore_table'),          # manual upload
    path('download/<str:filename>/', views.download_backup, name='download_backup'),
    
    
    
    path('panel/', views.backup_panel, name='backup_panel'),
    path('backup/all/', views.backup_all, name='backup_all'),
    path('backup/table/', views.backup_table, name='backup_table'),
    path('status/<str:job_id>/', views.restore_status, name='restore_status'),
    
    path('restore/', views.restore_from_file, name='restore_from_file'),
    path('restore/start/', views.restore_start, name='restore_start'),   # ← distinct path  
    
    path('restore/upload/', views.restore_manual_upload, name='restore_manual_upload'),
    path('logs/', views.backup_logs, name='backup_logs'),
    
    path('safe-restore/step1/', views.safe_restore_step1, name='safe_restore_step1'),
    path('safe-restore/step2/', views.safe_restore_step2, name='safe_restore_step2'),
    path('safe-restore/copy/', views.safe_restore_copy, name='safe_restore_copy'),
    
]
