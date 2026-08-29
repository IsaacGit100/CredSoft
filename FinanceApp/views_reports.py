# FinanceApp/views_reports.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import models
from decimal import Decimal
from datetime import datetime, timedelta
from .models import JournalLine, GeneralLedger
from coa.models import ChartOfAccounts

# ============================================================
# TRIAL BALANCE
# ============================================================

@login_required
def trial_balance(request):
    """Generate Trial Balance report"""
    
    as_at_date = request.GET.get('as_at_date', timezone.now().date())
    
    # Get all active accounts with their ledger balances
    accounts = ChartOfAccounts.objects.filter(is_active=True).order_by('accountno')
    
    trial_balance_data = []
    total_debit = Decimal('0')
    total_credit = Decimal('0')
    
    for account in accounts:
        # Get ledger balance
        ledger = GeneralLedger.objects.filter(account=account).first()
        balance = ledger.current_balance if ledger else Decimal('0')
        
        # Determine if balance is debit or credit based on account type
        if account.account_type in ['ASSET', 'EXPENSE']:
            # Assets and Expenses have debit normal balance
            debit = balance if balance > 0 else Decimal('0')
            credit = abs(balance) if balance < 0 else Decimal('0')
        else:
            # Liabilities, Equity, Income have credit normal balance
            credit = balance if balance > 0 else Decimal('0')
            debit = abs(balance) if balance < 0 else Decimal('0')
        
        # Only show accounts with non-zero balance
        if debit != 0 or credit != 0:
            trial_balance_data.append({
                'account': account,
                'debit': debit,
                'credit': credit,
            })
            total_debit += debit
            total_credit += credit
    
    # Calculate difference
    difference = abs(total_debit - total_credit)
    is_balanced = total_debit == total_credit
    
    context = {
        'trial_balance': trial_balance_data,
        'total_debit': total_debit,
        'total_credit': total_credit,
        'difference': difference,
        'is_balanced': is_balanced,
        'as_at_date': as_at_date,
        'today': timezone.now(),
    }
    return render(request, 'FinanceApp/trial_balance.html', context)


# ============================================================
# PROFIT & LOSS (INCOME STATEMENT)
# ============================================================

def profit_loss_print(request):
    pass


def profit_loss_pdf(request):
    pass


def profit_loss_excel(request):
    pass


@login_required
def profit_loss(request):
    """Generate Profit & Loss Statement (Income Statement)"""
    
    # Get date range
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    
    # Default to current month if not specified
    if not from_date or not to_date:
        today = timezone.now().date()
        from_date = today.replace(day=1)
        to_date = today
    
    # Get all income accounts
    income_accounts = ChartOfAccounts.objects.filter(
        account_type='INCOME',
        is_active=True
    ).order_by('accountno')
    
    # Get all expense accounts
    expense_accounts = ChartOfAccounts.objects.filter(
        account_type='EXPENSE',
        is_active=True
    ).order_by('accountno')
    
    # Calculate income totals
    income_data = []
    total_income = Decimal('0')
    
    for account in income_accounts:
        # Get journal lines for this account within date range
        lines = JournalLine.objects.filter(
            account=account,
            journal__entry_date__gte=from_date,
            journal__entry_date__lte=to_date,
            journal__status='POSTED'
        )
        
        # Calculate total credit (income increases with credit)
        amount = lines.aggregate(total=models.Sum('credit'))['total'] or Decimal('0')
        
        if amount != 0:
            income_data.append({
                'account': account,
                'amount': amount,
            })
            total_income += amount
    
    # Calculate expense totals
    expense_data = []
    total_expense = Decimal('0')
    
    for account in expense_accounts:
        # Get journal lines for this account within date range
        lines = JournalLine.objects.filter(
            account=account,
            journal__entry_date__gte=from_date,
            journal__entry_date__lte=to_date,
            journal__status='POSTED'
        )
        
        # Calculate total debit (expenses increase with debit)
        amount = lines.aggregate(total=models.Sum('debit'))['total'] or Decimal('0')
        
        if amount != 0:
            expense_data.append({
                'account': account,
                'amount': amount,
            })
            total_expense += amount
    
    net_income = total_income - total_expense
    
    context = {
        'income_data': income_data,
        'expense_data': expense_data,
        'total_income': total_income,
        'total_expense': total_expense,
        'net_income': net_income,
        'from_date': from_date,
        'to_date': to_date,
        'is_profit': net_income > 0,
        'is_loss': net_income < 0,
        'today': timezone.now(),
    }
    return render(request, 'FinanceApp/profit_loss.html', context)


