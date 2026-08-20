from django import forms
from .models import AssetCategory, FixedAsset
from coa.models import ChartOfAccounts


class FixedAssetForm(forms.ModelForm):
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

from django import forms
from django_ledger.models import AccountModel
from .models import FixedAsset



from django import forms
from django_ledger.models import AccountModel
from .models import AssetCategory


class AssetCategoryForm(forms.ModelForm):
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
