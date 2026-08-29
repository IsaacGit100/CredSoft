# core/templatetags/formatting_tags.py
from django import template
from django.utils import timezone
from decimal import Decimal
import datetime

register = template.Library()


@register.filter
def currency(value):
    """Format a number as currency with commas and two decimals."""
    if value is None:
        return '₵0.00'
    try:
        value = Decimal(str(value))
        # Format with commas, always two decimals
        return f'₵{value:,.2f}'
    except:
        return '₵0.00'

@register.filter
def comma(value):
    """Format a number with commas as thousand separators (no currency symbol)."""
    if value is None:
        return '0'
    try:
        value = Decimal(str(value))
        return f'{value:,.2f}'
    except:
        return '0'