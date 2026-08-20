# Tech/forms.py
from django import forms
from django_ledger.models import EntityModel
from django.contrib.auth import get_user_model

User = get_user_model()


  # Tech/forms.py
from django import forms
from django_ledger.models import EntityModel
from django.contrib.auth import get_user_model

User = get_user_model()


class EntityForm(forms.ModelForm):
    admin = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        help_text="Select an admin user for this entity.",
    )

    class Meta:
        model = EntityModel
        fields = [
            "name",
            # 'slug',   # <-- removed because it's non-editable
            "admin",
            "hidden",
            "accrual_method",
            "fy_start_month",
            "address_1",
            "address_2",
            "city",
            "state",
            "zip_code",
            "country",
            "email",
            "website",
            "phone",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "hidden": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "accrual_method": forms.Select(attrs={"class": "form-select"}),
            "fy_start_month": forms.Select(attrs={"class": "form-select"}),
            "address_1": forms.TextInput(attrs={"class": "form-control"}),
            "address_2": forms.TextInput(attrs={"class": "form-control"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "state": forms.TextInput(attrs={"class": "form-control"}),
            "zip_code": forms.TextInput(attrs={"class": "form-control"}),
            "country": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "website": forms.URLInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
        }
        labels = {
            "fy_start_month": "Fiscal Year Start Month",
            "accrual_method": "Accrual Method",
        }
