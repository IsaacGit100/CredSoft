from decimal import Decimal
from .models import ChartOfAccounts, GeneralLedger

def get_trial_balance_data(as_at_date=None):
    """
    Build trial balance data: account code, name, debit balance, credit balance.
    Uses opening_balance from GeneralLedger as the base.
    """
    accounts = ChartOfAccounts.objects.filter(is_active=True).order_by('accountno')
    trial_balance = []
    total_debit = Decimal('0.00')
    total_credit = Decimal('0.00')

    for account in accounts:
        ledger = GeneralLedger.objects.filter(account=account).first()
        if ledger:
            # For trial balance, use current_balance (which includes opening + transactions)
            balance = ledger.current_balance
        else:
            balance = Decimal('0.00')

        # Determine if it's a debit or credit balance
        if balance > 0:
            # Assets and Expenses normally have debit balance
            if account.account_type in ['ASSET', 'EXPENSE']:
                debit = balance
                credit = Decimal('0.00')
            else:
                # Liabilities, Equity, Income normally have credit balance
                debit = Decimal('0.00')
                credit = balance
        else:
            debit = Decimal('0.00')
            credit = Decimal('0.00')

        # Only include accounts with non‑zero balance
        if debit != 0 or credit != 0:
            trial_balance.append({
                'account': account,
                'debit': debit,
                'credit': credit,
            })
            total_debit += debit
            total_credit += credit

    difference = total_debit - total_credit
    is_balanced = abs(difference) < Decimal('0.01')

    return {
        'trial_balance': trial_balance,
        'total_debit': total_debit,
        'total_credit': total_credit,
        'difference': difference,
        'is_balanced': is_balanced,
        'as_at_date': as_at_date,
    }