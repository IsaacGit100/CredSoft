from django import forms
from .models import Investment, Bank
from django.core.validators import DecimalValidator
from decimal import Decimal

from core.CommaDecimalFormat import CommaDecimalField
#from core.form_fields import CommaDecimalField
from core.ddmmyyyyDateFormat import DDMMYYYYDateField

from django import forms


class BankForm(forms.ModelForm):
    class Meta:
        model = Bank
        fields = ['name', 'branch', 'sort_code', 'bic_code']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'branch': forms.TextInput(attrs={'class': 'form-control'}),
            'sort_code': forms.TextInput(attrs={'class': 'form-control'}),
            'bic_code': forms.TextInput(attrs={'class': 'form-control'}),
        }


class InvestmentForm(forms.ModelForm):
    class Meta:
        model = Investment
        fields = [
            'certificate_no', 'date', 'amount', 'account_no', 
            'bank', 'other_company', 'branch', 'term_days', 'maturity_date',
            'investment_type', 'other_investment_type', 'rate', 'rollover', 
            'processed_date', 'period', 'other_period', 'interest_earned'
        ]
        widgets = {
            'certificate_no': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'account_no': forms.TextInput(attrs={'class': 'form-control'}),
            'bank': forms.Select(attrs={'class': 'form-control'}),
            'other_company': forms.TextInput(attrs={'class': 'form-control'}),
            'branch': forms.TextInput(attrs={'class': 'form-control'}),
            'term_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'maturity_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'investment_type': forms.Select(attrs={'class': 'form-control'}),
            'other_investment_type': forms.TextInput(attrs={'class': 'form-control'}),
            'rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'rollover': forms.Select(attrs={'class': 'form-control'}),
            'processed_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'period': forms.Select(attrs={'class': 'form-control'}),
            'other_period': forms.TextInput(attrs={'class': 'form-control'}),
            'interest_earned': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial values for date fields to today
        self.fields['date'].initial = forms.DateField().widget.attrs.get('value')
        
from django import forms
from .models import Investment

class InvestmentStatusUpdateForm(forms.ModelForm):
    
    interest_earned = CommaDecimalField(max_digits=15, decimal_places=2, label='Interest Earned (₵)', required=False)
    
    written_off_date = DDMMYYYYDateField(label='Written Off Date (dd/mm/yyyy)', required=False)
    discounted_date = DDMMYYYYDateField(label='Discounted Date (dd/mm/yyyy)', required=False)
    
    discounted = forms.BooleanField(required=False, initial=False)
    written_off = forms.BooleanField(required=False, initial=False)
    
    def clean_interest_earned(self):
        value = self.cleaned_data.get('interest_earned')
        if value is None:
            return None
        # Ensure value is Decimal
        return value
    
    class Meta:
        model = Investment
        fields = ['interest_earned', 'discounted', 'discounted_date', 'written_off', 'written_off_date']
        
   