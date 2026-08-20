# SysSetup/context_processors.py
from .models import SystemSettings


def system_settings(request):
    """
    Make system settings available to all templates
    """
    # Get or create settings
    settings, created = SystemSettings.objects.get_or_create(id=1)
    
    return {
        'system_settings': settings,
        'company_name': settings.company_name,
        'company_short_name': settings.company_short_name,
        'currency': settings.currency,
        'currency_symbol': settings.currency_symbol,
        'date_format': settings.date_format,
    }