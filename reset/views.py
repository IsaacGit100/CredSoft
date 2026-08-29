from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.management import call_command
from django.db import connection
from django.http import HttpResponseNotAllowed
from django.contrib.auth.models import User
from django.utils import timezone

@staff_member_required
def confirm_reset(request):
    """Display confirmation page for factory reset."""
    # Optional: count tables for display
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE()")
        table_count = cursor.fetchone()[0]
    context = {'table_count': table_count}
    return render(request, 'reset/confirm.html', context)


@staff_member_required
def perform_reset(request):
    """Execute the factory reset."""
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    
    if not request.POST.get('confirm'):
        messages.error(request, "You must confirm the factory reset.")
        return redirect('reset:confirm')
    
    try:
        # Use Django's flush command: removes all data, resets sequences (auto-increment)
        call_command('flush', interactive=False, verbosity=0)
        
        # Optional: keep the first superuser account? Flush removes all users!
        # If you want to keep a specific user, you must recreate them after flush.
        # Instead, we'll just flush and rely on `createsuperuser` later.
        # But we can create a default admin user if needed (optional).
        # For now, just flush.
        
        # Log the action (if you have a BackupLog model, you can log; otherwise skip)
        # We'll just show success.
        
        messages.success(request, "Factory reset completed. All data has been erased and auto-increment counters reset.")
        return render(request, 'reset/success.html')  # success page
    
    except Exception as e:
        messages.error(request, f"Factory reset failed: {str(e)}")
        return redirect('reset:confirm')