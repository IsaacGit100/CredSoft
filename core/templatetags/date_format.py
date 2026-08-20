# core/templatetags/formatting_tags.py
from django import template
from django.utils import timezone
from decimal import Decimal
import datetime

# core/templatetags/date_format.py (if in core app)
from django import template
import datetime

register = template.Library()

@register.filter
def dmy(value):
    """Convert date to dd/mm/yyyy."""
    if not value:
        return ''
    if isinstance(value, datetime.datetime):
        value = value.date()
    if isinstance(value, datetime.date):
        return value.strftime('%d/%m/%Y')
    return value
