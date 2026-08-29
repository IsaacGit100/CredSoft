# templatetags/help_tags.py
from django import template
from django.urls import resolve

register = template.Library()

@register.simple_tag
def get_help_url(request):
    """Get help URL based on current page"""
    current_url = resolve(request.path_info).url_name
    
    help_map = {
        'system_setup': 'SYSTEM_SETUP',
        'user_list': 'USERS',
        'member_list': 'MEMBERS',
        'chart_of_accounts_list': 'CHART_OF_ACCOUNTS',
        'loan_list': 'LOANS',
        'receipt_list': 'RECEIPTS_PAYMENTS',
        'financial_reports': 'FINANCE',
        'investment_list': 'INVESTMENTS',
    }
    
    module = help_map.get(current_url, '')
    if module:
        return f'/help/module/{module}/'
    return '/help/'