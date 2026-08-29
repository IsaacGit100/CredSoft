from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from decimal import Decimal
from django_ledger.models import EntityModel
from MembersApp.models import Master
from LoanApp.models import Loan
from RecPayApp.models import Trans
from django.utils import timezone


@login_required
def union_dashboard(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)

    # Access check (same as other views)
    try:
        profile = request.user.djan_led_profile
        if entity not in profile.allowed_entities.all() and entity != profile.default_entity:
            return render(request, 'djan_led/access_denied.html', {'entity': entity})
    except:
        pass

    # --- Statistics ---
    # Members
    total_members = Master.objects.filter(entity=entity, is_deleted=False).count()
    active_members = Master.objects.filter(entity=entity, is_deleted=False, mem_status='Active').count()

    # Loans
    total_loans = Loan.objects.filter(entity=entity).count()
    active_loans = Loan.objects.filter(entity=entity, status='Active').count()
    total_loan_balance = Loan.objects.filter(entity=entity).aggregate(Sum('loan_balance'))['loan_balance__sum'] or Decimal('0')
    total_disbursed = Loan.objects.filter(entity=entity).aggregate(Sum('principal'))['principal__sum'] or Decimal('0')

    # Savings – use Master.tot_deposits as a proxy
    total_savings = Master.objects.filter(entity=entity).aggregate(Sum('tot_deposits'))['tot_deposits__sum'] or Decimal('0')

    # Recent Transactions (last 10)
    recent_trans = Trans.objects.filter(entity=entity).order_by('-date')[:10]

    # Today's date
    today = timezone.now().date()

    context = {
        'entity': entity,
        'total_members': total_members,
        'active_members': active_members,
        'total_loans': total_loans,
        'active_loans': active_loans,
        'total_loan_balance': total_loan_balance,
        'total_disbursed': total_disbursed,
        'total_savings': total_savings,
        'recent_trans': recent_trans,
        'today': today,
    }
    return render(request, 'CreditUnion/credit_union_dashboard.html', context)

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django_ledger.models import EntityModel
from RecPayApp.models import Trans
from services.transaction_posting_service import process_transaction


@login_required
def run_pending_transactions(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)

    # Only supervisors (or staff) can access – adjust as needed
    if not request.user.is_staff:
        messages.error(request, "You are not authorised.")
        return redirect("djan_led:entity_dashboard", slug=slug)

    # Get all pending transactions for this entity
    pending_trans = Trans.objects.filter(
        entity=entity,
        status="DRAFT",  # or 'PENDING' – adjust to your field
        journal_status="PENDING",  # if you have this field
    ).order_by("-date")

    results = {
        "success": [],
        "failed": [],
        "total": pending_trans.count(),
    }

    if request.method == "POST":
        for trans in pending_trans:
            try:
                result = process_transaction(trans, request.user, slug)
                if result.get("success"):
                    results["success"].append(trans.id)
                else:
                    results["failed"].append(
                        {
                            "id": trans.id,
                            "error": result.get("errors", ["Unknown error"])[0],
                        }
                    )
            except Exception as e:
                results["failed"].append({"id": trans.id, "error": str(e)})

        # Redirect to a results page or re-render with results
        return render(request, "Supervisor/pending_transactions.html", {"entity": entity, "pending_trans": pending_trans, "results": results,
                "processed": True,
            },
        )

    return render(request, "Supervisor/pending_transactions.html", {"entity": entity, "pending_trans": pending_trans, "processed": False})


# services/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from MembersApp.models import Master, Sav_Int_Table

from .forms import SavIntSearchForm
from django_ledger.models import EntityModel
from django.contrib.admin.views.decorators import staff_member_required

@login_required
@staff_member_required
def sav_int_audit(request, entity_slug):
    entity = get_object_or_404(EntityModel, slug=entity_slug)
    member = None
    records = []
    monthly_summary = []
    form = SavIntSearchForm(request.GET or None)

    if request.GET and "search" in request.GET:
        search_term = request.GET.get("search", "").strip()
        # Try to find member by id or last_name
        members = Master.objects.filter(is_deleted=False)
        if search_term.isdigit():
            members = members.filter(id=int(search_term))
        else:
            members = members.filter(last_name__icontains=search_term)

        if members.count() == 1:
            member = members.first()
            records = Sav_Int_Table.objects.filter(
                master=member, entity=entity
            ).order_by("date")

            # Monthly summary
            monthly_summary = (
                records.annotate(month=TruncMonth("date"))
                .values("month")
                .annotate(
                    total_interest=Sum("sav_int"),
                    total_days=Sum("no_of_days"),
                    record_count=Count("id"),
                )
                .order_by("month")
            )
        elif members.count() > 1:
            # Multiple matches; we could show a list, but for simplicity we set a message
            form.add_error(
                "search",
                f"Multiple members found ({members.count()}). Please be more specific.",
            )
        elif search_term:
            form.add_error("search", "No member found with that ID or last name.")

    context = {
        "entity": entity,
        "form": form,
        "member": member,
        "records": records,
        "monthly_summary": monthly_summary,
    }
    return render(request, "CreditUnion/sav_int_audit.html", context)
