# coa/management/commands/init_full_coa.py
from django.core.management.base import BaseCommand
from coa.models import ChartOfAccounts
from django.db import connection

class Command(BaseCommand):
    help = 'Initialize complete Chart of Accounts with all accounts'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force reset without confirmation',
        )
    
    def handle(self, *args, **options):
        if not options['force']:
            confirm = input("⚠️  This will DELETE ALL existing accounts and create new ones.\n"
                          "Type 'YES' to continue: ")
            if confirm != 'YES':
                self.stdout.write(self.style.WARNING("Operation cancelled."))
                return
        
        self.create_chart_of_accounts()
    
    def create_chart_of_accounts(self):
        # Clear existing accounts
        self.stdout.write("Clearing existing accounts...")
        with connection.cursor() as cursor:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
            ChartOfAccounts.objects.all().delete()
            cursor.execute("ALTER TABLE coa_chartofaccounts AUTO_INCREMENT = 1;")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        
        self.stdout.write(self.style.SUCCESS("✅ Database cleared\n"))
        
        self.stdout.write("="*70)
        self.stdout.write("CREATING COMPLETE CHART OF ACCOUNTS")
        self.stdout.write("Format: X-XX-XX-XXX (e.g., 1-01-01-001)")
        self.stdout.write("="*70)
        
        # ============================================================
        # LEVEL 1: MAJOR CATEGORIES
        # ============================================================
        self.stdout.write("\n📁 LEVEL 1: Major Categories")
        self.stdout.write("-"*50)
        
        assets = ChartOfAccounts.objects.create(
            accountno='10000000', name='ASSETS', account_type='ASSET',
            behavior='NORMAL', is_data_entry=False,
        )
        self.stdout.write(f"  {assets.accountno} - {assets.name}")
        
        liabilities = ChartOfAccounts.objects.create(
            accountno='20000000', name='LIABILITIES', account_type='LIABILITY',
            behavior='NORMAL', is_data_entry=False,
        )
        self.stdout.write(f"  {liabilities.accountno} - {liabilities.name}")
        
        equity = ChartOfAccounts.objects.create(
            accountno='30000000', name='EQUITY', account_type='EQUITY',
            behavior='NORMAL', is_data_entry=False,
        )
        self.stdout.write(f"  {equity.accountno} - {equity.name}")
        
        income = ChartOfAccounts.objects.create(
            accountno='40000000', name='INCOME', account_type='INCOME',
            behavior='NORMAL', is_data_entry=False,
        )
        self.stdout.write(f"  {income.accountno} - {income.name}")
        
        expenses = ChartOfAccounts.objects.create(
            accountno='50000000', name='EXPENSES', account_type='EXPENSE',
            behavior='NORMAL', is_data_entry=False,
        )
        self.stdout.write(f"  {expenses.accountno} - {expenses.name}")
        
        contra = ChartOfAccounts.objects.create(
            accountno='60000000', name='CONTRA ACCOUNTS', account_type='ASSET_CONTRA',
            behavior='NORMAL', is_data_entry=False,
        )
        self.stdout.write(f"  {contra.accountno} - {contra.name}")
        
        # ============================================================
        # LEVEL 2: UNDER ASSETS
        # ============================================================
        self.stdout.write("\n📁 LEVEL 2: Under ASSETS")
        self.stdout.write("-"*50)
        
        assets_parent = ChartOfAccounts.objects.get(accountno='10000000')
        
        current_assets = ChartOfAccounts.objects.create(
            accountno='10100000', name='CURRENT ASSETS', account_type='ASSET',
            behavior='NORMAL', parent_account=assets_parent, is_data_entry=False,
        )
        self.stdout.write(f"  {current_assets.accountno} - {current_assets.name}")
        
        fixed_assets = ChartOfAccounts.objects.create(
            accountno='10200000', name='FIXED ASSETS', account_type='ASSET',
            behavior='NORMAL', parent_account=assets_parent, is_data_entry=False,
        )
        self.stdout.write(f"  {fixed_assets.accountno} - {fixed_assets.name}")
        
        other_receivables = ChartOfAccounts.objects.create(
            accountno='10300000', name='OTHER RECEIVABLES', account_type='ASSET',
            behavior='NORMAL', parent_account=assets_parent, is_data_entry=False,
        )
        self.stdout.write(f"  {other_receivables.accountno} - {other_receivables.name}")
        
        # ============================================================
        # LEVEL 3: Under CURRENT ASSETS
        # ============================================================
        self.stdout.write("\n📁 LEVEL 3: Under CURRENT ASSETS")
        self.stdout.write("-"*50)
        
        current_parent = ChartOfAccounts.objects.get(accountno='10100000')
        
        cash_bank = ChartOfAccounts.objects.create(
            accountno='10101000', name='CASH AND BANK', account_type='ASSET',
            behavior='NORMAL', parent_account=current_parent, is_data_entry=False,
        )
        self.stdout.write(f"  {cash_bank.accountno} - {cash_bank.name}")
        
        loans_receivable = ChartOfAccounts.objects.create(
            accountno='10102000', name='LOANS RECEIVABLE', account_type='ASSET',
            behavior='LOAN', parent_account=current_parent, is_data_entry=False,
        )
        self.stdout.write(f"  {loans_receivable.accountno} - {loans_receivable.name}")
        
        investments = ChartOfAccounts.objects.create(
            accountno='10103000', name='INVESTMENTS', account_type='ASSET',
            behavior='NORMAL', parent_account=current_parent, is_data_entry=False,
        )
        self.stdout.write(f"  {investments.accountno} - {investments.name}")
        
        other_assets = ChartOfAccounts.objects.create(
            accountno='10104000', name='OTHER ASSETS', account_type='ASSET',
            behavior='NORMAL', parent_account=current_parent, is_data_entry=False,
        )
        self.stdout.write(f"  {other_assets.accountno} - {other_assets.name}")
        
        # ============================================================
        # LEVEL 4: Cash and Bank Accounts
        # ============================================================
        self.stdout.write("\n📁 LEVEL 4: Cash and Bank Accounts")
        self.stdout.write("-"*50)
        
        cash_parent = ChartOfAccounts.objects.get(accountno='10101000')
        
        cash_accounts = [
            ('10101001', 'Cash In Hand', 'CASH'),
            ('10101002', 'Bank - GCB PLC', 'BANK'),
            ('10101003', 'Bank - NIB PLC', 'BANK'),
            ('10101004', 'Bank - Absa PLC', 'BANK'),
        ]
        
        for acc_no, name, behavior in cash_accounts:
            ChartOfAccounts.objects.create(
                accountno=acc_no, name=name, account_type='ASSET',
                behavior=behavior, parent_account=cash_parent, is_data_entry=True,
            )
        self.stdout.write(f"  Created {len(cash_accounts)} cash/bank accounts")
        
        # ============================================================
        # LEVEL 4: Loans Receivable Accounts
        # ============================================================
        self.stdout.write("\n📁 LEVEL 4: Loans Receivable Accounts")
        self.stdout.write("-"*50)
        
        loans_parent = ChartOfAccounts.objects.get(accountno='10102000')
        
        loan_accounts = [
            ('10102001', 'Principal'),
            ('10102002', 'Loan Balance'),
            ('10102003', 'Loan Interest'),
            ('10102004', 'Loan Repayment'),
            ('10102005', 'Loan Repayment Overdue'),
            ('10102006', 'Loan Interest Overdue'),
            ('10102007', 'Loan Guaranteed'),
        ]
        
        for acc_no, name in loan_accounts:
            ChartOfAccounts.objects.create(
                accountno=acc_no, name=name, account_type='ASSET',
                behavior='LOAN', parent_account=loans_parent, is_data_entry=True,
            )
        self.stdout.write(f"  Created {len(loan_accounts)} loan accounts")
        
        # ============================================================
        # LEVEL 4: Investment Accounts
        # ============================================================
        self.stdout.write("\n📁 LEVEL 4: Investment Accounts")
        self.stdout.write("-"*50)
        
        invest_parent = ChartOfAccounts.objects.get(accountno='10103000')
        
        investment_accounts = [
            ('10103001', 'Fixed Deposit'),
            ('10103002', 'Fixed Deposit Interest'),
            ('10103003', 'Treasury Bills'),
            ('10103004', 'Treasury Bills Interest'),
            ('10103005', 'Call Deposit'),
            ('10103006', 'Call Deposit Interest'),
            ('10103007', 'Bonds'),
            ('10103008', 'Bonds Interest'),
            ('10103009', 'Investment Savings'),
            ('10103010', 'Investment Savings Interest'),
        ]
        
        for acc_no, name in investment_accounts:
            ChartOfAccounts.objects.create(
                accountno=acc_no, name=name, account_type='ASSET',
                behavior='NORMAL', parent_account=invest_parent, is_data_entry=True,
            )
        self.stdout.write(f"  Created {len(investment_accounts)} investment accounts")
        
        # ============================================================
        # LEVEL 4: Other Asset Accounts
        # ============================================================
        self.stdout.write("\n📁 LEVEL 4: Other Asset Accounts")
        self.stdout.write("-"*50)
        
        other_parent = ChartOfAccounts.objects.get(accountno='10104000')
        
        other_asset_accounts = [
            ('10104001', 'Stationery Inventory'),
            ('10104002', 'Office Equipment'),
            ('10104003', 'Office Equipment Repairs'),
        ]
        
        for acc_no, name in other_asset_accounts:
            ChartOfAccounts.objects.create(
                accountno=acc_no, name=name, account_type='ASSET',
                behavior='NORMAL', parent_account=other_parent, is_data_entry=True,
            )
        self.stdout.write(f"  Created {len(other_asset_accounts)} other asset accounts")
        
        # ============================================================
        # LEVEL 2: UNDER LIABILITIES
        # ============================================================
        self.stdout.write("\n📁 LEVEL 2: Under LIABILITIES")
        self.stdout.write("-"*50)
        
        liab_parent = ChartOfAccounts.objects.get(accountno='20000000')
        
        member_liabilities = ChartOfAccounts.objects.create(
            accountno='20100000', name='MEMBER LIABILITIES', account_type='LIABILITY',
            behavior='NORMAL', parent_account=liab_parent, is_data_entry=False,
        )
        self.stdout.write(f"  {member_liabilities.accountno} - {member_liabilities.name}")
        
        other_liabilities = ChartOfAccounts.objects.create(
            accountno='20200000', name='OTHER LIABILITIES', account_type='LIABILITY',
            behavior='NORMAL', parent_account=liab_parent, is_data_entry=False,
        )
        self.stdout.write(f"  {other_liabilities.accountno} - {other_liabilities.name}")
        
        # ============================================================
        # LEVEL 3: Under MEMBER LIABILITIES
        # ============================================================
        self.stdout.write("\n📁 LEVEL 3: Under MEMBER LIABILITIES")
        self.stdout.write("-"*50)
        
        member_parent = ChartOfAccounts.objects.get(accountno='20100000')
        
        savings = ChartOfAccounts.objects.create(
            accountno='20101000', name='SAVINGS', account_type='LIABILITY',
            behavior='SAVINGS', parent_account=member_parent, is_data_entry=False,
        )
        self.stdout.write(f"  {savings.accountno} - {savings.name}")
        
        shares = ChartOfAccounts.objects.create(
            accountno='20102000', name='SHARES', account_type='LIABILITY',
            behavior='SHARES', parent_account=member_parent, is_data_entry=False,
        )
        self.stdout.write(f"  {shares.accountno} - {shares.name}")
        
        other_payables = ChartOfAccounts.objects.create(
            accountno='20103000', name='OTHER PAYABLES', account_type='LIABILITY',
            behavior='NORMAL', parent_account=member_parent, is_data_entry=False,
        )
        self.stdout.write(f"  {other_payables.accountno} - {other_payables.name}")
        
        # ============================================================
        # LEVEL 4: Savings Accounts
        # ============================================================
        self.stdout.write("\n📁 LEVEL 4: Savings Accounts")
        self.stdout.write("-"*50)
        
        savings_parent = ChartOfAccounts.objects.get(accountno='20101000')
        
        savings_accounts = [
            ('20101001', 'Savings Deposits'),
            ('20101002', 'Savings Withdrawal'),
            ('20101003', 'Savings Interest Accrued'),
        ]
        
        for acc_no, name in savings_accounts:
            ChartOfAccounts.objects.create(
                accountno=acc_no, name=name, account_type='LIABILITY',
                behavior='SAVINGS', parent_account=savings_parent, is_data_entry=True,
            )
        self.stdout.write(f"  Created {len(savings_accounts)} savings accounts")
        
        # ============================================================
        # LEVEL 4: Shares Accounts
        # ============================================================
        self.stdout.write("\n📁 LEVEL 4: Shares Accounts")
        self.stdout.write("-"*50)
        
        shares_parent = ChartOfAccounts.objects.get(accountno='20102000')
        
        shares_accounts = [
            ('20102001', 'Share Capital'),
            ('20102002', 'Shares Withdrawal'),
            ('20102003', 'Dividend Payable'),
            ('20102004', 'Dividend Withdrawal'),
        ]
        
        for acc_no, name in shares_accounts:
            ChartOfAccounts.objects.create(
                accountno=acc_no, name=name, account_type='LIABILITY',
                behavior='SHARES', parent_account=shares_parent, is_data_entry=True,
            )
        self.stdout.write(f"  Created {len(shares_accounts)} shares accounts")
        
        # ============================================================
        # LEVEL 4: Other Payables Accounts
        # ============================================================
        self.stdout.write("\n📁 LEVEL 4: Other Payables Accounts")
        self.stdout.write("-"*50)
        
        payables_parent = ChartOfAccounts.objects.get(accountno='20103000')
        
        payables_accounts = [
            ('20103001', 'Loan Processing Fees Payable'),
            ('20103002', 'Accrued Salaries'),
            ('20103003', 'Accrued Utilities'),
            ('20103004', 'Accrued Rent'),
        ]
        
        for acc_no, name in payables_accounts:
            ChartOfAccounts.objects.create(
                accountno=acc_no, name=name, account_type='LIABILITY',
                behavior='NORMAL', parent_account=payables_parent, is_data_entry=True,
            )
        self.stdout.write(f"  Created {len(payables_accounts)} payables accounts")
        
        # ============================================================
        # LEVEL 3: Under OTHER LIABILITIES
        # ============================================================
        self.stdout.write("\n📁 LEVEL 3: Under OTHER LIABILITIES")
        self.stdout.write("-"*50)
        
        other_liab_parent = ChartOfAccounts.objects.get(accountno='20200000')
        
        tax_payables = ChartOfAccounts.objects.create(
            accountno='20201000', name='TAX PAYABLES', account_type='LIABILITY',
            behavior='NORMAL', parent_account=other_liab_parent, is_data_entry=False,
        )
        self.stdout.write(f"  {tax_payables.accountno} - {tax_payables.name}")
        
        provisions = ChartOfAccounts.objects.create(
            accountno='20202000', name='PROVISIONS', account_type='LIABILITY',
            behavior='NORMAL', parent_account=other_liab_parent, is_data_entry=False,
        )
        self.stdout.write(f"  {provisions.accountno} - {provisions.name}")
        
        # ============================================================
        # LEVEL 4: Tax Payables
        # ============================================================
        self.stdout.write("\n📁 LEVEL 4: Tax Payables Accounts")
        self.stdout.write("-"*50)
        
        tax_parent = ChartOfAccounts.objects.get(accountno='20201000')
        
        tax_accounts = [
            ('20201001', 'PAYE Payable'),
            ('20201002', 'VAT Payable'),
            ('20201003', 'Withholding Tax Payable'),
        ]
        
        for acc_no, name in tax_accounts:
            ChartOfAccounts.objects.create(
                accountno=acc_no, name=name, account_type='LIABILITY',
                behavior='NORMAL', parent_account=tax_parent, is_data_entry=True,
            )
        self.stdout.write(f"  Created {len(tax_accounts)} tax accounts")
        
        # ============================================================
        # LEVEL 4: Provisions
        # ============================================================
        self.stdout.write("\n📁 LEVEL 4: Provisions Accounts")
        self.stdout.write("-"*50)
        
        provisions_parent = ChartOfAccounts.objects.get(accountno='20202000')
        
        provision_accounts = [
            ('20202001', 'Loan Loss Provision'),
            ('20202002', 'Staff Leave Provision'),
        ]
        
        for acc_no, name in provision_accounts:
            ChartOfAccounts.objects.create(
                accountno=acc_no, name=name, account_type='LIABILITY',
                behavior='NORMAL', parent_account=provisions_parent, is_data_entry=True,
            )
        self.stdout.write(f"  Created {len(provision_accounts)} provision accounts")
        
        # ============================================================
        # LEVEL 2: UNDER EQUITY
        # ============================================================
        self.stdout.write("\n📁 LEVEL 2: Under EQUITY")
        self.stdout.write("-"*50)
        
        equity_parent = ChartOfAccounts.objects.get(accountno='30000000')
        
        share_capital = ChartOfAccounts.objects.create(
            accountno='30100000', name='SHARE CAPITAL', account_type='EQUITY',
            behavior='NORMAL', parent_account=equity_parent, is_data_entry=False,
        )
        self.stdout.write(f"  {share_capital.accountno} - {share_capital.name}")
        
        reserves = ChartOfAccounts.objects.create(
            accountno='30200000', name='RESERVES', account_type='EQUITY',
            behavior='NORMAL', parent_account=equity_parent, is_data_entry=False,
        )
        self.stdout.write(f"  {reserves.accountno} - {reserves.name}")
        
        # ============================================================
        # LEVEL 3 & 4: Share Capital
        # ============================================================
        self.stdout.write("\n📁 LEVEL 3 & 4: Share Capital Accounts")
        self.stdout.write("-"*50)
        
        share_parent = ChartOfAccounts.objects.get(accountno='30100000')
        
        capital_group = ChartOfAccounts.objects.create(
            accountno='30101000', name='CAPITAL ACCOUNTS', account_type='EQUITY',
            behavior='NORMAL', parent_account=share_parent, is_data_entry=False,
        )
        self.stdout.write(f"  {capital_group.accountno} - {capital_group.name}")
        
        capital_accounts = [
            ('30101001', 'Authorized Share Capital'),
            ('30101002', 'Issued Share Capital'),
            ('30101003', 'Paid-up Capital'),
        ]
        
        for acc_no, name in capital_accounts:
            ChartOfAccounts.objects.create(
                accountno=acc_no, name=name, account_type='EQUITY',
                behavior='NORMAL', parent_account=capital_group, is_data_entry=True,
            )
        self.stdout.write(f"  Created {len(capital_accounts)} capital accounts")
        
        # ============================================================
        # LEVEL 3 & 4: Reserves
        # ============================================================
        self.stdout.write("\n📁 LEVEL 3 & 4: Reserves Accounts")
        self.stdout.write("-"*50)
        
        reserves_parent = ChartOfAccounts.objects.get(accountno='30200000')
        
        statutory = ChartOfAccounts.objects.create(
            accountno='30201000', name='STATUTORY RESERVES', account_type='EQUITY',
            behavior='NORMAL', parent_account=reserves_parent, is_data_entry=False,
        )
        self.stdout.write(f"  {statutory.accountno} - {statutory.name}")
        
        retained = ChartOfAccounts.objects.create(
            accountno='30202000', name='RETAINED EARNINGS', account_type='EQUITY',
            behavior='NORMAL', parent_account=reserves_parent, is_data_entry=False,
        )
        self.stdout.write(f"  {retained.accountno} - {retained.name}")
        
        # Statutory reserve accounts
        statutory_accounts = [
            ('30201001', 'Statutory Reserve Fund'),
            ('30201002', 'Regulatory Reserve'),
        ]
        
        for acc_no, name in statutory_accounts:
            ChartOfAccounts.objects.create(
                accountno=acc_no, name=name, account_type='EQUITY',
                behavior='NORMAL', parent_account=statutory, is_data_entry=True,
            )
        self.stdout.write(f"  Created {len(statutory_accounts)} statutory accounts")
        
        # Retained earnings accounts
        retained_accounts = [
            ('30202001', 'Accumulated Surplus'),
            ('30202002', 'Current Year Surplus'),
            ('30202003', 'Dividend Declared'),
        ]
        
        for acc_no, name in retained_accounts:
            ChartOfAccounts.objects.create(
                accountno=acc_no, name=name, account_type='EQUITY',
                behavior='NORMAL', parent_account=retained, is_data_entry=True,
            )
        self.stdout.write(f"  Created {len(retained_accounts)} retained earnings accounts")
        
        # ============================================================
        # LEVEL 2: UNDER INCOME
        # ============================================================
        self.stdout.write("\n📁 LEVEL 2: Under INCOME")
        self.stdout.write("-"*50)
        
        income_parent = ChartOfAccounts.objects.get(accountno='40000000')
        
        operating_income = ChartOfAccounts.objects.create(
            accountno='40100000', name='OPERATING INCOME', account_type='INCOME',
            behavior='INCOME', parent_account=income_parent, is_data_entry=False,
        )
        self.stdout.write(f"  {operating_income.accountno} - {operating_income.name}")
        
        other_income = ChartOfAccounts.objects.create(
            accountno='40200000', name='OTHER INCOME', account_type='INCOME',
            behavior='INCOME', parent_account=income_parent, is_data_entry=False,
        )
        self.stdout.write(f"  {other_income.accountno} - {other_income.name}")
        
        # ============================================================
        # LEVEL 3 & 4: Operating Income
        # ============================================================
        self.stdout.write("\n📁 LEVEL 3 & 4: Operating Income Accounts")
        self.stdout.write("-"*50)
        
        operating_parent = ChartOfAccounts.objects.get(accountno='40100000')
        
        fee_income = ChartOfAccounts.objects.create(
            accountno='40101000', name='FEE INCOME', account_type='INCOME',
            behavior='INCOME', parent_account=operating_parent, is_data_entry=False,
        )
        self.stdout.write(f"  {fee_income.accountno} - {fee_income.name}")
        
        interest_income = ChartOfAccounts.objects.create(
            accountno='40102000', name='INTEREST INCOME', account_type='INCOME',
            behavior='INCOME', parent_account=operating_parent, is_data_entry=False,
        )
        self.stdout.write(f"  {interest_income.accountno} - {interest_income.name}")
        
        invest_income = ChartOfAccounts.objects.create(
            accountno='40103000', name='INVESTMENT INCOME', account_type='INCOME',
            behavior='INCOME', parent_account=operating_parent, is_data_entry=False,
        )
        self.stdout.write(f"  {invest_income.accountno} - {invest_income.name}")
        
        # Fee income
        fee_accounts = [
            ('40101001', 'Enrollment Fees'),
            ('40101002', 'Loan Processing Fees'),
        ]
        
        for acc_no, name in fee_accounts:
            ChartOfAccounts.objects.create(
                accountno=acc_no, name=name, account_type='INCOME',
                behavior='INCOME', parent_account=fee_income, is_data_entry=True,
            )
        self.stdout.write(f"  Created {len(fee_accounts)} fee accounts")
        
        # Interest income
        interest_accounts = [
            ('40102001', 'Loan Interest Income'),
            ('40102002', 'Savings Interest Income'),
            ('40102003', 'Fixed Deposit Interest'),
            ('40102004', 'Treasury Bills Interest'),
            ('40102005', 'Call Deposit Interest'),
            ('40102006', 'Bonds Interest'),
        ]
        
        for acc_no, name in interest_accounts:
            ChartOfAccounts.objects.create(
                accountno=acc_no, name=name, account_type='INCOME',
                behavior='INCOME', parent_account=interest_income, is_data_entry=True,
            )
        self.stdout.write(f"  Created {len(interest_accounts)} interest accounts")
        
        # Investment income
        invest_accounts = [
            ('40103001', 'Dividend Income'),
            ('40103002', 'Gain on Sale of Investments'),
        ]
        
        for acc_no, name in invest_accounts:
            ChartOfAccounts.objects.create(
                accountno=acc_no, name=name, account_type='INCOME',
                behavior='INCOME', parent_account=invest_income, is_data_entry=True,
            )
        self.stdout.write(f"  Created {len(invest_accounts)} investment income accounts")
        
        # ============================================================
        # LEVEL 3 & 4: Other Income
        # ============================================================
        self.stdout.write("\n📁 LEVEL 3 & 4: Other Income Accounts")
        self.stdout.write("-"*50)
        
        other_inc_parent = ChartOfAccounts.objects.get(accountno='40200000')
        
        misc_income = ChartOfAccounts.objects.create(
            accountno='40201000', name='MISCELLANEOUS INCOME', account_type='INCOME',
            behavior='INCOME', parent_account=other_inc_parent, is_data_entry=False,
        )
        self.stdout.write(f"  {misc_income.accountno} - {misc_income.name}")
        
        recoveries = ChartOfAccounts.objects.create(
            accountno='40202000', name='RECOVERIES', account_type='INCOME',
            behavior='INCOME', parent_account=other_inc_parent, is_data_entry=False,
        )
        self.stdout.write(f"  {recoveries.accountno} - {recoveries.name}")
        
        # Miscellaneous income
        misc_accounts = [
            ('40201001', 'Commission Earned'),
            ('40201002', 'Rental Income'),
            ('40201003', 'Other Operating Income'),
        ]
        
        for acc_no, name in misc_accounts:
            ChartOfAccounts.objects.create(
                accountno=acc_no, name=name, account_type='INCOME',
                behavior='INCOME', parent_account=misc_income, is_data_entry=True,
            )
        self.stdout.write(f"  Created {len(misc_accounts)} miscellaneous accounts")
        
        # Recoveries
        ChartOfAccounts.objects.create(
            accountno='40202001', name='Recovery of Bad Debts', account_type='INCOME',
            behavior='INCOME', parent_account=recoveries, is_data_entry=True,
        )
        self.stdout.write(f"  Created recovery account")
        
        # ============================================================
        # LEVEL 2: UNDER EXPENSES
        # ============================================================
        self.stdout.write("\n📁 LEVEL 2: Under EXPENSES")
        self.stdout.write("-"*50)
        
        exp_parent = ChartOfAccounts.objects.get(accountno='50000000')
        
        operating_exp = ChartOfAccounts.objects.create(
            accountno='50100000', name='OPERATING EXPENSES', account_type='EXPENSE',
            behavior='EXPENSE', parent_account=exp_parent, is_data_entry=False,
        )
        self.stdout.write(f"  {operating_exp.accountno} - {operating_exp.name}")
        
        financial_exp = ChartOfAccounts.objects.create(
            accountno='50200000', name='FINANCIAL EXPENSES', account_type='EXPENSE',
            behavior='EXPENSE', parent_account=exp_parent, is_data_entry=False,
        )
        self.stdout.write(f"  {financial_exp.accountno} - {financial_exp.name}")
        
        # ============================================================
        # LEVEL 3 & 4: Operating Expenses
        # ============================================================
        self.stdout.write("\n📁 LEVEL 3 & 4: Operating Expense Accounts")
        self.stdout.write("-"*50)
        
        operating_exp_parent = ChartOfAccounts.objects.get(accountno='50100000')
        
        personnel = ChartOfAccounts.objects.create(
            accountno='50101000', name='PERSONNEL EXPENSES', account_type='EXPENSE',
            behavior='EXPENSE', parent_account=operating_exp_parent, is_data_entry=False,
        )
        self.stdout.write(f"  {personnel.accountno} - {personnel.name}")
        
        admin = ChartOfAccounts.objects.create(
            accountno='50102000', name='ADMINISTRATIVE EXPENSES', account_type='EXPENSE',
            behavior='EXPENSE', parent_account=operating_exp_parent, is_data_entry=False,
        )
        self.stdout.write(f"  {admin.accountno} - {admin.name}")
        
        utilities = ChartOfAccounts.objects.create(
            accountno='50103000', name='UTILITIES', account_type='EXPENSE',
            behavior='EXPENSE', parent_account=operating_exp_parent, is_data_entry=False,
        )
        self.stdout.write(f"  {utilities.accountno} - {utilities.name}")
        
        occupancy = ChartOfAccounts.objects.create(
            accountno='50104000', name='OCCUPANCY EXPENSES', account_type='EXPENSE',
            behavior='EXPENSE', parent_account=operating_exp_parent, is_data_entry=False,
        )
        self.stdout.write(f"  {occupancy.accountno} - {occupancy.name}")
        
        repairs = ChartOfAccounts.objects.create(
            accountno='50105000', name='REPAIRS & MAINTENANCE', account_type='EXPENSE',
            behavior='EXPENSE', parent_account=operating_exp_parent, is_data_entry=False,
        )
        self.stdout.write(f"  {repairs.accountno} - {repairs.name}")
        
        professional = ChartOfAccounts.objects.create(
            accountno='50106000', name='PROFESSIONAL FEES', account_type='EXPENSE',
            behavior='EXPENSE', parent_account=operating_exp_parent, is_data_entry=False,
        )
        self.stdout.write(f"  {professional.accountno} - {professional.name}")
        
        # Personnel expenses
        personnel_accounts = [
            ('50101001', 'Salary and Allowances'),
            ('50101002', 'Overtime Allowance'),
            ('50101003', 'Bonuses'),
            ('50101004', 'Staff Training'),
            ('50101005', 'Staff Welfare'),
        ]
        
        for acc_no, name in personnel_accounts:
            ChartOfAccounts.objects.create(
                accountno=acc_no, name=name, account_type='EXPENSE',
                behavior='EXPENSE', parent_account=personnel, is_data_entry=True,
            )
        self.stdout.write(f"  Created {len(personnel_accounts)} personnel accounts")
        
        # Administrative expenses
        admin_accounts = [
            ('50102001', 'Stationery'),
            ('50102002', 'Printing & Photocopying'),
            ('50102003', 'Postage & Courier'),
            ('50102004', 'Telephone & Internet'),
        ]
        
        for acc_no, name in admin_accounts:
            ChartOfAccounts.objects.create(
                accountno=acc_no, name=name, account_type='EXPENSE',
                behavior='EXPENSE', parent_account=admin, is_data_entry=True,
            )
        self.stdout.write(f"  Created {len(admin_accounts)} admin accounts")
        
        # Utilities
        utility_accounts = [
            ('50103001', 'Electricity Bills'),
            ('50103002', 'Water Bills'),
            ('50103003', 'Fuel & Generator'),
        ]
        
        for acc_no, name in utility_accounts:
            ChartOfAccounts.objects.create(
                accountno=acc_no, name=name, account_type='EXPENSE',
                behavior='EXPENSE', parent_account=utilities, is_data_entry=True,
            )
        self.stdout.write(f"  Created {len(utility_accounts)} utility accounts")
        
        # Occupancy expenses
        occupancy_accounts = [
            ('50104001', 'Rent Expense'),
            ('50104002', 'Building Maintenance'),
            ('50104003', 'Security Services'),
        ]
        
        for acc_no, name in occupancy_accounts:
            ChartOfAccounts.objects.create(
                accountno=acc_no, name=name, account_type='EXPENSE',
                behavior='EXPENSE', parent_account=occupancy, is_data_entry=True,
            )
        self.stdout.write(f"  Created {len(occupancy_accounts)} occupancy accounts")
        
        # Repairs and maintenance
        repair_accounts = [
            ('50105001', 'Office Equipment Repairs'),
            ('50105002', 'Computer Maintenance'),
            ('50105003', 'Vehicle Maintenance'),
        ]
        
        for acc_no, name in repair_accounts:
            ChartOfAccounts.objects.create(
                accountno=acc_no, name=name, account_type='EXPENSE',
                behavior='EXPENSE', parent_account=repairs, is_data_entry=True,
            )
        self.stdout.write(f"  Created {len(repair_accounts)} repair accounts")
        
        # Professional fees
        professional_accounts = [
            ('50106001', 'Audit Fees'),
            ('50106002', 'Legal Fees'),
            ('50106003', 'Consultancy Fees'),
        ]
        
        for acc_no, name in professional_accounts:
            ChartOfAccounts.objects.create(
                accountno=acc_no, name=name, account_type='EXPENSE',
                behavior='EXPENSE', parent_account=professional, is_data_entry=True,
            )
        self.stdout.write(f"  Created {len(professional_accounts)} professional fee accounts")
        
        # ============================================================
        # LEVEL 3 & 4: Financial Expenses
        # ============================================================
        self.stdout.write("\n📁 LEVEL 3 & 4: Financial Expense Accounts")
        self.stdout.write("-"*50)
        
        financial_parent = ChartOfAccounts.objects.get(accountno='50200000')
        
        interest_exp = ChartOfAccounts.objects.create(
            accountno='50201000', name='INTEREST EXPENSE', account_type='EXPENSE',
            behavior='EXPENSE', parent_account=financial_parent, is_data_entry=False,
        )
        self.stdout.write(f"  {interest_exp.accountno} - {interest_exp.name}")
        
        bank_charges = ChartOfAccounts.objects.create(
            accountno='50202000', name='BANK CHARGES', account_type='EXPENSE',
            behavior='EXPENSE', parent_account=financial_parent, is_data_entry=False,
        )
        self.stdout.write(f"  {bank_charges.accountno} - {bank_charges.name}")
        
        depreciation = ChartOfAccounts.objects.create(
            accountno='50203000', name='DEPRECIATION', account_type='EXPENSE',
            behavior='EXPENSE', parent_account=financial_parent, is_data_entry=False,
        )
        self.stdout.write(f"  {depreciation.accountno} - {depreciation.name}")
        
        # Interest expense
        interest_exp_accounts = [
            ('50201001', 'Interest on Savings'),
            ('50201002', 'Dividend on Shares'),
            ('50201003', 'Interest on Borrowings'),
        ]
        
        for acc_no, name in interest_exp_accounts:
            ChartOfAccounts.objects.create(
                accountno=acc_no, name=name, account_type='EXPENSE',
                behavior='EXPENSE', parent_account=interest_exp, is_data_entry=True,
            )
        self.stdout.write(f"  Created {len(interest_exp_accounts)} interest expense accounts")
        
        # Bank charges
        bank_accounts = [
            ('50202001', 'Bank Transaction Fees'),
            ('50202002', 'Mobile Money Charges'),
            ('50202003', 'Cheque Book Charges'),
        ]
        
        for acc_no, name in bank_accounts:
            ChartOfAccounts.objects.create(
                accountno=acc_no, name=name, account_type='EXPENSE',
                behavior='EXPENSE', parent_account=bank_charges, is_data_entry=True,
            )
        self.stdout.write(f"  Created {len(bank_accounts)} bank charge accounts")
        
        # Depreciation
        depreciation_accounts = [
            ('50203001', 'Depreciation - Buildings'),
            ('50203002', 'Depreciation - Office Equipment'),
            ('50203003', 'Depreciation - Vehicles'),
        ]
        
        for acc_no, name in depreciation_accounts:
            ChartOfAccounts.objects.create(
                accountno=acc_no, name=name, account_type='EXPENSE',
                behavior='EXPENSE', parent_account=depreciation, is_data_entry=True,
            )
        self.stdout.write(f"  Created {len(depreciation_accounts)} depreciation accounts")
        
        # ============================================================
        # FINAL DISPLAY
        # ============================================================
        self.stdout.write("\n" + "="*70)
        self.stdout.write("FINAL CHART OF ACCOUNTS STRUCTURE")
        self.stdout.write("Format: X-XX-XX-XXX (e.g., 1-01-01-001)")
        self.stdout.write("="*70)
        
        def show_tree(account, level=0):
            indent = "  " * level
            entry = " [DATA ENTRY]" if account.is_data_entry else ""
            if len(account.accountno) == 8:
                formatted = f"{account.accountno[0]}-{account.accountno[1:3]}-{account.accountno[3:5]}-{account.accountno[5:8]}"
            else:
                formatted = account.accountno
            self.stdout.write(f"{indent}{formatted} - {account.name}{entry}")
            for child in account.children.all().order_by('accountno'):
                show_tree(child, level + 1)
        
        roots = ChartOfAccounts.objects.filter(parent_account__isnull=True).order_by('accountno')
        for root in roots:
            show_tree(root)
        
        total = ChartOfAccounts.objects.count()
        self.stdout.write("\n" + "="*70)
        self.stdout.write(self.style.SUCCESS(f"✅ TOTAL ACCOUNTS CREATED: {total}"))
        self.stdout.write("="*70)