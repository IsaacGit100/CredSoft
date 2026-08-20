from django.apps import AppConfig


class FixedassetsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'FixedAssets'
    
    def ready(self):
        # Import inside ready, when app registry is ready
        from django_ledger.models import AccountModel



    def safe_account_str(self):
        """Override the buggy __str__ method that uses role_bs."""
        # Use balance_type if available, otherwise fallback to role.
        role_display = self.balance_type if hasattr(self, 'balance_type') else self.role
        return f"{self.code} - {self.name} ({self.role})"

class DjanLedConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'djan_led'

    def ready(self):
        # Monkey‑patch the __str__ method to avoid AttributeError
        AccountModel.__str__ = safe_account_str