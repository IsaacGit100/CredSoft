from django.apps import AppConfig


class RecPayAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "RecPayApp"

    def ready(self):
        # import RecPayApp.signals  # noqa    ← delete or comment this line
        pass
