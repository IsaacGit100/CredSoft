# djan_led/middleware.py
from django.utils.deprecation import MiddlewareMixin

class AccountModelPatchMiddleware(MiddlewareMixin):
    def process_request(self, request):
        from django_ledger.models import AccountModel

        # Patch only once
        if not hasattr(AccountModel, '_str_patched'):
            original_str = AccountModel.__str__

            def safe_str(self):
                try:
                    # Use balance_type if available, else fallback to role
                    role_display = self.balance_type if self.balance_type else self.role
                    return f"{self.code} - {self.name} ({role_display})"
                except AttributeError:
                    # Ultimate fallback
                    return f"{self.code} - {self.name}"

            AccountModel.__str__ = safe_str
            AccountModel._str_patched = True
            print("✅ Permanently patched AccountModel.__str__")

        return None