# Create your models here.
# SysSetup/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django_ledger.models import (EntityModel, LedgerModel, JournalEntryModel, AccountModel, TransactionModel)

class SystemSettings(models.Model):

    """
    Global system settings and variables
    
    """
    SETTING_TYPES = [
        ('COMPANY', 'Company Information'),
        ('FINANCIAL', 'Financial Settings'),
        ('LOAN', 'Loan Settings'),
        ('SAVINGS', 'Savings Settings'),
        ('SECURITY', 'Security Settings'),
        ('NOTIFICATION', 'Notification Settings'),
        ('REPORT', 'Report Settings'),
        ('SYSTEM', 'System Settings'),
    ]

    SAVINGS_INTEREST_APPLICATION_CHOICES = [
        ('DAILY', 'Daily'),
        ('MONTHLY', 'Monthly'),
        ('QUARTERLY', 'Quarterly'),
        ('YEARLY', 'Yearly'),
    ]
    
    SIMPLE_INTEREST_APPL_CHOICES = [
        ('DAILY', 'Daily'),
        ('MONTHLY', 'Monthly'),
        ('QUARTERLY', 'Quarterly'),
        ('YEARLY', 'Yearly'),
    ]
    
    MINIMUM_INTEREST_APPL_CHOICES = [
        ('DAILY', 'Daily'),
        ('MONTHLY', 'Monthly'),
        ('QUARTERLY', 'Quarterly'),
        ('YEARLY', 'Yearly'),
    ]
    
    
    SAVINGS_CALC_TYPE_CHOICES = [
        ('Simple_Sav_Interest', 'Simple_Sav_Interest'),
        ('Minimum_Sav_Interest', 'Minimum_Sav_Interest'),    
    ]
    
    LOAN_CALC_METHOD_CHOICES = [
        ('Straight Line', 'Straight Line'),
        ('Armortization', 'Armortization'),    
    ]
    
    # Company Information
