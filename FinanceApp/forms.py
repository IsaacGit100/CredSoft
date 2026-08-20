from django import forms
from .models import GeneralLedger

class LedgerOpeningBalanceForm(forms.ModelForm):
    class Meta:
        model = GeneralLedger
        fields = ['opening_balance', 'open_bal_date']
        widgets = {
            'open_bal_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'opening_balance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
        }
        labels = {
            'opening_balance': 'Opening Balance (₵)',
            'open_bal_date': 'Opening Balance Date',
        }