# Create your views here.

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.db import models
from django.utils import timezone
from MembersApp.models import Master
from RecPayApp.models import Trans


from django.contrib.admin.views.decorators import staff_member_required
from django_ledger.models import EntityModel
from services.transaction_posting_service import process_transaction


import io
from decimal import Decimal
from datetime import datetime, date as dt_date
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter

@staff_member_required
def pending_transactions1(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    pending = Trans.objects.filter(entity=entity, journal_status="PENDING").order_by(
        "-created_at"
    )

    context = {
        "entity": entity,
        "transactions": pending,
    }
    return render(request, "ChurchApp/pending_transactions.html", context)


@staff_member_required
def supervisor_queue1(request, slug):
    """
    Supervisor view: list all PENDING transactions for this entity.
    Allows selection and posting to journal.
    """
    entity = get_object_or_404(EntityModel, slug=slug)

    # Get filters
    module_filter = request.GET.get("module", "")
    trans_type_filter = request.GET.get("trans_type", "")
    date_from = request.GET.get("date_from", "")
    date_to = request.GET.get("date_to", "")

    pending = Trans.objects.filter(entity=entity, journal_status="PENDING")

    if module_filter:
        pending = pending.filter(module=module_filter)
    if trans_type_filter:
        pending = pending.filter(trans_type=trans_type_filter)
    if date_from:
        pending = pending.filter(date__gte=date_from)
    if date_to:
        pending = pending.filter(date__lte=date_to)

    pending = pending.order_by("-date", "-created_at")

    context = {
        "entity": entity,
        "transactions": pending,
        "pending_count": pending.count(),
        "module_filter": module_filter,
        "trans_type_filter": trans_type_filter,
        "date_from": date_from,
        "date_to": date_to,
        "module_choices": Trans.MODULE_CHOICES,
        "type_choices": Trans.TRANS_TYPE,
    }
    return render(request, "RecPayApp/supervisor_queue.html", context)


@staff_member_required
def supervisor_post_selected1(request, slug):
    """
    Post selected PENDING transactions to the journal.
    """
    if request.method != "POST":
        return redirect("RecPayApp:supervisor_queue", slug=slug)

    entity = get_object_or_404(EntityModel, slug=slug)
    selected_ids = request.POST.getlist("selected_transactions")

    if not selected_ids:
        messages.warning(request, "No transactions selected.")
        return redirect("RecPayApp:supervisor_queue", slug=slug)

    transactions = Trans.objects.filter(
        entity=entity, pk__in=selected_ids, journal_status="PENDING"
    )

    posted = []
    failed = []

    for trans in transactions:
        try:
            result = process_transaction(trans, request.user)
            if result.get("success"):
                trans.journal_status = "POSTED"
                trans.status = "POSTED"
                trans.save(update_fields=["journal_status", "status"])
                posted.append(trans.rec_vou_no)
            else:
                failed.append((trans.rec_vou_no, result.get("errors", "Unknown error")))
        except Exception as e:
            failed.append((trans.rec_vou_no, str(e)))

    if posted:
        messages.success(
            request,
            f" {len(posted)} transaction(s) posted to journal: {', '.join(posted)}",
        )
    if failed:
        for rec, err in failed:
            messages.error(request, f" {rec}: {err}")

    return redirect("RecPayApp:supervisor_queue", slug=entity.slug)


@staff_member_required
def supervisor_reject_selected1(request, slug):
    """
    Reject selected PENDING transactions.
    """
    if request.method != "POST":
        return redirect("RecPayApp:supervisor_queue", slug=slug)

    entity = get_object_or_404(EntityModel, slug=slug)
    selected_ids = request.POST.getlist("selected_transactions")

    if not selected_ids:
        messages.warning(request, "No transactions selected.")
        return redirect("RecPayApp:supervisor_queue", slug=entity.slug)

    updated = Trans.objects.filter(
        entity=entity, pk__in=selected_ids, journal_status="PENDING"
    ).update(journal_status="REJECTED")

    messages.warning(request, f"{updated} transaction(s) rejected.")
    return redirect("RecPayApp:supervisor_queue", slug=entity.slug)


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
    members = Master.objects.filter(entity=entity, is_deleted=0).order_by('-date_created')
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
    active_count = Master.objects.filter(entity=entity, is_deleted=False).count()
    deleted_count = Master.objects.filter(entity=entity, is_deleted=True).count()
    total_count = Master.objects.filter(entity=entity).count()
    
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
    members = Master.objects.filter(entity=entity, is_deleted=1).order_by('-date_created')
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
    active_count = Master.objects.filter(entity=entity, is_deleted=False).count()
    deleted_count = Master.objects.filter(entity=entity, is_deleted=True).count()
    total_count = Master.objects.filter(entity=entity).count()
    
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
    deleted_count = Master.objects.filter(entity=entity, is_deleted=True).count()
    active_count = Master.objects.filter(entity=entity, is_deleted=False).count()
    never_deleted = Master.objects.filter(
        entity=entity,  
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
                result = process_transaction(trans, request.user)
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


@staff_member_required
def supervisor_queue(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)

    module = request.GET.get("module", "")
    trans_type = request.GET.get("trans_type", "")
    date_from = request.GET.get("date_from", "")
    date_to = request.GET.get("date_to", "")

    qs = Trans.objects.filter(entity=entity, journal_status="PENDING")
    if module:
        qs = qs.filter(module=module)
    if trans_type:
        qs = qs.filter(trans_type=trans_type)
    if date_from:
        qs = qs.filter(date__gte=date_from)
    if date_to:
        qs = qs.filter(date__lte=date_to)

    qs = qs.order_by("-date", "-created_at")

    context = {
        "entity": entity,
        "transactions": qs,
        "pending_count": qs.count(),
        "module_filter": module,
        "trans_type_filter": trans_type,
        "date_from": date_from,
        "date_to": date_to,
        "module_choices": Trans.MODULE_CHOICES,
        "type_choices": Trans.TRANS_TYPE,
    }
    return render(request, "RecPayApp/supervisor_queue.html", context)


@staff_member_required
def supervisor_post_selected(request, slug):
    if request.method != "POST":
        return redirect("RecPayApp:supervisor_queue", slug=slug)

    entity = get_object_or_404(EntityModel, slug=slug)
    ids = request.POST.getlist("selected_transactions")

    if not ids:
        messages.warning(request, "No transactions selected.")
        return redirect("RecPayApp:supervisor_queue", slug=slug)

    qs = Trans.objects.filter(entity=entity, pk__in=ids, journal_status="PENDING")

    posted, failed = [], []
    for trans in qs:
        result = process_transaction(trans, request.user)
        if result["success"]:
            posted.append(trans.rec_vou_no)
        else:
            failed.append((trans.rec_vou_no, "; ".join(result["errors"])))

    if posted:
        messages.success(request, f" {len(posted)} posted: {', '.join(posted)}")
    for rec, err in failed:
        messages.error(request, f" {rec}: {err}")

    return redirect("RecPayApp:supervisor_queue", slug=slug)


@staff_member_required
def supervisor_reject_selected(request, slug):
    if request.method != "POST":
        return redirect("RecPayApp:supervisor_queue", slug=slug)

    entity = get_object_or_404(EntityModel, slug=slug)
    ids = request.POST.getlist("selected_transactions")

    if not ids:
        messages.warning(request, "No transactions selected.")
        return redirect("RecPayApp:supervisor_queue", slug=slug)

    count = Trans.objects.filter(
        entity=entity,
        pk__in=ids,
        journal_status="PENDING",
    ).update(journal_status="REJECTED")

    messages.warning(request, f"{count} transaction(s) rejected.")
    return redirect("RecPayApp:supervisor_queue", slug=slug)


## ========================================== Trans List ============================
def _trans_filter(request, entity):
    """Return (queryset, filter_dict) based on GET parameters."""
    qs = Trans.objects.filter(entity=entity).order_by("-date", "-id")

    date_from = request.GET.get("date_from", "").strip()
    date_to = request.GET.get("date_to", "").strip()
    sub_module = request.GET.get("sub_module", "").strip()

    # --- Status ---
    # No ?status= in URL  → default to PENDING (matches the supervisor queue)
    # ?status=ALL         → no filter (show every status)
    # ?status=POSTED etc. → filter by that status
    status_raw = request.GET.get("status", None)
    if status_raw is None:
        status = "PENDING"
    else:
        status = status_raw.strip()
        if status == "ALL":
            status = ""

    if date_from:
        qs = qs.filter(date__gte=date_from)
    if date_to:
        qs = qs.filter(date__lte=date_to)
    if status:
        qs = qs.filter(journal_status=status)
    if sub_module:
        qs = qs.filter(sub_module=sub_module)

    return qs, {
        "date_from": date_from,
        "date_to": date_to,
        "status": status,
        "sub_module": sub_module,
    }

@login_required
def trans_report(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    qs, filters = _trans_filter(request, entity)

    total_amount = qs.aggregate(t=Sum("amount"))["t"] or 0

    context = {
        "entity": entity,
        "trans_list": qs,
        "total_amount": total_amount,
        "total_count": qs.count(),
        "filters": filters,
        "status_choices": Trans.JOURNAL_STATUS_CHOICES,
        "sub_module_choices": Trans.SUB_MODULE_CHOICES,
    }
    return render(request, "Supervisor/trans_report.html", context)


@login_required
def trans_report_pdf(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    qs, filters = _trans_filter(request, entity)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=1.0 * cm,
        rightMargin=1.0 * cm,
        topMargin=1.2 * cm,
        bottomMargin=1.0 * cm,
        title=f"Trans Report -  {entity.name}",
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "T", parent=styles["Title"], fontSize=14, alignment=TA_CENTER, spaceAfter=4
    )
    sub_style = ParagraphStyle(
        "S",
        parent=styles["Normal"],
        fontSize=9,
        alignment=TA_CENTER,
        textColor=colors.grey,
        spaceAfter=8,
    )
    cell = ParagraphStyle("C", parent=styles["Normal"], fontSize=7, leading=9)
    cell_r = ParagraphStyle(
        "CR", parent=styles["Normal"], fontSize=7, leading=9, alignment=TA_RIGHT
    )

    elements = [
        Paragraph(entity.name, title_style),
        Paragraph("Transactions Report", sub_style),
    ]

    headers = [
        "#",
        "Voucher",
        "Date",
        "Sub-Module",
        "Type",
        "DR Code",
        "DR Name",
        "CR Code",
        "CR Name",
        "Amount",
        "Status",
    ]
    data = [[Paragraph(f"<b>{h}</b>", cell) for h in headers]]
    total = Decimal("0.00")

    for i, t in enumerate(qs, 1):
        if t.trans_type == "Receipts":
            dr_c, dr_n = "1010", "Cash"
            cr_c, cr_n = t.ledger_code or "-", t.ledger_name or "-"
        elif t.trans_type == "Payments":
            dr_c, dr_n = t.ledger_code or "-", t.ledger_name or "-"
            cr_c, cr_n = "1010", "Cash"
        else:
            dr_c, dr_n = t.debit_account_code or "-", t.debit_account_name or "-"
            cr_c, cr_n = t.credit_account_code or "-", t.credit_account_name or "-"

        total += t.amount
        data.append(
            [
                Paragraph(str(i), cell),
                Paragraph(t.rec_vou_no or "-", cell),
                Paragraph(t.date.strftime("%Y-%m-%d") if t.date else "-", cell),
                Paragraph(
                    (
                        t.get_sub_module_display()
                        if hasattr(t, "get_sub_module_display")
                        else (t.sub_module or "-")
                    ),
                    cell,
                ),
                Paragraph(t.trans_type, cell),
                Paragraph(dr_c, cell),
                Paragraph(dr_n[:22], cell),
                Paragraph(cr_c, cell),
                Paragraph(cr_n[:22], cell),
                Paragraph(f"{t.amount:,.2f}", cell_r),
                Paragraph(t.journal_status, cell),
            ]
        )

    data.append(
        [
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            Paragraph("<b>TOTAL</b>", cell_r),
            Paragraph(f"<b>{total:,.2f}</b>", cell_r),
            "",
        ]
    )

    col_w = [
        0.8 * cm,
        3.5 * cm,
        1.9 * cm,
        2.6 * cm,
        1.8 * cm,
        1.5 * cm,
        3.6 * cm,
        1.5 * cm,
        3.6 * cm,
        2.2 * cm,
        1.9 * cm,
    ]
    table = Table(data, colWidths=col_w, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a3a6c")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 2),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -2),
                    [colors.white, colors.HexColor("#f5f5f5")],
                ),
                ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e0e8f0")),
            ]
        )
    )
    elements.append(table)
    elements.append(Spacer(1, 6))
    elements.append(
        Paragraph(
            f"Filters: {filters} &nbsp;|&nbsp; Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} "
            f"&nbsp;|&nbsp; Records: {qs.count()}",
            ParagraphStyle(
                "F",
                parent=styles["Normal"],
                fontSize=6.5,
                textColor=colors.grey,
                alignment=TA_CENTER,
            ),
        )
    )

    doc.build(elements)
    buffer.seek(0)
    resp = HttpResponse(buffer, content_type="application/pdf")
    resp["Content-Disposition"] = (
        f'attachment; filename="trans_report_{entity.slug}.pdf"'
    )
    return resp

