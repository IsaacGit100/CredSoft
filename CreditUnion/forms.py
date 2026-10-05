# CreditUnion/forms.py
from django import forms
from MembersApp.models import Master
from django.core.exceptions import ValidationError
from decimal import Decimal
from RecPayApp.models import Trans


from datetime import datetime
from django_ledger.models import (
    EntityModel,
    JournalEntryModel,
    TransactionModel,
    AccountModel,
    LedgerModel,
)

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

class MasterForm(forms.ModelForm):
    """Member form with NOK percentage validation"""
    class Meta:
        model = Master
        fields = [
            'title', 'first_name', 'last_name', 'other_names', 
            'date_of_birth', 'date_enrolled', 'gender', 'marital_status',
            'church_member', 'profession', 'role', 'ghana_card_no',
            
            # Contact Information
            'postal_address', 'residential_address', 'city', 'street_name', 
            'near_landmark', 'gps', 'telephone1', 'telephone2', 'email_address',
            
            # Next of Kin 1
            'nok_name1', 'nok_relation1', 'nok_address1', 'nok_telephone1', 
            'nok_gps1', 'nok_email1', 'nok_percent1',
            
            # Next of Kin 2
            'nok_name2', 'nok_relation2', 'nok_address2', 'nok_telephone2', 
            'nok_gps2', 'nok_email2', 'nok_percent2',
            
            # Next of Kin 3
            'nok_name3', 'nok_relation3', 'nok_address3', 'nok_telephone3', 
            'nok_gps3', 'nok_email3', 'nok_percent3',
            
            # Financial
            'enroll_fees_paid', 'min_shares_purchased',
            
            # Approval
            'approved_by_chairman', 'approved_by_manager',
            
            # Image Processing
            'profile_image', 'signature', 'id_card_front', 'id_card_back',
        ]

        widgets = {
            'postal_address': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'residential_address': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'nok_address1': forms.Textarea(attrs={'rows': 1, 'class': 'form-control'}),
            'nok_address2': forms.Textarea(attrs={'rows': 1, 'class': 'form-control'}),
            'nok_address3': forms.Textarea(attrs={'rows': 1, 'class': 'form-control'}),
            
            'date_of_birth': forms.DateInput(
                format='%d/%m/%Y',
                attrs={
                    'class': 'form-control',
                    'type': 'text',
                    'placeholder': 'dd/mm/yyyy',
                    'pattern': '\\d{2}/\\d{2}/\\d{4}'
                }
            ),
            'date_enrolled': forms.DateInput(
                format='%d/%m/%Y',
                attrs={
                    'class': 'form-control',
                    'type': 'text',
                    'placeholder': 'dd/mm/yyyy',
                    'pattern': '\\d{2}/\\d{2}/\\d{4}'
                }
            ),
            'profile_image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'signature': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'id_card_front': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'id_card_back': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }


    def __init__(self, *args, entity=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.entity = entity
    
        # Add form-control class to all fields
        for field_name, field in self.fields.items():
            if field_name not in ['church_member', 'gender', 'marital_status', 'title', 
                                   'enroll_fees_paid', 'min_shares_purchased', 'role']:
                field.widget.attrs.update({'class': 'form-control'})

            # Add specific classes for select fields
            if field_name in ['title', 'gender', 'marital_status', 'church_member', 'role']:
                field.widget.attrs.update({'class': 'form-select'})

        # Set date input formats
        self.fields['date_of_birth'].input_formats = ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d']
        self.fields['date_enrolled'].input_formats = ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d']
        
        if entity is not None:
            self.fields["approved_by_chairman"].queryset = Master.objects.filter(
            entity=entity, role="Chairman", is_deleted=False,
            )
            self.fields["approved_by_manager"].queryset = Master.objects.filter(
            entity=entity, role="Manager", is_deleted=False,
            )
        else:
        # no entity → no choices; form will fail validation cleanly
            self.fields["approved_by_chairman"].queryset = Master.objects.none()
            self.fields["approved_by_manager"].queryset = Master.objects.none()

        # Make NOK percentage fields optional
        self.fields['nok_percent1'].required = False
        self.fields['nok_percent2'].required = False
        self.fields['nok_percent3'].required = False

    def clean_date_of_birth(self):
        date_str = self.cleaned_data.get('date_of_birth')
        if date_str:
            if isinstance(date_str, str):
                for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d']:
                    try:
                        return datetime.strptime(date_str, fmt).date()
                    except ValueError:
                        continue
                raise ValidationError('Please enter date in DD/MM/YYYY format')
        return date_str

    def clean_date_enrolled(self):
        date_str = self.cleaned_data.get('date_enrolled')
        if date_str:
            if isinstance(date_str, str):
                for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d']:
                    try:
                        return datetime.strptime(date_str, fmt).date()
                    except ValueError:
                        continue
                raise ValidationError('Please enter date in DD/MM/YYYY format')
        return date_str

    def clean(self):
        cleaned_data = super().clean()

        # Get NOK percentages
        percent1 = cleaned_data.get('nok_percent1', 0) or 0
        percent2 = cleaned_data.get('nok_percent2', 0) or 0
        percent3 = cleaned_data.get('nok_percent3', 0) or 0

        # Calculate total percentage
        total_percent = percent1 + percent2 + percent3

        # Validation: Either all are 0 (no NOK) OR total must be exactly 100%
        if total_percent > 0 and total_percent != 100:
            raise ValidationError(
                f'Next of Kin percentages must total 100%. Current total: {total_percent}%'
            )

        # If percentages are set, ensure NOK names are provided
        if percent1 > 0 and not cleaned_data.get('nok_name1'):
            raise ValidationError('Please provide name for Next of Kin 1')

        if percent2 > 0 and not cleaned_data.get('nok_name2'):
            raise ValidationError('Please provide name for Next of Kin 2')

        if percent3 > 0 and not cleaned_data.get('nok_name3'):
            raise ValidationError('Please provide name for Next of Kin 3')

        # Validate that percentages don't exceed 100 individually
        if percent1 > 100:
            raise ValidationError('NOK 1 percentage cannot exceed 100%')
        if percent2 > 100:
            raise ValidationError('NOK 2 percentage cannot exceed 100%')
        if percent3 > 100:
            raise ValidationError('NOK 3 percentage cannot exceed 100%')

        return cleaned_data


class MasterSearchForm(forms.Form):

    """Search form for members"""
    q = forms.CharField(required=False, label='Search', 
                        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by name, phone, email...'}))


class MemberSettingsForm(forms.ModelForm):
    class Meta:
        model = Master
        fields = ['sav_int_rate', 'sav_defer_int_appl', 'loan_int_rate']
        widgets = {
            'sav_int_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.0001',
                'placeholder': 'e.g., 2.5000'
            }),
            'sav_defer_int_appl': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'loan_int_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.0001',
                'placeholder': 'e.g., 3.0000'
            }),
        }
        labels = {
            'sav_int_rate': 'Savings Interest Rate (%)',
            'sav_defer_int_appl': 'Defer Interest Application',
            'loan_int_rate': 'Loan Interest Rate (%)',
        }


