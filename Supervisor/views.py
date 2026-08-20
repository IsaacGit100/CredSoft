from django.shortcuts import render

from django.contrib.auth.decorators import login_required

# Create your views here.


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from MembersApp.models import Master

@login_required
def main_dashboard(request):
    return redirect('/')

@login_required
def super_home(request, slug):
    return render(request, 'Supervisor/super_home.html')

def super_finance_home(request, slug):
    return render(request, 'Supervisor/super_finance_home.html')

@login_required
def del_restore_menu(request, slug):
    return render(request, 'Supervisor/del_restore_menu.html')

@login_required
def login_manager_menu(request, slug):
    return render(request, 'Supervisor/login_manager_menu.html')

@login_required
def tech_menu(request, slug):
    return render(request, 'Supervisor/tech_menu.html')

@login_required
def batch_process_menu(request, slug):
    return render(request, 'Supervisor/batch_processing_menu.html')

@login_required
def batch_process(request, slug):
    return render(request, 'CoreApp/batch_dashboard.html')

@login_required
def members_images(request, slug):
    return render(request, 'MembersApp/member_images.html')


def reports_index(request, slug):
    return render(request, 'Supervisor/reports_index.html')

@login_required
def member_view(request, slug, pk):
    """View detailed member information"""
    member = get_object_or_404(Master, pk=pk)
    
    # Calculate age
    age = None
    if member.date_of_birth:
        today = datetime.now().date()
        age = today.year - member.date_of_birth.year - (
            (today.month, today.day) < (member.date_of_birth.month, member.date_of_birth.day)
        )
    
    context = {
        'member': member,
        'age': age,
        'total_guaranteed': member.tot_guaranteed,
        'total_guaranted': member.tot_guaranted,
        'total_loans': member.tot_loans,
        'total_deposits': member.tot_deposits,
        'total_shares': member.tot_shares,
    }
    return render(request, 'MembersApp/member_view.html', context)

