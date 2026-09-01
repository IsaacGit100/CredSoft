from django import forms
from .models import Service


from django import forms
from .models import Member
from django_ledger.models import (EntityModel, JournalEntryModel, TransactionModel, AccountModel)

# ChurchApp/forms.py
from django import forms
from django_ledger.models import EntityModel
from .models import Member  # adjust import if Guild is in a different app
from RecPayApp.models import Trans
from MembersApp.models import Master


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

        #  KEY CHANGE: Make all fields optional except first_name, last_name, other_names
        required_fields = ["first_name", "last_name", "other_names"]

        for field_name, field in self.fields.items():
            if field_name not in required_fields:
                field.required = False

        # Limit guild choices to the entity
        if self.entity:
            from .models import Guild

            guild_qs = Guild.objects.filter(
                entity=self.entity,
                is_active=True
            ).order_by("name")

            guild_choices = [("", "Select Guild")] + [
                (guild.name, guild.name)
                for guild in guild_qs
            ]

            for field_name in ["guild_first", "guild_second", "guild_third"]:
                if field_name in self.fields:
                    self.fields[field_name] = forms.ChoiceField(
                        choices=guild_choices,
                        required=False,
                        widget=forms.Select(attrs={"class": "form-select"}),
                    )
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

# ChurchApp/forms.py


# ChurchApp/forms.py

from django import forms
from django.utils import timezone
from RecPayApp.models import Trans
from ChurchApp.models import Member


class DuesTitheTransactionForm(forms.ModelForm):
    payment_type = forms.ChoiceField(
        choices=[("Dues", "Dues"), ("Tithe", "Tithe")],
        widget=forms.Select(attrs={"class": "form-select"}),
        initial="Dues",
        label="Payment Type",
        required=True,
    )

    class Meta:
        model = Trans
        fields = [
            "date",
            "rec_vou_no",
            "church_member",
            "amount",
            "details",
            "purpose",
            "payment_type",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "rec_vou_no": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter receipt number"}
            ),
            "church_member": forms.Select(attrs={"class": "form-select"}),
            "amount": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "details": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g., January Dues"}
            ),
            "purpose": forms.HiddenInput(),  # Hidden, auto-set in save()
        }
        labels = {
            "rec_vou_no": "Receipt Number",
            "church_member": "Member",
            "amount": "Amount (₵)",
            "details": "Description/Notes",
        }

    def __init__(self, *args, **kwargs):
        self.entity = kwargs.pop("entity", None)
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if self.entity:
            self.fields["church_member"].queryset = Member.objects.filter(
                entity=self.entity, is_deleted=False
            ).order_by("full_name")
            self.fields["church_member"].empty_label = "Select Member"
            self.fields["church_member"].label_from_instance = lambda obj: obj.full_name

        self.fields["date"].initial = timezone.now().date()

    def clean_rec_vou_no(self):
        rec_no = self.cleaned_data.get("rec_vou_no")
        if rec_no:
            rec_no = rec_no.replace("REC-", "").replace("REC", "").strip()
            return f"REC-{rec_no}"
        return rec_no

    # ChurchApp/forms.py


def save(self, commit=True):
    trans = super().save(commit=False)

    # ⬇️ CRITICAL: Set module to 'church'
    trans.module = "church"
    trans.trans_type = "Receipts"
    trans.status = "DRAFT"
    trans.journal_status = "PENDING"
    trans.pay_mode = "Cash"

    # Get payment type
    payment_type = self.cleaned_data.get("payment_type", "Dues")

    # ⬇️ CRITICAL: Set ledger_code and purpose
    if payment_type == "Tithe":
        trans.ledger_code = "4012"
        trans.ledger_name = "Tithe"
    else:
        trans.ledger_code = "4011"
        trans.ledger_name = "Dues"

    trans.purpose = payment_type

    # ChurchApp/forms.py

from django import forms
from django.utils import timezone
from RecPayApp.models import Trans
from ChurchApp.models import Member


