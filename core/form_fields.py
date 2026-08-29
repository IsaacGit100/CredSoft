# core/form_fields.py
from django import forms
from django.core.exceptions import ValidationError
from decimal import Decimal
import datetime

class CommaDecimalField(forms.DecimalField):
    """Accepts numbers with commas (e.g., 1,234,567.89) and stores as Decimal."""
    def to_python(self, value):
        if value in self.empty_values:
            return None
        if isinstance(value, (int, float, Decimal)):
            return value
        value = str(value).replace(',', '')
        try:
            return super().to_python(value)
        except ValidationError:
            raise ValidationError("Enter a valid number (e.g., 1,234.56)")

    def prepare_value(self, value):
        if isinstance(value, (int, float, Decimal)):
            return f"{value:,.2f}"
        return value


class DDMMYYYYDateField(forms.DateField):
    """Accepts dates in dd/mm/yyyy format."""
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('input_formats', ['%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y'])
        super().__init__(*args, **kwargs)

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        attrs.setdefault('placeholder', 'dd/mm/yyyy')
        return attrs

    def prepare_value(self, value):
        if isinstance(value, datetime.date):
            return value.strftime('%d/%m/%Y')
        return value