# FinanceApp/forms.py
from django import forms
from .models import  OpeningBalanceLine
from coa.models import ChartOfAccounts


from django.core.exceptions import ValidationError


class OpeningBalanceLineForm(forms.ModelForm):
    class Meta:
        model = OpeningBalanceLine
        fields = ['account_code', 'debit_amount', 'credit_amount', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        debit_amount = cleaned_data.get('debit')
        credit_amount = cleaned_data.get('credit')

        # Ensure both are not empty (or zero)
        if not debit_amount and not credit_amount:
            raise ValidationError("Please enter either a debit or a credit amount.")

        # Ensure both are not filled
        if debit and credit:
            raise ValidationError("You cannot enter both a debit and a credit. Please enter only one.")

        # Ensure they are not negative (optional)
        if debit_amount and debit_amount < 0:
            raise ValidationError("Debit cannot be negative.")
        if credit_amount and credit_amount < 0:
            raise ValidationError("Credit cannot be negative.")

        return cleaned_data


class OpeningBalanceActionForm(forms.Form):
    confirm = forms.BooleanField(label='I confirm this action', required=True)
    # Optional: add a reason field for reversal
    reason = forms.CharField(widget=forms.Textarea, required=False, label='Reason for reversal')
    

