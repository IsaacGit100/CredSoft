# djan_led/utils.py



def user_can_access_entity(user, entity):
    try:
        profile = user.djan_led_profile
        if profile.role in ["technical", "super_admin"]:
            return True  #  Technical and Super Admin have full access
        if entity in profile.allowed_entities.all() or entity == profile.default_entity:
            return True
    except:
        pass
    return False


from django_ledger.models import AccountModel


def get_visible_accounts(user, entity):
    """
    Returns a queryset of AccountModel for the given entity,
    filtered by the user's account preferences (if any).
    """
    coa = entity.get_default_coa()
    if not coa:
        return AccountModel.objects.none()

    base_qs = AccountModel.objects.filter(
        coa_model=coa, active=True, depth__gt=1
    ).order_by("code")

    try:
        profile = user.djan_led_profile
        prefs = profile.account_preferences.get(entity.slug, [])
        if prefs:
            # Filter by the saved codes
            return base_qs.filter(code__in=prefs)
    except:
        pass

    # If no preferences, return all active accounts
    return base_qs


from django_ledger.models import (
    LedgerModel,
    JournalEntryModel,
    TransactionModel,
    AccountModel,
)
from decimal import Decimal


def post_manual_journal_entry(entry):
    try:
        entity = entry.entity
        ledger = LedgerModel.objects.filter(entity=entity).first()
        if not ledger:
            ledger = LedgerModel.objects.create(entity=entity, name="Default Ledger")

        coa = entity.get_default_coa()
        if not coa:
            return None

        debit_account = AccountModel.objects.get(
            coa_model=coa, code=entry.debit_account_code, active=True
        )
        credit_account = AccountModel.objects.get(
            coa_model=coa, code=entry.credit_account_code, active=True
        )

        je = JournalEntryModel.objects.create(
            ledger=ledger,
            timestamp=entry.date,
            description=entry.description,
            posted=False,
        )

        TransactionModel.objects.create(
            journal_entry=je,
            account=debit_account,
            amount=entry.amount,
            tx_type="debit",
        )
        TransactionModel.objects.create(
            journal_entry=je,
            account=credit_account,
            amount=entry.amount,
            tx_type="credit",
        )

        je.posted = True
        je.save()
        return je.uuid
    except Exception as e:
        print(f"Error posting: {e}")
        return None
from decimal import Decimal
from django_ledger.models import AccountModel