class DepositWithdrawalForm(forms.ModelForm):

    txn_type = forms.ChoiceField(
        choices=[("Deposit", "Deposit"), ("Withdrawal", "Withdrawal")],
        widget=forms.RadioSelect(attrs={"class": "dwd-radio"}),
        initial="Deposit",
        label="Transaction Type",
    )

    member = forms.ModelChoiceField(
        queryset=Master.objects.filter(is_deleted=False).order_by(
            "last_name", "first_name"
        ),
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Member",
        required=True,
    )

    class Meta:
        model = Trans
        fields = ["date", "trans_no", "amount", "details"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "trans_no": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Receipt / Voucher No",
                }
            ),
            "amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0.01",
                }
            ),
            "pay_mode": forms.Select(attrs={"class": "form-select"}),
            "details": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. Monthly savings",
                }
            ),
        }

    def __init__(self, *args, entity=None, user=None, **kwargs):
        self.entity = entity
        self.user = user
        super().__init__(*args, **kwargs)

        if entity:
            self.fields["member"].queryset = Master.objects.filter(
                entity=entity, is_deleted=False
            ).order_by("last_name", "first_name")
            self.fields["member"].label_from_instance = lambda obj: f"{obj.full_name} ({obj.id})"

        if self.instance and self.instance.pk:
            if self.instance.member_id:
                self.fields["member"].initial = self.instance.member

            if self.instance.sub_module == "savings_deposit":
                self.fields["txn_type"].initial = "Deposit"
            elif self.instance.sub_module == "savings_withdrawal":
                self.fields["txn_type"].initial = "Withdrawal"

    def save(self, commit=True):
        trans = super().save(commit=False)

        txn_type = self.cleaned_data.get("txn_type", "Deposit")
        is_deposit = txn_type == "Deposit"

        # tags
        trans.entity = self.entity
        trans.module = "credit_union"
        trans.sub_module = "savings_deposit" if is_deposit else "savings_withdrawal"
        trans.trans_type = "Receipts" if is_deposit else "Payments"
        trans.pay_mode = "Cash"

        # member
        member = self.cleaned_data.get("member")
        trans.member = member
        trans.member_no = member.id if member else 0
        trans.member_name = member.full_name if member else ""

        # ledger target — always Member Savings (2021)
        trans.ledger_code = "2021"
        trans.ledger_name = "Member Savings"
        trans.purpose = "Deposit" if is_deposit else "Withdrawal"

        # audit
        if self.user:
            trans.created_by = self.user
            trans.created_by_name = self.user.get_full_name() or self.user.username
            trans.created_by_username = self.user.username

        # rec/vou number prefix
        rec_vou_no = self.cleaned_data.get("trans_no") or ""
        if rec_vou_no:
            trans.rec_vou_no = (
                f"DEP:{rec_vou_no}" if is_deposit else f"WTH:{rec_vou_no}"
            )

        # journal flags
        trans.status = "DRAFT"
        trans.journal_status = "PENDING"

        if commit:
            trans.save()
        return trans

from django import forms
from .models import CreditUnionConfig


class CreditUnionConfigForm(forms.ModelForm):
    class Meta:
        model = CreditUnionConfig
        fields = [
            # Savings
            "savings_interest_rate",
            "savings_interest_application",
            "savings_calc_type",
            "min_savings_balance",
            "savings_frequency",
            # Loans
            "loan_interest_rate",
            "max_loan_term",
            "min_loan_amount",
            "moratorium_days",
            # Membership
            "membership_fee",
            "min_shares",
            # Account mappings
            "loan_asset_account_code",
            "loan_interest_income_code",
            "interest_expense_account_code",
            "savings_interest_payable_account_code",
        ]
        widgets = {
            "savings_interest_rate": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                }
            ),
            "savings_interest_application": forms.Select(
                attrs={"class": "form-select"}
            ),
            "savings_calc_type": forms.Select(attrs={"class": "form-select"}),
            "min_savings_balance": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                }
            ),
            "savings_frequency": forms.TextInput(attrs={"class": "form-control"}),
            "loan_interest_rate": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.0001",
                    "min": "0",
                }
            ),
            "max_loan_term": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                }
            ),
            "min_loan_amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                }
            ),
            "moratorium_days": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                }
            ),
            "membership_fee": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                }
            ),
            "min_shares": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                }
            ),
            "loan_asset_account_code": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. 1080",
                }
            ),
            "loan_interest_income_code": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. 4010",
                }
            ),
            "interest_expense_account_code": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. 6110",
                }
            ),
            "savings_interest_payable_account_code": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. 2022",
                }
            ),
        }
