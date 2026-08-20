from django.shortcuts import render

# Create your views here.
# views.py (create a main dashboard view - you can put this in any app)
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone


@login_required
def dashboard(request):
    """Main Dashboard / Home Page after login"""
    
    # Get user role and permissions
    user = request.user
    role = user.profile.role if hasattr(user, 'profile') else 'VIEWER'
    
    # Get statistics for dashboard cards (optional)
  #  from MembersApp.models import Master
  #  from QuickLoanApp.models import Loan
  #  from RecPayApp.models import Trans
    
    context = {
        'user': user,
        'role': role,
        'role_display': user.profile.get_role_display() if hasattr(user, 'profile') else 'User',
        'today': timezone.now(),
    
    }
    
    return render(request, 'dashboard.html', context)
  
# SysSetup/views.py
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .models import SystemSettings


@staff_member_required
def system_settings_edit(request):
    """Edit system settings (admin only)"""
    settings = SystemSettings.objects.first()
    
    if request.method == 'POST':
        # Company Information
        settings.company_name = request.POST.get('company_name')
        settings.company_short_name = request.POST.get('company_short_name')
        settings.company_address = request.POST.get('company_address')
        settings.company_city = request.POST.get('company_city')
        settings.company_region = request.POST.get('company_region')
        settings.company_country = request.POST.get('company_country')
        settings.company_phone = request.POST.get('company_phone')
        settings.company_email = request.POST.get('company_email')
        
        # Financial Settings
        settings.currency = request.POST.get('currency')
        settings.currency_symbol = request.POST.get('currency_symbol')
        settings.date_format = request.POST.get('date_format')
        
        # Loan Settings
        settings.default_interest_rate = request.POST.get('default_interest_rate')
        settings.default_loan_term = request.POST.get('default_loan_term')
        
        settings.save()
        
        messages.success(request, "System settings updated successfully!")
        return redirect('SysSetup:settings_edit')
    
    context = {
        'settings': settings,
        'date_formats': ['dd/mm/yyyy', 'mm/dd/yyyy', 'yyyy-mm-dd'],
        'currencies': [('GHS', 'Ghana Cedis'), ('USD', 'US Dollar'), ('EUR', 'Euro')],
    }
    return render(request, 'SysSetup/settings_edit.html', context)



# SysSetup/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from .models import SystemSettings, SystemPreference, FiscalPeriod, AuditLog
from .forms import SystemSettingsForm, SystemPreferenceForm, FiscalPeriodForm


@login_required
@staff_member_required
def company_setup1(request):
    """Company/Institution setup form"""
    
    # Get or create system settings (only one record exists)
    settings = SystemSettings.objects.first()
    if not settings:
        settings = SystemSettings.objects.create()
    
    if request.method == 'POST':
        form = SystemSettingsForm(request.POST, request.FILES, instance=settings)
        if form.is_valid():
            system = form.save(commit=False)
            system.updated_by = request.user
            system.save()
            
            # Log the action
            AuditLog.objects.create(
                user=request.user,
                action='UPDATE',
                model_name='SystemSettings',
                description=f"Updated system settings"
            )
            
            messages.success(request, 'Company settings updated successfully!')
            return redirect('SysSetup:company_setup')
    else:
        form = SystemSettingsForm(instance=settings)
    
    context = {
        'form': form,
        'settings': settings,
        'title': 'Company Setup',
    }
    return render(request, 'SysSetup/company_setup.html', context)


@login_required
def user_preferences(request):
    """User preferences setup"""
    
    preference, created = SystemPreference.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = SystemPreferenceForm(request.POST, instance=preference)
        if form.is_valid():
            form.save()
            messages.success(request, 'Preferences saved successfully!')
            return redirect('SysSetup:user_preferences')
    else:
        form = SystemPreferenceForm(instance=preference)
    
    context = {
        'form': form,
        'title': 'User Preferences',
    }
    return render(request, 'SysSetup/user_preferences.html', context)


