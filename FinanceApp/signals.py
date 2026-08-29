# FinanceApp/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
import sys

# Import models here, not at the top of the file
# This prevents circular imports

@receiver(post_save, sender='RecPayApp.Trans')  # Use string reference instead of direct import
def auto_create_journal_from_transaction(sender, instance, created, **kwargs):
    """Auto-create journal when transaction is saved"""
    
    if not created:
        return
    
    # Import models inside the function to avoid circular imports
    from .models import JournalEntry, JournalLine
    from coa.models import ChartOfAccounts
    
    # ... rest of your code