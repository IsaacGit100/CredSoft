# coa/views_visibility.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from .models import ChartOfAccounts

@login_required
def account_visibility_manager1(request):
    """Manage which accounts appear in transaction forms"""
    
    # Get all data entry accounts
    all_accounts = ChartOfAccounts.objects.filter(
        is_active=True,
        is_data_entry=True
    ).select_related('parent_account').order_by('accountno')
    
    # Build account list with current visibility
    accounts_with_visibility = []
    for account in all_accounts:
        accounts_with_visibility.append({
            'id': account.id,
            'accountno': account.accountno,
            'name': account.name,
            'account_type': account.get_account_type_display(),
            'behavior': account.get_behavior_display(),
            'parent_name': account.parent_account.name if account.parent_account else '-',
            'is_visible': account.is_data_view,
            'formatted_no': f"{account.accountno[0]}-{account.accountno[1:3]}-{account.accountno[3:5]}-{account.accountno[5:8]}"
        })
    
    # Group by account type
    grouped_accounts = {}
    for acc in accounts_with_visibility:
        acc_type = acc['account_type']
        if acc_type not in grouped_accounts:
            grouped_accounts[acc_type] = []
        grouped_accounts[acc_type].append(acc)
    
    # Statistics
    total_accounts = len(accounts_with_visibility)
    visible_count = sum(1 for acc in accounts_with_visibility if acc['is_visible'])
    hidden_count = total_accounts - visible_count
    
    context = {
        'grouped_accounts': grouped_accounts,
        'total_accounts': total_accounts,
        'visible_count': visible_count,
        'hidden_count': hidden_count,
    }
    return render(request, 'coa/account_visibility_manager.html', context)

@login_required
@transaction.atomic
def save_account_visibility1(request):
    """Save account visibility preferences - UPDATES is_data_view FIELD"""
    
    if request.method == 'POST':
        # Get all checked account IDs from form
        checked_accounts = request.POST.getlist('visible_accounts[]')
        checked_ids = set(int(id) for id in checked_accounts if id)
        
        # Get all data entry accounts
        all_accounts = ChartOfAccounts.objects.filter(
            is_active=True,
            is_data_entry=True
        )
        
        # Update is_data_view field for each account
        updated_count = 0
        for account in all_accounts:
            should_be_visible = account.id in checked_ids
            
            if account.is_data_view != should_be_visible:
                account.is_data_view = should_be_visible
                account.save()
                updated_count += 1
        
        messages.success(request, f'Updated {updated_count} account(s). {len(checked_ids)} account(s) now visible.')
        return redirect('coa:account_visibility_manager')
    
    return redirect('coa:account_visibility_manager')

@login_required
def reset_account_visibility1(request):
    """Reset all accounts to visible"""
    
    if request.method == 'POST':
        # Set all data entry accounts to visible
        updated = ChartOfAccounts.objects.filter(
            is_active=True,
            is_data_entry=True
        ).update(is_data_view=True)
        
        messages.success(request, f'Reset {updated} accounts to visible.')
        return redirect('coa:account_visibility_manager')
    
    return redirect('coa:account_visibility_manager')

@login_required
def get_visible_accounts_api1(request):
    """API endpoint to get visible accounts for transaction forms"""
    
    # Get accounts that are visible
    visible_accounts = ChartOfAccounts.objects.filter(
        is_active=True,
        is_data_entry=True,
        is_data_view=True  # Only accounts marked as visible
    ).order_by('accountno')
    
    # Format the response
    result = []
    for account in visible_accounts:
        # Format account number with hyphens for display
        if len(account.accountno) == 8:
            formatted_no = f"{account.accountno[0]}-{account.accountno[1:3]}-{account.accountno[3:5]}-{account.accountno[5:8]}"
        else:
            formatted_no = account.accountno
        
        result.append({
            'id': account.id,
            'accountno': account.accountno,
            'formatted_no': formatted_no,
            'name': account.name,
            'account_type': account.account_type,
            'behavior': account.behavior,
            'type_display': account.get_account_type_display(),
            'behavior_display': account.get_behavior_display(),
        })
    
    return JsonResponse({
        'success': True,
        'count': len(result),
        'accounts': result
    })
    
# coa/views_visibility.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from .models import ChartOfAccounts

