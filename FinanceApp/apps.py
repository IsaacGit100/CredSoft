from django.apps import AppConfig


class FinanceAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'FinanceApp'
    
    def ready(self):
        # Prevent duplicate signal registration
        import sys
        if 'makemigrations' not in sys.argv and 'migrate' not in sys.argv:
            try:
                import FinanceApp.signals
            except ImportError:
                pass