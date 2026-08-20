# add_accounts.py
import os

import django

try:
    import djan_led.lazy_loader_patch  # noqa
except ImportError:
    pass
os.environ['DJANGO_LEDGER_USE_DEPRECATED_BEHAVIOR'] = 'True'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CredSoft.settings')
django.setup()

from django_ledger.models import EntityModel, AccountModel

# Get the entity
entity = EntityModel.objects.get(slug='st-ann-parish')
coa = entity.get_default_coa()

# Get root nodes
root_assets = AccountModel.objects.get(coa_model=coa, name='Asset Accounts Root Node')
root_liabilities = AccountModel.objects.get(coa_model=coa, name='Liability Accounts Root Node')
root_capital = AccountModel.objects.get(coa_model=coa, name='Capital Accounts Root Node')
root_income = AccountModel.objects.get(coa_model=coa, name='Income Accounts Root Node')
root_expenses = AccountModel.objects.get(coa_model=coa, name='Expense Accounts Root Node')

# Define accounts: (code, name, role, balance_type, parent)
accounts_to_add = [
    # Assets (Debit balance)
    ('1010', 'Cash', 'asset', 'debit', root_assets),
    ('1020', 'Bank', 'asset', 'debit', root_assets),
    ('1030', 'Accounts Receivable', 'asset', 'debit', root_assets),
    ('1040', 'Inventory', 'asset', 'debit', root_assets),
    ('1050', 'Prepaid Expenses', 'asset', 'debit', root_assets),
    ('1060', 'Office Equipment', 'asset', 'debit', root_assets),
    ('1070', 'Buildings', 'asset', 'debit', root_assets),

    # Liabilities (Credit balance)
    ('2010', 'Accounts Payable', 'liability', 'credit', root_liabilities),
    ('2020', 'Accrued Expenses', 'liability', 'credit', root_liabilities),
    ('2030', 'Bank Loans', 'liability', 'credit', root_liabilities),

    # Equity (Credit balance)
    ('3010', "Owner's Equity", 'equity', 'credit', root_capital),
    ('3020', 'Retained Earnings', 'equity', 'credit', root_capital),

    # Revenue (Credit balance)
    ('4010', 'Revenue', 'revenue', 'credit', root_income),
    ('4020', 'Donations', 'revenue', 'credit', root_income),

    # Expenses (Debit balance)
    ('6010', 'Salaries Expense', 'expense', 'debit', root_expenses),
    ('6020', 'Rent Expense', 'expense', 'debit', root_expenses),
    ('6030', 'Utilities Expense', 'expense', 'debit', root_expenses),
    ('6040', 'Office Supplies Expense', 'expense', 'debit', root_expenses),
    ('6050', 'Insurance Expense', 'expense', 'debit', root_expenses),
]

created_count = 0
for code, name, role, balance_type, parent in accounts_to_add:
    # Check if account already exists
    existing = AccountModel.objects.filter(coa_model=coa, code=code).first()
    if existing:
        print(f"⏳ Already exists: {code} - {name}")
        continue

    # Create the account as root first, then move under parent
    acc = AccountModel.add_root(coa_model=coa, code=code, name=name, role=role, balance_type=balance_type)
    acc.move(parent, pos='last-child')
    print(f"✅ Created: {code} - {name}")
    created_count += 1

print(f"\n📊 Summary: {created_count} new accounts created.")