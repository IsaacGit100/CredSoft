from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import datetime
from .utils import get_consolidated_summary

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from datetime import datetime
from .utils import get_consolidated_summary
from calendar import monthrange
from decimal import Decimal


@login_required
def consolidated_dashboard(request):
    # Check if user is super admin
    try:
        profile = request.user.djan_led_profile
        if profile.role != 'super_admin':
            return redirect('after_login_redirect')
    except:
        return redirect('after_login_redirect')

    # Get the root entity (Head Office) – depth=1 for root nodes
    root = EntityModel.objects.filter(depth=1).first()
    if not root:
        return render(request, 'Consolidated/dashboard.html', {'error': 'No root entity found.'})

    # Get all descendants (including root itself)
    entities = root.get_descendants(include_self=True)

    # Date range: current month
    today = datetime.today()
    start_date = today.replace(day=1)
    end_date = today

    # Get consolidated data
    data = get_consolidated_summary(entities, start_date, end_date)

    context = {
        'root_entity': root,
        'entity_data': data['entity_data'],
        'total_revenue': data['total_revenue'],
        'total_expenses': data['total_expenses'],
        'net_income': data['net_income'],
        'month_name': today.strftime('%B %Y'),
    }
    return render(request, 'Consolidated/dashboard.html', context)


@login_required
def after_login_redirect(request):
    try:
        profile = request.user.djan_led_profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)

    if profile.role == 'super_admin':
        return redirect('Consolidated:consolidated_dashboard')

    if profile.default_entity:
        return redirect('djan_led:entity_dashboard', slug=profile.default_entity.slug)
    else:
        entities = profile.allowed_entities.all()
        if entities.count() == 1:
            return redirect('djan_led:entity_dashboard', slug=entities.first().slug)
        elif entities.count() > 1:
            return render(request, 'djan_led/select_entity.html', {'entities': entities})
        else:
            return render(request, 'djan_led/no_entity.html')


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django_ledger.models import EntityModel


@login_required
def super_admin_portal(request):
    # Check if user is super admin
    try:
        profile = request.user.djan_led_profile
        if profile.role != "super_admin":
            return redirect("after_login_redirect")
    except:
        return redirect("after_login_redirect")

    # Get all entities
    all_entities = EntityModel.objects.all().order_by("name")

    context = {
        "all_entities": all_entities,
        # ... other context
    }
    return render(request, "Consolidated/portal.html", context)


@login_required
def super_admin_portal1(request):
    from django_ledger.models import EntityModel
    # Check if user is super admin
    try:
        profile = request.user.djan_led_profile
        if profile.role != 'super_admin':
            return redirect('djan_led:after_login_redirect')
    except:
        return redirect('djan_led:after_login_redirect')
    
    root_entity = EntityModel.objects.filter(depth=1).first()


    # Get all entities (or only those the super admin has access to – but they have all)
    entities = EntityModel.objects.all().order_by('name')

    context = {
        'entities': entities,
        'root_entity': root_entity
    }
    return render(request, 'Consolidated/portal.html', context)


@login_required
def consolidated_income_statement(request):
    from django_ledger.models import EntityModel
    try:
        profile = request.user.djan_led_profile
        if profile.role != 'super_admin':
            return redirect('djan_led:after_login_redirect')
    except:
        return redirect('djan_led:after_login_redirect')

    root = EntityModel.objects.filter(depth=1).first()
    if not root:
        return render(request, 'Consolidated/generic_report.html', {'error': 'No root entity found.'})

    today = datetime.today()
    selected_month = int(request.GET.get('month', today.month))
    selected_year = int(request.GET.get('year', today.year))
    start_date = datetime(selected_year, selected_month, 1)
    end_date = datetime(selected_year, selected_month, monthrange(selected_year, selected_month)[1])

    entities = root.get_descendants(include_self=True)
    entity_data = []
    total_revenue = Decimal('0')
    total_expenses = Decimal('0')

    for entity in entities:
        data = get_entity_revenue_expense(entity, start_date, end_date)
        entity_data.append({
            'name': entity.name,
            'revenue': data['revenue'],
            'expenses': data['expenses'],
            'net_income': data['net_income'],
        })
        total_revenue += data['revenue']
        total_expenses += data['expenses']

    context = {
        'root_entity': root,
        'entity_data': entity_data,
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'net_income': total_revenue - total_expenses,
        'title': 'Consolidated Income Statement',
        'month_name': start_date.strftime('%B %Y'),
        'selected_month': selected_month,
        'selected_year': selected_year,
        'months': [{'value': i, 'label': f'{i:02d}'} for i in range(1, 13)],
        'years': [{'value': y, 'label': str(y)} for y in range(2022, 2031)],
    }
    return render(request, 'Consolidated/income_statement.html', context)


