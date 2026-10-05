from django.db.models.signals import pre_save
from django.dispatch import receiver
from django_ledger.models import AccountModel


@receiver(pre_save, sender=AccountModel)
def auto_activate_accounts(sender, instance, **kwargs):
    """Every new account starts active. Users can deactivate individually."""
    if instance._state.adding and not instance.active:
        instance.active = True