# ============================================================
# BALANCE SHEET
# ============================================================

# FinanceApp/views_reports.py (or wherever your balance_sheet view is)

from decimal import Decimal
from django.db.models import Sum
from django.shortcuts import render
from django.utils import timezone
from FixedAssets.models import AssetCategory
from coa.models import ChartOfAccounts
from FinanceApp.models import GeneralLedger

def balance_sheet(request):
    as_at_date = request.GET.get('as_at_date')
    if as_at_date:
        from datetime import datetime
        as_at_date = datetime.strptime(as_at_date, '%Y-%m-%d').date()
    else:
        as_at_date = timezone.now().date()

    # Get all active accounts
    accounts = ChartOfAccounts.objects.filter(is_active=True)

    # ---- 1. Fixed Assets ----
    asset_categories = AssetCategory.objects.all()
    fixed_asset_data = []
    total_fixed_assets_nbv = Decimal('0')

    for category in asset_categories:
        # Cost
        asset_ledger = GeneralLedger.objects.filter(account=category.asset_account).first()
        cost = asset_ledger.current_balance if asset_ledger else Decimal('0')

        # Accumulated Depreciation
        acc_dep_ledger = GeneralLedger.objects.filter(account=category.accumulated_depreciation_account).first()
        acc_dep = acc_dep_ledger.current_balance if acc_dep_ledger else Decimal('0')

        nbv = cost - acc_dep
        total_fixed_assets_nbv += nbv

        fixed_asset_data.append({
            'category': category,
            'cost': cost,
            'accumulated_depreciation': acc_dep,
            'net_book_value': nbv,
        })

    # ---- 2. Other Assets (non-fixed) ----
    # Exclude asset accounts that are linked to fixed asset categories
    exclude_account_ids = []
    for cat in asset_categories:
        exclude_account_ids.append(cat.asset_account.id)
        exclude_account_ids.append(cat.accumulated_depreciation_account.id)

    other_assets = []
    for account in accounts.filter(account_type='ASSET'):
        if account.id not in exclude_account_ids:
            ledger = GeneralLedger.objects.filter(account=account).first()
            balance = ledger.current_balance if ledger else Decimal('0')
            if balance != 0:
                other_assets.append({'account': account, 'balance': balance})

    # ---- 3. Liabilities ----
    liabilities = []
    total_liabilities = Decimal('0')
    for account in accounts.filter(account_type='LIABILITY'):
        ledger = GeneralLedger.objects.filter(account=account).first()
        balance = ledger.current_balance if ledger else Decimal('0')
        if balance != 0:
            liabilities.append({'account': account, 'balance': balance})
            total_liabilities += balance

    # ---- 4. Equity ----
    equity = []
    total_equity = Decimal('0')
    for account in accounts.filter(account_type='EQUITY'):
        ledger = GeneralLedger.objects.filter(account=account).first()
        balance = ledger.current_balance if ledger else Decimal('0')
        if balance != 0:
            equity.append({'account': account, 'balance': balance})
            total_equity += balance

    total_assets = total_fixed_assets_nbv + sum(item['balance'] for item in other_assets)

    context = {
        'fixed_asset_data': fixed_asset_data,              # list of dicts with cost, acc_dep, nbv
        'other_assets': other_assets,                      # list of dicts with account, balance
        'liabilities': liabilities,
        'equity': equity,
        'total_assets': total_assets,
        'total_liabilities': total_liabilities,
        'total_equity': total_equity,
        'total_fixed_assets_nbv': total_fixed_assets_nbv,  # <-- ADD THIS
        'as_at_date': as_at_date,
        'is_balanced': total_assets == (total_liabilities + total_equity),
        'today': timezone.now(),
    }
    return render(request, 'FinanceApp/balance_sheet.html', context)