@login_required
def consolidated_balance_sheet(request):
    from django_ledger.models import EntityModel
    # ... similar check
    root = EntityModel.objects.filter(depth=1).first()
    context = {'root_entity': root, 'title': 'Consolidated Balance Sheet'}
    return render(request, 'Consolidated/generic_report.html', context)

@login_required
def consolidated_cash_flow(request):
    
    # ... similar
    root = EntityModel.objects.filter(depth=1).first()
    context = {'root_entity': root, 'title': 'Consolidated Cash Flow Statement'}
    return render(request, 'Consolidated/generic_report.html', context)

# @login_required
# def consolidated_trial_balance(request):
#    # ... similar
#    root = EntityModel.objects.filter(depth=1).first()
#    context = {'root_entity': root, 'title': 'Consolidated Trial Balance'}
#    return render(request, 'Consolidated/generic_report.html', context)

@login_required
def consolidated_export_pdf(request):
    pass  # implement later

@login_required
def consolidated_export_excel(request):
    pass  # implement later     

from decimal import Decimal
from datetime import datetime
from calendar import monthrange
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from django.db.models import Sum
from .utils import (get_entity_revenue_expense, get_entity_balance_sheet_balances, get_entity_cash_flow, get_entity_trial_balance)

# Helper to check super admin
def is_super_admin(user):
    from django_ledger.models import EntityModel, AccountModel, TransactionModel
    try:
        return user.djan_led_profile.role == 'super_admin'
    except:
        return False

@login_required
def super_admin_portal2(request):
    from django_ledger.models import EntityModel, AccountModel, TransactionModel
    if not is_super_admin(request.user):
        return redirect('after_login_redirect')
    entities = EntityModel.objects.all().order_by('name')
    root = EntityModel.objects.filter(depth=1).first()
    return render(request, 'Consolidated/portal.html', {'entities': entities, 'root_entity': root})

@login_required
def consolidated_dashboard(request):
    from django_ledger.models import EntityModel, AccountModel, TransactionModel
    if not is_super_admin(request.user):
        return redirect('after_login_redirect')

    root = EntityModel.objects.filter(depth=1).first()
    if not root:
        return render(request, 'Consolidated/dashboard.html', {'error': 'No root entity found.'})

    today = datetime.today()
    start_date = today.replace(day=1)
    end_date = today

    entities = root.get_descendants(include_self=True)
    total_revenue = Decimal('0')
    total_expenses = Decimal('0')
    entity_data = []

    for entity in entities:
        data = get_entity_revenue_expense(entity, start_date, end_date)
        entity_data.append({
            'name': entity.name,
            'slug': entity.slug,
            'revenue': data['revenue'],
            'expenses': data['expenses'],
            'net_income': data['net_income'],
        })
        total_revenue += data['revenue']
        total_expenses += data['expenses']

    context = {
        'root_entity': root,
        'entity_data': entity_data,
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'net_income': total_revenue - total_expenses,
        'month_name': today.strftime('%B %Y'),
    }
    return render(request, 'Consolidated/dashboard.html', context)

@login_required
def consolidated_income_statement(request):
    from django_ledger.models import EntityModel, AccountModel, TransactionModel
    if not is_super_admin(request.user):
        return redirect('after_login_redirect')

    root = EntityModel.objects.filter(depth=1).first()
    if not root:
        return render(request, 'Consolidated/generic_report.html', {'error': 'No root entity found.'})

    today = datetime.today()
    selected_month = int(request.GET.get('month', today.month))
    selected_year = int(request.GET.get('year', today.year))
    start_date = datetime(selected_year, selected_month, 1)
    end_date = datetime(selected_year, selected_month, monthrange(selected_year, selected_month)[1])

    entities = root.get_descendants(include_self=True)
    entity_data = []
    total_revenue = Decimal('0')
    total_expenses = Decimal('0')

    for entity in entities:
        data = get_entity_revenue_expense(entity, start_date, end_date)
        entity_data.append({
            'name': entity.name,
            'revenue': data['revenue'],
            'expenses': data['expenses'],
            'net_income': data['net_income'],
        })
        total_revenue += data['revenue']
        total_expenses += data['expenses']

    context = {
        'root_entity': root,
        'entity_data': entity_data,
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'net_income': total_revenue - total_expenses,
        'title': 'Consolidated Income Statement',
        'month_name': start_date.strftime('%B %Y'),
        'selected_month': selected_month,
        'selected_year': selected_year,
        'months': [{'value': i, 'label': f'{i:02d}'} for i in range(1, 13)],
        'years': [{'value': y, 'label': str(y)} for y in range(2022, 2031)],
    }
    return render(request, 'Consolidated/income_statement.html', context)