def get_accounts_for_type(account_type, root_nodes):
    """
    Returns a list of accounts for a given entity type.
    root_nodes = (root_assets, root_liabilities, root_capital, root_income, root_expenses)
    """
    root_assets, root_liabilities, root_capital, root_income, root_expenses = root_nodes

    if account_type == 'church':
        return [
            ("1010", "Cash", "asset", "debit", root_assets),
            ("1020", "Bank", "asset", "debit", root_assets),
            ("1030", "Accounts Receivable", "asset", "debit", root_assets),
            ("1040", "Inventory", "asset", "debit", root_assets),
            ("1050", "Prepaid Expenses", "asset", "debit", root_assets),
            ("1060", "Office Equipment", "asset", "debit", root_assets),
            ("1070", "Buildings", "asset", "debit", root_assets),
            ("2010", "Accounts Payable", "liability", "credit", root_liabilities),
            ("2020", "Accrued Expenses", "liability", "credit", root_liabilities),
            ("2030", "Bank Loans", "liability", "credit", root_liabilities),
            ("3010", "Owner's Equity", "equity", "credit", root_capital),
            ("3020", "Retained Earnings", "equity", "credit", root_capital),
            
            
            ("4010", "General Offertory",	"revenue",	"credit", root_income),
            ("4011", "DayBorn Offerings", 	"revenue",	"credit", root_income),
            ("4012", "Guild Offerings", 	"revenue", 	"credit", root_income),
            ("4013", "Dues", "revenue",	"credit", root_income),
            ("4014", "Tithes", 	"revenue",	"credit", root_income),
            ("4015", "Special Thank Offering", "revenue", "credit", root_income),
            ("4016", "Easter Offering",	"revenue", "credit", root_income),
            ("4017", "Christmas Offering", "revenue", "credit", root_income),
            ("4018", "Harvest Offering", "revenue", "credit", root_income),
            ("4019", "Other Collections", "revenue", "credit", root_income),
            ("4020", "Donations", "revenue", "credit", root_income),
            #
            
            ("5010", "Cost of Goods Sold", "expense", "debit", root_expenses),
            ("6010", "Salaries Expense", "expense", "debit", root_expenses),
            ("6020", "Rent Expense", "expense", "debit", root_expenses),
            ("6030", "Utilities Expense", "expense", "debit", root_expenses),
            ("6040", "Office Supplies Expense", "expense", "debit", root_expenses),
            ("6050", "Insurance Expense", "expense", "debit", root_expenses),
            ("1090", "Fixed Assets - Cost", "asset", "debit", root_assets),
            ("1099", "Accumulated Depreciation", "asset", "credit", root_assets),
            ("6060", "Depreciation Expense", "expense", "debit", root_expenses),
            ("1110", "Property, Plant & Equipment", "asset", "debit", root_assets),
            ("1111", "Land", "asset", "debit", root_assets),
            ("1112", "Buildings", "asset", "debit", root_assets),
            ("1113", "Vehicles", "asset", "debit", root_assets),
            ("1114", "Furniture & Equipment", "asset", "debit", root_assets),
            # ... existing expense accounts ...
            ("6111", "Depreciation Expense - Land", "expense", "debit", root_expenses),
            ("6112", "Depreciation Expense - Buildings", "expense", "debit", root_expenses),
            ("6113", "Depreciation Expense - Vehicles",  "expense", "debit", root_expenses),
            ("6114", "Depreciation Expense - Furniture & Equipment", "expense", "debit", root_expenses),
            # Accumulated Depreciation (contra‑assets)
            ("1115", "Accumulated Depreciation - Land", "asset", "credit", root_assets),
            ("1116", "Accumulated Depreciation - Buildings", "asset", "credit", root_assets),
            ("1117", "Accumulated Depreciation - Vehicles", "asset", "credit", root_assets),
            ("1118", "Accumulated Depreciation - Furniture & Equipment", "asset", "credit", root_assets),
        ]

    elif account_type == 'school':
        return [
            ("1010", "Cash", "asset", "debit", root_assets),
            ("1020", "Bank", "asset", "debit", root_assets),
            ("1030", "Accounts Receivable", "asset", "debit", root_assets),
            ("1040", "Inventory", "asset", "debit", root_assets),
            ("1050", "Prepaid Expenses", "asset", "debit", root_assets),
            ("1060", "Office Equipment", "asset", "debit", root_assets),
            ("1070", "Buildings", "asset", "debit", root_assets),
            ("2010", "Accounts Payable", "liability", "credit", root_liabilities),
            ("2020", "Accrued Expenses", "liability", "credit", root_liabilities),
            ("2030", "Bank Loans", "liability", "credit", root_liabilities),
            ("3010", "Owner's Equity", "equity", "credit", root_capital),
            ("3020", "Retained Earnings", "equity", "credit", root_capital),
            ("4010", "Tuition Revenue", "revenue", "credit", root_income),
            ("4020", "Donations", "revenue", "credit", root_income),
            ("5010", "Cost of Goods Sold", "expense", "debit", root_expenses),
            ("6010", "Salaries Expense", "expense", "debit", root_expenses),
            ("6020", "Rent Expense", "expense", "debit", root_expenses),
            ("6030", "Utilities Expense", "expense", "debit", root_expenses),
            ("6040", "Office Supplies Expense", "expense", "debit", root_expenses),
            ("6050", "Insurance Expense", "expense", "debit", root_expenses),
            ("6060", "Teaching Materials Expense", "expense", "debit", root_expenses),
            ("1090", "Fixed Assets - Cost", "asset", "debit", root_assets),
            ("1099", "Accumulated Depreciation", "asset", "credit", root_assets),
            ("6060", "Depreciation Expense", "expense", "debit", root_expenses),
            ("1110", "Property, Plant & Equipment", "asset", "debit", root_assets),
            ("1111", "Land", "asset", "debit", root_assets),
            ("1112", "Buildings", "asset", "debit", root_assets),
            ("1113", "Vehicles", "asset", "debit", root_assets),
            ("1114", "Furniture & Equipment", "asset", "debit", root_assets),
            # ... existing expense accounts ...
            ("6111", "Depreciation Expense - Land", "expense", "debit", root_expenses),
            ("6112", "Depreciation Expense - Buildings", "expense", "debit", root_expenses),
            ("6113", "Depreciation Expense - Vehicles", "expense", "debit", root_expenses),
            ("6114", "Depreciation Expense - Furniture & Equipment", "expense", "debit", root_expenses),
            # Accumulated Depreciation (contra‑assets)
            ("1115", "Accumulated Depreciation - Land", "asset", "credit", root_assets),
            ("1116", "Accumulated Depreciation - Buildings", "asset", "credit", root_assets),
            ("1117", "Accumulated Depreciation - Vehicles", "asset", "credit", root_assets),
            ("1118", "Accumulated Depreciation - Furniture & Equipment", "asset", "credit", root_assets),
        ]

    elif account_type == 'credit_union':
        return [
            ("1010", "Cash", "asset", "debit", root_assets),
            ("1020", "Bank", "asset", "debit", root_assets),
            ("1030", "Accounts Receivable", "asset", "debit", root_assets),
            ("1040", "Inventory", "asset", "debit", root_assets),
            ("1050", "Prepaid Expenses", "asset", "debit", root_assets),
            ("1060", "Office Equipment", "asset", "debit", root_assets),
            ("1070", "Buildings", "asset", "debit", root_assets),
            ("1080", "Loan Portfolio", "asset", "debit", root_assets),
            ("1080", "Loan Portfolio", "asset", "debit", root_assets),
            #
            ("2010", "Accounts Payable", "liability", "credit", root_liabilities),
            ("2020", "Member Deposits", "liability", "credit", root_liabilities),
            ("2030", "Bank Loans", "liability", "credit", root_liabilities),
            #
            ("3010", "Owner's Equity", "equity", "credit", root_capital),
            ("3011", "Share Capital", "equity", "credit", root_capital),
            ("3020", "Retained Earnings", "equity", "credit", root_capital),
            #
            ("4010", "Interest Income", "revenue", "credit", root_income),
            ("4020", "Donations", "revenue", "credit", root_income),
            ("5010", "Interest Expense", "expense", "debit", root_expenses),
            #
            ("6010", "Salaries Expense", "expense", "debit", root_expenses),
            ("6020", "Rent Expense", "expense", "debit", root_expenses),
            ("6030", "Utilities Expense", "expense", "debit", root_expenses),
            ("6040", "Office Supplies Expense", "expense", "debit", root_expenses),
            ("6050", "Insurance Expense", "expense", "debit", root_expenses),
            ("1090", "Fixed Assets - Cost", "asset", "debit", root_assets),
            ("1099", "Accumulated Depreciation", "asset", "credit", root_assets),
            ("6060", "Depreciation Expense", "expense", "debit", root_expenses),
            
            ("1110", "Property, Plant & Equipment", "asset", "debit", root_assets),
            ("1111", "Land", "asset", "debit", root_assets),
            ("1112", "Buildings", "asset", "debit", root_assets),
            ("1113", "Vehicles", "asset", "debit", root_assets),
            ("1114", "Furniture & Equipment", "asset", "debit", root_assets),
            # ... existing expense accounts ...
            ("6111", "Depreciation Expense - Land", "expense", "debit", root_expenses),
            ("6112", "Depreciation Expense - Buildings", "expense", "debit", root_expenses),
            ("6113", "Depreciation Expense - Vehicles",  "expense", "debit", root_expenses),
            ("6114", "Depreciation Expense - Furniture & Equipment", "expense", "debit", root_expenses),
            # Accumulated Depreciation (contra‑assets)
            ("1115", "Accumulated Depreciation - Land", "asset", "credit", root_assets),
            ("1116", "Accumulated Depreciation - Buildings", "asset", "credit", root_assets),
            ("1117", "Accumulated Depreciation - Vehicles", "asset", "credit", root_assets),
            ("1118", "Accumulated Depreciation - Furniture & Equipment", "asset", "credit", root_assets),
        ]

    elif account_type == 'pos':
        return [
            ("1010", "Cash", "asset", "debit", root_assets),
            ("1020", "Bank", "asset", "debit", root_assets),
            ("1040", "Inventory", "asset", "debit", root_assets),
            ("1060", "Office Equipment", "asset", "debit", root_assets),
            ("2010", "Accounts Payable", "liability", "credit", root_liabilities),
            ("3010", "Owner's Equity", "equity", "credit", root_capital),
            ("4010", "Sales Revenue", "revenue", "credit", root_income),
            ("5010", "Cost of Goods Sold", "expense", "debit", root_expenses),
            ("6010", "Salaries Expense", "expense", "debit", root_expenses),
            ("6020", "Rent Expense", "expense", "debit", root_expenses),
            ("6030", "Utilities Expense", "expense", "debit", root_expenses),
            ("1090", "Fixed Assets - Cost", "asset", "debit", root_assets),
            ("1099", "Accumulated Depreciation", "asset", "credit", root_assets),
            ("6060", "Depreciation Expense", "expense", "debit", root_expenses),
            ("1110", "Property, Plant & Equipment", "asset", "debit", root_assets),
            ("1111", "Land", "asset", "debit", root_assets),
            ("1112", "Buildings", "asset", "debit", root_assets),
            ("1113", "Vehicles", "asset", "debit", root_assets),
            ("1114", "Furniture & Equipment", "asset", "debit", root_assets),
            # ... existing expense accounts ...
            ("6111", "Depreciation Expense - Land", "expense", "debit", root_expenses),
            ("6112", "Depreciation Expense - Buildings", "expense", "debit", root_expenses),
            ("6113", "Depreciation Expense - Vehicles", "expense", "debit", root_expenses),
            ("6114", "Depreciation Expense - Furniture & Equipment", "expense", "debit", root_expenses),
            # Accumulated Depreciation (contra‑assets)
            ("1115", "Accumulated Depreciation - Land", "asset", "credit", root_assets),
            ("1116", "Accumulated Depreciation - Buildings", "asset", "credit", root_assets),
            ("1117", "Accumulated Depreciation - Vehicles", "asset", "credit", root_assets),
            ("1118", "Accumulated Depreciation - Furniture & Equipment", "asset", "credit", root_assets),
        ]

    elif account_type == 'general':
        # A minimal set for any entity (asset, liability, equity, revenue, expense)
        return [
            ("1010", "Cash", "asset", "debit", root_assets),
            ("1020", "Bank", "asset", "debit", root_assets),
            ("1040", "Inventory", "asset", "debit", root_assets),
            ("1060", "Office Equipment", "asset", "debit", root_assets),
            ("2010", "Accounts Payable", "liability", "credit", root_liabilities),
            ("3010", "Owner's Equity", "equity", "credit", root_capital),
            ("4010", "Revenue", "revenue", "credit", root_income),
            ("5010", "Cost of Goods Sold", "expense", "debit", root_expenses),
            ("6010", "Salaries Expense", "expense", "debit", root_expenses),
            ("6020", "Rent Expense", "expense", "debit", root_expenses),
            ("6030", "Utilities Expense", "expense", "debit", root_expenses),
            ("1090", "Fixed Assets - Cost", "asset", "debit", root_assets),
            ("1099", "Accumulated Depreciation", "asset", "credit", root_assets),
            ("6060", "Depreciation Expense", "expense", "debit", root_expenses),
            ("1110", "Property, Plant & Equipment", "asset", "debit", root_assets),
            ("1111", "Land", "asset", "debit", root_assets),
            ("1112", "Buildings", "asset", "debit", root_assets),
            ("1113", "Vehicles", "asset", "debit", root_assets),
            ("1114", "Furniture & Equipment", "asset", "debit", root_assets),
            # ... existing expense accounts ...
            ("6111", "Depreciation Expense - Land", "expense", "debit", root_expenses),
            ("6112", "Depreciation Expense - Buildings", "expense", "debit", root_expenses),
            ("6113", "Depreciation Expense - Vehicles", "expense", "debit", root_expenses),
            ("6114", "Depreciation Expense - Furniture & Equipment", "expense", "debit", root_expenses),
            # Accumulated Depreciation (contra‑assets)
            ("1115", "Accumulated Depreciation - Land", "asset", "credit", root_assets),
            ("1116", "Accumulated Depreciation - Buildings", "asset", "credit", root_assets),
            ("1117", "Accumulated Depreciation - Vehicles", "asset", "credit", root_assets),
            ("1118", "Accumulated Depreciation - Furniture & Equipment", "asset", "credit", root_assets),
        ]

    else:
        return []


def add_accounts_to_coa(coa, accounts_list):
    created_count = 0
    for code, name, role, balance_type, parent in accounts_list:
        if AccountModel.objects.filter(coa_model=coa, code=code).exists():
            continue
        acc = AccountModel.add_root(
            coa_model=coa,
            code=code,
            name=name,
            role=role,
            balance_type=balance_type,
        )
        acc.move(parent, pos="last-child")
        created_count += 1
    return created_count  
