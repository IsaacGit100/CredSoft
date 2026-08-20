from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

@login_required
def dashboard(request):
    """Main dashboard with menu items"""
    return render(request, 'dashboard.html')

# credsoft/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django_ledger.models import EntityModel, JournalEntryModel

from django.utils import timezone

# credsoft/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django_ledger.models import EntityModel, JournalEntryModel, TransactionModel, AccountModel
from decimal import Decimal
from django.utils import timezone

@login_required
def finance_dashboard(request):
    # Get the user's default entity
    try:
        profile = request.user.userprofile
        entity = profile.default_entity
    except AttributeError:
        # Fallback: use the first entity if no profile
        entity = EntityModel.objects.first()

    if not entity:
        # No entities exist
        return render(request, 'FinanceApp/dashboard.html', {'error': 'No entity found'})

    # --- Get recent journal entries ---
    recent_entries = JournalEntryModel.objects.filter(
        entity=entity
    ).order_by('-date')[:10]

    # --- Calculate cash balance ---
    try:
        cash_account = AccountModel.objects.get(entity=entity, code='1010')
        debit_total = TransactionModel.objects.filter(
            account=cash_account,
            tx_type='debit'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        credit_total = TransactionModel.objects.filter(
            account=cash_account,
            tx_type='credit'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        cash_balance = debit_total - credit_total
    except AccountModel.DoesNotExist:
        cash_balance = Decimal('0')

    # --- Total Revenue (Account 4010) ---
    try:
        revenue_account = AccountModel.objects.get(entity=entity, code='4010')
        revenue_total = TransactionModel.objects.filter(
            account=revenue_account,
            tx_type='credit'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    except AccountModel.DoesNotExist:
        revenue_total = Decimal('0')

    # --- Total Expenses (all expense accounts) ---
    expense_accounts = AccountModel.objects.filter(
        entity=entity,
        role='expense'
    )
    expense_total = TransactionModel.objects.filter(
        account__in=expense_accounts,
        tx_type='debit'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    net_income = revenue_total - expense_total

    context = {
        'entity': entity,
        'recent_entries': recent_entries,
        'cash_balance': cash_balance,
        'revenue_total': revenue_total,
        'expense_total': expense_total,
        'net_income': net_income,
        'entity_slug': entity.slug,
    }
    return render(request, 'FinanceApp/dashboard.html', context)



def switch_entity(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    request.session['current_entity_slug'] = slug
    return redirect('FinanceApp:finance_dashboard')