@login_required
def consolidated_balance_sheet(request):
    from django_ledger.models import EntityModel, AccountModel, TransactionModel
    if not is_super_admin(request.user):
        return redirect('after_login_redirect')

    root = EntityModel.objects.filter(depth=1).first()
    if not root:
        return render(request, 'Consolidated/generic_report.html', {'error': 'No root entity found.'})

    entities = root.get_descendants(include_self=True)
    total_assets = Decimal('0')
    total_liabilities = Decimal('0')
    total_equity = Decimal('0')
    entity_data = []

    for entity in entities:
        data = get_entity_balance_sheet_balances(entity)
        entity_data.append({
            'name': entity.name,
            'assets': data['total_assets'],
            'liabilities': data['total_liabilities'],
            'equity': data['total_equity'],
        })
        total_assets += data['total_assets']
        total_liabilities += data['total_liabilities']
        total_equity += data['total_equity']

    context = {
        'root_entity': root,
        'entity_data': entity_data,
        'total_assets': total_assets,
        'total_liabilities': total_liabilities,
        'total_equity': total_equity,
        'title': 'Consolidated Balance Sheet',
    }
    return render(request, 'Consolidated/balance_sheet.html', context)

@login_required
def consolidated_cash_flow(request):
    from django_ledger.models import EntityModel, AccountModel, TransactionModel
    if not is_super_admin(request.user):
        return redirect('after_login_redirect')

    root = EntityModel.objects.filter(depth=1).first()
    if not root:
        return render(request, 'Consolidated/generic_report.html', {'error': 'No root entity found.'})

    today = datetime.today()
    selected_month = int(request.GET.get('month', today.month))
    selected_year = int(request.GET.get('year', today.year))
    start_date = datetime(selected_year, selected_month, 1)
    end_date = datetime(selected_year, selected_month, monthrange(selected_year, selected_month)[1])

    entities = root.get_descendants(include_self=True)
    total_inflows = Decimal('0')
    total_outflows = Decimal('0')
    entity_data = []

    for entity in entities:
        data = get_entity_cash_flow(entity, start_date, end_date)
        entity_data.append({
            'name': entity.name,
            'inflows': data['inflows'],
            'outflows': data['outflows'],
            'net': data['net'],
        })
        total_inflows += data['inflows']
        total_outflows += data['outflows']

    context = {
        'root_entity': root,
        'entity_data': entity_data,
        'total_inflows': total_inflows,
        'total_outflows': total_outflows,
        'net_cash': total_inflows - total_outflows,
        'title': 'Consolidated Cash Flow Statement',
        'month_name': start_date.strftime('%B %Y'),
        'selected_month': selected_month,
        'selected_year': selected_year,
        'months': [{'value': i, 'label': f'{i:02d}'} for i in range(1, 13)],
        'years': [{'value': y, 'label': str(y)} for y in range(2022, 2031)],
    }
    return render(request, 'Consolidated/cash_flow.html', context)

@login_required
def consolidated_trial_balance(request):
    from django_ledger.models import EntityModel, AccountModel, TransactionModel
    if not is_super_admin(request.user):
        return redirect('after_login_redirect')

    root = EntityModel.objects.filter(depth=1).first()
    if not root:
        return render(request, 'Consolidated/generic_report.html', {'error': 'No root entity found.'})

    entities = root.get_descendants(include_self=True)
    all_trial = []
    # Combine trial balances from all entities (sum by account code/name)
    for entity in entities:
        trial = get_entity_trial_balance(entity)
        for row in trial:
            # Find if this account already exists in combined list
            existing = next((item for item in all_trial if item['code'] == row['code']), None)
            if existing:
                existing['debit'] += row['debit']
                existing['credit'] += row['credit']
            else:
                all_trial.append({
                    'code': row['code'],
                    'name': row['name'],
                    'debit': row['debit'],
                    'credit': row['credit'],
                })

    total_debits = sum(item['debit'] for item in all_trial)
    total_credits = sum(item['credit'] for item in all_trial)

    context = {
        'root_entity': root,
        'trial_data': all_trial,
        'total_debits': total_debits,
        'total_credits': total_credits,
        'title': 'Consolidated Trial Balance',
    }
    return render(request, 'Consolidated/trial_balance.html', context)

