# management/commands/init_coa.py
from django.core.management.base import BaseCommand
from coa.models import ChartOfAccounts

class Command(BaseCommand):
    help = 'Initialize Chart of Accounts'
    
    def handle(self, *args, **options):
        # Clear existing
        ChartOfAccounts.objects.all().delete()
        self.stdout.write("Cleared existing accounts.\n")
        
        # ============================================================
        # LEVEL 1: Major Categories
        # ============================================================
        assets = ChartOfAccounts.objects.create(
            name='ASSETS',
            account_type='ASSET',
            behavior='NORMAL',
            is_data_entry=False,
        )
        self.stdout.write(f"Level 1: {assets.accountno} - {assets.name}")
        
        liabilities = ChartOfAccounts.objects.create(
            name='LIABILITIES',
            account_type='LIABILITY',
            behavior='NORMAL',
            is_data_entry=False,
        )
        self.stdout.write(f"Level 1: {liabilities.accountno} - {liabilities.name}")
        
        equity = ChartOfAccounts.objects.create(
            name="EQUITY",
            account_type='EQUITY',
            behavior='NORMAL',
            is_data_entry=False,
        )
        self.stdout.write(f"Level 1: {equity.accountno} - {equity.name}")
        
        income = ChartOfAccounts.objects.create(
            name='INCOME',
            account_type='INCOME',
            behavior='NORMAL',
            is_data_entry=False,
        )
        self.stdout.write(f"Level 1: {income.accountno} - {income.name}")
        
        expenses = ChartOfAccounts.objects.create(
            name='EXPENSES',
            account_type='EXPENSE',
            behavior='NORMAL',
            is_data_entry=False,
        )
        self.stdout.write(f"Level 1: {expenses.accountno} - {expenses.name}\n")
        
        # ============================================================
        # LEVEL 2: Sub Categories under ASSETS
        # ============================================================
        assets = ChartOfAccounts.objects.get(accountno='10000000')
        
        current_assets = ChartOfAccounts.objects.create(
            name='CURRENT ASSETS',
            account_type='ASSET',
            behavior='NORMAL',
            parent_account=assets,
            is_data_entry=False,
        )
        self.stdout.write(f"Level 2: {current_assets.accountno} - {current_assets.name}")
        
        # ============================================================
        # LEVEL 3: Groups under CURRENT ASSETS
        # ============================================================
        current_assets = ChartOfAccounts.objects.get(accountno='10100000')
        
        cash = ChartOfAccounts.objects.create(
            name='CASH AND CASH EQUIVALENTS',
            account_type='ASSET',
            behavior='NORMAL',
            parent_account=current_assets,
            is_data_entry=False,
        )
        self.stdout.write(f"Level 3: {cash.accountno} - {cash.name}")
        
        bank = ChartOfAccounts.objects.create(
            name='BANK ACCOUNTS',
            account_type='ASSET',
            behavior='NORMAL',
            parent_account=current_assets,
            is_data_entry=False,
        )
        self.stdout.write(f"Level 3: {bank.accountno} - {bank.name}\n")
        
        # ============================================================
        # LEVEL 4: Specific Accounts
        # ============================================================
        cash = ChartOfAccounts.objects.get(accountno='10101000')
        
        cash1 = ChartOfAccounts.objects.create(
            name='Cash in Hand - Main Office',
            account_type='ASSET',
            behavior='CASH',
            parent_account=cash,
            is_data_entry=True,
        )
        self.stdout.write(f"Level 4: {cash1.accountno} - {cash1.name}")
        
        cash2 = ChartOfAccounts.objects.create(
            name='Cash in Hand - Kumasi Branch',
            account_type='ASSET',
            behavior='CASH',
            parent_account=cash,
            is_data_entry=True,
        )
        self.stdout.write(f"Level 4: {cash2.accountno} - {cash2.name}")
        
        # Bank accounts
        bank = ChartOfAccounts.objects.get(accountno='10102000')
        
        gcb = ChartOfAccounts.objects.create(
            name='GCB Bank PLC',
            account_type='ASSET',
            behavior='BANK',
            parent_account=bank,
            is_data_entry=True,
        )
        self.stdout.write(f"Level 4: {gcb.accountno} - {gcb.name}")
        
        absa = ChartOfAccounts.objects.create(
            name='Absa Bank PLC',
            account_type='ASSET',
            behavior='BANK',
            parent_account=bank,
            is_data_entry=True,
        )
        self.stdout.write(f"Level 4: {absa.accountno} - {absa.name}\n")
        
        # ============================================================
        # LEVEL 2: Sub Categories under LIABILITIES
        # ============================================================
        liabilities = ChartOfAccounts.objects.get(accountno='20000000')
        
        member_funds = ChartOfAccounts.objects.create(
            name='MEMBER FUNDS',
            account_type='LIABILITY',
            behavior='NORMAL',
            parent_account=liabilities,
            is_data_entry=False,
        )
        self.stdout.write(f"Level 2: {member_funds.accountno} - {member_funds.name}")
        
        # Level 3
        member_funds = ChartOfAccounts.objects.get(accountno='20100000')
        
        savings = ChartOfAccounts.objects.create(
            name='SAVINGS ACCOUNTS',
            account_type='LIABILITY',
            behavior='SAVINGS',
            parent_account=member_funds,
            is_data_entry=False,
        )
        self.stdout.write(f"Level 3: {savings.accountno} - {savings.name}")
        
        # Level 4
        savings = ChartOfAccounts.objects.get(accountno='20101000')
        
        regular = ChartOfAccounts.objects.create(
            name='Regular Savings Account',
            account_type='LIABILITY',
            behavior='SAVINGS',
            parent_account=savings,
            is_data_entry=True,
        )
        self.stdout.write(f"Level 4: {regular.accountno} - {regular.name}")
        
        target = ChartOfAccounts.objects.create(
            name='Target Savings Account',
            account_type='LIABILITY',
            behavior='SAVINGS',
            parent_account=savings,
            is_data_entry=True,
        )
        self.stdout.write(f"Level 4: {target.accountno} - {target.name}")
        
        self.stdout.write(self.style.SUCCESS("\n✅ Chart of Accounts initialized successfully!"))