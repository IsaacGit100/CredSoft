from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class BackupLog(models.Model):
    ACTION_CHOICES = (
        ('BACKUP', 'Backup'),
        ('RESTORE', 'Restore'),
        ('DRY_RUN', 'Dry Run'),
    )
    RESULT_CHOICES = (
        ('SUCCESS', 'Success'),
        ('FAILURE', 'Failure'),
        ('ABORTED', 'Aborted'),
    )

    timestamp = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    result = models.CharField(max_length=10, choices=RESULT_CHOICES)
    table_name = models.CharField(max_length=100, blank=True, null=True)
    backup_file = models.CharField(max_length=255, blank=True, null=True)
    details = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Backup Log'
        verbose_name_plural = 'Backup Logs'

    def __str__(self):
        return f"{self.timestamp} - {self.user} - {self.action} - {self.result}"
    
# BackupRestore/models.py
class RestoreJob(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('RUNNING', 'Running'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    )
    job_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    table_name = models.CharField(max_length=100, blank=True)
    backup_file = models.CharField(max_length=255)
    error_message = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)