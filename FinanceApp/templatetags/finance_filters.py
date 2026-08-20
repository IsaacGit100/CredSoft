# finance/templatetags/finance_filters.py
from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def sum_debit(queryset):
    """Sum debit amounts in a queryset"""
    if not queryset:
        return Decimal('0')
    return sum(item.debit for item in queryset)

@register.filter
def sum_credit(queryset):
    """Sum credit amounts in a queryset"""
    if not queryset:
        return Decimal('0')
    return sum(item.credit for item in queryset)