@login_required
def member_list_delete(request, slug):
    """Display list of members that can be deleted"""
    
    # Get all members (including deleted ones for restore option)
    #members = Master.objects.all().order_by('-date_created')
    members = Master.objects.filter(is_deleted=0).order_by('-date_created')
    # Search functionality
    search_query = request.GET.get('q', '')
    if search_query:
        members = members.filter(
            Q(full_name__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(id__icontains=search_query) |
            Q(telephone1__icontains=search_query)
        )
    
    # Statistics
    active_count = Master.objects.filter(is_deleted=False).count()
    deleted_count = Master.objects.filter(is_deleted=True).count()
    total_count = Master.objects.count()
    
    context = {
        'members': members,
        'search_query': search_query,
        'active_count': active_count,
        'deleted_count': deleted_count,
        'total_count': total_count,
    }
    return render(request, 'Supervisor/member_list_delete.html', context)


@login_required
def member_list_restore(request, slug):
    """Display list of members that can be deleted"""
    
    # Get all members (including deleted ones for restore option)
   # members = Master.objects.all().order_by('-date_created')
    members = Master.objects.filter(is_deleted=1).order_by('-date_created')
    # Search functionality
    search_query = request.GET.get('q', '')
    if search_query:
        members = members.filter(
            Q(full_name__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(id__icontains=search_query) |
            Q(telephone1__icontains=search_query)
        )
    
    # Statistics
    active_count = Master.objects.filter(is_deleted=False).count()
    deleted_count = Master.objects.filter(is_deleted=True).count()
    total_count = Master.objects.count()
    
    context = {
        'members': members,
        'search_query': search_query,
        'active_count': active_count,
        'deleted_count': deleted_count,
        'total_count': total_count,
    }
    return render(request, 'Supervisor/member_list_restore.html', context)

@login_required
def member_delete_confirm(request, slug, pk):
    """Confirm deletion of a specific member"""
    
    member = get_object_or_404(Master, pk=pk)
    
    # Check if already deleted
    if member.is_deleted:
        messages.warning(request, f"Member '{member.full_name}' is already deleted!")
        return redirect('Supervisor:member_list_delete')
    
    # Get member details for display
    related_info = {
        'has_loans': member.loans.exists(),
        'has_guarantees': member.guarantor_set.exists(),
        'has_transactions': hasattr(member, 'trans_set') and member.trans_set.exists(),
        'loan_count': member.loans.count(),
        'guarantee_count': member.guarantor_set.count(),
    }
    
    context = {
        'member': member,
        'related_info': related_info,
    }
    return render(request, 'Supervisor/member_delete_confirm.html', context)

# MembersApp/views.py
from django.utils import timezone

@login_required
def member_delete_perform(request, slug, pk):
    """Soft delete a member with tracking"""
    
    if request.method == 'POST':
        member = get_object_or_404(Master, pk=pk)
        
        # Check if already deleted
        if member.is_deleted:
            messages.warning(request, f"Member '{member.full_name}' is already deleted!")
            return redirect('Supervisor:member_list_restore')
        
        # Append to delete_history
        history_entry = {
            'date': timezone.now().isoformat(),
            'datetime': str(timezone.now()),
        }
        
        if member.delete_history:
            member.delete_history.append(history_entry)
        else:
            member.delete_history = [history_entry]
        
        # Append to delete_users
        user_entry = {
            'user_id': request.user.id,
            'username': request.user.username,
            'date': timezone.now().isoformat(),
        }
        
        if member.delete_users:
            member.delete_users.append(user_entry)
        else:
            member.delete_users = [user_entry]
        
        # Perform soft delete
        member.is_deleted = True
        member.del_rec = 'Yes'
        member.save()
        
        messages.success(request, f"Member '{member.full_name}' has been deleted!")
        return redirect('Supervisor:member_list_restore')
    
    return redirect('Supervisor:member_list_restore')


@login_required
def member_restore(request, slug, pk):
    """Restore a soft-deleted member with tracking"""
    
    if request.method == 'POST':
        member = get_object_or_404(Master, pk=pk)
        
        # Check if already active
        if not member.is_deleted:
            messages.warning(request, f"Member '{member.full_name}' is already active!")
            return redirect('Supervisor:member_list_restore')
        
        # Append to restore_history
        history_entry = {
            'date': timezone.now().isoformat(),
            'datetime': str(timezone.now()),
        }
        
        if member.restore_history:
            member.restore_history.append(history_entry)
        else:
            member.restore_history = [history_entry]
        
        # Append to restore_users
        user_entry = {
            'user_id': request.user.id,
            'username': request.user.username,
            'date': timezone.now().isoformat(),
        }
        
        if member.restore_users:
            member.restore_users.append(user_entry)
        else:
            member.restore_users = [user_entry]
        
        # Perform restore
        member.is_deleted = False
        member.del_rec = 'No'
        member.save()
        
        messages.success(request, f"Member '{member.full_name}' has been restored!")
        return redirect('Supervisor:member_list_restore')
    
    return redirect('Supervisor:member_list_restore')


@login_required
def member_permanent_delete(request, slug, pk):
    """Permanently delete a member (admin only)"""
    
    if not request.user.is_superuser:
        messages.error(request, "Only administrators can permanently delete members!")
        return redirect('MembersApp:member_delete_list')
    
    member = get_object_or_404(Master, pk=pk)
    
    if request.method == 'POST':
        confirm = request.POST.get('confirm', '')
        if confirm == 'PERMANENT':
            member_name = member.full_name
            member.delete()  # Hard delete from database
            messages.success(request, f"Member '{member_name}' has been PERMANENTLY deleted!")
        else:
            messages.error(request, "Type 'PERMANENT' to confirm permanent deletion.")
            return redirect('MembersApp:member_delete_confirm', pk=pk)
        
        return redirect('MembersApp:member_list_delete')
    
    return redirect('MembersApp:member_list_delete')


# MembersApp/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q


@login_required
def delete_history_list(request, slug):
    """Display ALL members with their deletion/restoration history for audit"""

    # Get ALL members (both active and deleted) for audit
    all_members = Master.objects.all().order_by('-date_created')

    # Search functionality
    search_query = request.GET.get('q', '')
    if search_query:
        all_members = all_members.filter(
            Q(full_name__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(id__icontains=search_query) |
            Q(telephone1__icontains=search_query)
        )

    # Statistics
    total_members = all_members.count()
    deleted_count = Master.objects.filter(is_deleted=True).count()
    active_count = Master.objects.filter(is_deleted=False).count()
    never_deleted = Master.objects.filter(
        is_deleted=False, 
        delete_history__isnull=True
    ).count()

    context = {
        'members': all_members,
        'search_query': search_query,
        'total_members': total_members,
        'deleted_count': deleted_count,
        'active_count': active_count,
        'never_deleted': never_deleted,
    }
    return render(request, 'Supervisor/delete_history_list.html', context)


# RecPayApp/views.py
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required

# ============================ Savings Interest Calculations & Application
# from services.sav_int_service import InterestAccrualService


@login_required
def trigger_interest_accrual(request, slug):
    entity=get_object_or_404(EntityModel, slug=slug)
    service = InterestAccrualService(slug)
    results = service.run_daily_accrual()
    messages.success(
        request,
        f"Interest accrued: {results['total_accrued']}, applied: {results['total_applied']}",
    )

    return redirect("entity_dashboard", slug=slug)


from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django_ledger.models import EntityModel
# from services.sav_int_service import InterestAccrualService


@staff_member_required
def run_interest_accrual9(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    service = InterestAccrualService(slug)
    results = service.run_daily_accrual()
    messages.success(
        request,
        f"Interest accrued: {results['total_accrued']}, applied: {results['total_applied']}",
    )
    return redirect("Supervisor:super_home", slug=slug)


# @staff_member_required
@login_required
def run_interest_accrual(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)

    if request.method == "POST":
        # Actually run the accrual
        service = InterestAccrualService(slug)
        results = service.run_daily_accrual(dry_run=False)
        messages.success(
            request,
            f"Interest accrual completed. Total accrued: {results['total_accrued']}, "
            f"applied: {results['total_applied']}, failed: {len(results['failed'])}",
        )
        return redirect("Supervisor:super_home", slug=slug)

    # GET – show preview (dry run)
    service = InterestAccrualService(slug)
    results = service.run_daily_accrual(dry_run=True)
    context = {
        "entity": entity,
        "results": results,
        "dry_run": True,
    }
    return render(request, "Supervisor/sav_int_accrual_preview.html", context)

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django_ledger.models import EntityModel
from RecPayApp.models import Trans
from services.transaction_posting_service import process_transaction


@staff_member_required
def pending_transactions(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    # Get transactions that are not yet posted (journal_status='PENDING')
    transactions = Trans.objects.filter(
        entity=entity, journal_status="PENDING"
    ).order_by("-date", "-id")

    context = {
        "entity": entity,
        "transactions": transactions,
    }
    return render(request, "Supervisor/pending_transactions.html", context)


@staff_member_required
def post_selected_transactions(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    if request.method == "POST":
        selected_ids = request.POST.getlist("selected_ids")
        if not selected_ids:
            messages.warning(request, "No transactions selected.")
            return redirect("Supervisor:pending_transactions", slug=slug)

        posted_count = 0
        failed_count = 0
        for trans_id in selected_ids:
            try:
                trans = Trans.objects.get(
                    id=trans_id, entity=entity, journal_status="PENDING"
                )
                result = process_transaction(trans, request.user, slug)
                if result["success"]:
                    posted_count += 1
                else:
                    failed_count += 1
                    messages.error(
                        request,
                        f"Failed to post transaction {trans.rec_vou_no}: {result['errors']}",
                    )
            except Trans.DoesNotExist:
                messages.error(
                    request, f"Transaction {trans_id} not found or already posted."
                )

        messages.success(
            request, f"Posted {posted_count} transactions. Failed: {failed_count}."
        )
    return redirect("Supervisor:pending_transactions", slug=slug)
