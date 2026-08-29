# CoreApp/views_batch.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from .models import BatchProcess, BatchProcessLog
from .services.batch_service import BatchProcessingService

@staff_member_required
def batch_dashboard(request):
    """Dashboard showing all batch processes"""
    
    service = BatchProcessingService(request.user)
    processes = service.get_all_processes_status()
    
    # Statistics
    total_processes = len(processes)
    pending_count = sum(1 for p in processes if p['last_run_status'] == 'PENDING')
    completed_count = sum(1 for p in processes if p['last_run_status'] == 'COMPLETED')
    failed_count = sum(1 for p in processes if p['last_run_status'] == 'FAILED')
    due_count = sum(1 for p in processes if p['is_due'])
    
    context = {
        'processes': processes,
        'total_processes': total_processes,
        'pending_count': pending_count,
        'completed_count': completed_count,
        'failed_count': failed_count,
        'due_count': due_count,
        'today': timezone.now(),
    }
    return render(request, 'CoreApp/batch_dashboard.html', context)


@staff_member_required
def run_batch_process(request, process_type):
    """Run a specific batch process"""
    
    if request.method == 'POST':
        service = BatchProcessingService(request.user)
        result = service.run_process(process_type)
        
        if result['success']:
            messages.success(request, f"Process completed successfully!")
        else:
            messages.error(request, f"Process failed. Check logs for details.")
        
        return redirect('CoreApp:batch_dashboard')
    
    # GET request - show confirmation
    process = get_object_or_404(BatchProcess, process_type=process_type)
    
    context = {
        'process': process,
        'today': timezone.now(),
    }
    return render(request, 'CoreApp/confirm_run_process.html', context)


@staff_member_required
def batch_logs(request, process_id=None):
    """View batch process logs"""
    
    if process_id:
        process = get_object_or_404(BatchProcess, id=process_id)
        logs = process.logs.all()[:50]
    else:
        logs = BatchProcessLog.objects.all()[:100]
        process = None
    
    context = {
        'logs': logs,
        'process': process,
    }
    return render(request, 'CoreApp/batch_logs.html', context)


@staff_member_required
def reset_batch_process(request, process_id):
    """Reset a batch process (clear last run)"""
    
    if request.method == 'POST':
        process = get_object_or_404(BatchProcess, id=process_id)
        process.last_run = None
        process.last_run_by = None
        process.last_run_status = 'PENDING'
        process.last_run_message = ''
        process.next_run_due = timezone.now()
        process.save()
        
        messages.success(request, f"Process '{process.process_name}' has been reset.")
        return redirect('CoreApp:batch_dashboard')
    
    return redirect('core:batch_dashboard')

# CoreApp/views_batch.py - Update batch_logs function

@staff_member_required
def batch_logs(request, process_id=None):
    """View batch process logs"""
    
    from django.core.paginator import Paginator
    
    if process_id:
        process = get_object_or_404(BatchProcess, id=process_id)
        logs = process.logs.all().order_by('-started_at')
    else:
        process = None
        logs = BatchProcessLog.objects.all().order_by('-started_at')
        all_processes = BatchProcess.objects.all()
    
    # Pagination
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calculate summary
    total_logs = logs.count()
    completed_count = logs.filter(status='COMPLETED').count()
    failed_count = logs.filter(status='FAILED').count()
    
    # Calculate average duration
    from django.db.models import F, ExpressionWrapper, fields
    from django.db.models.functions import Extract
    # Simplified average calculation
    avg_duration = None
    if completed_count > 0:
        # This is simplified; for actual duration you'd need to calculate
        avg_duration = "~5"  # Placeholder
    
    context = {
        'logs': page_obj,
        'process': process,
        'all_processes': BatchProcess.objects.all(),
        'total_logs': total_logs,
        'completed_count': completed_count,
        'failed_count': failed_count,
        'avg_duration': avg_duration,
    }
    return render(request, 'CoreApp/batch_logs.html', context)