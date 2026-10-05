# Tech/forms.py

from django import forms
from django_ledger.models import EntityModel
from django.contrib.auth import get_user_model
from djan_led.models import EntityConfig

User = get_user_model()


class EntityForm(forms.ModelForm):

    #  Extra field (not on EntityModel  we save it to EntityConfig) 
    entity_type = forms.ChoiceField(
        choices=[
            ("", "-- Select Type --"),
            ("church", "Church"),
            ("school", "School"),
            ("credit_union", "Credit Union"),
            ("pos", "POS"),
            ("hospital", "Hospital"),
            ("hotel", "Hotel"),
            ("business", "Business"),
            ("ngo", "NGO"),
            ("other", "Other"),
        ],
        required=True,
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Entity Type",
        help_text="Select the type of this entity (Church, POS, School, etc.)",
    )

    admin = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
        help_text="Select an admin user for this entity.",
    )

    class Meta:
        model = EntityModel
        fields = [
            "name",
            # 'slug',  # non-editable
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Pre-fill entity_type from the related config when editing
        if self.instance and self.instance.pk:
            try:
                self.fields["entity_type"].initial = self.instance.config.entity_type
            except EntityConfig.DoesNotExist:
                pass

    def save(self, commit=True):
        # Save EntityModel first
        entity = super().save(commit=commit)

        if commit:
            # Save entity_type into the related EntityConfig
            entity_type = self.cleaned_data.get("entity_type", "")
            config, _ = EntityConfig.objects.get_or_create(entity=entity)
            config.entity_type = entity_type
            config.save()

        return entity
