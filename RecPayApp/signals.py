# recpayapp/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Trans
from .utils import post_trans_to_ledger

@receiver(post_save, sender=Trans)
def trans_posted_to_ledger(sender, instance, **kwargs):
    if instance.journal_status == 'APPROVED' and not instance.journal_entry_id:
        post_trans_to_ledger(instance)
        
