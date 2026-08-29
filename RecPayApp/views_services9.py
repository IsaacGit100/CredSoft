from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum, Q
from decimal import Decimal
from .models import Trans
from MembersApp.models import Master

@login_required
def transaction_list(request):
    """
    Display all transactions with filtering and pagination
    """
    
    # ============================================
    # Get all transactions, newest first
    # ============================================
    transactions = Trans.objects.select_related('member', 'loan').order_by('-date', '-id')
    
    # ============================================
    # Apply filters
    # ============================================
    
    # Filter by transaction type
    trans_type = request.GET.get('trans_type')
    if trans_type:
        transactions = transactions.filter(trans_type=trans_type)
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        transactions = transactions.filter(status=status)
    
    # Filter by date range
    from_date = request.GET.get('from_date')
    if from_date:
        transactions = transactions.filter(date__gte=from_date)
    
    to_date = request.GET.get('to_date')
    if to_date:
        transactions = transactions.filter(date__lte=to_date)
    
    # Filter by member
    member_id = request.GET.get('member_id')
    if member_id:
        transactions = transactions.filter(member_id=member_id)
    
    # Filter by voucher number
    voucher = request.GET.get('voucher')
    if voucher:
        transactions = transactions.filter(rec_vou_no__icontains=voucher)
    
    # ============================================
    # Calculate summary statistics
    # ============================================
    
    summary = {
        'total_count': transactions.count(),
        'total_amount': transactions.aggregate(total=Sum('amount'))['total'] or Decimal('0.00'),
        'receipts_count': transactions.filter(trans_type='Receipts').count(),
        'receipts_total': transactions.filter(trans_type='Receipts').aggregate(total=Sum('amount'))['total'] or Decimal('0.00'),
        'payments_count': transactions.filter(trans_type='Payments').count(),
        'payments_total': transactions.filter(trans_type='Payments').aggregate(total=Sum('amount'))['total'] or Decimal('0.00'),
        'draft_count': transactions.filter(status='DRAFT').count(),
        'draft_total': transactions.filter(status='DRAFT').aggregate(total=Sum('amount'))['total'] or Decimal('0.00'),
        'posted_count': transactions.filter(status='POSTED').count(),
        'posted_total': transactions.filter(status='POSTED').aggregate(total=Sum('amount'))['total'] or Decimal('0.00'),
    }
    
    # ============================================
    # Pagination (50 per page)
    # ============================================
    
    paginator = Paginator(transactions, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # ============================================
    # Get members for filter dropdown
    # ============================================
    
    members = Master.objects.filter(is_deleted=False).order_by('first_name', 'last_name')[:100]
    
    # ============================================
    # Context for template
    # ============================================
    
    context = {
        'transactions': page_obj,
        'summary': summary,
        'members': members,
        'filters': {
            'trans_type': trans_type,
            'status': status,
            'from_date': from_date,
            'to_date': to_date,
            'member_id': member_id,
            'voucher': voucher,
        },
        'total_count': transactions.count(),
    }
    
    return render(request, 'RecPayApp/transaction_list.html', context)

# RecPayApp/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from decimal import Decimal

from RecPayApp.models import Trans
from MembersApp.models import Master
from services.services_trans_posting import TransactionProcessor


@login_required
def transaction_list(request):
    """Display all transactions"""
    transactions = Trans.objects.select_related('member', 'loan').order_by('-date', '-id')
    
    # Apply filters
    trans_type = request.GET.get('trans_type')
    if trans_type:
        transactions = transactions.filter(trans_type=trans_type)
    
    status = request.GET.get('status')
    if status:
        transactions = transactions.filter(status=status)
    
    # Summary
    summary = {
        'total_count': transactions.count(),
        'total_amount': transactions.aggregate(total=Sum('amount'))['total'] or Decimal('0.00'),
        'receipts_count': transactions.filter(trans_type='Receipts').count(),
        'receipts_total': transactions.filter(trans_type='Receipts').aggregate(total=Sum('amount'))['total'] or Decimal('0.00'),
        'payments_count': transactions.filter(trans_type='Payments').count(),
        'payments_total': transactions.filter(trans_type='Payments').aggregate(total=Sum('amount'))['total'] or Decimal('0.00'),
        'draft_count': transactions.filter(status='DRAFT').count(),
        'draft_total': transactions.filter(status='DRAFT').aggregate(total=Sum('amount'))['total'] or Decimal('0.00'),
    }
    
    context = {
        'transactions': transactions[:100],
        'summary': summary,
        'members': Master.objects.filter(is_deleted=False)[:100],
        'filters': {'trans_type': trans_type, 'status': status},
    }
    return render(request, 'RecPayApp/transaction_list.html', context)


@login_required
def process_all_drafts(request):
    """Process all draft transactions"""
    drafts = Trans.objects.filter(status='DRAFT')
    draft_count = drafts.count()
    
    if request.method == 'POST':
        success_count = 0
        error_count = 0
        
        for trans in drafts:
            try:
                processor = TransactionProcessor(trans, request.user)
                result = processor.process()
                
                if result['success']:
                    success_count += 1
                else:
                    error_count += 1
                    for error in result['errors']:
                        messages.error(request, f"{trans.rec_vou_no}: {error}")
            except Exception as e:
                error_count += 1
                messages.error(request, f"{trans.rec_vou_no}: {str(e)}")
        
        messages.success(request, f"Processed {success_count} transactions successfully. Failed: {error_count}")
        return redirect('RecPayApp:transaction_list')
    
    context = {
        'draft_count': draft_count,
        'draft_total': drafts.aggregate(total=Sum('amount'))['total'] or Decimal('0.00'),
        'drafts': drafts[:20],
    }
    return render(request, 'RecPayApp/process_drafts.html', context)


@login_required
def process_single_transaction_view(request, trans_id):
    """Process a single transaction"""
    transaction = get_object_or_404(Trans, id=trans_id)
    
    if request.method == 'POST':
        try:
            processor = TransactionProcessor(transaction, request.user)
            result = processor.process()
            
            if result['success']:
                messages.success(request, f"✅ Transaction {transaction.rec_vou_no} processed successfully!")
            else:
                for error in result['errors']:
                    messages.error(request, error)
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
        
        return redirect('RecPayApp:transaction_list')
    
    context = {'transaction': transaction}
    return render(request, 'RecPayApp/confirm_process.html', context)


@login_required
def transaction_detail(request, trans_id):
    """View transaction details"""
    transaction = get_object_or_404(Trans.objects.select_related('member', 'loan'), id=trans_id)
    
    context = {'transaction': transaction}
    return render(request, 'RecPayApp/transaction_detail.html', context)