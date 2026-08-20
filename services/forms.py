# services/forms.py
from django import forms
from djan_led.models import EntityConfig


class EntityConfigForm(forms.ModelForm):
    class Meta:
        model = EntityConfig
        fields = [
            "savings_interest_rate",
            "savings_interest_application",
            "savings_calc_type",
            "interest_expense_account_code",
            "savings_interest_payable_account_code",
        ]
        widgets = {
            "savings_interest_rate": forms.NumberInput(
                attrs={"step": "0.0001", "class": "form-control"}
            ),
            "savings_interest_application": forms.Select(
                attrs={"class": "form-control"}
            ),
            "savings_calc_type": forms.Select(attrs={"class": "form-control"}),
            "interest_expense_account_code": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "savings_interest_payable_account_code": forms.TextInput(
                attrs={"class": "form-control"}
            ),
        }
        labels = {
            "savings_interest_rate": "Annual Interest Rate (%)",
            "savings_interest_application": "Application Frequency",
            "savings_calc_type": "Calculation Type",
            "interest_expense_account_code": "Interest Expense Account Code",
            "savings_interest_payable_account_code": "Interest Payable Account Code",
        }
