from django import forms
from .models import Service, Clergy, Ushers, Guild, Officiant


from django import forms
from .models import Member, Guild
from django_ledger.models import (EntityModel, JournalEntryModel, TransactionModel, AccountModel)

# ChurchApp/forms.py
from django import forms
from django_ledger.models import EntityModel
from .models import Member, Guild  # adjust import if Guild is in a different app


class MemberForm(forms.ModelForm):
    """
    Form for creating/editing Church members.
    Handles JSON conversion for children names automatically.
    Filters guild choices by the selected entity.
    """

    # Custom field for children names – stored as JSON, but presented as a textarea
    children_names = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "class": "form-control",
                "placeholder": "Enter each child's name on a new line",
            }
        ),
        help_text="Enter each child's name on a new line.",
        label="Children's Names",
    )

    class Meta:
        model = Member
        fields = "__all__"
        exclude = ["full_name", "created_at", "updated_at", "is_deleted", "entity"]
        widgets = {
            # ----- Personal Information -----
            "title": forms.Select(attrs={"class": "form-select"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "other_names": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "telephone1": forms.TextInput(attrs={"class": "form-control"}),
            "telephone2": forms.TextInput(attrs={"class": "form-control"}),
            "postal_address": forms.Textarea(
                attrs={"class": "form-control", "rows": 2}
            ),
            "res_address": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
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
            # ----- Office Information -----
            "office_name": forms.TextInput(attrs={"class": "form-control"}),
            "office_address": forms.TextInput(attrs={"class": "form-control"}),
            "office_res_address": forms.TextInput(attrs={"class": "form-control"}),
            "office_phone": forms.TextInput(attrs={"class": "form-control"}),
            "office_email": forms.EmailInput(attrs={"class": "form-control"}),
            "nature_of_business": forms.TextInput(attrs={"class": "form-control"}),
            # ----- Spouse Information -----
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
            # ----- Parents -----
            "father_name": forms.TextInput(attrs={"class": "form-control"}),
            "father_res_address": forms.TextInput(attrs={"class": "form-control"}),
            "father_telephone": forms.TextInput(attrs={"class": "form-control"}),
            "father_deceased": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "mother_name": forms.TextInput(attrs={"class": "form-control"}),
            "mother_res_address": forms.TextInput(attrs={"class": "form-control"}),
            "mother_telephone": forms.TextInput(attrs={"class": "form-control"}),
            "mother_deceased": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "telephone1": "Primary Phone",
            "telephone2": "Secondary Phone",
            "res_address": "Residential Address",
            "near_landmark": "Near Landmark",
            "ghana_card_no": "Ghana Card Number",
            "date_enrolled": "Date Enrolled",
            "date_expired": "Date Expired",
            "guild_first": "Primary Guild",
            "guild_second": "Secondary Guild",
            "guild_third": "Tertiary Guild",
            "office_res_address": "Office Residential Address",
            "spouse_res_address": "Spouse Residential Address",
        }

    def __init__(self, *args, **kwargs):
        # Extract the entity from kwargs (passed from the view)
        self.entity = kwargs.pop("entity", None)
        super().__init__(*args, **kwargs)

        # ---- Limit guild choices to those belonging to the entity ----
        if self.entity:
            guild_qs = Guild.objects.filter(entity=self.entity)
            for field in ["guild_first", "guild_second", "guild_third"]:
                if field in self.fields:
                    self.fields[field].queryset = guild_qs
                    self.fields[field].empty_label = "Select Guild"
        else:
            # Fallback: show all guilds if no entity is provided (should not happen)
            for field in ["guild_first", "guild_second", "guild_third"]:
                if field in self.fields:
                    self.fields[field].queryset = Guild.objects.all()
                    self.fields[field].empty_label = "Select Guild"

        # ---- Pre‑populate children_names from JSON field ----
        if self.instance and self.instance.pk:
            children_list = self.instance.names_of_children or []
            if children_list:
                self.initial["children_names"] = "\n".join(children_list)

    def clean_children_names(self):
        """Convert the textarea input into a list of strings."""
        data = self.cleaned_data.get("children_names")
        if data:
            # Split by newlines and remove empty lines
            names = [line.strip() for line in data.split("\n") if line.strip()]
            return names
        return []

    def save(self, commit=True):
        """Save the member and handle JSON conversion for children_names."""
        instance = super().save(commit=False)
        # Set the JSON field to the processed list
        instance.names_of_children = self.cleaned_data.get("children_names", [])
        if commit:
            instance.save()
        return instance


# ChurchApp/forms.py
from django import forms
from django_ledger.models import EntityModel
from .models import Member


class MemberForm1(forms.ModelForm):
    class Meta:
        model = Member
        fields = "__all__"
        exclude = ["full_name", "is_deleted", "created_at", "updated_at"]
        widgets = {
            # Personal
            "title": forms.Select(attrs={"class": "form-select"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "other_names": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
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
                attrs={"class": "form-control", "type": "date"}
            ),
            "date_baptised": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "date_confirmed": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "date_enrolled": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "date_expired": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "guild_first": forms.TextInput(attrs={"class": "form-control"}),
            "guild_second": forms.TextInput(attrs={"class": "form-control"}),
            "guild_third": forms.TextInput(attrs={"class": "form-control"}),
            "no_of_children": forms.NumberInput(attrs={"class": "form-control"}),
            "names_of_children": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
            # Office
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
                attrs={"class": "form-control", "type": "date"}
            ),
            "spouse_near_landmark": forms.TextInput(attrs={"class": "form-control"}),
            "spouse_church": forms.TextInput(attrs={"class": "form-control"}),
            # Family
            "father_name": forms.TextInput(attrs={"class": "form-control"}),
            "father_res_address": forms.TextInput(attrs={"class": "form-control"}),
            "father_telephone": forms.TextInput(attrs={"class": "form-control"}),
            "father_deceased": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "mother_name": forms.TextInput(attrs={"class": "form-control"}),
            "mother_res_address": forms.TextInput(attrs={"class": "form-control"}),
            "mother_telephone": forms.TextInput(attrs={"class": "form-control"}),
            "mother_deceased": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            # Entity
            "entity": forms.Select(attrs={"class": "form-select"}),
        }
        labels = {
            "telephone1": "Primary Phone",
            "telephone2": "Secondary Phone",
            "res_address": "Residential Address",
            "near_landmark": "Near Landmark",
            "ghana_card_no": "Ghana Card Number",
            "date_enrolled": "Date Enrolled",
            "date_expired": "Date Expired",
            "guild_first": "Primary Guild",
            "guild_second": "Secondary Guild",
            "guild_third": "Tertiary Guild",
            "names_of_children": "Names of Children (comma separated)",
        }


# ChurchApp/forms.py
from django import forms
from django.utils import timezone
from .models import Service, Officiant, Clergy, Ushers, Guild


class ServiceForm(forms.ModelForm):
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


class ClergyForm(forms.ModelForm):
    class Meta:
        model = Clergy
        fields = "__all__"
        exclude = [
            "full_name",
            "entity",
        ]  # entity set in view, full_name auto-generated
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
            "email_address": "Email",
            "res_address": "Residential Address",
            "date_arrived": "Date Arrived",
            "date_depart": "Date Departed",
        }

    def __init__(self, *args, **kwargs):
        self.entity = kwargs.pop("entity", None)
        super().__init__(*args, **kwargs)
        # Limit member choices to those belonging to the same entity
        if self.entity:
            self.fields["member"].queryset = Member.objects.filter(
                entity=self.entity, is_deleted=False
            )
        else:
            self.fields["member"].queryset = Member.objects.none()

# ChurchApp/forms.py
from django import forms
from .models import Ushers, Member


class UsherForm(forms.ModelForm):
    class Meta:
        model = Ushers
        fields = "__all__"
        exclude = ["entity"]  # entity set in the view
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "telephone": forms.TextInput(attrs={"class": "form-control"}),
            "member": forms.Select(attrs={"class": "form-select"}),
        }
        labels = {
            "name": "Full Name",
            "telephone": "Phone Number",
            "member": "Church Member",
        }

    def __init__(self, *args, **kwargs):
        self.entity = kwargs.pop("entity", None)
        super().__init__(*args, **kwargs)
        # Limit member choices to those belonging to the same entity
        if self.entity:
            self.fields["member"].queryset = Member.objects.filter(
                entity=self.entity, is_deleted=False
            ).order_by("full_name")
        else:
            self.fields["member"].queryset = Member.objects.none()


# ChurchApp/forms.py
from django import forms
from .models import Guild


class GuildForm(forms.ModelForm):
    class Meta:
        model = Guild
        fields = "__all__"
        exclude = ["entity"]  # entity set in the view
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
        labels = {
            "name": "Guild Name",
            "description": "Description",
        }


# ChurchApp/forms.py
from django import forms
from .models import Officiant, Member


class OfficiantForm(forms.ModelForm):
    class Meta:
        model = Officiant
        fields = "__all__"
        exclude = ["entity"]  # entity set in the view
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "member": forms.Select(attrs={"class": "form-select"}),
        }
        labels = {
            "name": "Officiant Name",
            "description": "Description / Role",
            "member": "Church Member",
        }

    def __init__(self, *args, **kwargs):
        self.entity = kwargs.pop("entity", None)
        super().__init__(*args, **kwargs)
        # Limit member choices to those belonging to the same entity
        if self.entity:
            self.fields["member"].queryset = Member.objects.filter(
                entity=self.entity, is_deleted=False
            ).order_by("full_name")
        else:
            self.fields["member"].queryset = Member.objects.none()
