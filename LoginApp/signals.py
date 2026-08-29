from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.dispatch import receiver
from .models import AdminLoginHistory
import datetime
from django.utils import timezone

@receiver(user_logged_in)
def log_admin_login(sender, request, user, **kwargs):
    """Record successful admin/staff login"""
    AdminLoginHistory.objects.create(
        user=user,
        login_time=datetime.datetime.now(),
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        login_status='SUCCESS',
    )

@receiver(user_login_failed)
def log_admin_failed_login(sender, credentials, request, **kwargs):
    """Record failed admin login attempt"""
    username = credentials.get('username', 'unknown')
    # We don't have a User object for failed attempts, so we create a dummy or skip
    # Instead, we can log with a placeholder or create a separate model for failed attempts.
    # But AdminLoginHistory requires a User foreign key. To log failed attempts, you need to allow null=True on user.
    # Modify your model: user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    # Then:
    # AdminLoginHistory.objects.create(
    #     user=None,
    #     username_attempted=username,   # add field if needed
    #     login_time=datetime.datetime.now(),
    #     ip_address=get_client_ip(request),
    #     login_status='FAILED',
    #     failure_reason='Invalid credentials'
    # )
    pass

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@receiver(user_login_failed)
def log_admin_failed_login(sender, credentials, request, **kwargs):
    username = credentials.get('username', '')
    AdminLoginHistory.objects.create(
        user=None,
        username_attempted=username,
        login_time=timezone.now(),
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        login_status='FAILED',
        failure_reason='Invalid credentials',
    )