from decimal import Decimal
from datetime import datetime
from calendar import monthrange
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from django.db.models import Sum
from .utils import (
    get_entity_revenue_expense,
    get_entity_balance_sheet_balances,
    get_entity_cash_flow,
    get_entity_trial_balance,
)

# Helper to check super admin
def is_super_admin(user):
    try:
        return user.djan_led_profile.role == 'super_admin'
    except:
        return False

@login_required
def super_admin_portal(request):
    from django_ledger.models import EntityModel, AccountModel, TransactionModel
    if not is_super_admin(request.user):
        return redirect('Consolidate:after_login_redirect')
    entities = EntityModel.objects.all().order_by('name')
    root = EntityModel.objects.filter(depth=1).first()
    return render(request, 'Consolidated/portal.html', {'entities': entities, 'root_entity': root})

@login_required
def consolidated_dashboard(request):
    from django_ledger.models import EntityModel, AccountModel, TransactionModel
    if not is_super_admin(request.user):
        return redirect('Consolidated:after_login_redirect')

    root = EntityModel.objects.filter(depth=1).first()
    if not root:
        return render(request, 'Consolidated/dashboard.html', {'error': 'No root entity found.'})

    today = datetime.today()
    start_date = today.replace(day=1)
    end_date = today

    entities = root.get_descendants(include_self=True)
    total_revenue = Decimal('0')
    total_expenses = Decimal('0')
    entity_data = []

    for entity in entities:
        data = get_entity_revenue_expense(entity, start_date, end_date)
        entity_data.append({
            'name': entity.name,
            'slug': entity.slug,
            'revenue': data['revenue'],
            'expenses': data['expenses'],
            'net_income': data['net_income'],
        })
        total_revenue += data['revenue']
        total_expenses += data['expenses']

    context = {
        'root_entity': root,
        'entity_data': entity_data,
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'net_income': total_revenue - total_expenses,
        'month_name': today.strftime('%B %Y'),
    }
    return render(request, 'Consolidated/dashboard.html', context)

@login_required
def consolidated_income_statement(request):
    from django_ledger.models import EntityModel, AccountModel, TransactionModel
    if not is_super_admin(request.user):
        return redirect('Consolidated:after_login_redirect')

    root = EntityModel.objects.filter(depth=1).first()
    if not root:
        return render(request, 'Consolidated/consolidated_generic_report.html', {'error': 'No root entity found.'})

    today = datetime.today()
    selected_month = int(request.GET.get('month', today.month))
    selected_year = int(request.GET.get('year', today.year))
    start_date = datetime(selected_year, selected_month, 1)
    end_date = datetime(selected_year, selected_month, monthrange(selected_year, selected_month)[1])

    entities = root.get_descendants(include_self=True)
    entity_data = []
    total_revenue = Decimal('0')
    total_expenses = Decimal('0')

    for entity in entities:
        data = get_entity_revenue_expense(entity, start_date, end_date)
        entity_data.append({
            'name': entity.name,
            'revenue': data['revenue'],
            'expenses': data['expenses'],
            'net_income': data['net_income'],
        })
        total_revenue += data['revenue']
        total_expenses += data['expenses']

    context = {
        'root_entity': root,
        'entity_data': entity_data,
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'net_income': total_revenue - total_expenses,
        'title': 'Consolidated Income Statement',
        'month_name': start_date.strftime('%B %Y'),
        'selected_month': selected_month,
        'selected_year': selected_year,
        'months': [{'value': i, 'label': f'{i:02d}'} for i in range(1, 13)],
        'years': [{'value': y, 'label': str(y)} for y in range(2022, 2031)],
    }
    return render(request, 'Consolidated/consolidated_income_statement.html', context)

