# djan_led/checks.py
from django.core.checks import register, Tags

@register(Tags.compatibility)
def patch_account_model(app_configs, **kwargs):
    from django_ledger.models import AccountModel

    if not hasattr(AccountModel, '_str_patched'):
        def safe_str(self):
            try:
                role_display = self.balance_type if self.balance_type else self.role
                return f"{self.code} - {self.name} ({role_display})"
            except AttributeError:
                return f"{self.code} - {self.name}"
        AccountModel.__str__ = safe_str
        AccountModel._str_patched = True
        print("✅ Permanently patched AccountModel.__str__ via system check")
    return []