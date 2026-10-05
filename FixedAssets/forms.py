from django import forms
from .models import AssetCategory, FixedAsset
from coa.models import ChartOfAccounts
from django_ledger.models import AccountModel

class FixedAssetForm1(forms.ModelForm):
    class Meta:
        model = FixedAsset
        fields = '__all__'
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'purchase_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'acquisition_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'disposal_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'salvage_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'override_depreciation_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            
            'asset_id': forms.TextInput(attrs={'class': 'form-control'}),
            'useful_life_years': forms.NumberInput(attrs={'class': 'form-control'}),
            'depreciation_method': forms.Select(attrs={'class': 'form-select'}),
            
       }


class AssetCategoryForm1(forms.ModelForm):
    asset_account = forms.ModelChoiceField(
        queryset=AccountModel.objects.none(),
        label="Asset Account",
        help_text="The GL account for the asset cost.",
    )
    accumulated_depreciation_account = forms.ModelChoiceField(
        queryset=AccountModel.objects.none(),
        label="Accumulated Depreciation Account",
        help_text="Contra-asset account.",
    )
    depreciation_expense_account = forms.ModelChoiceField(
        queryset=AccountModel.objects.none(),
        label="Depreciation Expense Account",
        help_text="Expense account for depreciation.",
    )

    class Meta:
        model = AssetCategory
        fields = [
            "name",
            "depreciation_method",
            "useful_life_years",
            "salvage_value_percent",
            "asset_account",
            "accumulated_depreciation_account",
            "depreciation_expense_account",
            "depreciation_rate",
        ]


# ===================================================================
# FixedAssets/forms.py

from django import forms
from .models import FixedAsset, AssetCategory


class FixedAssetForm(forms.ModelForm):
    class Meta:
        model = FixedAsset
        fields = [
            "category", "asset_id", "name", "description", "acquisition_date", "cost", "salvage_value", "useful_life_years",
            "depreciation_method", "override_depreciation_rate", "payment_mode", "bank_name", "bank_branch", "bank_account_no",
            "cheque_no", "seller_name", "seller_contact", "seller_address",
        ]
        
        widgets = {
            "category": forms.Select(attrs={"class": "form-select"}),
            "asset_id": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g., FA-001"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "acquisition_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "cost": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "salvage_value": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "useful_life_years": forms.NumberInput(attrs={"class": "form-control"}),
            "depreciation_method": forms.Select(attrs={"class": "form-select"}),
            "override_depreciation_rate": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
        }

    def __init__(self, *args, **kwargs):
        self.entity = kwargs.pop("entity", None)
        super().__init__(*args, **kwargs)
        if self.entity:
            self.fields["category"].queryset = AssetCategory.objects.filter(
                entity=self.entity
            )


class AssetCategoryForm(forms.ModelForm):
    class Meta:
        model = AssetCategory
        fields = [
            "name",
            "depreciation_method",
            "useful_life_years",
            "salvage_value_percent",
            "depreciation_rate",
            "asset_account",
            "accumulated_depreciation_account",
            "depreciation_expense_account",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "depreciation_method": forms.Select(attrs={"class": "form-select"}),
            "useful_life_years": forms.NumberInput(attrs={"class": "form-control"}),
            "salvage_value_percent": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "depreciation_rate": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "asset_account": forms.Select(attrs={"class": "form-select"}),
            "accumulated_depreciation_account": forms.Select(
                attrs={"class": "form-select"}
            ),
            "depreciation_expense_account": forms.Select(
                attrs={"class": "form-select"}
            ),
        }

    def __init__(self, *args, **kwargs):
        self.entity = kwargs.pop("entity", None)
        super().__init__(*args, **kwargs)

        if self.entity:
            coa = self.entity.get_default_coa()
            if coa:
                # Filter accounts by entity's COA
                accounts = AccountModel.objects.filter(coa_model=coa).order_by("code")

                # Asset accounts are usually under Assets (1xxx)
                self.fields["asset_account"].queryset = accounts.filter(
                    code__startswith="1"
                )
                # Accumulated depreciation is a contra-asset (also under 1xxx, credit)
                self.fields["accumulated_depreciation_account"].queryset = (
                    accounts.filter(code__startswith="1")
                )
                # Depreciation expense is under Expenses (6xxx)
                self.fields["depreciation_expense_account"].queryset = accounts.filter(
                    code__startswith="6"
                )

            # Make account fields optional during creation
            self.fields["asset_account"].required = False
            self.fields["accumulated_depreciation_account"].required = False
            self.fields["depreciation_expense_account"].required = False
