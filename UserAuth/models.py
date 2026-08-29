from django.db import models

# Create your models here.
# models.py (add this if you haven't already)
from django.db import models

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from django_ledger.models import EntityModel
#from .models import UserProfile

# UserAuth/models.py

class UserProfile(models.Model):
    USER_ROLES = [
        ('ADMIN', 'Administrator'),
        ('MANAGER', 'Manager'),
        ('CASHIER', 'Cashier'),
        ('LOAN_OFFICER', 'Loan Officer'),
        ('AUDITOR', 'Auditor'),
        ('VIEWER', 'View Only'),
    ]
    
    USER_TYPES = (
        ('church_admin', 'Church Admin'),
        ('school_admin', 'School Admin'),
        ('credit_union_admin', 'Credit Union Admin'),
        ('diocese_admin', 'Diocese Admin'),
        ('finance_officer', 'Finance Officer'),
    )
    user_type = models.CharField(max_length=30, choices=USER_TYPES, default='church_admin')
    allowed_entities = models.ManyToManyField(EntityModel, related_name='users', blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Additional fields
    phone = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=50, blank=True)
    role = models.CharField(max_length=20, choices=USER_ROLES, default='VIEWER')
    employee_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    
    # Security fields
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    login_attempts = models.IntegerField(default=0)
    account_locked = models.BooleanField(default=False)
    
    # Preferences
    theme = models.CharField(max_length=20, default='light')
    items_per_page = models.IntegerField(default=50)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    #def __str__(self):
    #    return f"{self.user.username} - {self.get_role_display()}"
    
    def __str__(self):
        return f"{self.user.username} - {self.user_type}"
    
    class Meta:
        permissions = [
            ('can_approve_loans', 'Can approve loans'),
            ('can_post_transactions', 'Can post transactions'),
            ('can_view_reports', 'Can view reports'),
            ('can_manage_users', 'Can manage users'),
        ]


# ============= SIGNALS TO AUTO-CREATE PROFILE =============

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile when a new User is created"""
    if created:
        UserProfile.objects.create(user=instance)
        print(f"Profile created for user: {instance.username}")

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the UserProfile when the User is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()