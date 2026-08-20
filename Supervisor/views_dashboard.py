from django.shortcuts import render
from django.db.models import Sum, Count, Q
from decimal import Decimal
from MembersApp.models import Master
from LoanApp.models import Loan
from InvestApp.models import Investment
from FinanceApp.models import GeneralLedger

def database_dashboard(request):
    # ======================== MEMBERS ========================
    all_members = Master.objects.all()
    
    active_count = all_members.filter(mem_status='Active').count()
    inactive_count = all_members.filter(mem_status='InActive').count()
    deleted_count = all_members.filter(is_deleted=True).count()
    
    # Active members aggregates
    active_agg = all_members.filter(mem_status='Active').aggregate(
        total_deposits=Sum('tot_deposits'),
        total_withdrawals=Sum('tot_deposit_withdrawal'),
        total_shares=Sum('tot_shares'),
        total_shares_withdrawal=Sum('tot_shares_withdrawal'),
        total_interest_accrued=Sum('tot_interest_accrued'),
        total_dividend=Sum('tot_dividend'),
        total_dividend_withdrawal=Sum('tot_dividend_withdrawal'),
    )
    # Inactive members aggregates
    inactive_agg = all_members.filter(mem_status='InActive').aggregate(
        total_deposits=Sum('tot_deposits'),
        total_withdrawals=Sum('tot_deposit_withdrawal'),
        total_shares=Sum('tot_shares'),
        total_shares_withdrawal=Sum('tot_shares_withdrawal'),
        total_interest_accrued=Sum('tot_interest_accrued'),
        total_dividend=Sum('tot_dividend'),
        total_dividend_withdrawal=Sum('tot_dividend_withdrawal'),
    )
    # Deleted members aggregates
    deleted_agg = all_members.filter(is_deleted=True).aggregate(
        total_deposits=Sum('tot_deposits'),
        total_withdrawals=Sum('tot_deposit_withdrawal'),
        total_shares=Sum('tot_shares'),
        total_shares_withdrawal=Sum('tot_shares_withdrawal'),
        total_interest_accrued=Sum('tot_interest_accrued'),
        total_dividend=Sum('tot_dividend'),
        total_dividend_withdrawal=Sum('tot_dividend_withdrawal'),
    )
    # Grand totals (all members)
    grand_member_totals = all_members.aggregate(
        total_deposits=Sum('tot_deposits'),
        total_withdrawals=Sum('tot_deposit_withdrawal'),
        net_deposits=Sum('tot_deposits') - Sum('tot_deposit_withdrawal'),
        total_shares=Sum('tot_shares'),
        total_shares_withdrawal=Sum('tot_shares_withdrawal'),
        net_shares=Sum('tot_shares') - Sum('tot_shares_withdrawal'),
        total_interest_accrued=Sum('tot_interest_accrued'),
        total_dividend=Sum('tot_dividend'),
        total_dividend_withdrawal=Sum('tot_dividend_withdrawal'),
        net_dividend=Sum('tot_dividend') - Sum('tot_dividend_withdrawal'),
    )
    # Convert None to 0
    for agg in [active_agg, inactive_agg, deleted_agg, grand_member_totals]:
        for key, value in agg.items():
            if value is None:
                agg[key] = Decimal('0.00')
    
    # ======================== LOANS ========================
    all_loans = Loan.objects.all()
    
    loan_status_counts = {
        'new': all_loans.filter(status='New Loan').count(),
        'active': all_loans.filter(status='Active').count(),
        'owing': all_loans.filter(status='Owing').count(),
        'completed': all_loans.filter(status='Completed').count(),
        'expired': all_loans.filter(status='Expired').count(),
    }
    
    loan_totals = {
        'new': all_loans.filter(status='New Loan').aggregate(
            total_principal=Sum('principal'),
            total_balance=Sum('loan_balance'),
            total_ded=Sum('tot_ded'),
            total_int=Sum('tot_int'),
        ),
        'active': all_loans.filter(status='Active').aggregate(
            total_principal=Sum('principal'),
            total_balance=Sum('loan_balance'),
            total_ded=Sum('tot_ded'),
            total_int=Sum('tot_int'),
        ),
        'owing': all_loans.filter(status='Owing').aggregate(
            total_principal=Sum('principal'),
            total_balance=Sum('loan_balance'),
            total_ded=Sum('tot_ded'),
            total_int=Sum('tot_int'),
        ),
        'completed': all_loans.filter(status='Completed').aggregate(
            total_principal=Sum('principal'),
            total_balance=Sum('loan_balance'),
            total_ded=Sum('tot_ded'),
            total_int=Sum('tot_int'),
        ),
        'expired': all_loans.filter(status='Expired').aggregate(
            total_principal=Sum('principal'),
            total_balance=Sum('loan_balance'),
            total_ded=Sum('tot_ded'),
            total_int=Sum('tot_int'),
        ),
    }
    grand_loan_totals = all_loans.aggregate(
        total_principal=Sum('principal'),
        total_balance=Sum('loan_balance'),
        total_ded=Sum('tot_ded'),
        total_int=Sum('tot_int'),
    )
    for status in loan_totals:
        for key, val in loan_totals[status].items():
            if val is None:
                loan_totals[status][key] = Decimal('0.00')
    for key, val in grand_loan_totals.items():
        if val is None:
            grand_loan_totals[key] = Decimal('0.00')
    
    # ======================== INVESTMENTS ========================
    all_investments = Investment.objects.all()  # remove the wrong filter
    investment_types = ['Savings', 'Fixed Deposit', 'T-Bill', 'Call Deposit', 'Bonds', 'Sweep Calls', 'Other']
    investment_data = {}
    for inv_type in investment_types:
        qs = all_investments.filter(investment_type=inv_type)
        investment_data[inv_type] = {
            'count': qs.count(),
            'total_invested': qs.aggregate(total=Sum('amount'))['total'] or Decimal('0.00'),
            'total_expected': qs.aggregate(total=Sum('interest_expected'))['total'] or Decimal('0.00'),
            'total_earned': qs.aggregate(total=Sum('interest_earned'))['total'] or Decimal('0.00'),
        }
    grand_investment_totals = {
        'total_invested': all_investments.aggregate(total=Sum('amount'))['total'] or Decimal('0.00'),
        'total_expected': all_investments.aggregate(total=Sum('interest_expected'))['total'] or Decimal('0.00'),
        'total_earned': all_investments.aggregate(total=Sum('interest_earned'))['total'] or Decimal('0.00'),
    }
    
    # ======================== CASH & BANK ========================
    def get_ledger_balance(account_number):
        ledger = GeneralLedger.objects.filter(account__accountno=account_number).first()
        return ledger.current_balance if ledger else Decimal('0.00')
    
    cash_bank = {
        'nib_accra': get_ledger_balance('10102001'),
        'gcb_haatso': get_ledger_balance('10102002'),
        'gcb_ablekuma': get_ledger_balance('10102003'),
        'current_cashier': get_ledger_balance('10101001'),
        'savings_cashier': get_ledger_balance('10101002'),
        'momo_cashier': get_ledger_balance('10103001'),
    }
    cash_bank['total_bank'] = cash_bank['nib_accra'] + cash_bank['gcb_haatso'] + cash_bank['gcb_ablekuma']
    cash_bank['total_cash'] = cash_bank['current_cashier'] + cash_bank['savings_cashier'] + cash_bank['momo_cashier']
    cash_bank['grand_total_liquid'] = cash_bank['total_bank'] + cash_bank['total_cash']
    
    # ======================== CONTEXT ========================
    context = {
        # Member
        'active_count': active_count,
        'inactive_count': inactive_count,
        'deleted_count': deleted_count,
        'active_agg': active_agg,
        'inactive_agg': inactive_agg,
        'deleted_agg': deleted_agg,
        'grand_member_totals': grand_member_totals,
        # Loan
        'loan_status_counts': loan_status_counts,
        'loan_totals': loan_totals,
        'grand_loan_totals': grand_loan_totals,
        # Investment
        'investment_data': investment_data,
        'grand_investment_totals': grand_investment_totals,
        # Cash & Bank
        'cash_bank': cash_bank,
    }
    return render(request, 'Supervisor/database_dashboard.html', context)