from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum, Count
from decimal import Decimal
from .models import Trans
from .services.posting_service import TransactionPostingService
from SysSetup.models import AuditLog

@login_required
@staff_member_required
def batch_posting_dashboard(request):
    """Secure dashboard for batch posting - Only accessible by staff"""
    
    # Get all draft transactions - ORDER BY date DESC
    draft_transactions = Trans.objects.filter(status='DRAFT').order_by('-date', '-id')
    
    # Debug print to see what's being passed
   
    for t in draft_transactions[:5]:
      #  print(f"  {t.date} - {t.trans_no} - {t.trans_type} - {t.amount}")
      I=1+1
    
    # Statistics
    stats = {
        'total_draft': draft_transactions.count(),
        'total_amount': draft_transactions.aggregate(total=Sum('amount'))['total'] or Decimal('0'),
        'receipts_count': draft_transactions.filter(trans_type='Receipts').count(),
        'payments_count': draft_transactions.filter(trans_type='Payments').count(),
        'receipts_amount': draft_transactions.filter(trans_type='Receipts').aggregate(total=Sum('amount'))['total'] or Decimal('0'),
        'payments_amount': draft_transactions.filter(trans_type='Payments').aggregate(total=Sum('amount'))['total'] or Decimal('0'),
    }
    
    # Group by ledger for summary
    ledger_summary = draft_transactions.values('ledger_name').annotate(
        count=Count('id'),
        total=Sum('amount')
    ).order_by('-total')[:10]
    
    context = {
        'transactions': draft_transactions,  # Make sure this is the correct variable name
        'stats': stats,
        'ledger_summary': ledger_summary,
        'today': timezone.now(),
    }
    return render(request, 'RecPayApp/batch_posting_dashboard.html', context)



@login_required
@staff_member_required
def batch_posting_preview(request):
    """Preview selected transactions before posting"""
    
    if request.method == 'POST':
        selected_ids = request.POST.getlist('selected_ids[]')
        
        if not selected_ids:
            messages.error(request, "No transactions selected")
            return redirect('RecPayApp:batch_posting_dashboard')
        
        # Store in session for the confirmation step
        request.session['batch_post_ids'] = selected_ids
        request.session['batch_post_time'] = timezone.now().isoformat()
        
        # Get selected transactions
        transactions = Trans.objects.filter(id__in=selected_ids, status='DRAFT')
        
        # Calculate totals
        total_amount = transactions.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        receipts_total = transactions.filter(trans_type='Receipts').aggregate(total=Sum('amount'))['total'] or Decimal('0')
        payments_total = transactions.filter(trans_type='Payments').aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Check for potential issues
        warnings = []
        for trans in transactions:
            if not trans.ledger_id:
                warnings.append(f"Transaction {trans.trans_no}: Missing ledger account")
            if trans.amount <= 0:
                warnings.append(f"Transaction {trans.trans_no}: Invalid amount")
        
        context = {
            'transactions': transactions,
            'total_count': len(selected_ids),
            'total_amount': total_amount,
            'receipts_total': receipts_total,
            'payments_total': payments_total,
            'warnings': warnings,
            'session_timeout': 300,  # 5 minutes timeout
        }
        return render(request, 'RecPayApp/batch_posting_preview.html', context)
    
    return redirect('RecPayApp:batch_posting_dashboard')
# RecPayApp/views_batch.py - Update the confirm view

@login_required
@staff_member_required
def batch_posting_confirm1(request):
    """Confirm and execute batch posting with security verification"""
    
    # Verify session exists
    if 'batch_post_ids' not in request.session:
        messages.error(request, "Session expired. Please select transactions again.")
        return redirect('RecPayApp:batch_posting_dashboard')
    
    # Check session timeout (5 minutes)
    session_time = request.session.get('batch_post_time')
    if session_time:
        from datetime import datetime
        session_time = datetime.fromisoformat(session_time)
        if (timezone.now() - session_time).seconds > 300:
            messages.error(request, "Session timed out. Please select transactions again.")
            del request.session['batch_post_ids']
            del request.session['batch_post_time']
            return redirect('RecPayApp:batch_posting_dashboard')
    
    selected_ids = request.session.get('batch_post_ids', [])
    
    if request.method == 'POST':
        # Security verification
        confirm_password = request.POST.get('confirm_password', '')
        confirm_text = request.POST.get('confirm_text', '')
        
        # Verify password
        if not request.user.check_password(confirm_password):
            messages.error(request, "❌ Incorrect password. Batch posting cancelled.")
            return redirect('RecPayApp:batch_posting_dashboard')
        
        # Verify confirmation text
        if confirm_text != 'CONFIRM BATCH POST':
            messages.error(request, "❌ Please type 'CONFIRM BATCH POST' to proceed.")
            return redirect('RecPayApp:batch_posting_preview')
        
        # Process the batch
        success_count = 0
        error_count = 0
        error_details = []
        posted_journals = []
        total_amount = Decimal('0')
        
        with transaction.atomic():
            for trans_id in selected_ids:
                try:
                    transaction_obj = Trans.objects.get(id=trans_id, status='DRAFT')
                    service = TransactionPostingService(transaction_obj, request.user)
                    result = service.process()
                    
                    if result['success']:
                        success_count += 1
                        total_amount += transaction_obj.amount
                        posted_journals.append({
                            'trans_no': transaction_obj.trans_no,
                            'journal': result['journal_entry'].entry_number if result['journal_entry'] else 'N/A',
                            'amount': transaction_obj.amount
                        })
                    else:
                        error_count += 1
                        error_details.append({
                            'trans_no': transaction_obj.trans_no,
                            'message': ', '.join(result['errors'])
                        })
                        
                except Trans.DoesNotExist:
                    error_count += 1
                    error_details.append({
                        'trans_no': f"ID: {trans_id}",
                        'message': "Transaction not found"
                    })
                except Exception as e:
                    error_count += 1
                    error_details.append({
                        'trans_no': f"ID: {trans_id}",
                        'message': str(e)
                    })
        
        # Clear session
        del request.session['batch_post_ids']
        del request.session['batch_post_time']
        
        # Log the batch operation
        from CoreApp.models import AuditLog
        AuditLog.objects.create(
            user=request.user,
            action='BATCH_POST',
            model_name='Transaction',
            description=f"Batch posted {success_count} transactions, {error_count} failed. Total: ₵{total_amount}",
            ip_address=get_client_ip(request)
        )
        
        # Render results page
        context = {
            'success_count': success_count,
            'error_count': error_count,
            'total_processed': success_count + error_count,
            'total_amount': total_amount,
            'posted_journals': posted_journals,
            'error_details': error_details,
            'processed_at': timezone.now(),
            'ip_address': get_client_ip(request),
        }
        return render(request, 'RecPayApp/batch_posting_confirm.html', context)
    
    return redirect('RecPayApp:batch_posting_dashboard')

