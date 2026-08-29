from django.urls import path
from . import views

app_name = 'BackupRestore'

urlpatterns = [
    path('panel/', views.backup_panel, name='backup_panel'),
    path('backup/all/', views.backup_all, name='backup_all'),
    path('backup/table/', views.backup_table, name='backup_table'),
    # Direct restore
    path('restore/start/', views.restore_start, name='restore_start'),
    path('status/<str:job_id>/', views.restore_status, name='restore_status'),
    # Safe restore
    path('safe-restore/start/', views.safe_restore_start, name='safe_restore_start'),
    path('safe-restore/status/<str:job_id>/', views.safe_restore_status, name='safe_restore_status'),
    path('safe-restore/step2/', views.safe_restore_step2, name='safe_restore_step2'),
    path('safe-restore/copy-start/', views.safe_restore_copy_start, name='safe_restore_copy_start'),
    path('copy-status/<str:copy_job_id>/', views.copy_status, name='copy_status'),
]