@login_required
def consolidated_balance_sheet(request):
    from django_ledger.models import EntityModel, AccountModel, TransactionModel
    if not is_super_admin(request.user):
        return redirect('Consolidated:after_login_redirect')

    root = EntityModel.objects.filter(depth=1).first()
    if not root:
        return render(request, 'Consolidated/consolidated_generic_report.html', {'error': 'No root entity found.'})

    entities = root.get_descendants(include_self=True)
    total_assets = Decimal('0')
    total_liabilities = Decimal('0')
    total_equity = Decimal('0')
    entity_data = []

    for entity in entities:
        data = get_entity_balance_sheet_balances(entity)
        entity_data.append({
            'name': entity.name,
            'assets': data['total_assets'],
            'liabilities': data['total_liabilities'],
            'equity': data['total_equity'],
        })
        total_assets += data['total_assets']
        total_liabilities += data['total_liabilities']
        total_equity += data['total_equity']

    context = {
        'root_entity': root,
        'entity_data': entity_data,
        'total_assets': total_assets,
        'total_liabilities': total_liabilities,
        'total_equity': total_equity,
        'title': 'Consolidated Balance Sheet',
    }
    return render(request, 'Consolidated/consolidated_balance_sheet.html', context)

@login_required
def consolidated_cash_flow(request):
    from django_ledger.models import EntityModel, AccountModel, TransactionModel
    if not is_super_admin(request.user):
        return redirect('Consolidated:after_login_redirect')

    root = EntityModel.objects.filter(depth=1).first()
    if not root:
        return render(request, 'Consolidated/consolidated_generic_report.html', {'error': 'No root entity found.'})

    today = datetime.today()
    selected_month = int(request.GET.get('month', today.month))
    selected_year = int(request.GET.get('year', today.year))
    start_date = datetime(selected_year, selected_month, 1)
    end_date = datetime(selected_year, selected_month, monthrange(selected_year, selected_month)[1])

    entities = root.get_descendants(include_self=True)
    total_inflows = Decimal('0')
    total_outflows = Decimal('0')
    entity_data = []

    for entity in entities:
        data = get_entity_cash_flow(entity, start_date, end_date)
        entity_data.append({
            'name': entity.name,
            'inflows': data['inflows'],
            'outflows': data['outflows'],
            'net': data['net'],
        })
        total_inflows += data['inflows']
        total_outflows += data['outflows']

    context = {
        'root_entity': root,
        'entity_data': entity_data,
        'total_inflows': total_inflows,
        'total_outflows': total_outflows,
        'net_cash': total_inflows - total_outflows,
        'title': 'Consolidated Cash Flow Statement',
        'month_name': start_date.strftime('%B %Y'),
        'selected_month': selected_month,
        'selected_year': selected_year,
        'months': [{'value': i, 'label': f'{i:02d}'} for i in range(1, 13)],
        'years': [{'value': y, 'label': str(y)} for y in range(2022, 2031)],
    }
    return render(request, 'Consolidated/consolidated_cash_flow.html', context)

@login_required
def consolidated_trial_balance(request):
    from django_ledger.models import EntityModel, AccountModel, TransactionModel
    if not is_super_admin(request.user):
        return redirect('Consolidated:after_login_redirect')

    root = EntityModel.objects.filter(depth=1).first()
    if not root:
        return render(request, 'Consolidated/generic_report.html', {'error': 'No root entity found.'})

    entities = root.get_descendants(include_self=True)
    all_trial = []
    # Combine trial balances from all entities (sum by account code/name)
    for entity in entities:
        trial = get_entity_trial_balance(entity)
        for row in trial:
            # Find if this account already exists in combined list
            existing = next((item for item in all_trial if item['code'] == row['code']), None)
            if existing:
                existing['debit'] += row['debit']
                existing['credit'] += row['credit']
            else:
                all_trial.append({
                    'code': row['code'],
                    'name': row['name'],
                    'debit': row['debit'],
                    'credit': row['credit'],
                })

    total_debits = sum(item['debit'] for item in all_trial)
    total_credits = sum(item['credit'] for item in all_trial)

    context = {
        'root_entity': root,
        'trial_data': all_trial,
        'total_debits': total_debits,
        'total_credits': total_credits,
        'title': 'Consolidated Trial Balance',
    }
    return render(request, 'Consolidated/consolidated_trial_balance.html', context)