@login_required
def trans_report_excel(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    qs, filters = _trans_filter(request, entity)

    wb = Workbook()
    ws = wb.active
    ws.title = "Trans Report"

    bold = Font(bold=True, color="FFFFFF")
    hfill = PatternFill("solid", fgColor="1a3a6c")
    thin = Side(style="thin", color="999999")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    center = Alignment(horizontal="center", vertical="center")

    headers = [
        "#",
        "ID",
        # core
        "Voucher No",
        "Trans No",
        "Voucher Seq",
        "Date",
        "Module",
        "Sub-Module",
        "Trans Type",
        "Amount",
        "Pay Mode",
        "Purpose",
        "Details",
        "Other Purpose",
        # ledger
        "Ledger ID",
        "Ledger Code",
        "Ledger Name",
        "Debit Code",
        "Debit Name",
        "Credit Code",
        "Credit Name",
        # party
        "Member No",
        "Member Name",
        "Non-Member Name",
        "Non-Member Contact",
        # bank
        "Bank Date",
        "Bank",
        "Bank No",
        "Bank Branch",
        "Cheque Date",
        "Cheque No",
        # momo
        "Momo No",
        "Momo Name",
        # loan
        "Loan Name",
        # status
        "Status",
        "Journal Status",
        "Journal Entry ID",
        "Posted At",
        # audit
        "Created By",
        "Created By Username",
        "Created At",
        "Updated At",
        # entity
        "Entity",
    ]
    ws.append(headers)
    for c in ws[ws.max_row]:
        c.font = bold
        c.fill = hfill
        c.alignment = center
        c.border = border

    def fmt(d):
        return d.strftime("%Y-%m-%d") if d else ""

    def fmt_dt(d):
        return d.strftime("%Y-%m-%d %H:%M") if d else ""

    for i, t in enumerate(qs, 1):
        ws.append(
            [
                i,
                t.id,
                t.rec_vou_no or "",
                t.trans_no or "",
                t.voucher_sequence,
                fmt(t.date),
                t.module or "",
                t.sub_module or "",
                t.trans_type or "",
                float(t.amount) if t.amount else 0,
                t.pay_mode or "",
                t.purpose or "",
                t.details or "",
                t.other_purpose or "",
                t.ledger_id or "",
                t.ledger_code or "",
                t.ledger_name or "",
                t.debit_account_code or "",
                t.debit_account_name or "",
                t.credit_account_code or "",
                t.credit_account_name or "",
                t.member_no or 0,
                t.member_name or "",
                t.non_member_name or "",
                t.non_member_contact or "",
                fmt(t.bank_date),
                t.bank or "",
                t.bank_no or "",
                t.bank_branch or "",
                fmt(t.cheque_date),
                t.cheque_no or "",
                t.momo_no or "",
                t.momo_name or "",
                t.loan_name or "",
                t.status or "",
                t.journal_status or "",
                t.journal_entry_id or "",
                fmt_dt(t.posted_at),
                t.created_by_name or "",
                t.created_by_username or "",
                fmt_dt(t.created_at),
                fmt_dt(t.updated_at),
                str(t.entity) if t.entity else "",
            ]
        )
        for c in ws[ws.max_row]:
            c.border = border

    # Totals row
    ws.append([""] * len(headers))
    total_row = ws.max_row
    ws.cell(row=total_row, column=2, value="TOTAL")
    amount_col = headers.index("Amount") + 1
    al = get_column_letter(amount_col)
    c = ws.cell(row=total_row, column=amount_col)
    c.value = f"=SUM({al}2:{al}{total_row-1})"
    c.font = Font(bold=True)
    c.fill = PatternFill("solid", fgColor="e0e8f0")

    for idx, h in enumerate(headers, 1):
        ws.column_dimensions[get_column_letter(idx)].width = max(
            12, min(len(h) + 3, 30)
        )

    ws.freeze_panes = "C2"

    resp = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    resp["Content-Disposition"] = (
        f'attachment; filename="trans_report_{entity.slug}.xlsx"'
    )
    wb.save(resp)
    return resp
