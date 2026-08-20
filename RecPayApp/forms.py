# RecPayApp/forms.py

from django import forms
from .models import Trans

class BaseTransForm(forms.ModelForm):
    class Meta:
        model = Trans
        fields = ['date', 'trans_no', 'trans_type', 'amount', 'pay_mode', 'details', 'ledger_code', 'ledger_name']