@login_required
def balance_sheet1(request):
    """Generate Balance Sheet"""
    
    as_at_date = request.GET.get('as_at_date', timezone.now().date())
    
    # Get all asset accounts
    asset_accounts = ChartOfAccounts.objects.filter(
        account_type='ASSET',
        is_active=True
    ).order_by('accountno')
    
    # Get all liability accounts
    liability_accounts = ChartOfAccounts.objects.filter(
        account_type='LIABILITY',
        is_active=True
    ).order_by('accountno')
    
    # Get all equity accounts
    equity_accounts = ChartOfAccounts.objects.filter(
        account_type='EQUITY',
        is_active=True
    ).order_by('accountno')
    
    # Calculate asset totals
    assets_data = []
    total_assets = Decimal('0')
    
    for account in asset_accounts:
        ledger = GeneralLedger.objects.filter(account=account).first()
        balance = ledger.current_balance if ledger else Decimal('0')
        
        if balance != 0:
            assets_data.append({
                'account': account,
                'amount': balance,
            })
            total_assets += balance
    
    # Calculate liability totals
    liabilities_data = []
    total_liabilities = Decimal('0')
    
    for account in liability_accounts:
        ledger = GeneralLedger.objects.filter(account=account).first()
        balance = ledger.current_balance if ledger else Decimal('0')
        
        if balance != 0:
            liabilities_data.append({
                'account': account,
                'amount': balance,
            })
            total_liabilities += balance
    
    # Calculate equity totals
    equity_data = []
    total_equity = Decimal('0')
    
    for account in equity_accounts:
        ledger = GeneralLedger.objects.filter(account=account).first()
        balance = ledger.current_balance if ledger else Decimal('0')
        
        if balance != 0:
            equity_data.append({
                'account': account,
                'amount': balance,
            })
            total_equity += balance
    
    # Calculate if balance sheet balances
    liabilities_equity = total_liabilities + total_equity
    difference = total_assets - liabilities_equity
    is_balanced = difference == 0
    
    context = {
        'assets_data': assets_data,
        'liabilities_data': liabilities_data,
        'equity_data': equity_data,
        'total_assets': total_assets,
        'total_liabilities': total_liabilities,
        'total_equity': total_equity,
        'liabilities_equity': liabilities_equity,
        'difference': difference,
        'is_balanced': is_balanced,
        'as_at_date': as_at_date,
        'today': timezone.now(),
    }
    return render(request, 'FinanceApp/balance_sheet.html', context)


# ============================================================
# REPORT DASHBOARD
# ============================================================

@login_required
def report_dashboard(request):
    """Financial Reports Dashboard"""
    
    # Get current period info
    today = timezone.now().date()
    current_month_start = today.replace(day=1)
    current_year_start = today.replace(month=1, day=1)
    
    # Get previous month
    if today.month == 1:
        prev_month_start = today.replace(year=today.year-1, month=12, day=1)
    else:
        prev_month_start = today.replace(month=today.month-1, day=1)
    
    # Get previous month end
    if today.month == 1:
        prev_month_end = today.replace(year=today.year-1, month=12, day=31)
    else:
        next_month = today.replace(day=28) + timedelta(days=4)
        prev_month_end = next_month - timedelta(days=next_month.day)
    
    context = {
        'current_month_start': current_month_start,
        'today': today,
        'current_year_start': current_year_start,
        'prev_month_start': prev_month_start,
        'prev_month_end': prev_month_end,
    }
    return render(request, 'FinanceApp/report_dashboard.html', context)


def general_ledger_print(request):
    pass


def general_ledger_pdf(request):
    pass


def general_ledger_excel(request):
    pass


def account_ledger_print(request):
    pass


def account_ledger_pdf(request):
    pass


def account_ledger_excel(request):
    pass

