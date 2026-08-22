from django import forms
from .models import Service


from django import forms
from .models import Member
from django_ledger.models import (EntityModel, JournalEntryModel, TransactionModel, AccountModel)

# ChurchApp/forms.py
from django import forms
from django_ledger.models import EntityModel
from .models import Member  # adjust import if Guild is in a different app



# ChurchApp/forms.py

from django import forms
from .models import Member


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = "__all__"
        exclude = ["full_name", "is_deleted", "created_at", "updated_at", "entity"]
        widgets = {
            # Personal details
            "title": forms.Select(attrs={"class": "form-select"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "other_names": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "telephone1": forms.TextInput(attrs={"class": "form-control"}),
            "telephone2": forms.TextInput(attrs={"class": "form-control"}),
            "postal_address": forms.TextInput(attrs={"class": "form-control"}),
            "res_address": forms.TextInput(attrs={"class": "form-control"}),
            "near_landmark": forms.TextInput(attrs={"class": "form-control"}),
            "education_level": forms.Select(attrs={"class": "form-select"}),
            "profession": forms.TextInput(attrs={"class": "form-control"}),
            "ghana_card_no": forms.TextInput(attrs={"class": "form-control"}),
            "date_of_birth": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "date_baptised": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "date_confirmed": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "date_enrolled": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "date_expired": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "guild_first": forms.Select(attrs={"class": "form-select"}),
            "guild_second": forms.Select(attrs={"class": "form-select"}),
            "guild_third": forms.Select(attrs={"class": "form-select"}),
            "no_of_children": forms.NumberInput(attrs={"class": "form-control"}),
            "names_of_children": forms.Textarea(
                attrs={"class": "form-control", "rows": 2}
            ),
            # Office details
            "office_name": forms.TextInput(attrs={"class": "form-control"}),
            "office_address": forms.TextInput(attrs={"class": "form-control"}),
            "office_res_address": forms.TextInput(attrs={"class": "form-control"}),
            "office_phone": forms.TextInput(attrs={"class": "form-control"}),
            "office_email": forms.EmailInput(attrs={"class": "form-control"}),
            "nature_of_business": forms.TextInput(attrs={"class": "form-control"}),
            # Spouse
            "spouse_title": forms.Select(attrs={"class": "form-select"}),
            "spouse_name": forms.TextInput(attrs={"class": "form-control"}),
            "spouse_postal_address": forms.TextInput(attrs={"class": "form-control"}),
            "spouse_email_address": forms.EmailInput(attrs={"class": "form-control"}),
            "spouse_telephone": forms.TextInput(attrs={"class": "form-control"}),
            "spouse_company_name": forms.TextInput(attrs={"class": "form-control"}),
            "spouse_res_address": forms.TextInput(attrs={"class": "form-control"}),
            "spouse_religion": forms.Select(attrs={"class": "form-select"}),
            "spouse_occupation": forms.TextInput(attrs={"class": "form-control"}),
            "spouse_education_level": forms.Select(attrs={"class": "form-select"}),
            "spouse_date_of_birth": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "spouse_near_landmark": forms.TextInput(attrs={"class": "form-control"}),
            "spouse_church": forms.TextInput(attrs={"class": "form-control"}),
            # Parents
            "father_name": forms.TextInput(attrs={"class": "form-control"}),
            "father_res_address": forms.TextInput(attrs={"class": "form-control"}),
            "father_telephone": forms.TextInput(attrs={"class": "form-control"}),
            "father_deceased": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "mother_name": forms.TextInput(attrs={"class": "form-control"}),
            "mother_res_address": forms.TextInput(attrs={"class": "form-control"}),
            "mother_telephone": forms.TextInput(attrs={"class": "form-control"}),
            "mother_deceased": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        self.entity = kwargs.pop("entity", None)
        super().__init__(*args, **kwargs)

        # 🟢 KEY CHANGE: Make all fields optional except first_name, last_name, other_names
        required_fields = ["first_name", "last_name", "other_names"]

        for field_name, field in self.fields.items():
            if field_name not in required_fields:
                field.required = False

        # Limit guild choices to the entity
        if self.entity:
            from .models import Guild

            guild_qs = Guild.objects.filter(entity=self.entity)
            for field in ["guild_first", "guild_second", "guild_third"]:
                if field in self.fields:
                    self.fields[field].queryset = guild_qs
                    self.fields[field].empty_label = "Select Guild"

        # Set member field for clergy (if editing)
        if self.instance and self.instance.pk:
            children_list = self.instance.names_of_children or []
            if children_list:
                self.initial["names_of_children"] = "\n".join(children_list)


# ChurchApp/forms.py
from django import forms
from django_ledger.models import EntityModel
from .models import Member




# ChurchApp/forms.py
from django import forms
from django.utils import timezone

# ChurchApp/forms.py

from django import forms
from .models import Service, Clergy, Member
from django_ledger.models import EntityModel


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = '__all__'
        exclude = ['grand_total', 'journal_entry_id', 'posted_to_ledger', 'created_by', 'created_at', 'updated_at', 'clergy', 'ushers']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'name_of_service': forms.TextInput(attrs={'class': 'form-control'}),
            'attendance': forms.NumberInput(attrs={'class': 'form-control'}),
            'communicants': forms.NumberInput(attrs={'class': 'form-control'}),
            'general_offertory': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'dues': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'tithes': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            # JSON fields as textarea (will handle in clean method)
            'day_born_offerings': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '{"Monday": 10.00, "Tuesday": 5.00}'}),
            'guild_offerings': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '[{"guild_name": "Choir", "amount": 20.00}]'}),
            'special_thank_offering': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': '[{"description": "Thanksgiving", "amount": 30.00}]'}),
            'easter_offering': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': '[{"description": "Easter", "amount": 50.00}]'}),
            'christmas_offering': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': '[{"description": "Christmas", "amount": 40.00}]'}),
            'harvest_offering': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': '[{"description": "Harvest", "amount": 60.00}]'}),
            'other_collections': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': '[{"description": "Other", "amount": 25.00}]'}),
        }
        labels = {
            'general_offertory': 'General Offertory',
            'name_of_service': 'Service Name',
            'day_born_offerings': 'Day-Born Offerings (JSON)',
            'guild_offerings': 'Guild Offerings (JSON)',
        }

    def __init__(self, *args, **kwargs):
        self.entity = kwargs.pop('entity', None)
        super().__init__(*args, **kwargs)
        
        # Show member names for clergy, ushers (if selecting from Member)
        if self.entity:
            # We'll use JSON fields instead of direct selection
            pass

