# SysSetup/forms.py
from django import forms
from .models import SystemSettings, SystemPreference, FiscalPeriod

class SystemSettingsForm(forms.ModelForm):
    """Form for system settings/company setup"""
    
    class Meta:
        model = SystemSettings
        fields = [
            # Company Information
            'company_name', 'company_short_name', 'company_registration', 'company_tax_id',
            'company_address', 'company_city', 'company_region', 'company_country',
            'company_phone', 'company_email', 'company_website', 'company_logo', 'company_favicon',
            
            # Financial Settings
            'currency', 'currency_symbol', 'date_format', 'fiscal_year_start', 'accounting_method',
            
            # Loan Settings
            'default_interest_rate', 'default_loan_term', 'max_loan_amount', 'min_loan_amount',
            'moratorium_period', 'late_payment_penalty', 'loan_calc_method',
           
            
            # Savings Settings
            'min_savings_balance', 'sav_no_days_int_calc', 'sav_min_days_int_calc', 'savings_calc_type',
            'simple_sav_interest_rate', 'minimum_sav_interest_rate', 'simple_sav_interest_appl', 'minimum_sav_interest_appl',
            
            # Banking Information - Account 1
            'bank_name1', 'bank_account_name1', 'bank_account_number1', 'bank_branch1',
            
            # Banking Information - Account 2
            'bank_name2', 'bank_account_name2', 'bank_account_number2', 'bank_branch2',
            
            # Security Settings
            'max_login_attempts', 'session_timeout', 'password_expiry_days', 'require_strong_password',
            
            # Notification Settings
            'email_notifications', 'sms_notifications', 'admin_email',
            
            # Report Settings
            'report_footer', 'show_audit_trail', 'default_items_per_page',
            
            # System Settings
            'system_name', 'system_version', 'maintenance_mode', 'debug_mode',
        ]
        
        widgets = {
           
            'company_address': forms.Textarea(attrs={'rows': 3}),
            'report_footer': forms.Textarea(attrs={'rows': 2}),
            'default_interest_rate': forms.NumberInput(attrs={'step': '0.01'}),
            'savings_interest_rate': forms.NumberInput(attrs={'step': '0.01'}),
            'late_payment_penalty': forms.NumberInput(attrs={'step': '0.01'}),
            'max_loan_amount': forms.NumberInput(attrs={'step': '0.01'}),
            'min_loan_amount': forms.NumberInput(attrs={'step': '0.01'}),
            'min_savings_balance': forms.NumberInput(attrs={'step': '0.01'}),
            'savings_calc_type': forms.RadioSelect,
            'loan_calc_method': forms.RadioSelect, 
                     
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set the initial value (replace 'Straight Line' with your exact choice value)
        self.fields['loan_calc_method'].initial = 'Straight Line'


class SystemPreferenceForm(forms.ModelForm):
    """Form for user preferences"""
    
    class Meta:
        model = SystemPreference
        fields = ['theme', 'items_per_page', 'email_notifications', 'sms_notifications', 
                  'show_dashboard_widgets', 'default_dashboard']
        widgets = {
            'items_per_page': forms.NumberInput(attrs={'min': 10, 'max': 200}),
        }


class FiscalPeriodForm(forms.ModelForm):
    """Form for fiscal periods"""
    
    class Meta:
        model = FiscalPeriod
        fields = ['name', 'period_type', 'start_date', 'end_date', 'status', 'is_current']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }