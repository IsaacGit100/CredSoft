# MembersApp/forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import Master
from datetime import datetime


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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
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
        
        # Set queryset for approval fields
        self.fields['approved_by_chairman'].queryset = Master.objects.filter(role='Chairman')
        self.fields['approved_by_manager'].queryset = Master.objects.filter(role='Manager')
        
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
 
 
    
# MembersApp/forms.py
from django import forms
from .models import Master

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