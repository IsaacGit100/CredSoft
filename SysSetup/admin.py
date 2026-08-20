from django.contrib import admin

# Register your models here.
# SysSetup/admin.py
from django.contrib import admin
from .models import SystemSettings


class SystemSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Company Information', {
            'fields': (
                'company_name', 'company_short_name', 'company_registration',
                'company_tax_id', 'company_address', 'company_city',
                'company_region', 'company_country', 'company_phone',
                'company_email', 'company_website', 'company_logo'
            )
        }),
        ('Financial Settings', {
            'fields': ('currency', 'currency_symbol', 'date_format', 
                      'fiscal_year_start', 'accounting_method')
        }),
        ('Loan Settings', {
            'fields': ('default_interest_rate', 'default_loan_term', 
                      'max_loan_amount', 'min_loan_amount', 
                      'moratorium_period', 'late_payment_penalty')
        }),
        ('Savings Settings', {
            'fields': ('min_savings_balance', 'savings_interest_rate')
        }),
        ('Security Settings', {
            'fields': ('max_login_attempts', 'session_timeout', 
                      'password_expiry_days', 'require_strong_password')
        }),
        ('Notification Settings', {
            'fields': ('email_notifications', 'sms_notifications', 'admin_email')
        }),
        ('Report Settings', {
            'fields': ('report_footer', 'show_audit_trail', 'default_items_per_page')
        }),
        ('System Settings', {
            'fields': ('system_name', 'system_version', 'maintenance_mode', 'debug_mode')
        }),
    )
    
    list_display = ['company_name', 'currency', 'default_interest_rate', 'updated_at']
    
    def has_add_permission(self, request):
        # Only allow one record
        if self.model.objects.exists():
            return False
        return True


admin.site.register(SystemSettings, SystemSettingsAdmin)