@login_required
def account_visibility_manager(request):
    """Manage which accounts appear in transaction forms"""
    
    # Get all data entry accounts
    all_accounts = ChartOfAccounts.objects.filter(
        is_active=True,
        is_data_entry=True
    ).select_related('parent_account').order_by('accountno')
    
    # Build account list with current visibility
    accounts_with_visibility = []
    for account in all_accounts:
        accounts_with_visibility.append({
            'id': account.id,
            'accountno': account.accountno,
            'name': account.name,
            'account_type': account.get_account_type_display(),
            'behavior': account.get_behavior_display(),
            'parent_name': account.parent_account.name if account.parent_account else '-',
            'is_visible': account.is_data_view,
            'formatted_no': format_account_number(account.accountno)
        })
    
    # Group by account type
    grouped_accounts = {}
    for acc in accounts_with_visibility:
        acc_type = acc['account_type']
        if acc_type not in grouped_accounts:
            grouped_accounts[acc_type] = []
        grouped_accounts[acc_type].append(acc)
    
    # Statistics
    total_accounts = len(accounts_with_visibility)
    visible_count = sum(1 for acc in accounts_with_visibility if acc['is_visible'])
    hidden_count = total_accounts - visible_count
    
    context = {
        'grouped_accounts': grouped_accounts,
        'total_accounts': total_accounts,
        'visible_count': visible_count,
        'hidden_count': hidden_count,
    }
    return render(request, 'coa/account_visibility_manager.html', context)


@login_required
@transaction.atomic
def save_account_visibility(request):
    """Save account visibility preferences"""
    
    if request.method == 'POST':
        # Get all checked account IDs from form
        checked_accounts = request.POST.getlist('visible_accounts[]')
        checked_ids = set(int(id) for id in checked_accounts if id)
        
        # Get all data entry accounts
        all_accounts = ChartOfAccounts.objects.filter(
            is_active=True,
            is_data_entry=True
        )
        
        # Update is_data_view field for each account
        updated_count = 0
        for account in all_accounts:
            should_be_visible = account.id in checked_ids
            
            if account.is_data_view != should_be_visible:
                account.is_data_view = should_be_visible
                account.save()
                updated_count += 1
        
        messages.success(request, f'✅ Updated {updated_count} account(s). {len(checked_ids)} account(s) now visible.')
        return redirect('coa:account_visibility_manager')
    
    return redirect('coa:account_visibility_manager')


@login_required
def refresh_account_visibility(request):
    """Refresh account visibility - clear cache and reload"""
    
    if request.method == 'POST':
        # Just a refresh action - no actual changes needed
        messages.success(request, '🔄 Account visibility settings have been refreshed!')
        return redirect('coa:account_visibility_manager')
    
    return redirect('coa:account_visibility_manager')


@login_required
def reset_account_visibility(request):
    """Reset all accounts to visible"""
    
    if request.method == 'POST':
        # Set all data entry accounts to visible
        updated = ChartOfAccounts.objects.filter(
            is_active=True,
            is_data_entry=True
        ).update(is_data_view=True)
        
        messages.success(request, f'✅ Reset {updated} accounts to visible.')
        return redirect('coa:account_visibility_manager')
    
    return redirect('coa:account_visibility_manager')


def format_account_number(accountno):
    """Format 8-digit account number to X-XX-XX-XXX format"""
    if len(accountno) == 8:
        return f"{accountno[0]}-{accountno[1:3]}-{accountno[3:5]}-{accountno[5:8]}"
    return accountno


@login_required
def get_visible_accounts_api(request):
    """API endpoint to get visible accounts for transaction forms"""
    
    # Get accounts that are visible
    visible_accounts = ChartOfAccounts.objects.filter(
        is_active=True,
        is_data_entry=True,
        is_data_view=True
    ).order_by('accountno')
    
    result = []
    for account in visible_accounts:
        if len(account.accountno) == 8:
            formatted_no = f"{account.accountno[0]}-{account.accountno[1:3]}-{account.accountno[3:5]}-{account.accountno[5:8]}"
        else:
            formatted_no = account.accountno
        
        result.append({
            'id': account.id,
            'accountno': account.accountno,
            'formatted_no': formatted_no,
            'name': account.name,
            'account_type': account.account_type,
            'behavior': account.behavior,
            'type_display': account.get_account_type_display(),
            'behavior_display': account.get_behavior_display(),
        })
    
    return JsonResponse({
        'success': True,
        'count': len(result),
        'accounts': result
    })