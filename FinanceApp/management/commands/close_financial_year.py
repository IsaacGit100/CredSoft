# management/commands/close_financial_year.py
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from FinanceApp.models import GeneralLedger, ChartOfAccounts
from coa.models import ChartOfAccounts
from FinanceApp.models import JournalEntry, JournalLine

class Command(BaseCommand):
    help = 'Close the financial year: reset income/expense accounts and transfer net profit to retained earnings.'

    def handle(self, *args, **options):
        # 1. Get all Income accounts
        income_accounts = ChartOfAccounts.objects.filter(account_type='INCOME', is_active=True)
        # 2. Get all Expense accounts
        expense_accounts = ChartOfAccounts.objects.filter(account_type='EXPENSE', is_active=True)

        total_income = Decimal('0')
        total_expense = Decimal('0')

        # 3. Calculate totals
        for acc in income_accounts:
            ledger = GeneralLedger.objects.filter(account=acc).first()
            if ledger:
                total_income += ledger.current_balance

        for acc in expense_accounts:
            ledger = GeneralLedger.objects.filter(account=acc).first()
            if ledger:
                total_expense += ledger.current_balance

        net_profit = total_income - total_expense

        # 4. Create the closing journal entry
        journal = JournalEntry.objects.create(
            entry_number=f'YE-{timezone.now().year}',
            entry_date=timezone.now().date(),
            description=f'Year-end closing entry for {timezone.now().year}',
            status='POSTED',
            posted=True,
            posted_at=timezone.now()
        )

        # 5. Debit each Income account (to zero it)
        for acc in income_accounts:
            ledger = GeneralLedger.objects.filter(account=acc).first()
            if ledger and ledger.current_balance != 0:
                JournalLine.objects.create(
                    journal=journal,
                    account=acc,
                    debit=ledger.current_balance,
                    credit=0,
                    line_description=f'Closing {acc.name}'
                )
                # Reset the balance
                ledger.current_balance = Decimal('0')
                ledger.save()

        # 6. Credit each Expense account (to zero it)
        for acc in expense_accounts:
            ledger = GeneralLedger.objects.filter(account=acc).first()
            if ledger and ledger.current_balance != 0:
                JournalLine.objects.create(
                    journal=journal,
                    account=acc,
                    debit=0,
                    credit=ledger.current_balance,
                    line_description=f'Closing {acc.name}'
                )
                ledger.current_balance = Decimal('0')
                ledger.save()

        # 7. Transfer Net Profit/Loss to Retained Earnings
        retained_earnings_account = ChartOfAccounts.objects.get(accountno='YOUR_RETAINED_EARNINGS_CODE')
        retained_ledger, _ = GeneralLedger.objects.get_or_create(account=retained_earnings_account)

        if net_profit > 0:
            # Profit: Credit Retained Earnings
            JournalLine.objects.create(
                journal=journal,
                account=retained_earnings_account,
                debit=0,
                credit=net_profit,
                line_description=f'Transfer of net profit {net_profit}'
            )
            retained_ledger.current_balance += net_profit
        else:
            # Loss: Debit Retained Earnings
            JournalLine.objects.create(
                journal=journal,
                account=retained_earnings_account,
                debit=abs(net_profit),
                credit=0,
                line_description=f'Transfer of net loss {abs(net_profit)}'
            )
            retained_ledger.current_balance -= abs(net_profit)

        retained_ledger.save()

        self.stdout.write(self.style.SUCCESS(f'Year-end closing completed. Net profit: {net_profit}'))