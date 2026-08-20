from django import template
from django.template.defaultfilters import stringfilter
from decimal import Decimal

register = template.Library()

@register.filter
def abs(value):
    """Return absolute value - works with int, float, Decimal, string"""
    if value is None:
        return 0
    
    try:
        # Handle Decimal objects
        if isinstance(value, Decimal):
            return abs(value)
        # Handle numbers
        if isinstance(value, (int, float)):
            return abs(value)
        # Handle strings
        if isinstance(value, str):
            return abs(float(value))
        return abs(value)
    except (ValueError, TypeError, AttributeError):
        return value

@register.filter
def currency(value):
    """Format as Ghana Cedi"""
    from django.contrib.humanize.templatetags.humanize import intcomma
    
    if value is None:
        return '₵0.00'
    
    try:
        val = float(value)
        is_negative = val < 0
        abs_val = abs(val)
        
        formatted = f"₵{intcomma(f'{abs_val:.2f}')}"
        
        if is_negative:
            return f"({formatted})"
        return formatted
    except (ValueError, TypeError):
        return '₵0.00'

@register.filter
def positive(value):
    """Return positive representation (for display)"""
    if value is None:
        return 0
    try:
        return abs(float(value))
    except (ValueError, TypeError):
        return value

@register.filter
def is_negative(value):
    """Check if value is negative"""
    try:
        return float(value) < 0
    except (ValueError, TypeError):
        return False