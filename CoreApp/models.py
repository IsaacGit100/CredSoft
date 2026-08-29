from django.db import models

# Create your models here.
# CoreApp/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class BatchProcess(models.Model):
    """Track batch processes and their execution status"""
    
    PROCESS_TYPES = [
        ('SAVINGS_INTEREST', 'Savings Interest Accrual'),
        ('LOAN_INTEREST', 'Loan Interest Calculation'),
        ('LOAN_PENALTY', 'Loan Penalty Calculation'),
        ('DAILY_REPORT', 'Daily Report Generation'),
        ('BACKUP', 'Database Backup'),
        ('STATEMENT', 'Member Statement Generation'),
        ('DIVIDEND', 'Dividend Calculation'),
        ('YEAR_END', 'Year End Closing'),
    ]
    
    FREQUENCY_CHOICES = [
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('QUARTERLY', 'Quarterly'),
        ('YEARLY', 'Yearly'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('RUNNING', 'Running'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('SKIPPED', 'Skipped'),
    ]
    
    # Process identification
    process_type = models.CharField(max_length=50, choices=PROCESS_TYPES, unique=True)
    process_name = models.CharField(max_length=100)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='DAILY')
    
    # Execution tracking
    last_run = models.DateTimeField(null=True, blank=True)
    last_run_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='last_run_processes')
    last_run_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    last_run_message = models.TextField(blank=True)
    
    next_run_due = models.DateTimeField(null=True, blank=True)
    
    # Statistics
    total_runs = models.IntegerField(default=0)
    successful_runs = models.IntegerField(default=0)
    failed_runs = models.IntegerField(default=0)
    
    # Settings
    is_active = models.BooleanField(default=True)
    requires_approval = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_processes')
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.process_name} - Last run: {self.last_run}"
    
    @property
    def is_due(self):
        """Check if process is due to run"""
        if not self.next_run_due:
            return True
        return timezone.now() >= self.next_run_due
    
    @property
    def days_since_last_run(self):
        if not self.last_run:
            return None
        return (timezone.now() - self.last_run).days
    
    class Meta:
        ordering = ['process_name']


class BatchProcessLog(models.Model):
    """Detailed log of each batch process execution"""
    
    process = models.ForeignKey(BatchProcess, on_delete=models.CASCADE, related_name='logs')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=BatchProcess.STATUS_CHOICES)
    message = models.TextField(blank=True)
    error_details = models.TextField(blank=True)
    records_processed = models.IntegerField(default=0)
    run_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.process.process_name} - {self.started_at} - {self.status}"
    
# CoreApp/models.py - Add this model
import os

class DatabaseBackup(models.Model):
    """Track database backups"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('RUNNING', 'Running'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    backup_name = models.CharField(max_length=200)
    backup_file = models.FileField(upload_to='backups/', null=True, blank=True)
    file_size = models.BigIntegerField(default=0, help_text="Size in bytes")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Backup details
    tables_backup = models.TextField(blank=True, help_text="List of tables backed up")
    backup_started = models.DateTimeField(auto_now_add=True)
    backup_completed = models.DateTimeField(null=True, blank=True)
    
    # Who created the backup
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Backup notes
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-backup_started']
    
    def __str__(self):
        return f"{self.backup_name} - {self.backup_started}"
    
    @property
    def file_size_mb(self):
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return 0
    
from django.db import models
from django.contrib.auth.models import User

class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='coreapp_audit_logs' )
    action = models.CharField(max_length=100)
    details = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action} - {self.timestamp}"