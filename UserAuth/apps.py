    
# UserAuth/apps.py
from django.apps import AppConfig

class UserAuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'UserAuth'
    
    def ready(self):
        import UserAuth.signals  # This loads the signals
