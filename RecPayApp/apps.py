from django.apps import AppConfig

class RecpayappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'RecPayApp'  # Must match the app name in INSTALLED_APPS

    def ready(self):
        import RecPayApp.signals  # noqa
