# help_module/context_processors.py
from .models import HelpCategory, HelpTopic

def help_context(request):
    """Add help data to all templates"""
    return {
        'help_categories': HelpCategory.objects.filter(is_active=True)[:5],
        'help_topics': HelpTopic.objects.filter(is_active=True, is_featured=True)[:5],
    }