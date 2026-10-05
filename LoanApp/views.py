from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Sum, Count
from django.utils import timezone
from decimal import Decimal
import json
from datetime import date, datetime, timedelta
from django.contrib.auth.decorators import login_required
from calendar import monthrange

from django.http import HttpResponse
from dateutil.relativedelta import relativedelta

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.rl_settings import underlineWidth
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from xml.sax.saxutils import escape
from decimal import Decimal, InvalidOperation
from datetime import datetime
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone

from .loan_schedule import build_schedule
from .pdf import build_loan_schedule_pdf


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.core.mail import EmailMessage
from django.views.decorators.http import require_POST
from django.utils import timezone

from .models import Loan

from .pdf import build_loan_schedule_pdf
from .loan_schedule import build_schedule

# ## Tables
from .models import Loan, Guarantor, LoanRepayment, GuarantorRelease
from MembersApp.models import Master
from django_ledger.models import EntityModel, AccountModel
from django.db import transaction
from RecPayApp.models import Trans

# ## Forms
from .forms import LoanEditForm, LoanApplicationForm, LoanRepaymentForm
from .forms import LoanApplicationForm

def loans_home(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    return render(request, 'LoanApp/loans_home.html')

@login_required
def back_to_home(request, slug):
    """Return to main dashboard"""
    return redirect('/')  # This takes user back to dashboard

@login_required
def main_menu(request):
    return render(request, 'SysSetup/loans_home.html')


@login_required
def loan_application(request, slug):
    """Single-page loan application form + list of recent loans."""
    entity = get_object_or_404(EntityModel, slug=slug)

    if request.method == "POST":
        form = LoanApplicationForm(request.POST, entity=entity)
        if form.is_valid():
            d = form.cleaned_data
            with transaction.atomic():
                loan = Loan.objects.create(
                    entity=entity,
                    member=d["member"],
                    principal=d["principal"],
                    interest_rate=d["interest_rate"],
                    term_months=d["term_months"],
                    purpose=d.get("purpose", ""),
                    date_applied=d["date_applied"],
                    member_balance_at_application=d["member"].available_balance,
                    status=Loan.STATUS_NEW,
                    created_by=request.user,
                )

                for entry in d["guarantors"]:
                    Guarantor.objects.create(
                        entity=entity,
                        loan=loan,
                        member=entry["member"],
                        amount=entry["amount"],
                    )

            messages.success(
                request,
                f"Loan {loan.loan_no} created with {len(d['guarantors'])} guarantor(s).",
            )
    #        return redirect("LoanApp:loan_application", entity.slug)
            return redirect(f"{reverse('LoanApp:loan_acceptance_letter', args=[entity.slug, loan.pk])}?print=1")
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = LoanApplicationForm(
            entity=entity,
            initial={
                "date_applied": timezone.now().date(),
            },
        )

    recent = (
        Loan.objects.filter(entity=entity)
        .select_related("member")
        .order_by("-date_applied", "-id")[:30]
    )

    # Member lookup data for JS
    members = Master.objects.filter(entity=entity, is_deleted=False)
    member_data = {
        str(m.id): {
            "id": m.id,
            "name": m.full_name,
            "credit": float(m.member_credit),
            "debit": float(m.member_debit),
            "available": float(m.available_balance),
            "rate": float(m.loan_int_rate or 0),
        }
        for m in members
    }

    return render(
        request,
        "LoanApp/loan_application.html",
        {
            "entity": entity,
            "form": form,
            "recent": recent,
            "member_data_json": json.dumps(member_data),
        },
    )


# ---------------------------------------------------------------------------
# LIST
# ---------------------------------------------------------------------------
@login_required
def loan_list(request, slug):
    """Loan list with search, filters, and totals."""
    entity = get_object_or_404(EntityModel, slug=slug)

    qs = (
        Loan.objects.filter(entity=entity)
        .select_related("member")
        .prefetch_related("guarantors__member")
        .order_by("-date_applied", "-id")
    )

    # Filters
    search = request.GET.get("q", "").strip()
    status_filter = request.GET.get("status", "").strip()

    if search:
        qs = qs.filter(
            Q(loan_no__icontains=search)
            | Q(member__full_name__icontains=search)
            | Q(member__telephone1__icontains=search)
            | Q(purpose__icontains=search)
        )

    if status_filter:
        qs = qs.filter(status=status_filter)

    # Totals
    totals = qs.aggregate(
        total_principal=Sum("principal"),
        total_balance=Sum("balance"),
        total_interest_paid=Sum("interest_paid"),
        total_principal_paid=Sum("principal_paid"),
    )

    return render(
        request,
        "LoanApp/loan_list.html",
        {
            "entity": entity,
            "loans": qs,
            "search": search,
            "status_filter": status_filter,
            "statuses": Loan.STATUS_CHOICES,
            "totals": totals,
            "count": qs.count(),
        },
    )


# ---------------------------------------------------------------------------
# DETAIL
# ---------------------------------------------------------------------------
@login_required
def loan_detail(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    loan = get_object_or_404(
        Loan.objects.select_related("member").prefetch_related(
            "guarantors__member", "repayments"
        ),
        pk=pk,
        entity=entity,
    )

    guarantors = loan.guarantors.select_related("member").order_by("date", "id")
    repayments = loan.repayments.select_related("member").order_by("-date", "-id")[:30]
    releases = (
        GuarantorRelease.objects.filter(repayment__loan=loan)
        .select_related("guarantor__member", "repayment")
        .order_by("-created_at")[:30]
    )

    return render(
        request,
        "LoanApp/loan_detail.html",
        {
            "entity": entity,
            "loan": loan,
            "guarantors": guarantors,
            "repayments": repayments,
            "releases": releases,
        },
    )


# ---------------------------------------------------------------------------
# EDIT
# ---------------------------------------------------------------------------
@login_required
def loan_edit(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    loan = get_object_or_404(Loan, pk=pk, entity=entity)

    # Block edits once disbursed/active
    if loan.status not in (Loan.STATUS_NEW, "New Loan"):
        messages.warning(
            request,
            f"Loan {loan.loan_no} is {loan.get_status_display()}. "
            "Only NEW loans can be edited.",
        )
        return redirect("LoanApp:loan_detail", entity.slug, loan.pk)

    if request.method == "POST":
        form = LoanEditForm(request.POST, instance=loan)
        if form.is_valid():
            updated = form.save(commit=False)

            # Recalculate shortfall against original application balance
            updated.member_balance_at_application = (
                updated.member_balance_at_application
                or loan.member_balance_at_application
            )
            updated.save()

            # Check that guarantor coverage still matches shortfall
            if updated.total_guaranteed < updated.shortfall:
                messages.warning(
                    request,
                    f"Guarantor coverage (₵{updated.total_guaranteed}) is now below "
                    f"the shortfall (₵{updated.shortfall}). Add more guarantees.",
                )
                return redirect("LoanApp:loan_detail", entity.slug, loan.pk)

            messages.success(request, f"Loan {updated.loan_no} updated.")
            return redirect("LoanApp:loan_detail", entity.slug, updated.pk)
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = LoanEditForm(instance=loan)

    return render(
        request,
        "LoanApp/loan_edit.html",
        {
            "entity": entity,
            "loan": loan,
            "form": form,
        },
    )


# ---------------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------------
@login_required
def loan_delete(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    loan = get_object_or_404(Loan, pk=pk, entity=entity)

    # Block delete if any repayments exist or guarantees have moved
    has_repayments = loan.repayments.exists()
    has_movements = loan.guarantors.filter(
        Q(released_amount__gt=0) | Q(called_amount__gt=0)
    ).exists()

    if has_repayments or has_movements:
        messages.warning(
            request,
            "This loan has repayments or released guarantees and cannot be deleted. "
            "Reverse them first.",
        )
        return redirect("LoanApp:loan_detail", entity.slug, loan.pk)

    if request.method == "POST":
        with transaction.atomic():
            # Release all guarantees held (return money to guarantors)
            for g in loan.guarantors.all():
                # This returns the full holding to the guarantor
                g.release(g.holding)
            # Delete the loan (cascades to guarantees)
            loan_no = loan.loan_no
            loan.delete()

        messages.success(request, f"Loan {loan_no} deleted and guarantees released.")
        return redirect("LoanApp:loan_list", entity.slug)

    return render(
        request,
        "LoanApp/loan_delete.html",
        {
            "entity": entity,
            "loan": loan,
        },
    )


# ---------------------------------------------------------------------------
# PDF / EXCEL
# ---------------------------------------------------------------------------
@login_required
def loan_list_pdf(request, slug):
    

    entity = get_object_or_404(EntityModel, slug=slug)
    cfg = getattr(entity, "config", None)
    loans = (
        Loan.objects.filter(entity=entity)
        .select_related("member")
        .order_by("-date_applied")
    )

    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=landscape(A4),
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    org = cfg.organization_name if cfg else "Organization"

    story = []
    story.append(
        Paragraph(
            escape(org),
            ParagraphStyle(
                "t",
                fontName="Helvetica-Bold",
                fontSize=14,
                alignment=1,
                textColor=colors.HexColor("#1e3a5f"),
            ),
        )
    )
    story.append(
        Paragraph(
            escape(entity.name),
            ParagraphStyle(
                "e",
                fontName="Helvetica-Bold",
                fontSize=11,
                alignment=1,
                textColor=colors.HexColor("#1a56db"),
            ),
        )
    )
    story.append(
        Paragraph(
            "Loan Register",
            ParagraphStyle(
                "r", fontName="Helvetica-Bold", fontSize=12, alignment=1, spaceAfter=10
            ),
        )
    )

    data = [
        ["Loan No.", "Date", "Member", "Principal", "Balance", "Interest", "Status"]
    ]

    for l in loans:
        data.append(
            [
                l.loan_no or "",
                l.date_applied.strftime("%d/%m/%Y") if l.date_applied else "",
                (l.member.full_name if l.member else "")[:30],
                f"{l.principal:,.2f}",
                f"{l.balance:,.2f}",
                f"{l.interest_rate:.2f}%",
                l.status,
            ]
        )

    tbl = Table(data, repeatRows=1)
    tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a56db")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ALIGN", (3, 1), (-1, -1), "RIGHT"),
                ("LINEBELOW", (0, 1), (-1, -1), 0.15, colors.HexColor("#e5e7eb")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(tbl)

    doc.build(story)
    resp = HttpResponse(buf.getvalue(), content_type="application/pdf")
    resp["Content-Disposition"] = f'inline; filename="loans_{entity.slug}.pdf"'
    return resp


@login_required
def loan_list_excel(request, slug):
    from Report.utils import render_excel

    entity = get_object_or_404(EntityModel, slug=slug)
    cfg = getattr(entity, "config", None)
    loans = (
        Loan.objects.filter(entity=entity)
        .select_related("member")
        .order_by("-date_applied")
    )

    headers = [
        "Loan No.",
        "Date Applied",
        "Status",
        "Member",
        "Principal",
        "Balance",
        "Interest Rate",
        "Term (months)",
        "Interest Paid",
        "Principal Paid",
        "Total Guaranteed",
        "Purpose",
    ]

    rows = []
    for l in loans:
        rows.append(
            [
                l.loan_no or "",
                l.date_applied.strftime("%d/%m/%Y") if l.date_applied else "",
                l.status,
                l.member.full_name if l.member else "",
                float(l.principal or 0),
                float(l.balance or 0),
                float(l.interest_rate or 0),
                l.term_months,
                float(l.interest_paid or 0),
                float(l.principal_paid or 0),
                float(l.total_guaranteed or 0),
                l.purpose or "",
            ]
        )

    return render_excel(
        headers,
        rows,
        filename=f"loans_{entity.slug}.xlsx",
        sheet_name="Loans",
        title=(cfg.organization_name if cfg else "Loan Register"),
        subtitle=entity.name,
    )


@login_required
def loan_acceptance_letter(request, slug, pk):
    """Printable loan acceptance letter with schedule."""
    entity = get_object_or_404(EntityModel, slug=slug)
    loan = get_object_or_404(
        Loan.objects.select_related("member").prefetch_related("guarantors__member"),
        pk=pk,
        entity=entity,
    )

    schedule = _generate_schedule(loan)

    return render(
        request,
        "LoanApp/loan_acceptance_letter.html",
        {
            "entity": entity,
            "entity_config": getattr(entity, "config", None),
            "loan": loan,
            "schedule": schedule,
        },
    )


def _generate_schedule(loan):
    """
    Build the amortization schedule for a loan.
    Returns a list of dicts.
    """
    rows = []
    principal = loan.principal or Decimal("0.00")
    rate = loan.interest_rate or Decimal("0.00")
    term = loan.term_months or 0
    moratorium = loan.moratorium_months or 0

    if principal <= 0 or rate <= 0 or term <= 0:
        return rows

    monthly_rate = rate / Decimal("100")
    monthly_principal = (principal / term).quantize(Decimal("0.01"))
    balance = principal
    start = loan.date_disbursed or loan.date_applied

    if not start:
        return rows

    n = 1

    # Moratorium period — interest only
    for i in range(1, moratorium + 1):
        interest = (balance * monthly_rate).quantize(Decimal("0.01"))
        year = start.year
        month = start.month + i
        while month > 12:
            month -= 12
            year += 1
        day = min(start.day, monthrange(year, month)[1])
        rows.append(
            {
                "n": n,
                "date": date(year, month, day),
                "balance": balance,
                "principal": Decimal("0.00"),
                "interest": interest,
                "total": interest,
                "is_moratorium": True,
            }
        )
        n += 1

    # Repayment period
    for i in range(1, term + 1):
        interest = (balance * monthly_rate).quantize(Decimal("0.01"))
        principal_part = monthly_principal
        if principal_part > balance:
            principal_part = balance
        total = principal_part + interest
        balance -= principal_part

        year = start.year
        month = start.month + moratorium + i
        while month > 12:
            month -= 12
            year += 1
        day = min(start.day, monthrange(year, month)[1])

        rows.append(
            {
                "n": n,
                "date": date(year, month, day),
                "balance": max(balance, Decimal("0.00")),
                "principal": principal_part,
                "interest": interest,
                "total": total,
                "is_moratorium": False,
            }
        )
        n += 1
        if balance <= 0:
            break

    return rows


@login_required
def loan_success(request, slug, loan_id):
    entity = get_object_or_404(EntityModel, slug=slug)
    """Loan success page"""
    loan = get_object_or_404(Loan, id=loan_id)
    guarantors = loan.guarantors.all()

    context = {
        "loan": loan,
        "guarantors": guarantors,
    }
    return render(request, "loan_success.html", context)


from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import Sum


def _cu_ledger_codes(entity):
    """Ledger codes for loans, with fallback defaults."""
    cfg = getattr(entity, "config", None)
    return {
        "loan_portfolio": (getattr(cfg, "loan_asset_account_code", None) or "1080"),
        "loan_interest": (getattr(cfg, "loan_interest_income_code", None) or "4010"),
        "penalty_income": "4011",
    }


def _get_account(coa, code):
    try:
        return AccountModel.objects.get(coa_model=coa, code=code)
    except AccountModel.DoesNotExist:
        return None


def _create_repayment_trans(
    *,
    entity,
    loan,
    repayment,
    code,
    amount,
    trans_type,
    ledger_name,
    request,
):
    """Create one Trans row linked to the repayment."""
    coa = entity.get_default_coa()
    acct = _get_account(coa, code)
    if not acct or amount <= 0:
        return None

    ct = ContentType.objects.get_for_model(LoanRepayment)

    return Trans.objects.create(
        entity=entity,
        module="credit_union",
        sub_module="loan_repayment",
        date=repayment.date,
        trans_no=repayment.reference or f"LR-{repayment.id}",
        rec_vou_no=f"LR:{repayment.reference or repayment.id}",
        trans_type=trans_type,
        amount=amount,
        pay_mode="Cash",
        purpose=ledger_name,
        details=f"{ledger_name} — {loan.loan_no} ({loan.member.full_name})",
        member=loan.member,
        member_no=loan.member.id,
        member_name=loan.member.full_name,
        loan=loan,
        ledger_id=str(acct.pk),
        ledger_code=str(acct.code),
        ledger_name=acct.name,
        status="DRAFT",
        journal_status="PENDING",
        source_content_type=ct,
        source_object_id=repayment.id,
        created_by_id=request.user.id,
        created_by_name=request.user.get_full_name() or request.user.username,
        created_by_username=request.user.username,
    )


@login_required
def loan_repayment_view(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    repayment = get_object_or_404(LoanRepayment, pk=pk, entity=entity)
    releases = repayment.guarantor_releases.select_related("guarantor__member")

    return render(
        request,
        "LoanApp/loan_repayment_view.html",
        {
            "entity": entity,
            "repayment": repayment,
            "releases": releases,
        },
    )


@login_required
def loan_repayment_create(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)

    if request.method == "POST":
        form = LoanRepaymentForm(request.POST, entity=entity)

        if form.is_valid():
            d = form.cleaned_data
            loan = d["loan"]
            amount = d["amount"]

            # ---- Split: interest first, remainder to principal ----
            due_interest = loan.due_interest or Decimal("0.00")
            interest_paid = min(due_interest, amount)
            principal_paid = amount - interest_paid
            penalty_paid = Decimal("0.00")

            # ---- Collect pending guarantor releases ----
            pending = []
            total_release = Decimal("0.00")
            for gid, amt in zip(
                request.POST.getlist("guarantor_id"),
                request.POST.getlist("release_amount"),
            ):
                if not gid or not amt:
                    continue
                try:
                    ramt = Decimal(str(amt))
                except Exception:
                    continue
                if ramt <= 0:
                    continue
                g = Guarantor.objects.filter(id=int(gid), loan=loan).first()
                if not g:
                    continue
                if ramt > g.holding:
                    ramt = g.holding
                pending.append({"guarantor_id": g.id, "amount": str(ramt)})
                total_release += ramt

            # ---- Validate: releases must equal principal portion ----
            if pending and abs(total_release - principal_paid) > Decimal("0.01"):
                messages.error(
                    request,
                    f"Total releases (₵{total_release:,.2f}) must equal the "
                    f"loan repayment portion (₵{principal_paid:,.2f}).",
                )
                return redirect("LoanApp:loan_repayment_create", entity.slug)

            # ---- Auto-set ledger ----
            cfg = getattr(entity, "config", None)
            ledger_code = getattr(cfg, "loan_asset_account_code", None) or "1080"
            coa = entity.get_default_coa()
            ledger = AccountModel.objects.filter(
                coa_model=coa, code=ledger_code
            ).first()
            if not ledger:
                messages.error(
                    request, f"Loan ledger account ({ledger_code}) not found."
                )
                return redirect("LoanApp:loan_repayment_create", entity.slug)

            with transaction.atomic():
                repayment = LoanRepayment.objects.create(
                    entity=entity,
                    loan=loan,
                    member=loan.member,
                    date=d["date"],
                    reference=d.get("reference", ""),
                    amount=amount,
                    due_interest_at_payment=due_interest,
                    principal_paid=principal_paid,
                    interest_paid=interest_paid,
                    penalty_paid=penalty_paid,
                    balance_before=loan.balance,
                    balance_after=loan.balance - principal_paid,
                    notes=d.get("notes", ""),
                    pending_releases=pending,
                    posted=False,
                    created_by=request.user,
                )

                trans = Trans.objects.create(
                    entity=entity,
                    module="credit_union",
                    sub_module="loan_repayment",
                    date=repayment.date,
                    trans_no=repayment.reference or f"LR-{repayment.id}",
                    rec_vou_no=f"LR:{repayment.reference or repayment.id}",
                    trans_type="Receipts",
                    amount=amount,
                    pay_mode="Cash",
                    purpose="Loan Repayment",
                    details=f"Loan Repayment — {loan.loan_no} ({loan.member.full_name})",
                    member=loan.member,
                    member_no=loan.member.id,
                    member_name=loan.member.full_name,
                    loan=loan,
                    ledger_id=str(ledger.pk),
                    ledger_code=str(ledger.code),
                    ledger_name=ledger.name,
                    status="DRAFT",
                    journal_status="PENDING",
                    created_by_id=request.user.id,
                    created_by_name=request.user.get_full_name()
                    or request.user.username,
                    created_by_username=request.user.username,
                )

                repayment.trans = trans
                repayment.save(update_fields=["trans"])

            messages.success(
                request,
                f"Repayment ₵{amount:,.2f} recorded "
                f"(interest ₵{interest_paid:,.2f}, principal ₵{principal_paid:,.2f}).",
            )
            return redirect("LoanApp:loan_repayment_create", entity.slug)
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        initial = {"date": timezone.now().date()}
        loan_id = request.GET.get("loan")
        if loan_id and loan_id.isdigit():
            initial["loan"] = loan_id
        form = LoanRepaymentForm(entity=entity, initial=initial)

    # Recent list
    recent = (
        LoanRepayment.objects.filter(entity=entity)
        .select_related("loan", "member", "trans")
        .order_by("-date", "-id")[:50]
    )

    # JSON data for JS
    import json

    loan_data = {}
    for l in (
        Loan.objects.filter(entity=entity)
        .exclude(status__in=[Loan.STATUS_COMPLETED, "Completed"])
        .select_related("member")
    ):
        loan_data[str(l.id)] = {
            "loan_no": l.loan_no,
            "member_name": l.member.full_name,
            "principal": float(l.principal or 0),
            "balance": float(l.balance or 0),
            "due_interest": float(l.due_interest or 0),
            "due_date": (
                l.next_repayment_date.strftime("%d/%m/%Y")
                if l.next_repayment_date
                else ""
            ),
        }

    guarantor_data = {}
    for g in (
        Guarantor.objects.filter(entity=entity)
        .exclude(status=Guarantor.STATUS_RELEASED)
        .select_related("member", "loan")
    ):
        guarantor_data.setdefault(str(g.loan_id), []).append(
            {
                "id": g.id,
                "member_name": g.member.full_name,
                "amount": float(g.amount or 0),
                "holding": float(g.holding or 0),
                "released_amount": float(g.released_amount or 0),
            }
        )

    return render(
        request,
        "LoanApp/loan_repayment.html",
        {
            "entity": entity,
            "form": form,
            "recent": recent,
            "loan_data_json": json.dumps(loan_data),
            "guarantor_data_json": json.dumps(guarantor_data),
        },
    )


@login_required
def loan_repayment_delete(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    repayment = get_object_or_404(LoanRepayment, pk=pk, entity=entity)

    # Block if any linked Trans already posted
    ct = ContentType.objects.get_for_model(LoanRepayment)
    posted = Trans.objects.filter(
        source_content_type=ct,
        source_object_id=repayment.id,
        journal_status="POSTED",
    ).exists()

    if posted:
        messages.warning(
            request, "This repayment is posted to journals. Cannot delete."
        )
        return redirect("LoanApp:loan_repayment_view", entity.slug, repayment.pk)

    if request.method == "POST":
        with transaction.atomic():
            loan = repayment.loan

            # Reverse loan balances
            loan.balance += repayment.principal_paid
            loan.principal_paid -= repayment.principal_paid
            loan.interest_paid -= repayment.interest_paid
            loan.penalty_paid -= repayment.penalty_paid
            loan.refresh_status()
            loan.save()

            # Reverse guarantee releases
            for rel in repayment.guarantor_releases.all():
                g = rel.guarantor
                g.released_amount = max(
                    g.released_amount - rel.amount_released, Decimal("0.00")
                )
                g._refresh_status()
                g.save()

                # Restore Member totals
                g.member.tot_gua_given = (
                    g.member.tot_gua_given or Decimal("0.00")
                ) + rel.amount_released
                g.member.save(update_fields=["tot_gua_given"])

                loan.member.tot_gua_received = (
                    loan.member.tot_gua_received or Decimal("0.00")
                ) + rel.amount_released
                loan.member.save(update_fields=["tot_gua_received"])

            # Delete Trans rows
            Trans.objects.filter(
                source_content_type=ct,
                source_object_id=repayment.id,
            ).delete()

            repayment.delete()

        messages.success(request, "Repayment reversed and deleted.")
        return redirect("LoanApp:loan_repayment_create", entity.slug)

    return render(
        request,
        "LoanApp/loan_repayment_delete.html",
        {
            "entity": entity,
            "repayment": repayment,
        },
    )


def _schedule_pdf_for(loan):
    rows, totals = build_schedule(
        principal=loan.principal,
        monthly_rate_pct=loan.interest_rate,
        term_months=loan.term_months,
        start_date=loan.date_applied,
    )
    return build_loan_schedule_pdf(
        entity=loan.entity,
        member=loan.member,
        loan=loan,
        rows=rows,
        totals=totals,
        generated_on=timezone.now(),
        currency="₵",
    )


@login_required
def loan_schedule_pdf(request, slug, loan_id):
    """
    Stream the PDF.
      ?disposition=inline      → preview in browser
      ?disposition=attachment  → download (default)
    """
    loan = get_object_or_404(Loan, pk=loan_id, entity__slug=slug)
    pdf = _schedule_pdf_for(loan)

    disposition = request.GET.get("disposition", "attachment")
    filename = f"Loan_Schedule_{loan.loan_no or loan.pk}.pdf"

    resp = HttpResponse(pdf, content_type="application/pdf")
    resp["Content-Disposition"] = f'{disposition}; filename="{filename}"'
    return resp


@login_required
@require_POST
def loan_schedule_email(request, slug, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id, entity__slug=slug)

    to = (request.POST.get("email") or "").strip()
    note = (
        request.POST.get("message") or ""
    ).strip() or "Please find attached your loan repayment schedule."

    if not to:
        messages.error(request, "No recipient email provided.")
        return redirect("Loans:loan_detail", slug=slug, loan_id=loan.pk)

    pdf = _schedule_pdf_for(loan)

    subject = f"Loan Repayment Schedule — {loan.loan_no or loan.pk}"
    email = EmailMessage(subject, note, to=[to])
    email.attach(
        f"Loan_Schedule_{loan.loan_no or loan.pk}.pdf",
        pdf,
        "application/pdf",
    )
    email.send(fail_silently=False)

    messages.success(request, f"Schedule emailed to {to}.")
    return redirect("Loans:loan_detail", slug=slug, loan_id=loan.pk)


from decimal import Decimal, InvalidOperation
from datetime import datetime
from io import BytesIO

from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils import timezone


from .pdf import build_loan_schedule_pdf


# ---------- A. PREVIEW from the application form (no loan_id yet) ----------
@login_required
@require_POST
def loan_schedule_preview_pdf(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)

    try:
        principal = Decimal(request.POST["principal"])
        rate = Decimal(request.POST["interest_rate"])
        term = int(request.POST["term_months"])
        start = datetime.strptime(request.POST["date_applied"], "%Y-%m-%d").date()
    except (KeyError, InvalidOperation, ValueError) as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=400)

    # Lightweight shims — no DB writes
    loan = {
        "loan_no": "PREVIEW",
        "principal": principal,
        "interest_rate": rate,
        "term_months": term,
        "date_applied": start,
        "purpose": request.POST.get("purpose", ""),
    }
    member = {
        "full_name": request.POST.get("member_name", ""),
        "member_no": "",
    }

    rows, totals = build_schedule(principal, rate, term, start)
    pdf = build_loan_schedule_pdf(
        entity=entity,
        member=member,
        loan=loan,
        rows=rows,
        totals=totals,
        generated_on=timezone.now(),
        currency="₵",
        footer_text="PREVIEW ONLY — loan not yet booked",
    )

    resp = HttpResponse(pdf, content_type="application/pdf")
    resp["Content-Disposition"] = 'inline; filename="Loan_Schedule_PREVIEW.pdf"'
    return resp


# ---------- B. PRINT from the Loan list / detail (loan exists) ----------
@login_required
def loan_schedule_pdf(request, slug, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id, entity__slug=slug)

    rows, totals = build_schedule(
        principal=loan.principal,
        monthly_rate_pct=loan.interest_rate,
        term_months=loan.term_months,
        start_date=loan.date_applied,
    )
    pdf = build_loan_schedule_pdf(
        entity=loan.entity,
        member=loan.member,
        loan=loan,
        rows=rows,
        totals=totals,
        generated_on=timezone.now(),
        currency="₵",
    )

    disposition = request.GET.get("disposition", "inline")  # default: preview in tab
    filename = f"Loan_Schedule_{loan.loan_no or loan.pk}.pdf"

    resp = HttpResponse(pdf, content_type="application/pdf")
    resp["Content-Disposition"] = f'{disposition}; filename="{filename}"'
    return resp

# ------------------------------------------------------------------
# Loan schedule PDF — two entry points, one builder
# ------------------------------------------------------------------


@login_required
@require_POST
def loan_schedule_preview_pdf(request, slug):
    """Preview from the application form — loan not saved yet."""
    entity = get_object_or_404(EntityModel, slug=slug)

    try:
        principal = Decimal(request.POST["principal"])
        rate = Decimal(request.POST["interest_rate"])
        term = int(request.POST["term_months"])
        start = datetime.strptime(request.POST["date_applied"], "%Y-%m-%d").date()
    except (KeyError, InvalidOperation, ValueError) as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=400)

    loan = {
        "loan_no": "PREVIEW",
        "principal": principal,
        "interest_rate": rate,
        "term_months": term,
        "date_applied": start,
        "purpose": request.POST.get("purpose", ""),
    }
    member = {
        "full_name": request.POST.get("member_name", ""),
        "member_no": "",
    }

    rows, totals = build_schedule(principal, rate, term, start)
    pdf = build_loan_schedule_pdf(
        entity=entity,
        member=member,
        loan=loan,
        rows=rows,
        totals=totals,
        generated_on=timezone.now(),
        currency="₵",
        footer_text="PREVIEW ONLY — loan not yet booked",
    )

    resp = HttpResponse(pdf, content_type="application/pdf")
    resp["Content-Disposition"] = 'inline; filename="Loan_Schedule_PREVIEW.pdf"'
    return resp


@login_required
def loan_schedule_pdf(request, slug, loan_id):
    """Print/download from the Loan List — loan exists."""
    loan = get_object_or_404(Loan, pk=loan_id, entity__slug=slug)

    rows, totals = build_schedule(
        loan.principal,
        loan.interest_rate,
        loan.term_months,
        loan.date_applied,
    )
    pdf = build_loan_schedule_pdf(
        entity=loan.entity,
        member=loan.member,
        loan=loan,
        rows=rows,
        totals=totals,
        generated_on=timezone.now(),
        currency="₵",
    )

    disposition = request.GET.get("disposition", "inline")
    filename = f"Loan_Schedule_{loan.loan_no or loan.pk}.pdf"

    resp = HttpResponse(pdf, content_type="application/pdf")
    resp["Content-Disposition"] = f'{disposition}; filename="{filename}"'
    return resp


## #####################################Old Views####################################
