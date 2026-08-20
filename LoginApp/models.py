# LoginApp/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class MemberLoginHistory(models.Model):
    """Track member login history"""
    
    LOGIN_STATUS = [
        ('SUCCESS', 'Successful'),
        ('FAILED', 'Failed'),
        ('LOCKED', 'Account Locked'),
        ('EXPIRED', 'Session Expired'),
    ]
    
    # Member information (using the existing Master model)
    member = models.ForeignKey('MembersApp.Master', on_delete=models.CASCADE, related_name='login_history')
    
    # Login details
    login_time = models.DateTimeField(default=timezone.now)
    logout_time = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    device_type = models.CharField(max_length=50, blank=True)
    browser = models.CharField(max_length=100, blank=True)
    operating_system = models.CharField(max_length=100, blank=True)
    
    # Session tracking
    session_key = models.CharField(max_length=40, blank=True)
    login_status = models.CharField(max_length=20, choices=LOGIN_STATUS, default='SUCCESS')
    failure_reason = models.TextField(blank=True)
    
    # Location (optional)
    location = models.CharField(max_length=200, blank=True)
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-login_time']
        verbose_name_plural = "Member Login Histories"
    
    def __str__(self):
        return f"{self.member.full_name} - {self.login_time} - {self.login_status}"
    
    @property
    def session_duration(self):
        """Calculate session duration in minutes"""
        if self.logout_time:
            duration = (self.logout_time - self.login_time).total_seconds() / 60
            return round(duration, 2)
        return None


class AdminLoginHistory(models.Model):
    """Track admin/staff login history"""
    
    LOGIN_STATUS = [
        ('SUCCESS', 'Successful'),
        ('FAILED', 'Failed'),
        ('LOCKED', 'Account Locked'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='login_history')
    login_time = models.DateTimeField(default=timezone.now)
    logout_time = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    device_type = models.CharField(max_length=50, blank=True)
    browser = models.CharField(max_length=100, blank=True)
    operating_system = models.CharField(max_length=100, blank=True)
    login_status = models.CharField(max_length=20, choices=LOGIN_STATUS, default='SUCCESS')
    failure_reason = models.TextField(blank=True)
    username_attempted = models.CharField(max_length=200, blank=True, null=True, default='')
    username = models.CharField(max_length=200, blank=True, null=True, default='')
    
    class Meta:
        ordering = ['-login_time']
        verbose_name_plural = "Admin Login Histories"
    
    def __str__(self):
        return f"{self.user.username} - {self.login_time} - {self.login_status}"
    
    