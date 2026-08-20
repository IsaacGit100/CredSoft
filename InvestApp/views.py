from django.shortcuts import render
from . import views

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Sum, Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# InvestApp/views.py
from django.db.models import Q, Sum
from django.utils import timezone
from decimal import Decimal

from .models import Investment, Bank
from .forms import InvestmentForm, BankForm
from django_ledger.models import EntityModel


@login_required
def invest_home(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    return render(request, "InvestApp/invest_home.html", {"entity": entity})

@login_required
def invest_update_list(request, slug):
    investments = Investment.objects.all().order_by('-date')
    return render(request, 'invest_update_list.html')

@login_required
def investment_list(request, slug):
    investments = Investment.objects.all().order_by('-date')
    today = timezone.now().date()

    # ---------- Status Filter ----------
    status_filter = request.GET.get('status_filter', 'all')
    
    if status_filter == 'active':
        # Active = not discounted, not written off, and maturity_date > today
        investments = investments.filter(
            discounted=False, 
            written_off=False, 
            maturity_date__gt=today
        )
    elif status_filter == 'matured_not_earned':
        # Matured by date, but interest_earned is 0 or None
        investments = investments.filter(
            maturity_date__lte=today, 
            interest_earned=0
        )
    elif status_filter == 'matured_earned':
        investments = investments.filter(
            maturity_date__lte=today, 
            interest_earned__gt=0
        )
    elif status_filter == 'discounted':
        investments = investments.filter(discounted=True)
    elif status_filter == 'written_off':
        investments = investments.filter(written_off=True)
    # else 'all' – no filter

    # ---------- Search Filter ----------
    search_query = request.GET.get('search', '')
    if search_query:
        investments = investments.filter(
            Q(certificate_no__icontains=search_query) |
            Q(bank__icontains=search_query) |
            Q(other_company__icontains=search_query) |
            Q(branch__icontains=search_query)
        )

    # ---------- Totals (based on filtered queryset) ----------
    total_invested = investments.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    total_interest_expected = investments.aggregate(Sum('interest_expected'))['interest_expected__sum'] or Decimal('0')
    total_interest_earned = investments.aggregate(Sum('interest_earned'))['interest_earned__sum'] or Decimal('0')

    # ---------- Summary counts (based on ALL investments, not filtered) ----------
    all_investments = Investment.objects.all()
    active_investments = all_investments.filter(
        discounted=False, written_off=False, maturity_date__gt=today
    ).count()
    matured_investments = all_investments.filter(maturity_date__lte=today).count()
    total_investments = all_investments.count()

    context = {
        'investments': investments,
        'status_filter': status_filter,
        'search_query': search_query,
        'total_invested': total_invested,
        'total_interest_expected': total_interest_expected,
        'total_interest_earned': total_interest_earned,
        'active_investments': active_investments,
        'matured_investments': matured_investments,
        'total_investments': total_investments,
    }
    return render(request, 'InvestApp/investment_list.html', context)

@login_required
def investment_create(request, slug):
    if request.method == 'POST':
        form = InvestmentForm(request.POST)
        if form.is_valid():
            investment = form.save()
            messages.success(request, 'Investment created successfully!')
            return redirect('InvestApp:investment_list')
    else:
        form = InvestmentForm()

    banks = Bank.objects.all()
    return render(request, 'InvestApp/investment_form.html', {'form': form, 'banks': banks, 'title': 'Add New Investment'})

@login_required
def investment_update(request, slug, pk):
    investment = get_object_or_404(Investment, pk=pk)
    if request.method == 'POST':
        form = InvestmentForm(request.POST, instance=investment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Investment updated successfully!')
            return redirect('InvestApp:investment_list')
    else:
        form = InvestmentForm(instance=investment)

    banks = Bank.objects.all()
    return render(request, 'InvestApp/investment_form.html', {'form': form, 'banks': banks, 'title': 'Edit Investment'})

@login_required
def investment_delete(request, slug, pk):
    investment = get_object_or_404(Investment, pk=pk)
    if request.method == 'POST':
        investment.delete()
        messages.success(request, 'Investment deleted successfully!')
        return redirect('InvestApp:investment_list')

    return render(request, 'InvestApp/investment_confirm_delete.html', {'investment': investment})

@login_required
def bank_list(request, slug):
    banks = Bank.objects.all()
    return render(request, 'InvestApp/bank_list.html', {'banks': banks})

@login_required
def bank_create(request, slug):
    if request.method == 'POST':
        form = BankForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bank created successfully!')
            return redirect('InvestApp:bank_list')
    else:
        form = BankForm()

    return render(request, 'InvestApp/bank_form.html', {'form': form, 'title': 'Add New Bank'})

@login_required
def bank_update(request, slug, pk):
    bank = get_object_or_404(Bank, pk=pk)
    if request.method == 'POST':
        form = BankForm(request.POST, instance=bank)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bank updated successfully!')
            return redirect('InvestApp:bank_list', entity.slug)
    else:
        form = BankForm(instance=bank)

    return render(request, 'InvestApp/bank_form.html', {'form': form, 'title': 'Edit Bank'})

@login_required
def bank_delete(request, slug, pk):
    bank = get_object_or_404(Bank, pk=pk)
    if request.method == 'POST':
        bank.delete()
        messages.success(request, 'Bank deleted successfully!')
        return redirect('InvestApp:bank_list',  entity.slug)

    return render(request, 'InvestApp/bank_confirm_delete.html', {'bank': bank})

@login_required
def calculate_interest(request, slug):
    if request.method == 'POST' and request.is_ajax():
        amount = float(request.POST.get('amount', 0))
        rate = float(request.POST.get('rate', 0))
        term_days = int(request.POST.get('term_days', 0))

        interest_expected = (amount * rate * term_days) / (100 * 365)
        return JsonResponse({'interest_expected': round(interest_expected, 2)})

    return JsonResponse({'error': 'Invalid request'})


# views.py
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Bank
from .forms import BankForm

@login_required
class BankListView(ListView):
    model = Bank
    template_name = 'bank_list.html'
    context_object_name = 'banks'

@login_required
class BankCreateView(CreateView):
    model = Bank
    form_class = BankForm
    template_name = 'bank_form.html'
    success_url = reverse_lazy('bank_list')

@login_required
class BankUpdateView(UpdateView):
    model = Bank
    form_class = BankForm
    template_name = 'bank_form.html'
    success_url = reverse_lazy('bank_list')

@login_required
class BankDeleteView(DeleteView):
    model = Bank
    template_name = 'bank_confirm_delete.html'
    success_url = reverse_lazy('bank_list')


# views.py
from .models import Investment

@login_required
def get_filtered_investments(request, slug):
    investments = Investment.objects.all()

    # Apply interest filter
    interest_filter = request.GET.get('interest_filter', 'all')
    if interest_filter == 'positive':
        investments = investments.filter(interest_earned__gt=0)

    # Apply search filter
    search_query = request.GET.get('search', '')
    if search_query:
        investments = investments.filter(
            Q(certificate_no__icontains=search_query) |
            Q(bank_company__icontains=search_query) |
            Q(branch__icontains=search_query)
        )

    return investments


# views.py
from django.shortcuts import render

@login_required
def export_investments_print(request, slug):
    # Get filtered data and totals (same as your main view)
    investments = get_filtered_investments(request)
    total_invested = sum(inv.amount for inv in investments)
    total_interest_expected = sum(inv.interest_expected for inv in investments)
    total_interest_earned = sum(inv.interest_earned for inv in investments)

    context = {
        'investments': investments,
        'total_invested': total_invested,
        'total_interest_expected': total_interest_expected,
        'total_interest_earned': total_interest_earned,
    }
    
    return render(request, 'InvestApp/investment_print.html', context)


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Q
from .models import Investment
from .forms import InvestmentStatusUpdateForm   # we'll create this form

@login_required
def investment_status_update(request, slug, pk=None):
    # If a specific investment is selected, show update form for that one
    if pk:
        investment = get_object_or_404(Investment, pk=pk)
        form = InvestmentStatusUpdateForm(instance=investment)
        if request.method == 'POST':
            form = InvestmentStatusUpdateForm(request.POST, instance=investment)
            if form.is_valid():
                form.save()
                messages.success(request, f'Investment {investment.certificate_no} status updated.')
                return redirect('InvestApp:investment_status_update')
            else:
                messages.error(request, 'Please correct the errors below.')
        context = {'form': form, 'investment': investment}
        return render(request, 'InvestApp/status_update_form.html', context)

    # Otherwise, show searchable list of investments
    search_query = request.GET.get('search', '')
    investments = Investment.objects.all().order_by('-date')
    if search_query:
        investments = investments.filter(
            Q(certificate_no__icontains=search_query) |
            Q(bank_company__icontains=search_query) |
            Q(branch__icontains=search_query)
        )
    context = {
        'investments': investments,
        'search_query': search_query,
    }
    return render(request, 'InvestApp/status_update_list.html', context)

from django.db.models import Sum, Q
from decimal import Decimal
@login_required
def quarterly_investment_report(request, slug):
    year = 2026  # or get from request.GET
    quarters = [
        {'name': 'Jan – Mar', 'months': (1, 2, 3), 'start': f'{year}-01-01', 'end': f'{year}-03-31'},
        {'name': 'Apr – Jun', 'months': (4, 5, 6), 'start': f'{year}-04-01', 'end': f'{year}-06-30'},
        {'name': 'Jul – Sep', 'months': (7, 8, 9), 'start': f'{year}-07-01', 'end': f'{year}-09-30'},
        {'name': 'Oct – Dec', 'months': (10, 11, 12), 'start': f'{year}-10-01', 'end': f'{year}-12-31'},
    ]
    
    quarterly_data = []
    for q in quarters:
        investments = Investment.objects.filter(
            maturity_date__range=[q['start'], q['end']]
        ).order_by('maturity_date')
        
        total_expected = investments.aggregate(Sum('interest_expected'))['interest_expected__sum'] or Decimal('0')
        total_earned = investments.aggregate(Sum('interest_earned'))['interest_earned__sum'] or Decimal('0')
        
        quarterly_data.append({
            'name': q['name'],
            'investments': investments,
            'total_expected': total_expected,
            'total_earned': total_earned,
            'count': investments.count(),
        })
    
    context = {
        'year': year,
        'quarterly_data': quarterly_data,
        'grand_total_expected': sum(q['total_expected'] for q in quarterly_data),
        'grand_total_earned': sum(q['total_earned'] for q in quarterly_data),
        'total_investments': sum(q['count'] for q in quarterly_data),
    }
    return render(request, 'InvestApp/invest_quarterly_report.html', context)
