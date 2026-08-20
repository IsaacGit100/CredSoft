# core/form_fields.py
from django import forms
from django.core.exceptions import ValidationError
from decimal import Decimal
import datetime

from django import forms
from decimal import Decimal
import datetime

class CommaDecimalField(forms.DecimalField):
    widget = forms.TextInput   # Force plain text input

    def __init__(self, *args, **kwargs):
        # Set defaults if not provided
        if 'max_digits' not in kwargs:
            kwargs['max_digits'] = 15
        if 'decimal_places' not in kwargs:
            kwargs['decimal_places'] = 2
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        if value in self.empty_values:
            return None
        if isinstance(value, (int, float, Decimal)):
            return value
        # Remove commas
        value = str(value).strip().replace(',', '')
        try:
            return super().to_python(value)
        except forms.ValidationError:
            raise forms.ValidationError("Enter a valid number (e.g., 1,234.56)")

    def prepare_value(self, value):
        # Display with commas
        if isinstance(value, (int, float, Decimal)):
            return f"{value:,.2f}"
        return value

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        attrs.setdefault('placeholder', '0.00')
        return attrs


