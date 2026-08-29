# RecPayApp/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from django.http import JsonResponse
from django.core.paginator import Paginator
from decimal import Decimal
from datetime import datetime
from .models import Trans
from MembersApp.models import Master
from coa.models import ChartOfAccounts
from LoanApp.models import Loan

@login_required
def trans_create(request):
    """Transaction creation with AJAX - no page reload"""
    
    # Get members and accounts
    members = Master.objects.filter(is_deleted=False).order_by('last_name', 'first_name')
    accounts = ChartOfAccounts.objects.filter(
        is_active=True,
        is_data_entry=True,
        is_data_view=True
    ).order_by('accountno')
    
    # IMPORTANT: Do NOT slice before filtering for statistics
    # Get base queryset for statistics
    all_transactions = Trans.objects.all()
    
    # Get recent transactions for display (slice only here)
    recent_transactions = Trans.objects.all().order_by('-date', '-id')[:50]
    
    # Calculate statistics using the base queryset (not sliced)
    receipts = all_transactions.filter(trans_type='Receipts')
    payments = all_transactions.filter(trans_type='Payments')
    
    context = {
        'members': members,
        'accounts': accounts,
        'transactions': recent_transactions,
        'receipts_count': receipts.count(),
        'payments_count': payments.count(),
        'receipts_total': receipts.aggregate(total=models.Sum('amount'))['total'] or Decimal('0'),
        'payments_total': payments.aggregate(total=models.Sum('amount'))['total'] or Decimal('0'),
        'total_records': all_transactions.count(),
        'today': datetime.now(),
    }
    return render(request, 'RecPayApp/trans_create.html', context)


@login_required
def trans_list(request):
    """Transaction list with pagination"""
    
    transactions = Trans.objects.all().order_by('-date', '-id')
    
    # Filters
    trans_type = request.GET.get('type')
    if trans_type:
        transactions = transactions.filter(trans_type=trans_type)
    
    status = request.GET.get('status')
    if status:
        transactions = transactions.filter(status=status)
    
    paginator = Paginator(transactions, 50)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    
    context = {
        'transactions': page_obj,
    }
    return render(request, 'RecPayApp/trans_list.html', context)


@login_required
def trans_detail(request, pk):
    """View transaction details"""
    
    transaction = get_object_or_404(Trans, pk=pk)
    
    context = {
        'transaction': transaction,
    }
    return render(request, 'RecPayApp/trans_detail.html', context)


@login_required
def trans_edit(request, pk):
    """Edit transaction"""
    
    transaction = get_object_or_404(Trans, pk=pk)
    
    if request.method == 'POST':
        transaction.amount = Decimal(request.POST.get('amount', 0))
        transaction.details = request.POST.get('details', '')
        transaction.save()
        messages.success(request, "Transaction updated successfully!")
        return redirect('RecPayApp:trans_detail', pk=transaction.pk)
    
    context = {
        'transaction': transaction,
    }
    return render(request, 'RecPayApp/trans_edit.html', context)


@login_required
def trans_delete(request, pk):
    """Delete transaction"""
    
    transaction = get_object_or_404(Trans, pk=pk)
    
    if request.method == 'POST':
        transaction.delete()
        messages.success(request, "Transaction deleted successfully!")
        return redirect('RecPayApp:trans_list')
    
    context = {
        'transaction': transaction,
    }
    return render(request, 'RecPayApp/trans_confirm_delete.html', context)


# ==================== API ENDPOINTS ====================

@login_required
def api_member_loans(request, member_id):
    """AJAX endpoint to get member's active loans"""
    
    try:
        member = Master.objects.get(id=member_id)
        loans = Loan.objects.filter(
            master=member,
            status__in=['Active', 'New Loan']
        ).values('id', 'loan_id', 'principal', 'balance')
        
        loan_list = []
        for loan in loans:
            loan_list.append({
                'id': loan['id'],
                'loan_id': loan['loan_id'],
                'principal': float(loan['principal']),
                'balance': float(loan['balance']),
            })
        
        return JsonResponse({
            'success': True,
            'member_name': member.full_name,
            'member_balance': float(member.available_balance),
            'loans': loan_list
        })
    except Master.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Member not found'}, status=404)


@login_required
def api_member_info(request, member_id):
    """AJAX endpoint to get member information"""
    
    try:
        member = Master.objects.get(id=member_id)
        return JsonResponse({
            'success': True,
            'id': member.id,
            'name': member.full_name,
            'balance': float(member.available_balance),
            'phone': member.telephone1,
            'email': member.email_address,
        })
    except Master.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Member not found'}, status=404)