class DuesTitheTransactionForm(forms.ModelForm):
    payment_type = forms.ChoiceField(
        choices=[("Dues", "Dues"), ("Tithe", "Tithe")],
        widget=forms.Select(attrs={"class": "form-select"}),
        initial="Dues",
        label="Payment Type",
        required=True,
    )

    class Meta:
        model = Trans
        fields = [
            "date",
            "rec_vou_no",
            "church_member",
            "amount",
            "details",
            "purpose",
            "payment_type",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "rec_vou_no": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter receipt number"}
            ),
            "church_member": forms.Select(attrs={"class": "form-select"}),
            "amount": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "details": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g., January Dues"}
            ),
            "purpose": forms.HiddenInput(),  # Hidden, auto-set in save()
        }
        labels = {
            "rec_vou_no": "Receipt Number",
            "church_member": "Member",
            "amount": "Amount (₵)",
            "details": "Description/Notes",
        }

    def __init__(self, *args, **kwargs):
        self.entity = kwargs.pop("entity", None)
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if self.entity:
            self.fields["church_member"].queryset = Member.objects.filter(
                entity=self.entity, is_deleted=False
            ).order_by("full_name")
            self.fields["church_member"].empty_label = "Select Member"
            self.fields["church_member"].label_from_instance = lambda obj: obj.full_name

        self.fields["date"].initial = timezone.now().date()

    def clean_rec_vou_no(self):
        rec_no = self.cleaned_data.get("rec_vou_no")
        if rec_no:
            rec_no = rec_no.replace("REC-", "").replace("REC", "").strip()
            return f"REC-{rec_no}"
        return rec_no

    # ChurchApp/forms.py


    def save(self, commit=True):
        trans = super().save(commit=False)

        # ⬇️ CRITICAL: Set module to 'church'
        trans.module = "church"
        trans.trans_type = "Receipts"
        trans.status = "DRAFT"
        trans.journal_status = "PENDING"
        trans.pay_mode = "Cash"

        # Get payment type
        payment_type = self.cleaned_data.get("payment_type", "Dues")

        # ⬇️ CRITICAL: Set ledger_code and purpose
        if payment_type == "Tithe":
            trans.ledger_code = "4012"
            trans.ledger_name = "Tithe"
        else:
            trans.ledger_code = "4011"
            trans.ledger_name = "Dues"

        trans.purpose = payment_type

    # ... rest of save method ...

    
        # Set created_by
        if self.user:
            trans.created_by = self.user
            trans.created_by_name = self.user.username
            trans.created_by_username = self.user.username

        # Set member name if church_member selected
        if trans.church_member:
            trans.member_name = trans.church_member.full_name
            trans.member_no = 0  # Church members don't have Master ID

        # Auto-generate receipt number if empty
        if not trans.rec_vou_no or trans.rec_vou_no == "REC-":
            prefix = "REC"
            last_trans = (
                Trans.objects.filter(trans_type="Receipts", module="church")
                .order_by("-id")
                .first()
            )

            if last_trans and last_trans.rec_vou_no:
                try:
                    last_num = int(last_trans.rec_vou_no.split("-")[-1])
                    new_num = last_num + 1
                except (ValueError, IndexError):
                    new_num = 1
            else:
                new_num = 1
            trans.rec_vou_no = f"{prefix}-{new_num:04d}"
            trans.trans_no = trans.rec_vou_no

        if commit:
            trans.save()

        return trans

# ChurchApp/forms.py

from django import forms
from django.utils import timezone
from .models import Service, Clergy, Member, Guild


class ServiceActivityForm(forms.ModelForm):
    """Sunday Service Activity Form"""
    
    class Meta:
        model = Service
        fields = [
            'date', 'name_of_service', 'attendance', 'communicants',
            'officiant', 'general_offertory', 'dues', 'tithes',
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'name_of_service': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Morning Service'}),
            'attendance': forms.NumberInput(attrs={'class': 'form-control'}),
            'communicants': forms.NumberInput(attrs={'class': 'form-control'}),
            'officiant': forms.Select(attrs={'class': 'form-select'}),
            'general_offertory': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'dues': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'tithes': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.entity = kwargs.pop('entity', None)
        super().__init__(*args, **kwargs)
        
        if self.entity:
            # Filter officiant by entity and role
            self.fields['officiant'].queryset = Member.objects.filter(
                entity=self.entity,
                is_deleted=False
            ).order_by('full_name')
            self.fields['officiant'].empty_label = "Select Officiant"
        
        self.fields['date'].initial = timezone.now().date()

# ChurchApp/forms.py

from django import forms
from .models import ChurchConfig


class ChurchConfigForm(forms.ModelForm):
    class Meta:
        model = ChurchConfig
        fields = [
            'church_name',
            'church_tagline',
            'founded_date',
            'denomination',
            'address',
            'phone',
            'email',
            'website',
            'default_service_name',
            'service_days',
            'default_offering_ledger',
            'default_dues_ledger',
            'default_tithe_ledger',
            'default_dayborn_ledger',
            'default_guild_ledger',
            'default_special_ledger',
        ]
        widgets = {
            'church_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter church full name'}),
            'church_tagline': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., "Building Lives, Transforming Communities"'}),
            'founded_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'denomination': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Anglican, Catholic, Presbyterian'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Physical address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Website URL'}),
            'default_service_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Default service name'}),
            'service_days': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., ["Sunday", "Wednesday"]'}),
            'default_offering_ledger': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 4010'}),
            'default_dues_ledger': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 4011'}),
            'default_tithe_ledger': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 4012'}),
            'default_dayborn_ledger': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 4013'}),
            'default_guild_ledger': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 4014'}),
            'default_special_ledger': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 4015'}),
        }
        labels = {
            'church_name': 'Church Name',
            'church_tagline': 'Tagline / Motto',
            'founded_date': 'Founded Date',
            'denomination': 'Denomination',
            'address': 'Church Address',
            'phone': 'Phone Number',
            'email': 'Email Address',
            'website': 'Website',
            'default_service_name': 'Default Service Name',
            'service_days': 'Service Days (JSON)',
            'default_offering_ledger': 'Offering Ledger Code',
            'default_dues_ledger': 'Dues Ledger Code',
            'default_tithe_ledger': 'Tithe Ledger Code',
            'default_dayborn_ledger': 'Dayborn Ledger Code',
            'default_guild_ledger': 'Guild Ledger Code',
            'default_special_ledger': 'Special Offering Ledger Code',
        }

# ChurchApp/forms.py

from django import forms
from .models import Guild


class GuildForm(forms.ModelForm):
    class Meta:
        model = Guild
        fields = ["name", "description", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "name": "Guild Name",
            "description": "Description",
            "is_active": "Active",
        }