@login_required
@staff_member_required
def fiscal_periods(request):
    """Manage fiscal periods"""
    
    periods = FiscalPeriod.objects.all().order_by('-start_date')
    
    if request.method == 'POST':
        form = FiscalPeriodForm(request.POST)
        if form.is_valid():
            period = form.save()
            messages.success(request, f'Fiscal period {period.name} created!')
            return redirect('SysSetup:fiscal_periods')
    else:
        form = FiscalPeriodForm()
    
    # Pagination
    paginator = Paginator(periods, 20)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    
    context = {
        'periods': page_obj,
        'form': form,
        'title': 'Fiscal Periods',
    }
    return render(request, 'SysSetup/fiscal_periods.html', context)


@login_required
@staff_member_required
def edit_fiscal_period(request, pk):
    """Edit a fiscal period"""
    
    period = get_object_or_404(FiscalPeriod, pk=pk)
    
    if request.method == 'POST':
        form = FiscalPeriodForm(request.POST, instance=period)
        if form.is_valid():
            form.save()
            messages.success(request, f'Fiscal period {period.name} updated!')
            return redirect('SysSetup:fiscal_periods')
    else:
        form = FiscalPeriodForm(instance=period)
    
    context = {
        'form': form,
        'period': period,
        'title': 'Edit Fiscal Period',
    }
    return render(request, 'SysSetup/fiscal_period_edit.html', context)


@login_required
@staff_member_required
def close_fiscal_period(request, pk):
    """Close a fiscal period"""
    
    period = get_object_or_404(FiscalPeriod, pk=pk)
    
    if request.method == 'POST':
        period.status = 'CLOSED'
        period.closed_by = request.user
        period.closed_at = timezone.now()
        period.save()
        
        messages.success(request, f'Period {period.name} closed successfully!')
        return redirect('SysSetup:fiscal_periods')
    
    context = {'period': period}
    return render(request, 'SysSetup/close_period_confirm.html', context)


@login_required
def system_dashboard(request):
    """System setup dashboard"""
    
    settings = SystemSettings.objects.first()
    fiscal_periods = FiscalPeriod.objects.all().order_by('-start_date')[:5]
    recent_audits = AuditLog.objects.all()[:10]
    
    context = {
        'settings': settings,
        'fiscal_periods': fiscal_periods,
        'recent_audits': recent_audits,
        'today': timezone.now(),
    }
    return render(request, 'SysSetup/system_dashboard.html', context)

# SysSetup/views.py - Update company_setup view
from coa.models import ChartOfAccounts

@login_required
@staff_member_required
def company_setup(request):
    """Company/Institution setup form"""
    
    # Get or create system settings
    settings = SystemSettings.objects.first()
    if not settings:
        settings = SystemSettings.objects.create()
    
    # Get Chart of Accounts statistics
    recent_accounts = ChartOfAccounts.objects.filter(is_active=True).order_by('-id')[:10]
    asset_count = ChartOfAccounts.objects.filter(account_type='ASSET', is_active=True).count()
    liability_count = ChartOfAccounts.objects.filter(account_type='LIABILITY', is_active=True).count()
    equity_count = ChartOfAccounts.objects.filter(account_type='EQUITY', is_active=True).count()
    income_count = ChartOfAccounts.objects.filter(account_type='INCOME', is_active=True).count()
    expense_count = ChartOfAccounts.objects.filter(account_type='EXPENSE', is_active=True).count()
    
    if request.method == 'POST':
        print("POST data:", request.POST)
        form = SystemSettingsForm(request.POST, request.FILES, instance=settings)
        if form.is_valid():
            system = form.save(commit=False)
            system.updated_by = request.user
            system.save()
            
            AuditLog.objects.create(
                user=request.user,
                action='UPDATE',
                model_name='SystemSettings',
                description=f"Updated system settings"
            )
            
            messages.success(request, 'Company settings updated successfully!')
            return redirect('SysSetup:company_setup')
        else:
            print("Form errors:", form.errors)
    else:
        form = SystemSettingsForm(instance=settings)
    
    context = {
        'form': form,
        'settings': settings,
        'recent_accounts': recent_accounts,
        'asset_count': asset_count,
        'liability_count': liability_count,
        'equity_count': equity_count,
        'income_count': income_count,
        'expense_count': expense_count,
        'title': 'Company Setup',
    }
    return render(request, 'SysSetup/company_setup.html', context)