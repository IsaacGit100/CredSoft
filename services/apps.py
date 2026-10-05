from django.apps import AppConfig


class ServicesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "services"

    def ready(self):
        from .posting_handlers import credit_union_handlers   # noqa
        from .posting_handlers import church_giving            # noqa
        from .posting_handlers import fixed_assets             # noqa
