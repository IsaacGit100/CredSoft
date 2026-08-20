import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CredSoft.settings')
django.setup()

from django_ledger.models import EntityModel, LedgerModel, JournalEntryModel, AccountModel, TransactionModel
from decimal import Decimal

entity = EntityModel.objects.get(slug='st-ann-parish')

# Get or create a ledger
ledger = LedgerModel.objects.filter(entity=entity).first()
if not ledger:
    ledger = LedgerModel.objects.create(
        entity=entity,
        name='Default Ledger',
    )
    print(f"✅ Created ledger: {ledger.name}")
else:
    print(f"✅ Using existing ledger: {ledger.name}")

# Step 1: Create Journal Entry as DRAFT (posted=False)
je = JournalEntryModel.objects.create(
    entity=entity,
    ledger=ledger,
    date='2026-01-01',
    description='Opening balance',
    posted=False,  # <-- Important: create as draft
)

# Get accounts
cash = AccountModel.objects.get(coa_model__entity=entity, code='1010')
equity = AccountModel.objects.get(coa_model__entity=entity, code='3010')

# Create transactions
TransactionModel.objects.create(
    journal_entry=je,
    account=cash,
    amount=Decimal('10000.00'),
    tx_type='debit'
)
TransactionModel.objects.create(
    journal_entry=je,
    account=equity,
    amount=Decimal('10000.00'),
    tx_type='credit'
)

# Step 2: Mark as posted
je.posted = True
je.save()

print("✅ Opening balance posted for St. Ann Parish")
print(f"   Cash: +10000.00 (debit)")
print(f"   Owner's Equity: +10000.00 (credit)")