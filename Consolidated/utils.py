def user_can_access_entity(user, entity):
    """Check if a user (normal or super_admin) can access the given entity."""
    try:
        profile = user.djan_led_profile
        if profile.role == 'super_admin':
            return True
        if entity in profile.allowed_entities.all() or entity == profile.default_entity:
            return True
        return False
    except:
        return False
    
from django.db.models import Sum
from django_ledger.models import AccountModel, TransactionModel
from decimal import Decimal

    
from django.db.models import Sum
from django_ledger.models import AccountModel, TransactionModel
from decimal import Decimal


def get_entity_summary(entity, start_date, end_date):
    """Get revenue, expenses, and net income for a single entity."""
    revenue_accounts = AccountModel.objects.filter(coa_model__entity=entity, role='revenue')
    expense_accounts = AccountModel.objects.filter(coa_model__entity=entity, role='expense')

    revenue = TransactionModel.objects.filter(
        account__in=revenue_accounts,
        tx_type='credit',
        journal_entry__timestamp__range=[start_date, end_date]
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')

    expenses = TransactionModel.objects.filter(
        account__in=expense_accounts,
        tx_type='debit',
        journal_entry__timestamp__range=[start_date, end_date]
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')

    return {
        'revenue': revenue,
        'expenses': expenses,
        'net_income': revenue - expenses,
    }

def get_consolidated_summary(entities, start_date, end_date):
    """Aggregate summary across multiple entities."""
    total_revenue = Decimal('0')
    total_expenses = Decimal('0')
    entity_data = []

    for entity in entities:
        summary = get_entity_summary(entity, start_date, end_date)
        entity_data.append({
            'name': entity.name,
            'slug': entity.slug,
            'revenue': summary['revenue'],
            'expenses': summary['expenses'],
            'net_income': summary['net_income'],
        })
        total_revenue += summary['revenue']
        total_expenses += summary['expenses']

    return {
        'entity_data': entity_data,
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'net_income': total_revenue - total_expenses,
    }
    
def user_can_access_entity(user, entity):
    try:
        profile = user.djan_led_profile
        if profile.role == 'super_admin':
            return True
        if entity in profile.allowed_entities.all() or entity == profile.default_entity:
            return True
    except:
        pass
    return False


from decimal import Decimal
from django.db.models import Sum
from django_ledger.models import AccountModel, TransactionModel

def get_entity_revenue_expense(entity, start_date, end_date):
    """Get revenue and expenses for an entity in a date range."""
    revenue_accounts = AccountModel.objects.filter(coa_model__entity=entity, role='revenue')
    expense_accounts = AccountModel.objects.filter(coa_model__entity=entity, role='expense')

    revenue = TransactionModel.objects.filter(
        account__in=revenue_accounts,
        tx_type='credit',
        journal_entry__timestamp__range=[start_date, end_date]
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')

    expenses = TransactionModel.objects.filter(
        account__in=expense_accounts,
        tx_type='debit',
        journal_entry__timestamp__range=[start_date, end_date]
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')

    return {'revenue': revenue, 'expenses': expenses, 'net_income': revenue - expenses}

def get_entity_balance_sheet_balances(entity):
    """Get total assets, liabilities, equity for an entity (all dates)."""
    def get_account_balance(account):
        debits = TransactionModel.objects.filter(account=account, tx_type='debit').aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        credits = TransactionModel.objects.filter(account=account, tx_type='credit').aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        if account.balance_type == 'debit':
            return debits - credits
        else:
            return credits - debits

    assets = AccountModel.objects.filter(coa_model__entity=entity, role='asset')
    liabilities = AccountModel.objects.filter(coa_model__entity=entity, role='liability')
    equity = AccountModel.objects.filter(coa_model__entity=entity, role='equity')

    total_assets = sum(get_account_balance(acc) for acc in assets)
    total_liabilities = sum(get_account_balance(acc) for acc in liabilities)
    total_equity = sum(get_account_balance(acc) for acc in equity)

    return {
        'total_assets': total_assets,
        'total_liabilities': total_liabilities,
        'total_equity': total_equity,
    }

def get_entity_cash_flow(entity, start_date, end_date):
    """Simplified cash flow: sum of all debit/credit transactions to Cash accounts."""
    cash_accounts = AccountModel.objects.filter(
        coa_model__entity=entity,
        role='asset',
        code__in=['1010', '1020', '1211', '1212']  # common cash/bank codes
    )
    inflows = TransactionModel.objects.filter(
        account__in=cash_accounts,
        tx_type='debit',
        journal_entry__timestamp__range=[start_date, end_date]
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')

    outflows = TransactionModel.objects.filter(
        account__in=cash_accounts,
        tx_type='credit',
        journal_entry__timestamp__range=[start_date, end_date]
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')

    return {'inflows': inflows, 'outflows': outflows, 'net': inflows - outflows}

def get_entity_trial_balance(entity):
    """Get all accounts with debit and credit totals."""
    accounts = AccountModel.objects.filter(coa_model__entity=entity).exclude(role='root').order_by('code')
    trial_data = []
    for acc in accounts:
        debits = TransactionModel.objects.filter(account=acc, tx_type='debit').aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        credits = TransactionModel.objects.filter(account=acc, tx_type='credit').aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        if debits or credits:
            trial_data.append({
                'code': acc.code,
                'name': acc.name,
                'debit': debits,
                'credit': credits,
            })
    return trial_data
