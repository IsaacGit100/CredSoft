from django import forms
from django.core.exceptions import ValidationError
from decimal import Decimal
import datetime
from django import template

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