#    entity = models.ForeignKey(EntityModel, on_delete=models.SET_NULL, null=True, blank=True, related_name='sys_set' )
    company_name = models.CharField(max_length=200, default='St. Andrews Co-Operative Credit Union')
    company_short_name = models.CharField(max_length=50, default='St. Andrews Credit Union') 
    company_registration = models.CharField(max_length=50, blank=True)
    company_tax_id = models.CharField(max_length=50, blank=True)
    
    # Contact Information
    company_address = models.TextField(blank=True)
    company_city = models.CharField(max_length=100, blank=True)
    company_region = models.CharField(max_length=100, blank=True)
    company_country = models.CharField(max_length=100, default='Ghana')
    company_phone = models.CharField(max_length=50, blank=True)
    company_email = models.EmailField(blank=True)
    company_website = models.URLField(blank=True)
    company_logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    company_favicon = models.ImageField(upload_to='favicons/', blank=True, null=True)
    
    # Financial Settings
    currency = models.CharField(max_length=3, default='GHS')
    currency_symbol = models.CharField(max_length=5, default='₵')
    date_format = models.CharField(max_length=20, default='dd/mm/yyyy')
    fiscal_year_start = models.IntegerField(default=1)  # 1 = January
    accounting_method = models.CharField(max_length=20, default='accrual', choices=[
        ('accrual', 'Accrual Basis'),
        ('cash', 'Cash Basis'),
    ])
    
    # Loan Settings
    loan_calc_method = models.CharField(max_length=25, choices=LOAN_CALC_METHOD_CHOICES, default='Straight Line')
    default_interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    loan_interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    default_loan_term = models.IntegerField(default=12)
    late_payment_penalty = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    max_loan_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    min_loan_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    moratorium_period = models.IntegerField(default=0)
    
    # Savings Settings
    savings_calc_type = models.CharField(max_length=25, choices= SAVINGS_CALC_TYPE_CHOICES, default='')
    min_savings_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    last_interest_accrual_run = models.DateField(null=True, blank=True, default=None)
    
    
    ## =======================
    savings_calc_type = models.CharField(max_length=25, choices= SAVINGS_CALC_TYPE_CHOICES, default='')
    
    simple_sav_interest_rate = models.DecimalField(max_digits=8, decimal_places=4, default=0.0000)
    minimum_sav_interest_rate = models.DecimalField(max_digits=8, decimal_places=4, default=0.0000)
    
    simple_sav_interest_appl = models.CharField(max_length=10, choices=SIMPLE_INTEREST_APPL_CHOICES, default='')
    minimum_sav_interest_appl = models.CharField(max_length=10, choices=MINIMUM_INTEREST_APPL_CHOICES, default='')
    ## =======================
    
    savings_interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    savings_interest_application = models.CharField(max_length=13, choices=SAVINGS_INTEREST_APPLICATION_CHOICES, default='')
    stop_savings_interest_calculation = models.BooleanField(default=False)
    sav_min_days_int_calc = models.IntegerField(null=True, blank=True, default=0)
    sav_no_days_int_calc = models.IntegerField(null=True, blank=True, default=0)
    
    last_interest_accrual_date = models.DateTimeField(null=True, blank=True, default=None)
    min_savings_balance_days = models.IntegerField(null=True, blank=True, default=0)
    last_savings_min_proc_date = models.DateField(null=True, blank=True, default=None)
    
    
     # Banking Information
    bank_name1 = models.CharField(max_length=200, blank=True)
    bank_account_name1 = models.CharField(max_length=200, blank=True)
    bank_account_number1 = models.CharField(max_length=100, blank=True)
    bank_branch1 = models.CharField(max_length=200, blank=True)
    
     # Banking Information
    bank_name2 = models.CharField(max_length=200, blank=True)
    bank_account_name2 = models.CharField(max_length=200, blank=True)
    bank_account_number2 = models.CharField(max_length=100, blank=True)
    bank_branch2 = models.CharField(max_length=200, blank=True)
    
    
    # Security Settings
    max_login_attempts = models.IntegerField(default=5)
    session_timeout = models.IntegerField(default=30)  # minutes
    password_expiry_days = models.IntegerField(default=90)
    require_strong_password = models.BooleanField(default=True)
    
    # Notification Settings
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    admin_email = models.EmailField(blank=True)
    
    # Report Settings
    report_footer = models.TextField(blank=True, default='Thank you for banking with us')
    show_audit_trail = models.BooleanField(default=True)
    default_items_per_page = models.IntegerField(default=50)
    
    # System Settings
    system_name = models.CharField(max_length=100, default='Loan Management System')
    system_version = models.CharField(max_length=20, default='1.0')
    maintenance_mode = models.BooleanField(default=False)
    debug_mode = models.BooleanField(default=False)
    
    # Dividend
    dividend_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, default=0.00)
    dividend_date = models.DateField(null=True, blank=True, default=None)
    dividend_period = models.CharField(max_length=50, null=True, blank=True, default='')
    
    # Audit fields
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name_plural = "System Settings"
    
    def __str__(self):
        return f"System Settings (Updated: {self.updated_at.strftime('%d/%m/%Y')})"
    
    def save(self, *args, **kwargs):
        # Ensure only one record exists
        if not self.pk and SystemSettings.objects.exists():
            # If settings already exist, update instead of creating new
            existing = SystemSettings.objects.first()
            self.pk = existing.pk
        super().save(*args, **kwargs)
    
    
    @property
    def first_quarter_end(self):
        from datetime import date
        year = date.today().year
        return date(year, 3, 31)
    
    @property
    def second_quarter_end(self):
        from datetime import date
        year = date.today().year
        return date(year, 6, 30)
    
    @property
    def third_quarter_end(self):
        from datetime import date
        year = date.today().year
        return date(year, 9, 30)
    
    @property
    def fourth_quarter_end(self):
        from datetime import date
        year = date.today().year
        return date(year, 12, 31)   
    
    @property
    def first_quarter_start(self):
        """Returns first quarter start date (1st January)"""
        from datetime import date
        
        current_year = date.today().year
        fiscal_start_month = self.fiscal_year_start
        
        if date.today().month < fiscal_start_month:
            year = current_year - 1
        else:
            year = current_year
            
        return date(year, 1, 1)
    
    @property
    def second_quarter_start(self):
        """Returns second quarter start date (1st April)"""
        from datetime import date, timedelta
        return self.first_quarter_end + timedelta(days=1)
    
    @property
    def third_quarter_start(self):
        """Returns third quarter start date (1st July)"""
        from datetime import timedelta
        return self.second_quarter_end + timedelta(days=1)
    
    @property
    def fourth_quarter_start(self):
        """Returns fourth quarter start date (1st October)"""
        from datetime import timedelta
        return self.third_quarter_end + timedelta(days=1)
    
    @property
    def current_quarter(self):
        """Returns current quarter (1, 2, 3, or 4)"""
        from datetime import date
        
        today = date.today()
        
        if today <= self.first_quarter_end:
            return 1
        elif today <= self.second_quarter_end:
            return 2
        elif today <= self.third_quarter_end:
            return 3
        else:
            return 4
    
    @property
    def current_quarter_start(self):
        """Returns start date of current quarter"""
        quarter = self.current_quarter
        if quarter == 1:
            return self.first_quarter_start
        elif quarter == 2:
            return self.second_quarter_start
        elif quarter == 3:
            return self.third_quarter_start
        else:
            return self.fourth_quarter_start
    
    @property
    def current_quarter_end(self):
        """Returns end date of current quarter"""
        quarter = self.current_quarter
        if quarter == 1:
            return self.first_quarter_end
        elif quarter == 2:
            return self.second_quarter_end
        elif quarter == 3:
            return self.third_quarter_end
        else:
            return self.fourth_quarter_end
    
    @property
    def first_quarter_display(self):
        """Display format: Q1 (Jan - Mar)"""
        return f"Q1 (Jan - Mar) - Ends {self.first_quarter_end.strftime('%d/%m/%Y')}"
    
    @property
    def second_quarter_display(self):
        """Display format: Q2 (Apr - Jun)"""
        return f"Q2 (Apr - Jun) - Ends {self.second_quarter_end.strftime('%d/%m/%Y')}"
    
    @property
    def third_quarter_display(self):
        """Display format: Q3 (Jul - Sep)"""
        return f"Q3 (Jul - Sep) - Ends {self.third_quarter_end.strftime('%d/%m/%Y')}"
    
    @property
    def fourth_quarter_display(self):
        """Display format: Q4 (Oct - Dec)"""
        return f"Q4 (Oct - Dec) - Ends {self.fourth_quarter_end.strftime('%d/%m/%Y')}"


