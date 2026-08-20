# djan_led/lazy_loader_patch.py
"""
Monkey‑patch the LazyLoader in django‑ledger to prevent AppRegistryNotReady.
Place this file and import it at the very top of manage.py and wsgi.py.
"""
import sys

# The problematic class
target = 'django_ledger.models.utils.LazyLoader'

# Define a safe __getattribute__ that never raises AppRegistryNotReady
def safe_getattribute(self, name):
    if name == '__class__':
        return object.__getattribute__(self, name)
    try:
        # Use the original method if possible
        orig = object.__getattribute__(self, '_orig_getattribute')
        return orig(name)
    except AttributeError:
        # Fallback: return None for any missing attribute
        return None

def apply_patch():
    try:
        import django_ledger.models.utils as utils
        LazyLoader = utils.LazyLoader

        # Store the original __getattribute__ if not already patched
        if not hasattr(LazyLoader, '_patched'):
            orig = LazyLoader.__getattribute__
            LazyLoader._orig_getattribute = orig
            LazyLoader.__getattribute__ = safe_getattribute
            LazyLoader._patched = True
            print("✅ LazyLoader patched successfully.")
        else:
            print("ℹ️ LazyLoader already patched.")
    except Exception as e:
        print(f"⚠️ Could not patch LazyLoader: {e}")

# Apply the patch immediately when this module is imported
apply_patch()