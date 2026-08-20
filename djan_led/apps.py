from django.apps import AppConfig


from django.apps import AppConfig
from django.apps import apps

class DjanLedConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'djan_led'

    def ready(self):
        try:
            AccountModel = apps.get_model('django_ledger', 'AccountModel')
            if not hasattr(AccountModel, '_str_patched'):
                def safe_str(self):
                    try:
                        role_display = self.balance_type if self.balance_type else self.role
                        return f"{self.code} - {self.name} ({role_display})"
                    except AttributeError:
                        return f"{self.code} - {self.name}"
                AccountModel.__str__ = safe_str
                AccountModel._str_patched = True
                print("✅ Patched AccountModel.__str__")
        except Exception as e:
            print(f"⚠️ Could not patch AccountModel: {e}")