class SystemPreference(models.Model):
    """User/system preferences"""
    
    THEME_CHOICES = [
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('auto', 'Auto'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='preferences')
#    entity = models.ForeignKey(EntityModel, on_delete=models.CASCADE, related_name='sys_pref')
    # Display Preferences
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='light')
    items_per_page = models.IntegerField(default=50)
    
    
    # Notification Preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    
    # Dashboard Preferences
    show_dashboard_widgets = models.BooleanField(default=True)
    default_dashboard = models.CharField(max_length=50, default='main')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Preferences"

class FiscalPeriod(models.Model):
    """Fiscal/Accounting periods"""
    
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('CLOSED', 'Closed'),
        ('LOCKED', 'Locked'),
    ]
#    entity = models.ForeignKey(EntityModel, on_delete=models.SET_NULL, null=True, blank=True, related_name='fisc_Period') 
    name = models.CharField(max_length=100)
    period_type = models.CharField(max_length=20, choices=[('MONTH', 'Month'), ('QUARTER', 'Quarter'), ('YEAR', 'Year')])
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='OPEN')
    is_current = models.BooleanField(default=False)
    
    closed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.start_date} to {self.end_date})"
    
    class Meta:
        ordering = ['-start_date']


class AuditLog(models.Model):
    """System audit log"""
    
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('LOGIN', 'Login'),
    
        ('LOGOUT', 'Logout'),
        ('POST', 'Post'),
        ('PRINT', 'Print'),
        ('EXPORT', 'Export'),
    ]
#    entity=models.ForeignKey(EntityModel, on_delete=models.SET_NULL, null=True, blank=True, related_name='aud_log')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100, blank=True)
    record_id = models.IntegerField(null=True, blank=True)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.timestamp} - {self.user} - {self.action}"
    
    class Meta:
        ordering = ['-timestamp']
