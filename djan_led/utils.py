# djan_led/utils.py
# djan_led/utils.py  (or core/utils.py)

from django.urls import reverse
from django_ledger.models import EntityModel

# Map entity_type → URL name of that module's dashboard
ENTITY_TYPE_DASHBOARD = {
    "church": "ChurchApp:church_dashboard",
    "school": "SchoolApp:school_dashboard",
    "credit_union": "CreditUnion:credit_union_dashboard",
    "pos": "POS:dashboard",
    "hospital": "HospitalApp:dashboard",
    "hotel": "HotelApp:dashboard",
    "business": "BusinessApp:dashboard",
    "ngo": "NGOApp:dashboard",
    "other": "Tech:entity_management",
}


def get_module_home_url(entity):
    """
    Return the dashboard URL for the given entity based on its entity_type.
    Falls back to the entity management page if the type is unknown.
    """
    if not entity:
        return reverse("Tech:entity_management")

    # Try to read entity_type from EntityConfig
    entity_type = None
    try:
        entity_type = entity.config.entity_type
    except Exception:
        pass

    if entity_type and entity_type in ENTITY_TYPE_DASHBOARD:
        try:
            return reverse(
                ENTITY_TYPE_DASHBOARD[entity_type], kwargs={"slug": entity.slug}
            )
        except Exception:
            pass

    # Fallback
    return reverse("Tech:entity_management")


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

    base_qs = (
        AccountModel.objects.filter(coa_model=coa)
        .exclude(role__startswith="root_")
        .order_by("code")
    )

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
            ("3099", "Opening Balance Equity", "equity", "credit", root_capital),
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
            # Accumulated Depreciation (contra-assets)
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
            ("3099", "Opening Balance Equity", "equity", "credit", root_capital),
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
            ("6114", "Depreciation Expense - Furniture & Equipment",
                "expense",
                "debit",
                root_expenses,
            ),
            # Accumulated Depreciation (contra-assets)
            ("1115", "Accumulated Depreciation - Land", "asset", "credit", root_assets),
            (
                "1116",
                "Accumulated Depreciation - Buildings",
                "asset",
                "credit",
                root_assets,
            ),
            (
                "1117",
                "Accumulated Depreciation - Vehicles",
                "asset",
                "credit",
                root_assets,
            ),
            (
                "1118",
                "Accumulated Depreciation - Furniture & Equipment",
                "asset",
                "credit",
                root_assets,
            ),
        ]

    elif account_type == "credit_union":
        return [
            # ===== ASSETS (1xxx) =====
            ("1010", "Cash",                                "asset",     "debit",  root_assets),
            ("1020", "Bank",                                "asset",     "debit",  root_assets),
            ("1030", "Accounts Receivable",                 "asset",     "debit",  root_assets),
            ("1040", "Inventory",                           "asset",     "debit",  root_assets),
            ("1050", "Prepaid Expenses",                    "asset",     "debit",  root_assets),
            ("1060", "Office Equipment",                    "asset",     "debit",  root_assets),
            ("1070", "Buildings",                           "asset",     "debit",  root_assets),

            # Loan book
            ("1080", "Loan Portfolio",                      "asset",     "debit",  root_assets),
            ("1081", "Allowance for Loan Losses",           "asset",     "credit", root_assets),  # NEW
            ("1082", "Interest Receivable on Loans",        "asset",     "debit",  root_assets),  # NEW

            # Investments
            ("1100", "Investments",                         "asset",     "debit",  root_assets),  # NEW
            ("1101", "Investment Income Receivable",        "asset",     "debit",  root_assets),  # NEW

            # Fixed assets
            ("1090", "Fixed Assets - Cost",                 "asset",     "debit",  root_assets),
            ("1099", "Accumulated Depreciation",            "asset",     "credit", root_assets),
            ("1110", "Property, Plant & Equipment",         "asset",     "debit",  root_assets),
            ("1111", "Land",                                "asset",     "debit",  root_assets),
            ("1112", "Buildings",                           "asset",     "debit",  root_assets),
            ("1113", "Vehicles",                            "asset",     "debit",  root_assets),
            ("1114", "Furniture & Equipment",               "asset",     "debit",  root_assets),
            ("1115", "Accumulated Depreciation - Land",     "asset",     "credit", root_assets),
            ("1116", "Accumulated Depreciation - Buildings", "asset",    "credit", root_assets),
            ("1117", "Accumulated Depreciation - Vehicles", "asset",     "credit", root_assets),
            ("1118", "Accumulated Depreciation - Furniture & Equipment", "asset", "credit", root_assets),

            # ===== LIABILITIES (2xxx) =====
            ("2010", "Accounts Payable",                    "liability", "credit", root_liabilities),
            ("2020", "Member Shares",                       "liability", "credit", root_liabilities),   # renamed
            ("2021", "Member Savings",                      "liability", "credit", root_liabilities),   # NEW
            ("2022", "Interest Payable on Savings",         "liability", "credit", root_liabilities),   # NEW
            ("2023", "Dividend Payable",                    "liability", "credit", root_liabilities),   # NEW
            ("2024", "Susu Savings",                        "liability", "credit", root_liabilities),   # NEW (optional)
            ("2030", "Bank Loans",                          "liability", "credit", root_liabilities),

            # ===== EQUITY (3xxx) =====
            ("3010", "Owner's Equity",                      "equity",    "credit", root_capital),
            ("3011", "Share Capital",                       "equity",    "credit", root_capital),
            ("3012", "Statutory Reserve",                   "equity",    "credit", root_capital),   # NEW
            ("3013", "Dividend Paid",                       "equity",    "debit",  root_capital),   # NEW (contra-equity)
            ("3099", "Opening Balance Equity",              "equity",    "credit", root_capital),   # NEW
            ("3020", "Retained Earnings",                   "equity",    "credit", root_capital),

            # ===== REVENUE (4xxx) =====
            ("4010", "Interest Income on Loans",            "revenue",   "credit", root_income),
            ("4011", "Penalty / Late Fee Income",           "revenue",   "credit", root_income),   # NEW
            ("4012", "Loan Processing Fee Income",          "revenue",   "credit", root_income),   # NEW
            ("4013", "Membership Fee Income",               "revenue",   "credit", root_income),   # NEW
            ("4014", "Investment Income",                   "revenue",   "credit", root_income),   # NEW
            ("4015", "Other Operating Income",              "revenue",   "credit", root_income),   # NEW
            ("4020", "Donations",                           "revenue",   "credit", root_income),

            # ===== EXPENSES (6xxx) =====
            ("6010", "Salaries Expense",                    "expense",   "debit",  root_expenses),
            ("6020", "Rent Expense",                        "expense",   "debit",  root_expenses),
            ("6030", "Utilities Expense",                   "expense",   "debit",  root_expenses),
            ("6040", "Office Supplies Expense",             "expense",   "debit",  root_expenses),
            ("6050", "Insurance Expense",                   "expense",   "debit",  root_expenses),
            ("6060", "Depreciation Expense",                "expense",   "debit",  root_expenses),

            # Loan loss
            ("6100", "Loan Loss Provision",                 "expense",   "debit",  root_expenses),   # NEW (was 5010)

            # Savings cost
            ("6110", "Interest Expense on Savings",         "expense",   "debit",  root_expenses),   # NEW

            # Depreciation breakdown
            ("6111", "Depreciation Expense - Land",         "expense",   "debit",  root_expenses),
            ("6112", "Depreciation Expense - Buildings",    "expense",   "debit",  root_expenses),
            ("6113", "Depreciation Expense - Vehicles",     "expense",   "debit",  root_expenses),
            ("6114", "Depreciation Expense - Furniture & Equipment", "expense", "debit", root_expenses),
        ]

    elif account_type == 'pos':
        return [
            ("1010", "Cash", "asset", "debit", root_assets),
            ("1020", "Bank", "asset", "debit", root_assets),
            ("1040", "Inventory", "asset", "debit", root_assets),
            ("1060", "Office Equipment", "asset", "debit", root_assets),
            ("2010", "Accounts Payable", "liability", "credit", root_liabilities),
            ("3010", "Owner's Equity", "equity", "credit", root_capital),
            ("3099", "Opening Balance Equity", "equity", "credit", root_capital),
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
            # Accumulated Depreciation (contra-assets)
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
            ("3099", "Opening Balance Equity", "equity", "credit", root_capital),
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
            # Accumulated Depreciation (contra-assets)
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
