# services/forms.py
from django import forms


class SavIntSearchForm(forms.Form):
    search = forms.CharField(
        label="Search by ID or Last Name",
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter member ID or last name...",
            }
        ),
    )