@login_required
@staff_member_required
def batch_posting_confirm(request):
    """Confirm and execute batch posting with security verification"""
    
    # Verify session exists
    if 'batch_post_ids' not in request.session:
        messages.error(request, "Session expired. Please select transactions again.")
        return redirect('RecPayApp:batch_posting_dashboard')
    
    # Check session timeout (5 minutes)
    session_time = request.session.get('batch_post_time')
    if session_time:
        from datetime import datetime
        session_time = datetime.fromisoformat(session_time)
        if (timezone.now() - session_time).seconds > 300:
            messages.error(request, "Session timed out. Please select transactions again.")
            del request.session['batch_post_ids']
            del request.session['batch_post_time']
            return redirect('RecPayApp:batch_posting_dashboard')
    
    selected_ids = request.session.get('batch_post_ids', [])
    
    if request.method == 'POST':
        # Security verification
        confirm_password = request.POST.get('confirm_password', '')
        confirm_text = request.POST.get('confirm_text', '')
        
        # Verify password
        if not request.user.check_password(confirm_password):
            messages.error(request, "❌ Incorrect password. Batch posting cancelled.")
            return redirect('RecPayApp:batch_posting_dashboard')
        
        # Verify confirmation text
        if confirm_text != 'CONFIRM BATCH POST':
            messages.error(request, "❌ Please type 'CONFIRM BATCH POST' to proceed.")
            return redirect('RecPayApp:batch_posting_preview')
        
        # Process the batch
        success_count = 0
        error_count = 0
        error_details = []
        posted_journals = []
        
        with transaction.atomic():
            for trans_id in selected_ids:
                try:
                    transaction_obj = Trans.objects.get(id=trans_id, status='DRAFT')
                    service = TransactionPostingService(transaction_obj, request.user)
                    result = service.process()
                    
                    if result['success']:
                        success_count += 1
                        posted_journals.append({
                            'trans_no': transaction_obj.trans_no,
                            'journal': result['journal_entry'].entry_number if result['journal_entry'] else 'N/A',
                        })
                    else:
                        error_count += 1
                        error_details.append(f"{transaction_obj.trans_no}: {', '.join(result['errors'])}")
                        
                except Trans.DoesNotExist:
                    error_count += 1
                    error_details.append(f"Transaction {trans_id} not found")
                except Exception as e:
                    error_count += 1
                    error_details.append(f"Transaction {trans_id}: {str(e)}")
        
        # Clear session
        del request.session['batch_post_ids']
        del request.session['batch_post_time']
        
        # Log the batch operation
    #    from CoreApp.models import AuditLog
        from SysSetup.models import AuditLog
        AuditLog.objects.create(
            user=request.user,
            action='BATCH_POST',
            model_name='Transaction',
            description=f"Batch posted {success_count} transactions, {error_count} failed",
            ip_address=get_client_ip(request)
        )
        
        # Show results
        if success_count > 0:
            messages.success(request, 
                f"Batch posting completed! Posted {success_count} transaction(s)."
            )
        
        if error_count > 0:
            messages.warning(request, f" {error_count} transaction(s) failed.")
            for detail in error_details[:5]:
                messages.error(request, detail)
        
        return redirect('RecPayApp:batch_posting_dashboard')
    
    return redirect('RecPayApp:batch_posting_dashboard')


def get_client_ip(request):
    """Get client IP address for audit log"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
    
    
    
    
    
    
