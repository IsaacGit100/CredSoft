from django import forms
from django.utils.text import slugify
from decimal import Decimal
from django_ledger.models import EntityModel, AccountModel

class CreateParishForm(forms.Form):
    from django_ledger.models import EntityModel, AccountModel
    name = forms.CharField(
        max_length=100,
        label="Parish Name",
        help_text="e.g., St. Ann Parish"
    )
    slug = forms.SlugField(
        max_length=100,
        label="Slug (URL identifier)",
        help_text="Auto-generated from name if left blank.",
        required=False
    )
    parent_entity = forms.ModelChoiceField(
        queryset=EntityModel.objects.all(),  # all entities allowed as parent
        label="Parent Entity",
        required=True,
    )


    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        name = self.cleaned_data.get('name')
        if not slug:
            slug = slugify(name)
        if EntityModel.objects.filter(slug=slug).exists():
            raise forms.ValidationError(f"A parish with slug '{slug}' already exists.")
        return slug


class RecordOfferingForm(forms.Form):
    from django_ledger.models import EntityModel, AccountModel
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    amount = forms.DecimalField(
        max_digits=15, 
        decimal_places=2,
        min_value=0.01,
        widget=forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0.00'})
    )
    description = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Offering - St. Ann Parish'})
    )  


class AddAccountForm(forms.Form):
    
   
    parent = forms.ModelChoiceField(
       
        queryset=AccountModel.objects.none(),  # Will be set dynamically
        label="Parent Account (Main Heading)",
        help_text="Select the main heading this account belongs to."
    )
    role = forms.ChoiceField(
        choices=[
            ('asset', 'Asset'),
            ('liability', 'Liability'),
            ('equity', 'Equity'),
            ('revenue', 'Revenue'),
            ('expense', 'Expense'),
        ],
        label="Role"
    )
    balance_type = forms.ChoiceField(
        choices=[
            ('debit', 'Debit'),
            ('credit', 'Credit'),
        ],
        label="Balance Type",
        help_text="Debit for Assets & Expenses; Credit for Liabilities, Equity & Revenue."
    )
    code = forms.CharField(
        max_length=20,
        label="Account Code",
        help_text="e.g., 1010 or 1050.01"
    )
    name = forms.CharField(
        max_length=100,
        label="Account Name",
        help_text="e.g., Cash, Building Fund"
    )

    def __init__(self, *args, **kwargs):
        # Pop the 'entity' argument passed from the view
        entity = kwargs.pop('entity', None)
        # Call super().__init__ with the remaining args and kwargs
        super().__init__(*args, **kwargs)

        if entity:
            coa = entity.get_default_coa()
            if coa:
                # Show account type roots (depth=2) as parent options
                self.fields['parent'].queryset = AccountModel.objects.filter(
                    coa_model=coa,
                    depth=2
                ).order_by('code')
            else:
                self.fields['parent'].help_text = "No Chart of Accounts found. Please autofill first."

class OpeningBalanceForm(forms.Form):
    from django_ledger.models import EntityModel, AccountModel
    """
    A form that dynamically creates fields for each account.
    Each account gets a debit and credit field, but only one should be filled.
    """
    def __init__(self, *args, **kwargs):
        accounts = kwargs.pop('accounts', [])
        super().__init__(*args, **kwargs)
        for acc in accounts:
            # We'll create two fields per account: debit_<code> and credit_<code>
            self.fields[f'debit_{acc.code}'] = forms.DecimalField(
                required=False,
                min_value=0,
                decimal_places=2,
                max_digits=15,
                initial=0,
                widget=forms.NumberInput(attrs={'class': 'form-control debit-input', 'data-code': acc.code, 'step': '0.01'})
            )
            self.fields[f'credit_{acc.code}'] = forms.DecimalField(
                required=False,
                min_value=0,
                decimal_places=2,
                max_digits=15,
                initial=0,
                widget=forms.NumberInput(attrs={'class': 'form-control credit-input', 'data-code': acc.code, 'step': '0.01'})
            )
            # Store the account object for later use
            self.fields[f'debit_{acc.code}'].account = acc
            self.fields[f'credit_{acc.code}'].account = acc

    def clean(self):
        cleaned_data = super().clean()
        total_debits = Decimal('0')
        total_credits = Decimal('0')
        # Collect balances per account
        for field_name, value in cleaned_data.items():
            if field_name.startswith('debit_') and value:
                total_debits += value
            elif field_name.startswith('credit_') and value:
                total_credits += value
        # Ensure at least one balance is entered
        if total_debits == 0 and total_credits == 0:
            raise forms.ValidationError("Please enter at least one opening balance.")
        if total_debits != total_credits:
            raise forms.ValidationError(f"Total Debits ({total_debits}) must equal Total Credits ({total_credits}).")
        return cleaned_data

from django import forms
from .models import EntityConfig


class EntityConfigForm(forms.ModelForm):
    class Meta:
        model = EntityConfig
        exclude = ["entity"]  # entity is set automatically
        widgets = {
            "fiscal_year_start": forms.DateInput(attrs={"type": "date"}),
        }
