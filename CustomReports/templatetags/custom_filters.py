
# CustomReports/templatetags/custom_filters.py
from django import template


    
from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """Get an item from a dictionary by key"""
    if dictionary is None:
        return '-'
    try:
        return dictionary.get(key, '-')
    except AttributeError:
        return '-'