class ServiceForm1(forms.ModelForm):
    # Ask user whether to post to ledger (must confirm)
    post_to_ledger = forms.BooleanField(
        required=False,
        initial=True,
        label="Post to accounting ledger",
        help_text="Uncheck to save without creating journal entries.",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    class Meta:
        model = Service
        fields = "__all__"
        exclude = [
            "grand_total",
            "journal_entry_id",
            "posted_to_ledger",
            "created_by",
            "created_at",
            "updated_at",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "name_of_service": forms.TextInput(attrs={"class": "form-control"}),
            "officiant": forms.Select(attrs={"class": "form-select"}),
            "attendance": forms.NumberInput(attrs={"class": "form-control"}),
            "communicants": forms.NumberInput(attrs={"class": "form-control"}),
            "general_offertory": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "dues": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "tithes": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            # JSON fields are hidden – we will manage them with custom widgets
            "clergy": forms.HiddenInput(),
            "ushers": forms.HiddenInput(),
            "day_born_offerings": forms.HiddenInput(),
            "guild_offerings": forms.HiddenInput(),
            "special_thank_offering": forms.HiddenInput(),
            "easter_offering": forms.HiddenInput(),
            "christmas_offering": forms.HiddenInput(),
            "harvest_offering": forms.HiddenInput(),
            "other_collections": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        self.entity = kwargs.pop("entity", None)
        super().__init__(*args, **kwargs)
        # Filter officiant choices by entity
        if self.entity:
            self.fields["officiant"].queryset = Officiant.objects.filter(
                entity=self.entity
            )
        else:
            self.fields["officiant"].queryset = Officiant.objects.none()


# ChurchApp/forms.py
from django import forms
from .models import Clergy, Member


# ChurchApp/forms.py

from django import forms
from .models import Clergy, Member


class ClergyForm(forms.ModelForm):
    class Meta:
        model = Clergy
        fields = "__all__"
        exclude = ["entity", "full_name"]  # full_name auto-generated
        widgets = {
            "title": forms.Select(attrs={"class": "form-select"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "other_names": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email_address": forms.EmailInput(attrs={"class": "form-control"}),
            "telephone": forms.TextInput(attrs={"class": "form-control"}),
            "postal_address": forms.TextInput(attrs={"class": "form-control"}),
            "res_address": forms.TextInput(attrs={"class": "form-control"}),
            "date_arrived": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "date_depart": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "member": forms.Select(attrs={"class": "form-select"}),
        }
        labels = {
            "email_address": "Email Address",
            "res_address": "Residential Address",
            "date_arrived": "Date Arrived",
            "date_depart": "Date Departed",
        }

    def __init__(self, *args, **kwargs):
        self.entity = kwargs.pop("entity", None)
        super().__init__(*args, **kwargs)

        if self.entity:
            self.fields["member"].queryset = Member.objects.filter(
                entity=self.entity, is_deleted=False
            ).order_by("full_name")
            self.fields["member"].empty_label = "---------"
            self.fields["member"].required = False  # ⬅️ Make it optional
        else:
            self.fields["member"].queryset = Member.objects.none()





class MemberRoleForm(forms.Form):
    """
    Form to assign roles to a member (checkboxes).
    """

    def __init__(self, *args, **kwargs):
        self.entity = kwargs.pop("entity", None)
        self.member = kwargs.pop("member", None)
        super().__init__(*args, **kwargs)

        # Get all roles for this entity
        roles = Role.objects.filter(entity=self.entity, is_active=True)

        # Get existing roles for this member
        existing_roles = []
        if self.member:
            existing_roles = self.member.member_roles.filter(
                is_active=True
            ).values_list("role_id", flat=True)

        # Create a checkbox for each role
        for role in roles:
            self.fields[f"role_{role.id}"] = forms.BooleanField(
                required=False,
                initial=(role.id in existing_roles),
                label=role.display_name,
                widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
            )

    def save(self, member):
        """Save the selected roles."""
        for field_name, value in self.cleaned_data.items():
            if field_name.startswith("role_"):
                role_id = int(field_name.split("_")[1])
                role = Role.objects.get(id=role_id)

                if value:
                    # Add role if not already assigned
                    MemberRole.objects.get_or_create(
                        member=member,
                        role=role,
                        entity=member.entity,
                        defaults={"is_active": True},
                    )
                else:
                    # Remove role (soft delete)
                    MemberRole.objects.filter(member=member, role=role).update(
                        is_active=False, date_removed=timezone.now().date()
                    )


# ChurchApp/forms.py

from django import forms
from .models import Member, Role, MemberRole


class RoleAssignmentForm(forms.Form):
    """
    Form to assign/remove roles for a specific member.
    """

    def __init__(self, *args, **kwargs):
        self.entity = kwargs.pop("entity", None)
        self.member = kwargs.pop("member", None)
        super().__init__(*args, **kwargs)

        if not self.entity:
            return

        # Get all active roles for this entity
        roles = Role.objects.filter(entity=self.entity, is_active=True)

        # Get existing active roles for this member
        existing_roles = []
        if self.member:
            existing_roles = self.member.member_roles.filter(
                is_active=True
            ).values_list("role_id", flat=True)

        # Create a checkbox for each role
        for role in roles:
            self.fields[f"role_{role.id}"] = forms.BooleanField(
                required=False,
                initial=(role.id in existing_roles),
                label=role.display_name,
                widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
            )

    def save(self, member):
        """Save the selected roles."""
        for field_name, value in self.cleaned_data.items():
            if field_name.startswith("role_"):
                role_id = int(field_name.split("_")[1])
                role = Role.objects.get(id=role_id)

                if value:
                    # Add role if not already assigned
                    obj, created = MemberRole.objects.get_or_create(
                        member=member,
                        role=role,
                        entity=member.entity,
                        defaults={"is_active": True},
                    )
                    if not created and not obj.is_active:
                        # Reactivate if it was inactive
                        obj.is_active = True
                        obj.date_removed = None
                        obj.save()
                else:
                    # Remove role (soft delete)
                    MemberRole.objects.filter(member=member, role=role).update(
                        is_active=False, date_removed=timezone.now().date()
                    )
