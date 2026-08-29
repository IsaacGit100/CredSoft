#from django.apps import AppConfig


#class DjanLedConfig(AppConfig):
#    default_auto_field = "django.db.models.BigAutoField"
#    name = "djan_led"

from django.apps import AppConfig, apps


class DjanLedConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "djan_led"

    def ready(self):
        try:
            AccountModel = apps.get_model(
                "django_ledger",
                "AccountModel"
            )
        except LookupError:
            return

        if getattr(AccountModel, "_djan_led_str_patched", False):
            return

        def safe_str(self):
            try:
                code = getattr(self, "code", "")
                name = getattr(self, "name", "")

                balance_type = getattr(self, "balance_type", None)
                role = getattr(self, "role", None)

                role_display = balance_type or role or ""

                if role_display:
                    return f"{code} - {name} ({role_display})"

                return f"{code} - {name}"

            except Exception:
                return "Account"

        AccountModel.__str__ = safe_str
        AccountModel._djan_led_str_patched = True