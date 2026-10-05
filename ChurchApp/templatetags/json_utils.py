# ChurchApp/templatetags/json_utils.py

from django import template
from decimal import Decimal

register = template.Library()


@register.filter
def sum_json_offering(value):
    """Sum the 'amount' fields from a JSON list of objects."""
    if not value or not isinstance(value, list):
        return Decimal("0.00")
    total = sum(
        Decimal(item.get("amount", 0)) for item in value if isinstance(item, dict)
    )
    return total.quantize(Decimal("0.01"))
