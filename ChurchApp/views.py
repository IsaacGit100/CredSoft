# Create your views here.

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django_ledger.models import (EntityModel, LedgerModel, JournalEntryModel, AccountModel, TransactionModel)
from decimal import Decimal
from django.utils import timezone
from datetime import datetime
from django.db.models import Q, Sum, Count
from django.db import transaction


from .models import Role   

from .models import Service, Member, Event, Guild, Clergy, Role, MemberRole, ChurchConfig
from .forms import ServiceForm, GuildForm, ClergyForm, MemberForm, RoleAssignmentForm, MemberRoleForm
from .forms import DuesTitheTransactionForm, ServiceActivityForm, ChurchConfigForm
from MembersApp.models import Master
from RecPayApp.models import Trans

from djan_led.utils import get_visible_accounts


from LoanApp.models import Loan

from django.db import transaction, models
from django.contrib.contenttypes.models import ContentType

from services.journal_engine import JournalEngine  # adjust import path

import json
from django.http import JsonResponse
from django.core.paginator import Paginator

# ChurchApp/views.py

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import io
from openpyxl import Workbook
from io import BytesIO

from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.worksheet.page import PageMargins

from django.core.paginator import Paginator

from django.http import HttpResponse
from datetime import datetime, timedelta

from django.urls import reverse

from Report.pdf_builder import Col, build_report_pdf
from Report.utils import render_excel




from datetime import datetime
from io import BytesIO
from django.shortcuts import render, get_object_or_404

from Report.pdf_builder import Col, build_report_pdf
from Report.utils import parse_date, render_excel, for_period_label

from .models import Member, MemberContribution





@login_required
def church_home(request, slug):
    pass

@login_required
def service_home(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    services = Service.objects.filter(entity=entity).order_by("-date")
    context = {
        "entity": entity,
        "services": services,
    }
    return render(request, "ChurchApp/service_home.html", context)  

@login_required
def supervisor_church(request, slug):
    return render(request, "ChurchApp/supervisor_church.html", {"entity_slug": slug})


@login_required
@staff_member_required
def church_dashboard(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)

    # Filter all church models by this entity
    members = Member.objects.filter(entity=entity)
  #  offerings = Offering.objects.filter(entity=entity)
    events = Event.objects.filter(entity=entity)
  #  finances = FinancialRecord.objects.filter(entity=entity)

    context = {
        "entity": entity,
        "total_members": members.count(),
#        "total_offerings": offerings.aggregate(total=Sum("amount"))["total"] or 0,
        "total_events": events.count(),
#        "recent_offerings": offerings.order_by("-date")[:5],
        "upcoming_events": events.filter(date__gte=timezone.now().date()).order_by(
            "date"
        )[:5],
    }
    return render(request, "ChurchApp/church_dashboard.html", context)


@login_required
def member_list_manage(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    members = Member.objects.filter(entity=entity, is_deleted=False).order_by(
        "-created_at"
    )
    # members = Member.objects.filter(entity=entity).order_by("-created_at")
    q = request.GET.get("q")
    if q:
        members = members.filter(full_name__icontains=q)
    context = {
        "entity": entity,
        "members": members,
    }
    return render(request, "ChurchApp/member_list_manage.html", context)


def member_create(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    if request.method == "POST":
        form = MemberForm(request.POST, entity=entity)
        if form.is_valid():
            member = form.save(commit=False)
            member.entity = entity
            member.save()
            messages.success(request, "Member created.")
            return redirect("ChurchApp:member_list_manage", slug=entity.slug)
    else:
        form = MemberForm(entity=entity)
    return render(request, 'ChurchApp/member_create.html', {'form': form, "entity": entity})


@login_required
def member_edit(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    member = get_object_or_404(Member, pk=pk, entity=entity, is_deleted=False)

    if request.method == "POST":
        form = MemberForm(request.POST, request.FILES, instance=member, entity=entity)

        if form.is_valid():
            with transaction.atomic():
                updated = form.save(commit=False)
                updated.entity = entity
                updated.save()
                form.save_m2m()  # if the form has M2M (roles)

            messages.success(request, f"Member '{updated.full_name}' updated.")
            return redirect("ChurchApp:member_detail", entity.slug, updated.pk)

        # Invalid — fall through, bound form renders with errors
    else:
        form = MemberForm(instance=member, entity=entity)

    context = {
        "entity": entity,
        "form": form,
        "member": member,  # template uses {% if member %} to switch mode
        "title": f"Edit Member — {member.full_name}",
    }
    return render(request, "ChurchApp/member_form.html", context)


@login_required
def member_detail(request, slug, pk):
    """
    Display detailed information about a single member.
    """
    entity = get_object_or_404(EntityModel, slug=slug)
    member = get_object_or_404(Member, pk=pk, entity=entity)

    context = {
        "entity": entity,
        "member": member,
        "title": f"Member Details: {member.full_name}",
    }
    return render(request, "ChurchApp/member_detail.html", context)


@login_required
@staff_member_required
def member_delete(request, slug, pk):
    """Soft-delete a member — sets is_deleted=True, no row is removed."""
    entity = get_object_or_404(EntityModel, slug=slug)
    member = get_object_or_404(Member, pk=pk, entity=entity)

    if request.method == "POST":
        member.is_deleted = True
        member.save(update_fields=["is_deleted", "updated_at"])
        messages.success(
            request,
            f"Member '{member.full_name}' has been removed from the active list.",
        )
        return redirect("ChurchApp:member_list_manage", entity.slug)

    # GET — show a confirm page (optional; you can also just POST from the list)
    return render(request, "ChurchApp/member_delete_confirm.html", {
        "entity": entity,
        "member": member,
    })


@login_required
@staff_member_required
def member_restore(request, slug, pk):
    """Restore a soft-deleted member — sets is_deleted=False."""
    entity = get_object_or_404(EntityModel, slug=slug)
    member = get_object_or_404(Member, pk=pk, entity=entity)

    if request.method == "POST":
        member.is_deleted = False
        member.save(update_fields=["is_deleted", "updated_at"])
        messages.success(request, f"Member '{member.full_name}' restored.")
        return redirect("ChurchApp:member_list_manage", entity.slug)

    return redirect("ChurchApp:member_list_manage", entity.slug)
    return render(
        request,
        "ChurchApp/member_confirm_restore.html",
        {"entity": entity, "member": member},
    )


def _member_to_rows(member):
    """Return a list of (label, value) tuples for a member — used by PDF & Excel."""
    return [
        ("PERSONAL DETAILS", ""),
        ("Title", member.get_title_display() if member.title else ""),
        ("First Name", member.first_name or ""),
        ("Other Names", member.other_names or ""),
        ("Last Name", member.last_name or ""),
        ("Email", member.email or ""),
        ("Telephone 1", member.telephone1 or ""),
        ("Telephone 2", member.telephone2 or ""),
        ("Ghana Card No.", member.ghana_card_no or ""),
        (
            "Date of Birth",
            member.date_of_birth.strftime("%d/%m/%Y") if member.date_of_birth else "",
        ),
        (
            "Education",
            member.get_education_level_display() if member.education_level else "",
        ),
        ("Profession", member.profession or ""),
        ("Postal Address", member.postal_address or ""),
        ("Res. Address", member.res_address or ""),
        ("Near Landmark", member.near_landmark or ""),
        ("CHURCH DETAILS", ""),
        (
            "Date Baptised",
            member.date_baptised.strftime("%d/%m/%Y") if member.date_baptised else "",
        ),
        (
            "Date Confirmed",
            member.date_confirmed.strftime("%d/%m/%Y") if member.date_confirmed else "",
        ),
        (
            "Date Enrolled",
            member.date_enrolled.strftime("%d/%m/%Y") if member.date_enrolled else "",
        ),
        (
            "Date Expired",
            member.date_expired.strftime("%d/%m/%Y") if member.date_expired else "",
        ),
        ("Guild (1st)", member.guild_first or ""),
        ("Guild (2nd)", member.guild_second or ""),
        ("Guild (3rd)", member.guild_third or ""),
        ("No. of Children", member.no_of_children or 0),
        ("Roles", ", ".join(member.get_role_names()) or ""),
        ("Total Tithe", float(member.tot_tithe or 0)),
        ("Total Dues", float(member.tot_dues or 0)),
        ("Total Special", float(member.tot_special_offering or 0)),
        ("OFFICE INFORMATION", ""),
        ("Office Name", member.office_name or ""),
        ("Office Phone", member.office_phone or ""),
        ("Office Email", member.office_email or ""),
        ("Nature of Business", member.nature_of_business or ""),
        ("Office Address", member.office_address or ""),
        ("Office Res. Addr.", member.office_res_address or ""),
        ("SPOUSE INFORMATION", ""),
        (
            "Spouse Title",
            member.get_spouse_title_display() if member.spouse_title else "",
        ),
        ("Spouse Name", member.spouse_name or ""),
        ("Spouse Phone", member.spouse_telephone or ""),
        ("Spouse Email", member.spouse_email_address or ""),
        (
            "Spouse DOB",
            (
                member.spouse_date_of_birth.strftime("%d/%m/%Y")
                if member.spouse_date_of_birth
                else ""
            ),
        ),
        ("Spouse Religion", member.spouse_religion or ""),
        (
            "Spouse Education",
            (
                member.get_spouse_education_level_display()
                if member.spouse_education_level
                else ""
            ),
        ),
        ("Spouse Occupation", member.spouse_occupation or ""),
        ("Spouse Company", member.spouse_company_name or ""),
        ("Spouse Church", member.spouse_church or ""),
        ("PARENTS", ""),
        ("Father's Name", member.father_name or ""),
        ("Father's Phone", member.father_telephone or ""),
        ("Father Deceased", "Yes" if member.father_deceased else "No"),
        ("Mother's Name", member.mother_name or ""),
        ("Mother's Phone", member.mother_telephone or ""),
        ("Mother Deceased", "Yes" if member.mother_deceased else "No"),
    ]


@login_required
@staff_member_required
def member_pdf(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    cfg = getattr(entity, "config", None)
    member = get_object_or_404(Member, pk=pk, entity=entity, is_deleted=False)

    rows = _member_to_rows(member)

    pdf_bytes = build_report_pdf(
        entity=entity,
        entity_config=cfg,
        report_title=f"Member Profile — {member.full_name}",
        period_label="",
        columns=[
            Col("Field", 35, "left"),
            Col("Value", 65, "left"),
        ],
        rows=rows,
        totals=None,
        filename=f"member_{member.pk}.pdf",
    )

    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    mode = "attachment" if request.GET.get("download") == "1" else "inline"
    response["Content-Disposition"] = (
        f'{mode}; filename="member_{member.pk}_{timezone.now():%Y%m%d}.pdf"'
    )
    return response


@login_required
@staff_member_required
def member_excel(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    cfg = getattr(entity, "config", None)
    member = get_object_or_404(Member, pk=pk, entity=entity, is_deleted=False)

    rows = _member_to_rows(member)

    return render_excel(
        headers=["Field", "Value"],
        rows=[[label, value] for label, value in rows],
        filename=f"member_{member.pk}_{timezone.now():%Y%m%d}.xlsx",
        sheet_name="Member",
        title=(cfg.organization_name if cfg else "Member Profile"),
        subtitle=member.full_name,
    )


@login_required
def service_list_manage(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    services = Service.objects.filter(entity=entity).order_by("-date")
    # Search
    q = request.GET.get("q")
    if q:
        services = services.filter(date__icontains=q) | services.filter(
            name_of_service__icontains=q
        )
    context = {
        "entity": entity,
        "services": services,
    }
    return render(request, "ChurchApp/service_list_manage.html", context)


@login_required
def service_post_to_ledger(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    service = get_object_or_404(Service, pk=pk, entity=entity)
    if service.posted_to_ledger:
        messages.warning(request, "Already posted.")
        return redirect("ChurchApp:service_detail", slug=slug, pk=pk)

    ledger = LedgerModel.objects.filter(entity=entity).first()
    if not ledger:
        ledger = LedgerModel.objects.create(entity=entity, name="Default Ledger")

    coa = entity.get_default_coa()
    if not coa:
        messages.error(request, "No Chart of Accounts.")
        return redirect("ChurchApp:service_list", slug=slug)

    # Map accounts – you need to create these in your COA
    account_map = {
        "general_offertory": "4010",  # General Offertory
        "day_born": "4011",  # DayBorn Offerings
        "guild": "4012",  # Guild Offerings
        "dues": "4013",  # Dues
        "tithes": "4014",  # Tithes
        "special_thank": "4015",  # Special Thank Offering
        "easter": "4016",  # Easter Offering
        "christmas": "4017",  # Christmas Offering
        "harvest": "4018",  # Harvest Offering
        "other": "4019",  # Other Collections
    }

    # Get Cash account (asset)
    try:
        cash = AccountModel.objects.get(coa_model=coa, code="1010")
    except AccountModel.DoesNotExist:
        messages.error(request, "Cash account not found.")
        return redirect("ChurchApp:service_detail", slug=slug, pk=pk)

    je = JournalEntryModel.objects.create(
        ledger=ledger,
        timestamp=service.date,
        description=f"Sunday Service: {service.name_of_service} - {service.date}",
        posted=False,
    )

    # Debit Cash for total offerings (grand_total)
    TransactionModel.objects.create(
        journal_entry=je,
        account=cash,
        amount=service.grand_total,
        tx_type="debit",
    )

    # Helper to add credit transactions
    def add_credit(amount, account_code):
        if amount <= 0:
            return
        try:
            acc = AccountModel.objects.get(coa_model=coa, code=account_code)
            TransactionModel.objects.create(
                journal_entry=je,
                account=acc,
                amount=amount,
                tx_type="credit",
            )
        except AccountModel.DoesNotExist:
            messages.warning(request, f"Account {account_code} not found. Skipping.")

    # Add credits for each offering type
    add_credit(service.general_offertory, account_map["general_offertory"])

    # DayBorn offerings – sum all day amounts
    day_total = (
        sum(service.day_born_offerings.values())
        if isinstance(service.day_born_offerings, dict)
        else 0
    )
    add_credit(day_total, account_map["day_born"])

    # Guild offerings – sum all guild amounts
    guild_total = sum(
        item.get("amount", 0)
        for item in service.guild_offerings
        if isinstance(item, dict)
    )
    add_credit(guild_total, account_map["guild"])

    add_credit(service.dues, account_map["dues"])
    add_credit(service.tithes, account_map["tithes"])

    # Special Thank Offering
    special_total = sum(
        item.get("amount", 0)
        for item in service.special_thank_offering
        if isinstance(item, dict)
    )
    add_credit(special_total, account_map["special_thank"])

    easter_total = sum(
        item.get("amount", 0)
        for item in service.easter_offering
        if isinstance(item, dict)
    )
    add_credit(easter_total, account_map["easter"])

    christmas_total = sum(
        item.get("amount", 0)
        for item in service.christmas_offering
        if isinstance(item, dict)
    )
    add_credit(christmas_total, account_map["christmas"])

    harvest_total = sum(
        item.get("amount", 0)
        for item in service.harvest_offering
        if isinstance(item, dict)
    )
    add_credit(harvest_total, account_map["harvest"])

    other_total = sum(
        item.get("amount", 0)
        for item in service.other_collections
        if isinstance(item, dict)
    )
    add_credit(other_total, account_map["other"])

    # Post the journal
    je.posted = True
    je.save()

    service.posted_to_ledger = True
    service.journal_entry_id = je.uuid
    service.save()

    messages.success(request, f"Service posted to ledger with Journal Entry {je.uuid}.")
    return redirect("ChurchApp:service_detail", slug=slug, pk=pk)

# ====================================== Clergy CRUD ====================================
@login_required
@staff_member_required
def clergy_list_manage(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    clergy_list = Clergy.objects.filter(entity=entity)
    context = {
        "entity": entity,
        "clergy_list": clergy_list,
        "total_clergy": clergy_list.count(),
    }
    return render(request, "ChurchApp/clergy_list_manage.html", context)


@login_required
@staff_member_required
def clergy_create(request, slug):
    print(f">>> clergy_create HIT: method={request.method}, path={request.path}")
    print(f">>> POST keys: {list(request.POST.keys())}")

    entity = get_object_or_404(EntityModel, slug=slug)

    if request.method == "POST":
        print(">>> Entering POST branch")
        form = ClergyForm(request.POST, entity=entity)
        print(f">>> Form valid? {form.is_valid()}")
        if not form.is_valid():
            print(f">>> Form errors: {form.errors}")
        if form.is_valid():
            clergy = form.save(commit=False)
            clergy.entity = entity
            clergy.save()
            messages.success(request, f"Clergy {clergy.full_name} created.")
            return redirect("ChurchApp:clergy_list_manage", slug=entity.slug)
    else:
        form = ClergyForm(entity=entity)

    context = {
        "entity": entity,
        "form": form,
        "title": "Add Clergy",
    }
    return render(request, "ChurchApp/clergy_create.html", context)


@staff_member_required
def clergy_edit(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    clergy = get_object_or_404(Clergy, pk=pk, entity=entity)
    if request.method == "POST":
        form = ClergyForm(request.POST, instance=clergy, entity=entity)
        if form.is_valid():
            form.save()
            messages.success(request, f"Clergy {clergy.full_name} updated.")
            return redirect("ChurchApp:clergy_list_manage", slug=entity.slug)
    else:
        form = ClergyForm(instance=clergy, entity=entity)
    context = {
        "entity": entity,
        "form": form,
        "clergy": clergy,
        "title": f"Edit Clergy: {clergy.full_name}",
    }
    return render(request, "ChurchApp/clergy_create.html", context)


@staff_member_required
def clergy_delete(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    clergy = get_object_or_404(Clergy, pk=pk, entity=entity)
    if request.method == "POST":
        clergy.delete()
        messages.success(request, f"Clergy {clergy.full_name} deleted.")
        return redirect("ChurchApp:clergy_list_manage", slug=entity.slug)
    context = {
        "entity": entity,
        "clergy": clergy,
    }
    return render(request, "ChurchApp/clergy_confirm_delete.html", context)


@staff_member_required
def clergy_detail(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    clergy = get_object_or_404(Clergy, pk=pk, entity=entity)
    context = {
        "entity": entity,
        "clergy": clergy,
    }
    return render(request, "ChurchApp/clergy_detail.html", context)


@login_required
@staff_member_required
def usher_delete(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    usher = get_object_or_404(Ushers, pk=pk, entity=entity)
    if request.method == "POST":
        usher.delete()
        messages.success(request, f"Usher {usher.name} deleted successfully.")
        return redirect("ChurchApp:usher_list_manage", slug=entity.slug)
    context = {
        "entity": entity,
        "usher": usher,
    }
    return render(request, "ChurchApp/usher_confirm_delete.html", context)


@staff_member_required
def usher_detail(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    usher = get_object_or_404(Ushers, pk=pk, entity=entity)
    context = {
        "entity": entity,
        "usher": usher,
    }
    return render(request, "ChurchApp/usher_detail.html", context)

## ====================================Service Modules =======================
@staff_member_required
def service_create(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)

    if request.method == "POST":
        form = ServiceForm(request.POST)
        if form.is_valid():
            # Save the Service
            service = form.save(commit=False)
            service.entity = entity
            service.created_by = request.user
            service.created_at = timezone.now()
            service.updated_at = timezone.now()
            service.save()

            # Create a Trans record for approval
            # This will be posted to journal after approval
            trans = Trans.objects.create(
                entity=entity,
                trans_type="Receipts",  # Service offerings are receipts
                date=service.date,
                amount=service.grand_total,
                pay_mode="Cash",  # You can make this dynamic
                ledger_code="4010",  # Offering income account
                ledger_name="Service Offerings",
                details=f"Service: {service.name_of_service} on {service.date}",
                status="PENDING",  # Needs approval
                created_by=request.user,
                created_by_name=request.user.username,
                created_by_username=request.user.username,
                # Link back to service
                service=service,
            )

            messages.success(
                request,
                f"Service saved. Trans record created for approval (Ref: {trans.rec_vou_no})",
            )
            return redirect("ChurchApp:service_list", slug=entity.slug)
    else:
        form = ServiceForm(initial={"date": timezone.now().date()})

    context = {
        "entity": entity,
        "form": form,
        "title": "Add Service",
    }
    return render(request, "ChurchApp/service_form.html", context)


@staff_member_required
def service_update(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    service = get_object_or_404(Service, pk=pk, entity=entity)
    if request.method == "POST":
        form = ServiceForm(request.POST, instance=service, entity=entity)
        if form.is_valid():
            service = form.save(commit=False)
            service.updated_at = timezone.now()
            service.save()

            # Post to ledger if checked and not already posted (or allow repost?)
            if (
                form.cleaned_data.get("post_to_ledger", False)
                and not service.posted_to_ledger
            ):
                try:
                    journal_entry = create_service_journal(service, entity)
                    service.journal_entry_id = str(journal_entry.uuid)
                    service.posted_to_ledger = True
                    service.save(update_fields=["journal_entry_id", "posted_to_ledger"])
                    messages.success(request, "Service updated and posted to ledger.")
                except Exception as e:
                    messages.warning(
                        request, f"Service updated, but journal entry failed: {e}"
                    )
            else:
                messages.info(request, "Service updated without ledger posting.")

            return redirect("ChurchApp:service_list", slug=entity.slug)
    else:
        form = ServiceForm(instance=service, entity=entity)

    context = {
        "entity": entity,
        "form": form,
        "service": service,
        "title": f"Edit Service: {service.name_of_service}",
    }
    return render(request, "ChurchApp/service_form.html", context)


def create_service_journal(service, entity):
    """
    Create a journal entry for the service offerings using JournalEngine.
    Returns the journal entry object.
    """
    engine = JournalEngine(entity.slug)

    # Prepare account codes (you can store these in EntityConfig)
    # Typically: cash account = 1010 (or bank = 1020), income accounts for different types
    # We'll use a general offering income account (e.g., 4010) and separate accounts if needed.
    from decimal import Decimal

    total_offerings = service.grand_total
    if total_offerings <= 0:
        return None

    # For simplicity, we credit a single income account for all offerings.
    # In a real system, you might split by offering type.
    income_account_code = (
        "4010"  # Interest Income (or create a specific Offering Income)
    )
    cash_account_code = "1010"  # Cash

    description = f"Service: {service.name_of_service} on {service.date}"

    journal = engine.record_transaction(
        amount=total_offerings,
        debit_account_code=cash_account_code,
        credit_account_code=income_account_code,
        description=description,
        date=service.date,
    )
    return journal


@staff_member_required
def clergy_list_modal(request, slug):
    """
    Display clergy list and handle AJAX form submission.
    """
    entity = get_object_or_404(EntityModel, slug=slug)
    clergy_list = Clergy.objects.filter(entity=entity).order_by("last_name")

    # Handle AJAX POST request (when modal form is submitted)
    if (
        request.method == "POST"
        and request.headers.get("X-Requested-With") == "XMLHttpRequest"
    ):
        form = ClergyForm(request.POST, entity=entity)
        if form.is_valid():
            clergy = form.save(commit=False)
            clergy.entity = entity
            clergy.save()
            return JsonResponse(
                {
                    "success": True,
                    "message": f"Clergy {clergy.full_name} added successfully!",
                    "clergy": {
                        "id": clergy.id,
                        "title": clergy.title,
                        "full_name": clergy.full_name,
                        "email_address": clergy.email_address,
                        "telephone": clergy.telephone,
                        "member_name": clergy.member.full_name if clergy.member else "",
                    },
                }
            )
        else:
            return JsonResponse({"success": False, "errors": form.errors}, status=400)

    # GET request - render the page
    context = {
        "entity": entity,
        "clergy_list": clergy_list,
        "total_clergy": clergy_list.count(),
    }
    return render(request, "ChurchApp/clergy_list.html", context)

@staff_member_required
def clergy_delete_modal(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    clergy = get_object_or_404(Clergy, pk=pk, entity=entity)

    if request.method == "POST":
        clergy.delete()
        return JsonResponse(
            {
                "success": True,
                "message": f"Clergy {clergy.full_name} deleted successfully.",
            }
        )

    return JsonResponse({"success": False, "message": "Invalid request."}, status=400)


@login_required
def clergy_edit_modal(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    clergy = get_object_or_404(Clergy, pk=pk, entity=entity)

    if (
        request.method == "POST"
        and request.headers.get("X-Requested-With") == "XMLHttpRequest"
    ):
        form = ClergyForm(request.POST, instance=clergy, entity=entity)
        if form.is_valid():
            clergy = form.save()
            return JsonResponse(
                {
                    "success": True,
                    "message": f"Clergy {clergy.full_name} updated successfully!",
                    "clergy": {
                        "id": clergy.id,
                        "title": clergy.title,
                        "full_name": clergy.full_name,
                        "email_address": clergy.email_address,
                        "telephone": clergy.telephone,
                    },
                }
            )
        else:
            return JsonResponse({"success": False, "errors": form.errors}, status=400)

    # GET request – return form data as JSON
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse(
            {
                "id": clergy.id,
                "title": clergy.title,
                "first_name": clergy.first_name,
                "other_names": clergy.other_names,
                "last_name": clergy.last_name,
                "email_address": clergy.email_address,
                "telephone": clergy.telephone,
                "postal_address": clergy.postal_address,
                "res_address": clergy.res_address,
                "date_arrived": clergy.date_arrived,
                "date_depart": clergy.date_depart,
                "member": clergy.member.id if clergy.member else "",
            }
        )

    # Fallback: render edit page
    context = {
        "entity": entity,
        "form": ClergyForm(instance=clergy, entity=entity),
        "clergy": clergy,
        "title": f"Edit Clergy: {clergy.full_name}",
    }
    return render(request, "ChurchApp/clergy_form.html", context)

def church_data_entry_home(request, slug):
    return render(request, 'ChurchApp/church_data_entry_home.html')

# ===================================Role Management==========================
@login_required
def role_management(request, slug):
    """
    List all members with their roles.
    """
    entity = get_object_or_404(EntityModel, slug=slug)
    members = Member.objects.filter(entity=entity, is_deleted=False).order_by(
        "full_name"
    )

    context = {
        "entity": entity,
        "members": members,
        "total_members": members.count(),
        "roles": Role.objects.filter(entity=entity).order_by("display_name"),
    }
    return render(request, "ChurchApp/role_management.html", context)

@login_required
@staff_member_required
def member_roles_edit(request, slug, pk):
    """
    Edit roles for a specific member.
    """
    entity = get_object_or_404(EntityModel, slug=slug)
    member = get_object_or_404(Member, pk=pk, entity=entity)

    if request.method == "POST":
        form = MemberRoleForm(request.POST, entity=entity, member=member)

        if form.is_valid():
            form.save(member)

            messages.success(request, f"Roles updated for {member.full_name}")

            return redirect("ChurchApp:role_management", slug=entity.slug)
    else:
        form = MemberRoleForm(entity=entity, member=member)

    context = {
        "entity": entity,
        "member": member,
        "form": form,
        "title": f"Manage Roles: {member.full_name}",
        "roles": Role.objects.filter(entity=entity).order_by("display_name"),
    }

    return render(request, "ChurchApp/member_roles_edit.html", context)


@login_required
@staff_member_required
def role_create(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        display_name = request.POST.get("display_name", "").strip()
        description = request.POST.get("description", "").strip()

        if not name or not display_name:
            messages.error(request, "Name and Display Name are required.")
        else:
            Role.objects.create(
                entity=entity,
                name=name.lower().replace(" ", "_"),
                display_name=display_name,
                description=description,
            )
            messages.success(request, f"Role '{display_name}' created.")
            return redirect("ChurchApp:role_create", slug=slug)   # stay on the page

    return render(request, "ChurchApp/role_create.html", {
        "entity": entity,
        "roles":  Role.objects.filter(entity=entity).order_by("display_name"),
        "title":  "Create New Role",
    })

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django_ledger.models import EntityModel

from .models import Role  # adjust to your actual model name


@login_required
def role_update(request, slug, pk):
    """
    Edit an existing role.
    Split layout: form on left, list on right (with the current one highlighted).
    """
    entity = get_object_or_404(EntityModel, slug=slug)
    role = get_object_or_404(Role, pk=pk, entity=entity)

    if request.method == "POST":
        name = (request.POST.get("name") or "").strip()
        display_name = (request.POST.get("display_name") or "").strip()
        description = (request.POST.get("description") or "").strip()

        errors = []
        if not name:
            errors.append("Role Name is required.")
        if not display_name:
            errors.append("Display Name is required.")

        # uniqueness check (excluding this role)
        clean_name = name.lower().replace(" ", "_")
        if (
            Role.objects.filter(entity=entity, name=clean_name)
            .exclude(pk=role.pk)
            .exists()
        ):
            errors.append(f"A role with the name '{clean_name}' already exists.")

        if errors:
            for e in errors:
                messages.error(request, e)
        else:
            role.name = clean_name
            role.display_name = display_name
            role.description = description
            role.save()
            messages.success(request, f"Role '{display_name}' updated.")
            return redirect("ChurchApp:role_update", slug=entity.slug, pk=role.pk)

    return render(
        request,
        "ChurchApp/role_update.html",
        {
            "entity": entity,
            "role": role,
            "roles": Role.objects.filter(entity=entity).order_by("display_name"),
            "title": f"Edit Role — {role.display_name}",
        },
    )
    # adjust to your actual model name


@login_required
def role_delete(request, slug, pk):
    """
    Delete a role.
    GET  → show confirmation page with any dependents.
    POST → perform the delete, return to the role list.
    """
    entity = get_object_or_404(EntityModel, slug=slug)
    role = get_object_or_404(Role, pk=pk, entity=entity)

    if request.method == "POST":
        display = role.display_name
        with transaction.atomic():
            role.delete()
        messages.success(request, f"Role '{display}' deleted.")
        return redirect("ChurchApp:role_management", slug=entity.slug)

    # --- detect dependents: every FK in every app pointing at Role ---
    from django.apps import apps

    dependents = {}

    for model in apps.get_models():
        for f in model._meta.fields:
            if f.get_internal_type() != "ForeignKey":
                continue
            if f.remote_field and f.remote_field.model == Role:
                count = model.objects.filter(**{f.name: role}).count()
                if count:
                    label = model._meta.verbose_name_plural.title()
                    dependents[label] = count

    return render(
        request,
        "ChurchApp/role_delete.html",
        {
            "entity": entity,
            "role": role,
            "dependents": dependents,
            "can_delete": True,
        },
    )


@login_required
@staff_member_required
def member_roles_detail(request, slug, pk):
    """
    Display detailed roles information for a specific member.
    """
    entity = get_object_or_404(EntityModel, slug=slug)
    member = get_object_or_404(Member, pk=pk, entity=entity)

    # Get all roles for this member (active and inactive)
    member_roles = (
        member.member_roles.all()
        .select_related("role")
        .order_by("-is_active", "-date_assigned")
    )

    # Separate active and inactive roles
    active_roles = member_roles.filter(is_active=True)
    inactive_roles = member_roles.filter(is_active=False)

    context = {
        "entity": entity,
        "member": member,
        "member_roles": member_roles,
        "active_roles": active_roles,
        "inactive_roles": inactive_roles,
        "total_roles": member_roles.count(),
        "title": f"Roles: {member.full_name}",
    }
    return render(request, "ChurchApp/member_roles_detail.html", context)


@login_required
@staff_member_required
def dues_tithe_list_manage(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)

    DUES_CODE  = "4013"
    TITHE_CODE = "4014"

    transactions = Trans.objects.filter(
        entity=entity,
        module="church",
        sub_module="dues_tithe",
        trans_type="Receipts",
        ledger_code__in=[DUES_CODE, TITHE_CODE],
    ).filter(
        Q(journal_entry_id__isnull=True) | Q(journal_entry_id="")
    ).order_by("-date", "-id")


    payment_type = request.GET.get("type", "")
    search       = request.GET.get("search", "")
    start_date   = request.GET.get("start", "")
    end_date     = request.GET.get("end", "")

    if payment_type == "dues":
        transactions = transactions.filter(ledger_code=DUES_CODE)
    elif payment_type == "tithe":
        transactions = transactions.filter(ledger_code=TITHE_CODE)

    if search:
        transactions = transactions.filter(
            models.Q(church_member__full_name__icontains=search)
            | models.Q(member__full_name__icontains=search)
            | models.Q(non_member_name__icontains=search)
            | models.Q(rec_vou_no__icontains=search)
        )

    if start_date:
        transactions = transactions.filter(date__gte=start_date)
    if end_date:
        transactions = transactions.filter(date__lte=end_date)

    base_qs = Trans.objects.filter(
        entity=entity, module="church", sub_module="dues_tithe"
    ).filter(
        Q(journal_entry_id__isnull=True) | Q(journal_entry_id="")
    )
    
    total_dues = base_qs.filter(ledger_code=DUES_CODE).aggregate(
        total=models.Sum("amount"))["total"] or 0
    total_tithes = base_qs.filter(ledger_code=TITHE_CODE).aggregate(
        total=models.Sum("amount"))["total"] or 0
    total_amount = total_dues + total_tithes

    context = {
        "entity": entity,
        "transactions": transactions,
        "total_dues": total_dues,
        "total_tithes": total_tithes,
        "total_amount": total_amount,
        "payment_type": payment_type,
        "search": search,
        "start_date": start_date,
        "end_date": end_date,
    }
    return render(request, "ChurchApp/dues_tithe_list_manage.html", context)


@login_required
@staff_member_required
def dues_tithe_create(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)

    if request.method == "POST":
        form = DuesTitheTransactionForm(request.POST, entity=entity, user=request.user)

        if form.is_valid():
            trans = form.save()

            # Debug: Print saved trans
            print(
                f"Saved Trans: {trans.rec_vou_no}, Purpose: {trans.purpose}, Amount: {trans.amount}"
            )

            # Update member's totals if church_member selected
            if trans.church_member:
                member = trans.church_member
                if trans.purpose and trans.purpose.lower() == "tithe":
                    member.tot_tithe = (
                        getattr(member, "tot_tithe", 0) or 0
                    ) + trans.amount
                else:
                    member.tot_dues = (
                        getattr(member, "tot_dues", 0) or 0
                    ) + trans.amount
                member.save()
                print(
                    f"Updated member {member.full_name}: tot_tithe={member.tot_tithe}, tot_dues={member.tot_dues}"
                )

            messages.success(
                request,
                f"{trans.purpose} recorded. Transaction {trans.rec_vou_no} pending approval.",
            )
            return redirect("ChurchApp:dues_tithe_list_manage", slug=entity.slug)
        else:
            # Print form errors
            print("Form is invalid:", form.errors)
    else:
        purpose = request.GET.get("purpose", "Dues")
        form = DuesTitheTransactionForm(
            entity=entity,
            user=request.user,
            initial={
                "date": timezone.now().date(),
                "payment_type": purpose,
            },
        )

    context = {
        "entity": entity,
        "form": form,
        "title": f'Record {request.GET.get("purpose", "Dues")} Payment',
    }
    return render(request, "ChurchApp/dues_tithe_form.html", context)

from decimal import Decimal
from django.db import transaction


@login_required
@staff_member_required
def dues_tithe_edit(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)

    trans = get_object_or_404(
        Trans,
        pk=pk,
        entity=entity,
        module="church",
        sub_module="dues_tithe",
    )

    # Guard — don't edit rows that are already posted to journals
    if trans.journal_entry_id:
        messages.warning(
            request,
            "This record has been posted to journals. Reverse the journal entry first.",
        )
        return redirect("ChurchApp:dues_tithe_list_manage", slug=entity.slug)

    if request.method == "POST":
        form = DuesTitheTransactionForm(
            request.POST,
            instance=trans,
            entity=entity,
            user=request.user,
        )

        if form.is_valid():
            # Capture old state before we mutate anything
            old_member = trans.church_member
            old_amount = trans.amount or Decimal("0")
            old_is_tithe = (trans.purpose or "").lower() == "tithe"

            with transaction.atomic():
                updated = form.save(commit=False)

                # Preserve the original creator; set the editor as updated_by
                updated.created_by = trans.created_by
                updated.created_by_name = trans.created_by_name
                updated.created_by_username = trans.created_by_username
                updated.updated_by = request.user
                updated.save()

                new_member = updated.church_member
                new_amount = updated.amount or Decimal("0")
                new_is_tithe = (updated.purpose or "").lower() == "tithe"

                # Reverse the old contribution on the old member
                if old_member:
                    if old_is_tithe:
                        old_member.tot_tithe = max(
                            (getattr(old_member, "tot_tithe", 0) or 0) - old_amount,
                            Decimal("0"),
                        )
                    else:
                        old_member.tot_dues = max(
                            (getattr(old_member, "tot_dues", 0) or 0) - old_amount,
                            Decimal("0"),
                        )
                    old_member.save()

                # Apply the new contribution on the (possibly different) member
                if new_member:
                    if new_is_tithe:
                        new_member.tot_tithe = (
                            getattr(new_member, "tot_tithe", 0) or 0
                        ) + new_amount
                    else:
                        new_member.tot_dues = (
                            getattr(new_member, "tot_dues", 0) or 0
                        ) + new_amount
                    new_member.save()

            messages.success(
                request,
                f"{updated.purpose} updated — {updated.rec_vou_no or updated.pk}.",
            )
            return redirect("ChurchApp:dues_tithe_list_manage", slug=entity.slug)

        # Invalid: fall through to render with bound form (errors visible)

    else:
        form = DuesTitheTransactionForm(
            instance=trans,
            entity=entity,
            user=request.user,
            initial={"payment_type": trans.purpose or "Dues"},
        )

    context = {
        "entity": entity,
        "form": form,
        "trans": trans,  # template uses {% if trans %} to switch mode
        "title": f"Edit {trans.purpose or 'Dues / Tithe'} — {trans.rec_vou_no or trans.pk}",
    }
    return render(request, "ChurchApp/dues_tithe_form.html", context)


@staff_member_required
def dues_tithe_delete(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    trans = get_object_or_404(Trans, pk=pk, entity=entity)

    # --- EDIT LOCK ---
    if not trans.can_delete:
        messages.error(request, trans.lock_reason())
        return redirect('ChurchApp:dues_tithe_view', slug=entity.slug, pk=trans.pk)

    if request.method == 'POST':
        rec_vou_no = trans.rec_vou_no
        trans.delete()
        messages.success(request, f"Transaction {rec_vou_no} deleted successfully.")
        return redirect('ChurchApp:dues_tithe_list_manage', slug=entity.slug)

    context = {
        'entity': entity,
        'trans': trans,
    }
    return render(request, 'ChurchApp/dues_tithe_confirm_delete.html', context)


@staff_member_required
def dues_tithe_view(request, slug, pk):
    """
    View details of a specific dues/tithe transaction.
    """
    entity = get_object_or_404(EntityModel, slug=slug)
    trans = get_object_or_404(Trans, pk=pk, entity=entity)

    context = {
        "entity": entity,
        "trans": trans,
        "title": f"Transaction Details: {trans.rec_vou_no}",
    }
    return render(request, "ChurchApp/dues_tithe_view.html", context)


# ChurchApp/views.py

from django.http import HttpResponse
from django.template.loader import get_template
from django.shortcuts import get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django_ledger.models import EntityModel
from RecPayApp.models import Trans
from xhtml2pdf import pisa
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side
from decimal import Decimal


@staff_member_required
def dues_tithe_pdf(request, slug, pk):
    """Export a single Dues/Tithe transaction to PDF."""
    entity = get_object_or_404(EntityModel, slug=slug)
    trans = get_object_or_404(Trans, pk=pk, entity=entity)

    context = {
        "entity": entity,
        "trans": trans,
        "title": f"Dues/Tithe Receipt – {trans.rec_vou_no}",
    }

    template = get_template("ChurchApp/dues_tithe_pdf.html")
    html = template.render(context)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="dues_tithe_{trans.rec_vou_no}.pdf"'
    )

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("PDF generation error", status=500)
    return response


@staff_member_required
def dues_tithe_excel(request, slug, pk):
    """Export a single Dues/Tithe transaction to Excel."""
    entity = get_object_or_404(EntityModel, slug=slug)
    trans = get_object_or_404(Trans, pk=pk, entity=entity)

    wb = Workbook()
    ws = wb.active
    ws.title = "Dues-Tithe Receipt"

    bold = Font(bold=True)
    right = Alignment(horizontal="right")
    thin = Side(style="thin")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    # Title
    ws.merge_cells("A1:C1")
    ws["A1"] = f"{entity.name}"
    ws["A1"].font = Font(size=14, bold=True)
    ws["A1"].alignment = Alignment(horizontal="center")

    ws.merge_cells("A2:C2")
    ws["A2"] = f"Dues / Tithe Receipt – {trans.rec_vou_no}"
    ws["A2"].font = Font(size=12, bold=True)
    ws["A2"].alignment = Alignment(horizontal="center")

    row = 4
    data = [
        ("Voucher No:", trans.rec_vou_no),
        ("Date:", trans.date.strftime("%Y-%m-%d")),
        (
            "Member:",
            (
                trans.church_member.full_name
                if trans.church_member
                else (
                    trans.member.full_name
                    if trans.member
                    else trans.non_member_name or "—"
                )
            ),
        ),
        ("Payment Type:", trans.purpose or "—"),
        ("Amount:", f"₵{trans.amount:.2f}"),
        ("Payment Mode:", trans.pay_mode),
        ("Ledger Code:", f"{trans.ledger_code or '—'} – {trans.ledger_name or '—'}"),
        ("Description:", trans.details or "—"),
        ("Status:", trans.get_journal_status_display()),
        ("Created By:", trans.created_by_name or "—"),
        (
            "Created At:",
            trans.created_at.strftime("%Y-%m-%d %H:%M") if trans.created_at else "—",
        ),
    ]

    for label, value in data:
        ws.cell(row=row, column=1, value=label).font = bold
        ws.cell(row=row, column=2, value=str(value))
        ws.cell(row=row, column=1).border = border
        ws.cell(row=row, column=2).border = border
        row += 1

    ws.column_dimensions["A"].width = 20
    ws.column_dimensions["B"].width = 40

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = (
        f'attachment; filename="dues_tithe_{trans.rec_vou_no}.xlsx"'
    )
    wb.save(response)
    return response


@staff_member_required
def dues_tithe_list_pdf(request, slug):
    """Export filtered list of Dues/Tithe transactions to PDF."""
    from django.db.models import Q, Sum
    from datetime import datetime, timedelta

    entity = get_object_or_404(EntityModel, slug=slug)

    # Date range
    start_date = (
        request.GET.get("start")
        or (timezone.now().date() - timedelta(days=30)).isoformat()
    )
    end_date = request.GET.get("end") or timezone.now().date().isoformat()

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        start = timezone.now().date() - timedelta(days=30)
        end = timezone.now().date()

    # Base query
    qs = Trans.objects.filter(
        entity=entity,
        ledger_code__in=["4013", "4014"],
        date__gte=start,
        date__lte=end,
    ).order_by("-date")

    # Type filter
    payment_type = request.GET.get("type")
    if payment_type == "dues":
        qs = qs.filter(ledger_code="4011")
    elif payment_type == "tithe":
        qs = qs.filter(ledger_code="4012")

    # Search
    search = request.GET.get("search")
    if search:
        qs = qs.filter(
            Q(church_member__full_name__icontains=search)
            | Q(member__full_name__icontains=search)
            | Q(non_member_name__icontains=search)
            | Q(rec_vou_no__icontains=search)
        )

    total_dues = qs.filter(ledger_code="4011").aggregate(t=Sum("amount"))[
        "t"
    ] or Decimal("0.00")
    total_tithes = qs.filter(ledger_code="4012").aggregate(t=Sum("amount"))[
        "t"
    ] or Decimal("0.00")

    context = {
        "entity": entity,
        "transactions": qs,
        "start_date": start,
        "end_date": end,
        "total_dues": total_dues,
        "total_tithes": total_tithes,
        "grand_total": total_dues + total_tithes,
        "now": timezone.now(),
    }

    template = get_template("ChurchApp/dues_tithe_list_pdf.html")
    html = template.render(context)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="dues_tithe_report_{start}_{end}.pdf"'
    )
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("PDF generation error", status=500)
    return response


@staff_member_required
def dues_tithe_list_excel(request, slug):
    """Export filtered list of Dues/Tithe transactions to Excel."""
    from django.db.models import Q, Sum
    from datetime import datetime, timedelta

    entity = get_object_or_404(EntityModel, slug=slug)

    start_date = (
        request.GET.get("start")
        or (timezone.now().date() - timedelta(days=30)).isoformat()
    )
    end_date = request.GET.get("end") or timezone.now().date().isoformat()

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        start = timezone.now().date() - timedelta(days=30)
        end = timezone.now().date()

    qs = Trans.objects.filter(
        entity=entity,
        ledger_code__in=["4011", "4012"],
        date__gte=start,
        date__lte=end,
    ).order_by("-date")

    payment_type = request.GET.get("type")
    if payment_type == "dues":
        qs = qs.filter(ledger_code="4011")
    elif payment_type == "tithe":
        qs = qs.filter(ledger_code="4012")

    search = request.GET.get("search")
    if search:
        qs = qs.filter(
            Q(church_member__full_name__icontains=search)
            | Q(member__full_name__icontains=search)
            | Q(non_member_name__icontains=search)
            | Q(rec_vou_no__icontains=search)
        )

    wb = Workbook()
    ws = wb.active
    ws.title = "Dues & Tithes"

    bold = Font(bold=True)
    thin = Side(style="thin")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    right_align = Alignment(horizontal="right")

    # Title
    ws.merge_cells("A1:G1")
    ws["A1"] = f"{entity.name} – Dues & Tithes Report"
    ws["A1"].font = Font(size=14, bold=True)
    ws["A1"].alignment = Alignment(horizontal="center")

    ws.merge_cells("A2:G2")
    ws["A2"] = f"Period: {start} to {end}"
    ws["A2"].alignment = Alignment(horizontal="center")
    ws["A2"].font = Font(italic=True, color="666666")

    # Headers
    headers = ["Voucher", "Date", "Member", "Type", "Amount", "Pay Mode", "Status"]
    ws.append([])  # blank row
    ws.append(headers)
    header_row = ws.max_row
    for cell in ws[header_row]:
        cell.font = bold
        cell.border = border
        cell.alignment = Alignment(horizontal="center")

    # Data rows
    for t in qs:
        member_name = (
            t.church_member.full_name
            if t.church_member
            else (t.member.full_name if t.member else (t.non_member_name or "—"))
        )
        ws.append(
            [
                t.rec_vou_no,
                t.date.strftime("%Y-%m-%d"),
                member_name,
                t.purpose or "—",
                float(t.amount),
                t.pay_mode,
                t.get_journal_status_display(),
            ]
        )
        for cell in ws[ws.max_row]:
            cell.border = border
        ws.cell(row=ws.max_row, column=5).alignment = right_align

    # Totals
    total_dues = qs.filter(ledger_code="4011").aggregate(t=Sum("amount"))[
        "t"
    ] or Decimal("0.00")
    total_tithes = qs.filter(ledger_code="4012").aggregate(t=Sum("amount"))[
        "t"
    ] or Decimal("0.00")
    grand = total_dues + total_tithes

    ws.append([])
    ws.append(["", "", "", "Total Dues:", float(total_dues), "", ""])
    ws.append(["", "", "", "Total Tithes:", float(total_tithes), "", ""])
    ws.append(["", "", "", "GRAND TOTAL:", float(grand), "", ""])
    for r in range(ws.max_row - 2, ws.max_row + 1):
        ws.cell(row=r, column=4).font = bold
        ws.cell(row=r, column=5).font = bold
        ws.cell(row=r, column=5).alignment = right_align
        ws.cell(row=r, column=5).border = border
        ws.cell(row=r, column=4).border = border

    # Column widths
    widths = {"A": 18, "B": 14, "C": 30, "D": 15, "E": 15, "F": 14, "G": 14}
    for col, w in widths.items():
        ws.column_dimensions[col].width = w

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = (
        f'attachment; filename="dues_tithe_report_{start}_{end}.xlsx"'
    )
    wb.save(response)
    return response


## ===============================================TRANS =================================================
@login_required
@staff_member_required
def trans_create(request, slug):
    """
    Create receipts and payments transactions.
    Handles both Credit Union (Master) and Church (Member) members.
    """
    entity = get_object_or_404(EntityModel, slug=slug)

    # ----- Chart of Accounts -----
    try:
        coa = entity.get_default_coa()
    except Exception:
        messages.error(
            request,
            "This entity does not have a Chart of Accounts. Please create one first.",
        )
        return redirect("djan_led:chart_of_accounts", slug=entity.slug)

    if not coa:
        messages.error(request, "No Chart of Accounts found for this entity.")
        return redirect("djan_led:chart_of_accounts", slug=entity.slug)

   
    accounts = get_visible_accounts(request.user, entity)
    church_members = Member.objects.filter(entity=entity, is_deleted=False).order_by("full_name")
    
    members = list(church_members)
    
    
    
    

    selected_member_id = request.GET.get("member_id") or request.POST.get("member_id")
    selected_member = None
    selected_member_type = None
    active_loans = []

    if selected_member_id and selected_member_id.isdigit():
        try:
            selected_member = Member.objects.get(
                id=int(selected_member_id), entity=entity,
            )
            selected_member_type = "member"
            active_loans = []
        except Member.DoesNotExist:
            selected_member = None
            selected_member_type = None
            active_loans = []
    # ----- Transactions list — RP form only -----
    transactions = Trans.objects.filter(
        entity=entity,
        module="church",
        sub_module="receipts_payments",
        trans_type__in=["Receipts", "Payments"],
    ).order_by("-date", "-id")

    total_records = transactions.count()
    receipts = transactions.filter(trans_type="Receipts")
    payments = transactions.filter(trans_type="Payments")
    receipts_count = receipts.count()
    payments_count = payments.count()
    receipts_total = receipts.aggregate(Sum("amount"))["amount__sum"] or Decimal("0.00")
    payments_total = payments.aggregate(Sum("amount"))["amount__sum"] or Decimal("0.00")
    net_balance = receipts_total - payments_total

    paginator = Paginator(transactions, 50)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # ----- Context (built BEFORE POST so error branches can add to it) -----
    context = {
        "tran": page_obj,
        "members": members,
        "loans": active_loans,
        "accounts": accounts,
        "selected_member": selected_member,
        "selected_member_id": selected_member_id,
        "selected_member_type": selected_member_type,
        "total_records": total_records,
        "receipts_count": receipts_count,
        "payments_count": payments_count,
        "receipts_total": receipts_total,
        "payments_total": payments_total,
        "net_balance": net_balance,
        "today": datetime.now().date(),
        "entity": entity,
    }

    # ============================================
    # POST
    # ============================================
    if request.method == "POST":

        # ----- Close button -----
        if "close" in request.POST:
            return redirect("ChurchApp:church_dashboard", entity.slug)

        # ----- Save -----
        if "save" in request.POST:
            try:
                # 1. Basic fields
                date_str   = request.POST.get("date", "").strip()
                trans_no   = request.POST.get("trans_no", "").strip()
                trans_type = request.POST.get("trans_type", "").strip()
                amount_str = request.POST.get("amount", "").replace(",", "").strip()
                pay_mode   = request.POST.get("pay_mode", "").strip()
                name_type  = request.POST.get("name_type", "").strip()
                details    = request.POST.get("details", "").strip()

                if not date_str or not trans_no or not amount_str:
                    messages.error(request, "Date, Reference No and Amount are required.")
                    context["form"] = request.POST
                    return render(request, "ChurchApp/trans_create.html", context)

                # 2. Amount
                amount = Decimal(amount_str)

                # 3. Date
                date = None
                for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
                    try:
                        date = datetime.strptime(date_str, fmt).date()
                        break
                    except ValueError:
                        continue
                if not date:
                    messages.error(request, "Invalid date. Use DD/MM/YYYY.")
                    context["form"] = request.POST
                    return render(request, "ChurchApp/trans_create.html", context)

                # 4. Ledger account (pk is a UUID — no int() cast)
                chart_value = request.POST.get("chart_account", "").strip()
                if not chart_value:
                    messages.error(request, "Please select a Ledger account.")
                    context["form"] = request.POST
                    return render(request, "ChurchApp/trans_create.html", context)

                parts = chart_value.split(",")
                ledger = AccountModel.objects.get(
                    pk=parts[0].strip(), coa_model=coa, active=True
                )

                # 5. Member / non-member
                master_obj = None
                church_member_obj = None
                member_no = 0
                member_name = ""
                non_member_name = ""
                non_member_contact = ""

                if name_type == "Member":
                    member_id = request.POST.get("member_id", "")
                    if member_id and member_id.isdigit():
                        try:
                            master_obj = Master.objects.get(id=int(member_id))
                            member_no = master_obj.id
                            member_name = master_obj.full_name
                        except Master.DoesNotExist:
                            try:
                                church_member_obj = Member.objects.get(id=int(member_id))
                                member_name = church_member_obj.full_name
                            except Member.DoesNotExist:
                                pass
                elif name_type == "Non Member":
                    non_member_name = request.POST.get("non_member_name", "").strip()
                    non_member_contact = request.POST.get("non_member_contact", "").strip()

                # 6. Loan
                loan_obj = None
                loan_id = request.POST.get("loan_id", "")
                if loan_id and loan_id.isdigit():
                    try:
                        loan_obj = Loan.objects.get(id=int(loan_id))
                    except Loan.DoesNotExist:
                        loan_obj = None

                # 7. Payment method extras
                cheque_date = None
                if pay_mode == "Cheque":
                    cd_str = request.POST.get("cheque_date", "").strip()
                    if cd_str:
                        for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
                            try:
                                cheque_date = datetime.strptime(cd_str, fmt).date()
                                break
                            except ValueError:
                                continue
                    bank        = request.POST.get("bank", "").strip()
                    bank_no     = request.POST.get("bank_no", "").strip()
                    bank_branch = request.POST.get("bank_branch", "").strip()
                    cheque_no   = request.POST.get("cheque_no", "").strip()
                    momo_no     = ""
                    momo_name   = ""
                elif pay_mode == "Transfer":
                    bank        = ""
                    bank_no     = ""
                    bank_branch = ""
                    cheque_no   = ""
                    momo_no     = request.POST.get("momo_no", "").strip()
                    momo_name   = request.POST.get("momo_name", "").strip()
                else:  # Cash
                    bank = bank_no = bank_branch = cheque_no = momo_no = momo_name = ""

                # 8. Save
                rec_vou_no = (
                    f"REC:{trans_no}" if trans_type == "Receipts" else f"VOU:{trans_no}"
                )

                with transaction.atomic():
                    Trans.objects.create(
                        entity=entity,
                        date=date,
                        trans_no=trans_no,
                        rec_vou_no=rec_vou_no,
                        trans_type=trans_type,
                        amount=amount,
                        pay_mode=pay_mode,
                        purpose=ledger.name,
                        details=details,
                        member=master_obj,
                        member_no=member_no,
                        member_name=member_name,
                        church_member=church_member_obj,
                        non_member_name=non_member_name,
                        non_member_contact=non_member_contact,
                        loan=loan_obj,
                        bank=bank,
                        bank_no=bank_no,
                        bank_branch=bank_branch,
                        momo_no=momo_no,
                        momo_name=momo_name,
                        cheque_no=cheque_no,
                        cheque_date=cheque_date,
                        ledger_id=str(ledger.pk),
                        ledger_code=str(ledger.code),
                        ledger_name=ledger.name,
                        module="church",
                        sub_module="receipts_payments",
                        created_by_id=request.user.id,
                        created_by_name=request.user.get_full_name(),
                        created_by_username=request.user.username,
                    )

            except AccountModel.DoesNotExist:
                messages.error(
                    request,
                    "Selected ledger account was not found for this entity.",
                )
                context["form"] = request.POST
                return render(request, "ChurchApp/trans_create.html", context)

            except Exception as exc:
                messages.error(request, f"Could not save: {exc}")
                import traceback
                traceback.print_exc()
                context["form"] = request.POST
                return render(request, "ChurchApp/trans_create.html", context)

            messages.success(request, f"Transaction {trans_no} posted successfully!")
            return redirect(
                f"{reverse('ChurchApp:trans_create', args=[entity.slug])}"
                f"?keep={trans_type}&mode={pay_mode}"
                f"&date={date.strftime('%d/%m/%Y')}"
            )

    return render(request, "ChurchApp/trans_create.html", context)


@login_required
def trans_edit(request, slug, pk):
    """Edit an existing Receipts/Payments transaction."""
    entity = get_object_or_404(EntityModel, slug=slug)

    # Only RP rows are editable via this form
    trans = get_object_or_404(
        Trans,
        pk=pk,
        entity=entity,
        module="church",
        sub_module="receipts_payments",
    )

    # ----- Chart of Accounts (same as trans_create) -----
    try:
        coa = entity.get_default_coa()
    except Exception:
        messages.error(request, "This entity does not have a Chart of Accounts.")
        return redirect("djan_led:chart_of_accounts", slug=entity.slug)

    if not coa:
        messages.error(request, "No Chart of Accounts found for this entity.")
        return redirect("djan_led:chart_of_accounts", slug=entity.slug)
    
    accounts = get_visible_accounts(request.user, entity)

    # Ensure the record's current account appears even if hidden
    if trans.ledger_code:
        current_acct = AccountModel.objects.filter(
            coa_model=coa, code=trans.ledger_code
        ).first()
        if current_acct and not accounts.filter(pk=current_acct.pk).exists():
            accounts = accounts | AccountModel.objects.filter(pk=current_acct.pk)
    # ----- Members (same as trans_create) -----
    master_members = Master.objects.filter(entity=entity, is_deleted=False).order_by(
        "last_name", "first_name"
    )
    church_members = Member.objects.filter(entity=entity, is_deleted=False).order_by(
        "full_name"
    )
    members = list(master_members) + list(church_members)

    context = {
        "entity": entity,
        "accounts": accounts,
        "members": members,
        "today": datetime.now().date(),
        "trans": trans,  # ← the row being edited
        "tran": None,  # hide the list on the edit page
    }

    if request.method == "POST":
        if "close" in request.POST:
            return redirect("ChurchApp:trans_create", entity.slug)

        if "save" in request.POST:
            try:
                # ----- Parse (same as trans_create) -----
                date_str = request.POST.get("date", "").strip()
                trans_no = request.POST.get("trans_no", "").strip()
                trans_type = request.POST.get("trans_type", "").strip()
                amount_str = request.POST.get("amount", "").replace(",", "").strip()
                pay_mode = request.POST.get("pay_mode", "").strip()
                name_type = request.POST.get("name_type", "").strip()
                details = request.POST.get("details", "").strip()

                if not date_str or not trans_no or not amount_str:
                    messages.error(
                        request, "Date, Reference No and Amount are required."
                    )
                    context["form"] = request.POST
                    return render(request, "ChurchApp/trans_create.html", context)

                amount = Decimal(amount_str)

                date = None
                for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
                    try:
                        date = datetime.strptime(date_str, fmt).date()
                        break
                    except ValueError:
                        continue
                if not date:
                    messages.error(request, "Invalid date. Use DD/MM/YYYY.")
                    context["form"] = request.POST
                    return render(request, "ChurchApp/trans_create.html", context)

                chart_value = request.POST.get("chart_account", "").strip()
                if not chart_value:
                    messages.error(request, "Please select a Ledger account.")
                    context["form"] = request.POST
                    return render(request, "ChurchApp/trans_create.html", context)

                parts = chart_value.split(",")
                if len(parts) != 3 or not parts[0].strip():
                    messages.error(request, "Invalid ledger selection.")
                    context["form"] = request.POST
                    return render(request, "ChurchApp/trans_create.html", context)

                ledger = AccountModel.objects.get(
                    pk=parts[0].strip(), coa_model=coa, active=True
                )

                # ----- Member / non-member -----
                master_obj = None
                church_member_obj = None
                member_no = None
                member_name = ""
                non_member_name = ""
                non_member_contact = ""

                if name_type == "Member":
                    member_id = request.POST.get("member_id", "")
                    if member_id and member_id.isdigit():
                        try:
                            master_obj = Master.objects.get(id=int(member_id))
                            member_no = master_obj.pk
                            member_name = master_obj.full_name
                        except Master.DoesNotExist:
                            try:
                                church_member_obj = Member.objects.get(
                                    id=int(member_id)
                                )
                                member_name = church_member_obj.full_name
                            except Member.DoesNotExist:
                                pass
                elif name_type == "Non Member":
                    non_member_name = request.POST.get("non_member_name", "").strip()
                    non_member_contact = request.POST.get(
                        "non_member_contact", ""
                    ).strip()

                # ----- Loan -----
                loan_obj = None
                loan_id = request.POST.get("loan_id", "")
                if loan_id and loan_id.isdigit():
                    try:
                        loan_obj = Loan.objects.get(id=int(loan_id))
                    except Loan.DoesNotExist:
                        loan_obj = None

                # ----- Payment method extras -----
                cheque_date = None
                bank = bank_no = bank_branch = momo_no = momo_name = cheque_no = ""
                if pay_mode == "Cheque":
                    cd_str = request.POST.get("cheque_date", "").strip()
                    if cd_str:
                        for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
                            try:
                                cheque_date = datetime.strptime(cd_str, fmt).date()
                                break
                            except ValueError:
                                continue
                    bank = request.POST.get("bank", "").strip()
                    bank_no = request.POST.get("bank_no", "").strip()
                    bank_branch = request.POST.get("bank_branch", "").strip()
                    cheque_no = request.POST.get("cheque_no", "").strip()
                elif pay_mode == "Transfer":
                    momo_no = request.POST.get("momo_no", "").strip()
                    momo_name = request.POST.get("momo_name", "").strip()

                # ----- Update the record in place -----
                rec_vou_no = (
                    f"REC:{trans_no}" if trans_type == "Receipts" else f"VOU:{trans_no}"
                )

                with transaction.atomic():
                    trans.date = date
                    trans.trans_no = trans_no
                    trans.rec_vou_no = rec_vou_no
                    trans.trans_type = trans_type
                    trans.amount = amount
                    trans.pay_mode = pay_mode
                    trans.purpose = ledger.name
                    trans.details = details

                    trans.member = master_obj
                    trans.member_no = member_no
                    trans.member_name = member_name
                    trans.church_member = church_member_obj
                    trans.non_member_name = non_member_name
                    trans.non_member_contact = non_member_contact

                    trans.loan = loan_obj
                    trans.bank = bank
                    trans.bank_no = bank_no
                    trans.bank_branch = bank_branch
                    trans.momo_no = momo_no
                    trans.momo_name = momo_name
                    trans.cheque_no = cheque_no
                    trans.cheque_date = cheque_date

                    trans.ledger_id = str(ledger.pk)
                    trans.ledger_code = str(ledger.code)
                    trans.ledger_name = ledger.name

                    trans.save()

            except AccountModel.DoesNotExist:
                messages.error(
                    request, "Selected ledger account was not found for this entity."
                )
                context["form"] = request.POST
                return render(request, "ChurchApp/trans_create.html", context)
            except Exception as exc:
                messages.error(request, f"Could not update: {exc}")
                import traceback

                traceback.print_exc()
                context["form"] = request.POST
                return render(request, "ChurchApp/trans_create.html", context)

            messages.success(request, f"Transaction {trans_no} updated successfully!")
            return redirect("ChurchApp:trans_create", entity.slug)

    return render(request, "ChurchApp/trans_create.html", context)


def parse_offering_list(request, prefix):
    """Parse offering list from POST data"""
    items = []
    names = request.POST.getlist(f'{prefix}_names[]')
    amounts = request.POST.getlist(f'{prefix}_amounts[]')
    for i, name in enumerate(names):
        if name.strip():
            try:
                amount = Decimal(amounts[i]) if i < len(amounts) else Decimal('0')
                if amount > 0:
                    items.append({
                        'name': name.strip(),
                        'amount': float(amount)
                    })
            except:
                pass
    return items

# ============================================Church Service Activity=========================
# =========================================== Helper Functions =========================

@login_required
def role_list(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)

    roles = (
        Role.objects
        .filter(entity=entity)
        .annotate(
            active_member_count=Count(
                "role_members",
                filter=Q(role_members__is_active=True),
                distinct=True,
            )
        )
        .order_by("id")
    )

    context = {
        "entity": entity,
        "roles": roles,
    }

    return render(request, "ChurchApp/role_list.html", context)


FIXED_SERVICE_ROLES = {
    "Priest Warden": "priest_warden",
    "People's Warden": "peoples_warden",
    "Verger": "verger",
    "Parish-Clerk": "parish_clerk",
    "Accounts-Clerk": "accounts_clerk",
    "PCC": "pcc_members",
}


def get_active_member_roles(entity, role_name):
    """
    Get members who currently have the specified active role
    for this church/entity.
    """

    return (MemberRole.objects.filter(entity=entity, role__name=role_name, is_active=True).select_related("member", "role"))


def populate_service_offices(service):
    """
    Get the current active holders of the fixed church offices
    and save their names into the Service record.
    """

    office_roles = {
        "priest_warden": "priest_warden",
        "peoples_warden": "peoples_warden",
        "verger": "verger",
        "parish_clerk": "parish_clerk",
        "accounts_clerk": "accounts_clerk",
    }

    for field_name, role_name in office_roles.items():

        member_role = (
            MemberRole.objects.filter(
                entity=service.entity,
                role__name=role_name,
                is_active=True,
            )
            .select_related("member")
            .first()
        )

        if member_role:
            setattr(service, field_name, member_role.member.full_name)
        else:
            setattr(service, field_name, "")

    # PCC can have several active members
    pcc_roles = MemberRole.objects.filter(
        entity=service.entity,
        role__name="PCC",
        is_active=True,
    ).select_related("member")

    service.pcc_members = [
        role.member.full_name for role in pcc_roles
    ]

    service.save(
        update_fields=[
            "priest_warden",
            "peoples_warden",
            "verger",
            "parish_clerk",
            "accounts_clerk",
            "pcc_members",
        ]
    )

    return service


def get_member_roles_for_service_date(entity, service_date, role_name):
    """
    Return MemberRole records whose appointment was valid
    on the Service date.
    """

    return MemberRole.objects.filter(
        entity=entity,
        role__name=role_name,
        date_assigned__lte=service_date
    ).filter(
        Q(date_removed__isnull=True) |
        Q(date_removed__gte=service_date)
    ).select_related("member", "role")


# =========================================== Service Activity Views =========================
@login_required
def service_activity_create(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)

    # Get data for dropdowns
    clergy_list = Clergy.objects.filter(entity=entity).order_by("full_name")         ## Okay
    officiants = Member.objects.filter(entity=entity, is_deleted=False).order_by("full_name")  ## Okay
    ushers = Member.objects.filter(
        entity=entity,
        is_deleted=False,
        member_roles__role__name="usher",
        member_roles__is_active=True,
    ).order_by("full_name").distinct()  ## Okay

    #    )
    guilds = Guild.objects.filter(entity=entity, is_active=True).order_by("name")

    chalice_assistants = Member.objects.filter(
        entity=entity,
        is_deleted=False,
        member_roles__role__name="chalice_assistant",
        member_roles__is_active=True,
    ).order_by("full_name").distinct()

    selected_clergy = Clergy.objects.none()
    selected_ushers = Member.objects.none()
    selected_chalice_assistants = Member.objects.none()

    if request.method == "POST":

        try:
            with transaction.atomic():

                # ============================================================
                # BASIC SERVICE DATA
                # ===========================================================
                date = datetime.strptime(request.POST.get("date"), "%Y-%m-%d").date()
                service_name = request.POST.get("service_name", "")
                attendance = request.POST.get("attendance", 0)
                communicants = request.POST.get("communicants", 0)

                # Create service record
                service = Service.objects.create(
                    entity=entity,
                    date=date,
                    name_of_service=service_name,
                    attendance=attendance,
                    communicants=communicants,
                    created_by=request.user,
                )

                # 2. Get selected IDs
                clergy_ids = [
                    v.strip()
                    for v in request.POST.get("clergy_ids", "").split(",")
                    if v.strip()
                ]

                usher_ids = [
                    v.strip()
                    for v in request.POST.get("usher_ids", "").split(",")
                    if v.strip()
                ]

                chalice_assistant_ids = [
                    v.strip()
                    for v in request.POST.get("chalice_assistant_ids", "").split(",")
                    if v.strip()
                ]

                # 3. Start with empty selections
                selected_clergy = Clergy.objects.none()
                selected_ushers = Member.objects.none()
                selected_chalice_assistants = Member.objects.none()

                # 4. Get selected clergy
                if clergy_ids:
                    selected_clergy = Clergy.objects.filter(
                        entity=entity,
                        id__in=clergy_ids
                    )

                # 5. Get selected ushers
                if usher_ids:
                    selected_ushers = Member.objects.filter(
                        entity=entity,
                        is_deleted=False,
                        id__in=usher_ids
                    )

                # 6. Get selected chalice assistants
                if chalice_assistant_ids:
                    selected_chalice_assistants = Member.objects.filter(
                        entity=entity,
                        is_deleted=False,
                        id__in=chalice_assistant_ids
                    )

                # 7. Save the ManyToMany selections
                service.clergy.set(selected_clergy)
                service.ushers.set(selected_ushers)
                service.chalice_assistants.set(selected_chalice_assistants)

                # 8. Save the single Officiant
                officiant_id = request.POST.get("officiant")

                if officiant_id:
                    officiant = Member.objects.filter(
                        entity=entity,
                        is_deleted=False,
                        id=officiant_id
                    ).first()

                    if officiant:
                        service.officiant = officiant
                        service.save(update_fields=["officiant"])
                                

                # ============================================================
                # CLERGY
                # ============================================================
                clergy_ids = [
                    value.strip()
                    for value in request.POST.get("clergy_ids", "").split(",")
                    if value.strip()
                ]
                #
                if clergy_ids:
                    selected_clergy = Clergy.objects.filter(entity=entity, id__in=clergy_ids)
                service.clergy.set(selected_clergy)

                # ===========OFFICIANTS=================================================#                ]
                officiant_id = request.POST.get("officiant")

                if officiant_id:
                    officiant = Member.objects.filter(
                        entity=entity,
                        is_deleted=False,
                        id=officiant_id,
                    ).first()

                    if officiant:
                        service.officiant = officiant
                # ==========USHERS==================================================
                usher_ids = [
                    value.strip()
                    for value in request.POST.get("usher_ids", "").split(",")
                    if value.strip()
                ]
                if usher_ids:
                    selected_ushers = Member.objects.filter(entity=entity, is_deleted=False, id__in=usher_ids)
                service.ushers.set(selected_ushers)

                # ========CHALICE ASSISTANTS====================================================
                chalice_assistant_ids = [
                    value.strip()
                    for value in request.POST.get("chalice_assistant_ids", "").split(",")
                    if value.strip()
                ]   
                if chalice_assistant_ids:
                    selected_chalice_assistants = Member.objects.filter(
                    entity=entity,
                    is_deleted=False,
                    id__in=chalice_assistant_ids,
                )
                service.chalice_assistants.set(selected_chalice_assistants)            
                # ============================================================
                # GENERAL OFFERTORY / DUES / TITHES
                # ============================================================

                service.general_offertory = Decimal(
                    request.POST.get("general_offertory", "0").replace(",", "") or "0"
                )

                service.dues = Decimal(
                    request.POST.get("dues", "0").replace(",", "") or "0"
                )

                service.tithes = Decimal(
                    request.POST.get("tithes", "0").replace(",", "") or "0"
                )

                # ============================================================
                # DAY BORN OFFERINGS
                # ============================================================

                day_born = {}

                days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

                for day in days:
                    val = request.POST.get(f"day_born_{day}", "0").replace(",", "")

                    try:
                        amount = Decimal(val) if val else Decimal("0")

                        if amount > 0:
                            day_born[day.capitalize()] = str(amount)

                    except (ValueError, TypeError, ArithmeticError):
                        pass

                service.day_born_offerings = day_born  ##  Day born offerings stored as JSON

                # ============================================================
                # GUILD OFFERINGS
                # ============================================================

                guild_raw = request.POST.get("guild_offerings", "[]")

                try:
                    guild_data = json.loads(guild_raw) if guild_raw else []
                except (json.JSONDecodeError, TypeError):
                    guild_data = []

                if not isinstance(guild_data, list):
                    guild_data = []

                clean_guild_data = []

                for item in guild_data:
                    if not isinstance(item, dict):
                        continue

                    guild_id = item.get("guild_id")
                    guild_name = str(item.get("guild_name", "")).strip()
                    amount = item.get("amount", "0")

                    try:
                        amount = Decimal(str(amount).replace(",", "").strip() or "0")
                    except (ValueError, TypeError, ArithmeticError):
                        amount = Decimal("0")

                    if amount > 0 and guild_name:
                        clean_guild_data.append(
                            {
                                "guild_id": guild_id,
                                "guild_name": guild_name,
                                "amount": str(amount),
                            }
                        )

                service.guild_offerings = clean_guild_data

                # ============================================================
                # SPECIAL THANK OFFERING
                # ============================================================

                special_amount = request.POST.get("special_thank_amount", "0").replace(
                    ",", ""
                )

                try:
                    special_decimal = (
                        Decimal(special_amount) if special_amount else Decimal("0")
                    )
                except (ValueError, TypeError, ArithmeticError):
                    special_decimal = Decimal("0")

                service.special_thank_offering = (              ## Special Thank Offering stored as JSON
                    [{"name": "Special Thank Offering", "amount": str(special_decimal)}]
                    if special_decimal > 0
                    else []
                )

                # ============================================================
                # HARVEST THANK OFFERING
                # ============================================================

                harvest_amount = request.POST.get("harvest_thank_amount", "0").replace(
                    ",", ""
                )

                try:
                    harvest_decimal = (
                        Decimal(harvest_amount) if harvest_amount else Decimal("0")
                    )
                except (ValueError, TypeError, ArithmeticError):
                    harvest_decimal = Decimal("0")

                service.harvest_offering = (              ## Harvest Thank Offering stored as JSON          
                    [{"name": "Harvest Thank Offering", "amount": str(harvest_decimal)}]
                    if harvest_decimal > 0
                    else []
                )

                # ============================================================
                # CHRISTMAS OFFERINGS
                # ============================================================

                christmas_raw = request.POST.get("christmas_offering", "[]")

                try:
                    christmas_data = json.loads(christmas_raw) if christmas_raw else []
                except (json.JSONDecodeError, TypeError):
                    christmas_data = []

                if not isinstance(christmas_data, list):
                    christmas_data = []

                clean_christmas_data = []

                for item in christmas_data:
                    if not isinstance(item, dict):
                        continue

                    name = str(item.get("name", "")).strip()
                    amount = item.get("amount", "0")

                    try:
                        amount = Decimal(str(amount).replace(",", "").strip() or "0")
                    except (ValueError, TypeError, ArithmeticError):
                        amount = Decimal("0")

                    if name and amount > 0:
                        clean_christmas_data.append(
                            {
                                "name": name,
                                "amount": str(amount),
                            }
                        )

                service.christmas_offering = clean_christmas_data

                # ============================================================
                # EASTER OFFERINGS
                # ============================================================

                easter_raw = request.POST.get("easter_offering", "[]")

                try:
                    easter_data = json.loads(easter_raw) if easter_raw else []
                except (json.JSONDecodeError, TypeError):
                    easter_data = []

                if not isinstance(easter_data, list):
                    easter_data = []

                clean_easter_data = []

                for item in easter_data:
                    if not isinstance(item, dict):
                        continue

                    name = str(item.get("name", "")).strip()
                    amount = item.get("amount", "0")

                    try:
                        amount = Decimal(str(amount).replace(",", "").strip() or "0")
                    except (ValueError, TypeError, ArithmeticError):
                        amount = Decimal("0")

                    if name and amount > 0:
                        clean_easter_data.append(
                            {
                                "name": name,
                                "amount": str(amount),
                            }
                        )

                service.easter_offering = clean_easter_data

                # ============================================================
                # OTHER COLLECTIONS
                # ============================================================

                other_raw = request.POST.get("other_collections", "[]")

                try:
                    other_data = json.loads(other_raw) if other_raw else []
                except (json.JSONDecodeError, TypeError):
                    other_data = []

                if not isinstance(other_data, list):
                    other_data = []

                clean_other_data = []

                for item in other_data:
                    if not isinstance(item, dict):
                        continue

                    name = str(item.get("name", "")).strip()
                    amount = item.get("amount", "0")

                    try:
                        amount = Decimal(str(amount).replace(",", "").strip() or "0")
                    except (ValueError, TypeError, ArithmeticError):
                        amount = Decimal("0")

                    if name and amount > 0:
                        clean_other_data.append(
                            {
                                "name": name,
                                "amount": str(amount),
                            }
                        )

                service.other_collections = clean_other_data

                # ============================================================
                # SAVE SERVICE
                # Service.calculate_totals() runs from service.save()
                # ============================================================

                service.save()

                # ============================================================
                # POPULATE FIXED CHURCH OFFICES
                # ============================================================

                populate_service_offices(service)

                # Service is the source of these transactions
                service_content_type = ContentType.objects.get_for_model(Service)

                def to_decimal(value):
                    try:
                        if value is None or value == "":
                            return Decimal("0.00")

                        if isinstance(value, str):
                            value = value.replace(",", "").strip()

                        return Decimal(str(value))

                    except (ValueError, TypeError, ArithmeticError):
                        return Decimal("0.00")

        except Exception as e:
            messages.error(request, f"Error saving service: {str(e)}")
            import traceback
            traceback.print_exc()
            return redirect("ChurchApp:service_activity_create", slug=entity.slug)

        return redirect("ChurchApp:service_list_manage", slug=entity.slug)

    context = {
        "entity": entity,
        "clergy_list": clergy_list,
        "officiants": officiants,
        "chalice_assistants": chalice_assistants,
        "ushers": ushers,
        "guilds": guilds,
        "today": timezone.now().date(),
        "title": "Sunday Service Activity",
    }

    return render(request, "ChurchApp/service_activity_form.html", context)


@login_required
def service_post_to_trans(request, slug, service_id):
    """
    Confirm and post a Church Service to RecPayApp.Trans.

    Posting is allowed only when the user submits exactly:
        POST

    The Service is first displayed on the confirmation page.
    After successful posting, the Service is marked as posted and the
    user is redirected to the posting-success page.
    """

    entity = get_object_or_404(
        EntityModel,
        slug=slug,
    )

    service = get_object_or_404(
        Service,
        id=service_id,
        entity=entity,
    )

    # ---------------------------------------------------------
    # GET REQUEST
    # ---------------------------------------------------------
    # Display the confirmation page.
    if request.method == "GET":
        return render(
            request,
            "ChurchApp/service_post_confirm.html",
            {
                "entity": entity,
                "service": service,
            },
        )

    # ---------------------------------------------------------
    # ONLY POST REQUESTS MAY CONTINUE
    # ---------------------------------------------------------
    if request.method != "POST":
        messages.error(
            request,
            "Invalid request. Posting was not completed.",
        )

        return redirect(
            "ChurchApp:service_list_manage",
            slug=entity.slug,
        )

    # ---------------------------------------------------------
    # EXACT POST CONFIRMATION
    # ---------------------------------------------------------
    confirmation = request.POST.get("confirmation", "")

    if confirmation != "POST":
        return render(
            request,
            "ChurchApp/service_post_confirm.html",
            {
                "entity": entity,
                "service": service,
                "error": "Posting cancelled. You must type POST exactly to confirm.",
                "confirmation_value": confirmation,
            },
        )

    # ---------------------------------------------------------
    # PREVENT DUPLICATE POSTING
    # ---------------------------------------------------------
    if service.posted_to_ledger:
        messages.warning(
            request,
            "This Service has already been posted to Transactions.",
        )

        return redirect(
            "ChurchApp:service_post_success",
            slug=entity.slug,
            service_id=service.id,
        )

    # ---------------------------------------------------------
    # GENERIC RELATION TO SERVICE
    # ---------------------------------------------------------
    service_content_type = ContentType.objects.get_for_model(Service)

    # ---------------------------------------------------------
    # SECONDARY DUPLICATE PROTECTION
    # ---------------------------------------------------------
    existing_transactions = Trans.objects.filter(
        source_content_type=service_content_type,
        source_object_id=service.id,
    )

    if existing_transactions.exists():
        return render(request, "ChurchApp/service_post_confirm.html", {"entity": entity, "service": service, "error": (
                    "Transactions already exist for this Service. "
                    "Posting has been stopped to prevent duplicates."
                ),
            },
        )

    # ---------------------------------------------------------
    # DECIMAL HELPERS
    # ---------------------------------------------------------
    def to_decimal(value):
        if value is None or value == "":
            return Decimal("0")

        try:
            return Decimal(str(value).replace(",", ""))
        except (
            TypeError,
            ValueError,
            ArithmeticError,
        ):
            return Decimal("0")

    def list_total(items):
        if not isinstance(items, list):
            return Decimal("0")

        return sum(
            (
                to_decimal(item.get("amount", 0))
                for item in items
                if isinstance(item, dict)
            ),
            Decimal("0"),
        )

    # ---------------------------------------------------------
    # CALCULATE SERVICE AMOUNTS
    # ---------------------------------------------------------
    general_offertory_amount = to_decimal(service.general_offertory)

    dues_amount = to_decimal(service.dues)

    tithes_amount = to_decimal(service.tithes)

    # Day Born is stored as a dictionary.
    day_born_amount = Decimal("0")

    if isinstance(service.day_born_offerings, dict):
        day_born_amount = sum(
            (to_decimal(amount) for amount in service.day_born_offerings.values()),
            Decimal("0"),
        )

    # Lists of dictionaries.

    easter_amount = service.easter_total
    christmas_amount = service.christmas_total
    harvest_amount = service.harvest_total
    special_thanksgiving_amount = service.special_thank_offering_total 
    other_collections_amount = service.other_collections_total

    guild_amount = service.guild_total

    # ---------------------------------------------------------
    # THE 10 SERVICE TRANSACTION CATEGORIES
    # ---------------------------------------------------------
    service_transactions = [
        ("General Offertory",      "4010", general_offertory_amount),
        ("DayBorn Offerings",      "4011", day_born_amount),
        ("Guild Offerings",        "4012", guild_amount),
        ("Dues",                   "4013", dues_amount),
        ("Tithes",                 "4014", tithes_amount),
        ("Special Thank Offering", "4015", special_thanksgiving_amount),
        ("Easter Offering",        "4016", easter_amount),
        ("Christmas Offering",     "4017", christmas_amount),
        ("Harvest Offering",       "4018", harvest_amount),
        ("Other Collections",      "4019", other_collections_amount),
           
    ]

    # ------special_thanksgiving_amount = service.special_thank_offering_total---------------------------------------------------
    # CREATE TRANSACTIONS ATOMICALLY
    # ---------------------------------------------------------
    created_transactions = []

    with transaction.atomic():

        for category_name, ledger_code, amount in service_transactions:

            # Trans.amount has a minimum validator of 0.01.
            # Therefore, do not create zero-value transactions.
            if amount <= Decimal("0"):
                continue

            trans = Trans.objects.create(
                entity=entity,
                module="church",
                sub_module="service",
                source_content_type=service_content_type,
                source_object_id=service.id,
                date=service.date,
                trans_type="Receipts",
                amount=amount,
                pay_mode="Cash",
                ledger_code=ledger_code,
                ledger_name=category_name,
                purpose=category_name,
                details=(
                    f"{category_name} - "
                    f"{service.name_of_service or 'Sunday Service'}"
                ),
                status="POSTED",
                journal_status="PENDING",
                created_by=request.user,
                updated_by=request.user,
                created_by_name=(request.user.get_full_name() or request.user.username),
                created_by_username=request.user.username,
            )

            created_transactions.append(trans)

        # -----------------------------------------------------
        # MARK SERVICE AS POSTED ONLY AFTER TRANSACTIONS
        # -----------------------------------------------------
        service.posted_to_ledger = True

        service.save(
            update_fields=[
                "posted_to_ledger",
                "updated_at",
            ]
        )

    # ---------------------------------------------------------
    # SUCCESS
    # ---------------------------------------------------------
    return redirect(
        "ChurchApp:service_post_success",
        slug=entity.slug,
        service_id=service.id,
    )


@login_required
def service_post_success(request, slug, service_id):
    entity = get_object_or_404(EntityModel, slug=slug)
    service = get_object_or_404(Service, id=service_id, entity=entity)

    transaction_count = Trans.objects.filter(
        source_content_type=ContentType.objects.get_for_model(Service),
        source_object_id=service.id,
    ).count()

    return render(request, "ChurchApp/service_post_success.html", {"entity": entity, "service": service, "transaction_count": transaction_count})


@login_required
@staff_member_required
def service_activity_edit(request, slug, service_id):
    entity = get_object_or_404(EntityModel, slug=slug)

    service = get_object_or_404(
        Service,
        id=service_id,
        entity=entity,
    )

    # ------------------------------------------------------------
    # Do not allow editing after posting to Trans
    # ------------------------------------------------------------
    if service.posted_to_ledger:
        messages.error(
            request,
            "This service has already been posted to Trans and cannot be edited."
        )
        return redirect(
            "ChurchApp:service_list_manage",
            slug=entity.slug
        )

    # ------------------------------------------------------------
    # Dropdown data
    # ------------------------------------------------------------
    clergy_list = Clergy.objects.filter(
        entity=entity
    ).order_by("full_name")

    officiants = Member.objects.filter(
        entity=entity,
        is_deleted=False
    ).order_by("full_name")

    ushers = Member.objects.filter(
        entity=entity,
        is_deleted=False,
        member_roles__role__name="usher",
        member_roles__is_active=True,
    ).order_by("full_name").distinct()

    chalice_assistants = Member.objects.filter(
        entity=entity,
        is_deleted=False,
        member_roles__role__name="chalice_assistant",
        member_roles__is_active=True,
    ).order_by("full_name").distinct()

    guilds = Guild.objects.filter(
        entity=entity,
        is_active=True
    ).order_by("name")

    # ------------------------------------------------------------
    # Current selections
    # ------------------------------------------------------------
    selected_clergy = service.clergy.all()
    selected_ushers = service.ushers.all()
    selected_chalice_assistants = service.chalice_assistants.all()

    # ------------------------------------------------------------
    # POST - UPDATE SERVICE
    # ------------------------------------------------------------
    if request.method == "POST":

        try:
            with transaction.atomic():

                # ====================================================
                # BASIC SERVICE DATA
                # ====================================================

                date = datetime.strptime(
                    request.POST.get("date"),
                    "%Y-%m-%d"
                ).date()

                service.name_of_service = request.POST.get(
                    "service_name",
                    ""
                )

                service.date = date

                service.attendance = int(
                    request.POST.get("attendance", 0) or 0
                )

                service.communicants = int(
                    request.POST.get("communicants", 0) or 0
                )

                # ====================================================
                # CLERGY
                # ====================================================

                clergy_ids = [
                    value.strip()
                    for value in request.POST.get(
                        "clergy_ids",
                        ""
                    ).split(",")
                    if value.strip()
                ]

                selected_clergy = Clergy.objects.filter(
                    entity=entity,
                    id__in=clergy_ids
                )

                service.clergy.set(selected_clergy)

                # ====================================================
                # OFFICIANT
                # ====================================================

                officiant_id = request.POST.get("officiant")

                if officiant_id:
                    officiant = Member.objects.filter(
                        entity=entity,
                        is_deleted=False,
                        id=officiant_id,
                    ).first()

                    service.officiant = officiant
                else:
                    service.officiant = None

                # ====================================================
                # USHERS
                # ====================================================

                usher_ids = [
                    value.strip()
                    for value in request.POST.get(
                        "usher_ids",
                        ""
                    ).split(",")
                    if value.strip()
                ]

                selected_ushers = Member.objects.filter(
                    entity=entity,
                    is_deleted=False,
                    id__in=usher_ids
                )

                service.ushers.set(selected_ushers)

                # ====================================================
                # CHALICE ASSISTANTS
                # ====================================================

                chalice_assistant_ids = [
                    value.strip()
                    for value in request.POST.get(
                        "chalice_assistant_ids",
                        ""
                    ).split(",")
                    if value.strip()
                ]

                selected_chalice_assistants = Member.objects.filter(
                    entity=entity,
                    is_deleted=False,
                    id__in=chalice_assistant_ids
                )

                service.chalice_assistants.set(
                    selected_chalice_assistants
                )

                # ====================================================
                # GENERAL OFFERTORY / DUES / TITHES
                # ====================================================

                service.general_offertory = Decimal(
                    request.POST.get(
                        "general_offertory",
                        "0"
                    ).replace(",", "") or "0"
                )

                service.dues = Decimal(
                    request.POST.get(
                        "dues",
                        "0"
                    ).replace(",", "") or "0"
                )

                service.tithes = Decimal(
                    request.POST.get(
                        "tithes",
                        "0"
                    ).replace(",", "") or "0"
                )

                # ====================================================
                # DAY BORN OFFERINGS
                # ====================================================

                day_born = {}

                days = [
                    "monday",
                    "tuesday",
                    "wednesday",
                    "thursday",
                    "friday",
                    "saturday",
                    "sunday",
                ]

                for day in days:

                    val = request.POST.get(
                        f"day_born_{day}",
                        "0"
                    ).replace(",", "")

                    try:
                        amount = (
                            Decimal(val)
                            if val
                            else Decimal("0")
                        )

                        if amount > 0:
                            day_born[day.capitalize()] = str(
                                amount
                            )

                    except (
                        ValueError,
                        TypeError,
                        ArithmeticError
                    ):
                        pass

                service.day_born_offerings = day_born

                # ====================================================
                # GUILD OFFERINGS
                # ====================================================

                guild_raw = request.POST.get(
                    "guild_offerings",
                    "[]"
                )

                try:
                    guild_data = (
                        json.loads(guild_raw)
                        if guild_raw
                        else []
                    )
                except (
                    json.JSONDecodeError,
                    TypeError
                ):
                    guild_data = []

                if not isinstance(guild_data, list):
                    guild_data = []

                clean_guild_data = []

                for item in guild_data:

                    if not isinstance(item, dict):
                        continue

                    guild_id = item.get("guild_id")

                    guild_name = str(
                        item.get(
                            "guild_name",
                            ""
                        )
                    ).strip()

                    amount = item.get(
                        "amount",
                        "0"
                    )

                    try:
                        amount = Decimal(
                            str(amount)
                            .replace(",", "")
                            .strip() or "0"
                        )
                    except (
                        ValueError,
                        TypeError,
                        ArithmeticError
                    ):
                        amount = Decimal("0")

                    if amount > 0 and guild_name:

                        clean_guild_data.append({
                            "guild_id": guild_id,
                            "guild_name": guild_name,
                            "amount": str(amount),
                        })

                service.guild_offerings = clean_guild_data

                # ====================================================
                # SPECIAL THANK OFFERING
                # ====================================================

                special_amount = request.POST.get(
                    "special_thank_amount",
                    "0"
                ).replace(",", "")

                try:
                    special_decimal = (
                        Decimal(special_amount)
                        if special_amount
                        else Decimal("0")
                    )
                except (
                    ValueError,
                    TypeError,
                    ArithmeticError
                ):
                    special_decimal = Decimal("0")

                service.special_thank_offering = (
                    [
                        {
                            "name": "Special Thank Offering",
                            "amount": str(special_decimal)
                        }
                    ]
                    if special_decimal > 0
                    else []
                )

                # ====================================================
                # HARVEST THANK OFFERING
                # ====================================================

                harvest_amount = request.POST.get(
                    "harvest_thank_amount",
                    "0"
                ).replace(",", "")

                try:
                    harvest_decimal = (
                        Decimal(harvest_amount)
                        if harvest_amount
                        else Decimal("0")
                    )
                except (
                    ValueError,
                    TypeError,
                    ArithmeticError
                ):
                    harvest_decimal = Decimal("0")

                service.harvest_offering = (
                    [
                        {
                            "name": "Harvest Thank Offering",
                            "amount": str(harvest_decimal)
                        }
                    ]
                    if harvest_decimal > 0
                    else []
                )

                # ====================================================
                # CHRISTMAS OFFERINGS
                # ====================================================

                christmas_raw = request.POST.get(
                    "christmas_offering",
                    "[]"
                )

                try:
                    christmas_data = (
                        json.loads(christmas_raw)
                        if christmas_raw
                        else []
                    )
                except (
                    json.JSONDecodeError,
                    TypeError
                ):
                    christmas_data = []

                if not isinstance(christmas_data, list):
                    christmas_data = []

                clean_christmas_data = []

                for item in christmas_data:

                    if not isinstance(item, dict):
                        continue

                    name = str(
                        item.get("name", "")
                    ).strip()

                    amount = item.get(
                        "amount",
                        "0"
                    )

                    try:
                        amount = Decimal(
                            str(amount)
                            .replace(",", "")
                            .strip() or "0"
                        )
                    except (
                        ValueError,
                        TypeError,
                        ArithmeticError
                    ):
                        amount = Decimal("0")

                    if name and amount > 0:

                        clean_christmas_data.append({
                            "name": name,
                            "amount": str(amount),
                        })

                service.christmas_offering = clean_christmas_data

                # ====================================================
                # EASTER OFFERINGS
                # ====================================================

                easter_raw = request.POST.get(
                    "easter_offering",
                    "[]"
                )

                try:
                    easter_data = (
                        json.loads(easter_raw)
                        if easter_raw
                        else []
                    )
                except (
                    json.JSONDecodeError,
                    TypeError
                ):
                    easter_data = []

                if not isinstance(easter_data, list):
                    easter_data = []

                clean_easter_data = []

                for item in easter_data:

                    if not isinstance(item, dict):
                        continue

                    name = str(
                        item.get("name", "")
                    ).strip()

                    amount = item.get(
                        "amount",
                        "0"
                    )

                    try:
                        amount = Decimal(
                            str(amount)
                            .replace(",", "")
                            .strip() or "0"
                        )
                    except (
                        ValueError,
                        TypeError,
                        ArithmeticError
                    ):
                        amount = Decimal("0")

                    if name and amount > 0:

                        clean_easter_data.append({
                            "name": name,
                            "amount": str(amount),
                        })

                service.easter_offering = clean_easter_data
                # ====================================================
                # OTHER COLLECTIONS
                # ====================================================

                other_raw = request.POST.get(
                    "other_collections",
                    "[]"
                )

                try:
                    other_data = (
                        json.loads(other_raw)
                        if other_raw
                        else []
                    )
                except (
                    json.JSONDecodeError,
                    TypeError
                ):
                    other_data = []

                if not isinstance(other_data, list):
                    other_data = []

                clean_other_data = []

                for item in other_data:

                    if not isinstance(item, dict):
                        continue

                    name = str(
                        item.get("name", "")
                    ).strip()

                    amount = item.get(
                        "amount",
                        "0"
                    )

                    try:
                        amount = Decimal(
                            str(amount)
                            .replace(",", "")
                            .strip() or "0"
                        )
                    except (
                        ValueError,
                        TypeError,
                        ArithmeticError
                    ):
                        amount = Decimal("0")

                    if name and amount > 0:

                        clean_other_data.append({
                            "name": name,
                            "amount": str(amount),
                        })

                service.other_collections = clean_other_data

                # ====================================================
                # SAVE UPDATED SERVICE
                # ====================================================

                service.save()

                messages.success(
                    request,
                    "Service updated successfully."
                )

                return redirect(
                    "ChurchApp:service_list_manage",
                    slug=entity.slug
                )

        except Exception as e:

            messages.error(
                request,
                f"Error updating service: {str(e)}"
            )

            import traceback
            traceback.print_exc()

    # ------------------------------------------------------------
    # EXISTING DATA FOR EDIT FORM
    # ------------------------------------------------------------

    initial_clergy_ids = list(
        service.clergy.values_list(
            "id",
            flat=True
        )
    )

    initial_usher_ids = list(
        service.ushers.values_list(
            "id",
            flat=True
        )
    )

    initial_chalice_assistant_ids = list(
        service.chalice_assistants.values_list(
            "id",
            flat=True
        )
    )

    initial_guild_offerings = (
        service.guild_offerings or []
    )

    initial_christmas_offerings = (
        service.christmas_offering or []
    )

    initial_easter_offerings = (
        service.easter_offering or []
    )

    initial_other_offerings = (
        service.other_collections or []
    )

    special_thank_amount = (
        service.special_thank_offering[0].get(
            "amount",
            "0"
        )
        if service.special_thank_offering
        else "0"
    )

    harvest_thank_amount = (
        service.harvest_offering[0].get(
            "amount",
            "0"
        )
        if service.harvest_offering
        else "0"
    )

    # ------------------------------------------------------------
    # RENDER EDIT FORM
    # ------------------------------------------------------------

    return render(
        request,
        "ChurchApp/service_activity_edit.html",
        {
            "entity": entity,
            "service": service,

            "clergy_list": clergy_list,
            "officiants": officiants,
            "ushers": ushers,
            "chalice_assistants": chalice_assistants,
            "guilds": guilds,

            "selected_clergy": selected_clergy,
            "selected_ushers": selected_ushers,
            "selected_chalice_assistants": (
                selected_chalice_assistants
            ),

            "initial_clergy_ids": initial_clergy_ids,
            "initial_usher_ids": initial_usher_ids,
            "initial_chalice_assistant_ids": (
                initial_chalice_assistant_ids
            ),

            "initial_guild_offerings": (
                initial_guild_offerings
            ),

            "initial_christmas_offerings": (
                initial_christmas_offerings
            ),

            "initial_easter_offerings": (
                initial_easter_offerings
            ),

            "initial_other_offerings": (
                initial_other_offerings
            ),

            "special_thank_amount": (
                special_thank_amount
            ),

            "harvest_thank_amount": (
                harvest_thank_amount
            ),

            "today": service.date,
        }
    )


@login_required
@staff_member_required
def service_delete(request, slug, service_id):
    entity = get_object_or_404(EntityModel, slug=slug)

    service = get_object_or_404(Service, id=service_id, entity=entity)

    if request.method == "POST":
        service.delete()

        messages.success(request, "Service deleted successfully.")

        return redirect("ChurchApp:service_list_manage", slug=entity.slug)

    return render(request, "ChurchApp/service_delete_confirm.html", {"entity": entity, "service": service})


##========================================END OF CHURCH SERVICE=============================================

@login_required
@staff_member_required
def church_config_edit(request, slug):
    """
    Edit church-specific configuration.
    """
    entity = get_object_or_404(EntityModel, slug=slug)

    # Get or create the church config
    config, created = ChurchConfig.objects.get_or_create(entity=entity)

    if request.method == "POST":
        form = ChurchConfigForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f" Church configuration for {entity.name} updated successfully!",
            )
            return redirect("ChurchApp:church_config_edit", slug=entity.slug)
        else:
            messages.error(request, " Please correct the errors below.")
    else:
        form = ChurchConfigForm(instance=config)

    context = {
        "entity": entity,
        "form": form,
        "config": config,
        "title": "Church Configuration",
        "created": created,
    }
    return render(request, "ChurchApp/church_config_form.html", context)

@staff_member_required
def guild_list_manage(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    guilds = Guild.objects.filter(entity=entity).order_by("name")
    context = {
        "entity": entity,
        "guilds": guilds,
        "total_guilds": guilds.count(),
    }
    return render(request, "ChurchApp/guild_list_manage.html", context)


@staff_member_required
def guild_create(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)

    if request.method == "POST":
        form = GuildForm(request.POST)
        if form.is_valid():
            guild = form.save(commit=False)
            guild.entity = entity
            guild.save()
            messages.success(request, f"Guild '{guild.name}' created successfully.")
            return redirect("ChurchApp:guild_list_manage", slug=entity.slug)
    else:
        form = GuildForm()
    context = {
        "entity": entity,
        "form": form,
        "title": "Add Guild",
        "guilds": Guild.objects.filter(entity=entity).order_by("name"),
    }
    return render(request, "ChurchApp/guild_form.html", context)


@staff_member_required
def guild_update(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    guild = get_object_or_404(Guild, pk=pk, entity=entity)
    if request.method == "POST":
        form = GuildForm(request.POST, instance=guild)
        if form.is_valid():
            form.save()
            messages.success(request, f"Guild '{guild.name}' updated successfully.")
            return redirect("ChurchApp:guild_list_manage", slug=entity.slug)
    else:
        form = GuildForm(instance=guild)
    context = {
        "entity": entity,
        "form": form,
        "guild": guild,
        "title": f"Edit Guild: {guild.name}",
        "guilds": Guild.objects.filter(entity=entity).order_by("name"),
    }
    return render(request, "ChurchApp/guild_form.html", context)


@staff_member_required
def guild_delete(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    guild = get_object_or_404(Guild, pk=pk, entity=entity)
    if request.method == "POST":
        guild.delete()
        messages.success(request, f"Guild '{guild.name}' deleted successfully.")
        return redirect("ChurchApp:guild_list_manage", slug=entity.slug)
    context = {
        "entity": entity,
        "guild": guild,
    }
    return render(request, "ChurchApp/guild_confirm_delete.html", context)


@staff_member_required
def guild_detail(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    guild = get_object_or_404(Guild, pk=pk, entity=entity)
    context = {
        "entity": entity,
        "guild": guild,
    }
    return render(request, "ChurchApp/guild_detail.html", context)


## =========================================ChatGpt ==============================

@login_required
def service_activity_view(request, slug, service_id):
    entity = get_object_or_404(EntityModel, slug=slug)

    service = get_object_or_404(Service, id=service_id, entity=entity)

    # Get all Trans records created from this Service
    service_transactions = Trans.objects.filter(
        source_content_type=ContentType.objects.get_for_model(Service),
        source_object_id=service.id
    ).order_by("id")

    context = {
        "entity": entity,
        "service": service,
        "service_transactions": service_transactions,
    }

    return render(request, "ChurchApp/service_activity_view.html", context)


@login_required
def service_activity_pdf(request, slug, service_id):
    """
    Generate an A4 portrait PDF for a single Service activity.

    Uses the existing Service model properties for totals and
    ordered Day-Born offerings.
    """

    entity = get_object_or_404(EntityModel, slug=slug)

    service = get_object_or_404(Service, id=service_id, entity=entity)

    template_path = "ChurchApp/service_activity_pdf.html"

    context = {
        "entity": entity,
        "service": service,
    }

    template = get_template(template_path)

    html = template.render(context)

    response = HttpResponse(content_type="application/pdf")

    filename = (
        f"service_activity_{service.id}_" f"{service.date.strftime('%Y%m%d')}.pdf"
    )

    response["Content-Disposition"] = f'inline; filename="{filename}"'

    pisa_status = pisa.CreatePDF(
        html,
        dest=response,
    )

    if pisa_status.err:
        return HttpResponse("PDF generation failed.", status=500)

    return response


@login_required
def service_activity_excel(request, slug, service_id):
    entity = get_object_or_404(EntityModel, slug=slug)

    service = get_object_or_404(
        Service,
        id=service_id,
        entity=entity,
    )

    # ---------------------------------------------------------
    # CREATE WORKBOOK
    # ---------------------------------------------------------
    wb = Workbook()
    ws = wb.active
    ws.title = "Service Activity"

    # ---------------------------------------------------------
    # A4 PRINT SETTINGS
    # ---------------------------------------------------------
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.orientation = ws.ORIENTATION_PORTRAIT

    # One page wide, but allow multiple pages vertically.
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True

    ws.page_margins = PageMargins(
        left=0.35,
        right=0.35,
        top=0.45,
        bottom=0.45,
        header=0.20,
        footer=0.20,
    )

    ws.sheet_view.showGridLines = False
    ws.freeze_panes = "A6"

    # ---------------------------------------------------------
    # STYLES
    # ---------------------------------------------------------
    thin = Side(style="thin", color="B7B7B7")
    medium = Side(style="medium", color="404040")

    normal_border = Border(left=thin, right=thin, top=thin, bottom=thin)
    total_border = Border(left=thin, right=thin, top=medium, bottom=medium)
    title_fill = PatternFill(fill_type="solid", fgColor="D9EAF7")
    section_fill = PatternFill(fill_type="solid", fgColor="EDEDED")
    header_fill = PatternFill(fill_type="solid", fgColor="404040")
    total_fill = PatternFill(fill_type="solid", fgColor="E2F0D9")

    currency_format = "₵#,##0.00"
    integer_format = "#,##0"

    # ---------------------------------------------------------
    # HELPER FUNCTIONS
    # ---------------------------------------------------------
    def section_title(row, title):
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=4)

        cell = ws.cell(row=row, column=1)
        cell.value = title
        cell.font = Font(bold=True, size=11)
        cell.fill = section_fill
        cell.border = Border(
            top=medium,
            bottom=thin,
        )
        cell.alignment = Alignment(
            horizontal="left",
            vertical="center",
        )

        return row + 1

    def table_header(row, headers):
        for column, value in enumerate(headers, start=1):
            cell = ws.cell(
                row=row,
                column=column,
            )
            cell.value = value
            cell.font = Font(
                bold=True,
                color="FFFFFF",
            )
            cell.fill = header_fill
            cell.border = normal_border
            cell.alignment = Alignment(
                horizontal="center",
                vertical="center",
            )

        return row + 1

    def convert_amount(value):
        """
        Convert JSON amount values such as:
        '800'
        '2,400'
        800
        Decimal('800.00')
        into an Excel-compatible numeric value.
        """
        from decimal import Decimal, InvalidOperation

        if value in (None, ""):
            return Decimal("0.00")

        try:
            return Decimal(str(value).replace(",", ""))
        except (
            InvalidOperation,
            TypeError,
            ValueError,
        ):
            return Decimal("0.00")

    # ---------------------------------------------------------
    # TITLE
    # ---------------------------------------------------------
    ws.merge_cells("A1:D1")

    ws["A1"] = service.name_of_service or "Sunday Service"

    ws["A1"].font = Font(
        bold=True,
        size=18,
    )

    ws["A1"].fill = title_fill
    ws["A1"].alignment = Alignment(
        horizontal="center",
        vertical="center",
    )

    ws.row_dimensions[1].height = 28

    # ---------------------------------------------------------
    # ENTITY + DATE
    # ---------------------------------------------------------
    ws.merge_cells("A2:D2")

    ws["A2"] = f"{entity.name} | " f"{service.date.strftime('%d %B %Y')}"

    ws["A2"].font = Font(
        italic=True,
        size=10,
    )

    ws["A2"].alignment = Alignment(
        horizontal="center",
    )

    # ---------------------------------------------------------
    # STATUS
    # ---------------------------------------------------------
    ws.merge_cells("A3:D3")

    ws["A3"] = "POSTED" if service.posted_to_ledger else "PENDING"

    ws["A3"].font = Font(
        bold=True,
        size=10,
    )

    ws["A3"].alignment = Alignment(
        horizontal="center",
    )

    # ---------------------------------------------------------
    # START ROW
    # ---------------------------------------------------------
    row = 5

    # =========================================================
    # SERVICE INFORMATION
    # =========================================================
    row = section_title(
        row,
        "SERVICE INFORMATION",
    )

    service_information = [
        ("Service", service.name_of_service or ""),
        (
            "Date",
            service.date.strftime("%d %B %Y"),
        ),
        ("Attendance", service.attendance),
        ("Communicants", service.communicants),
    ]

    for label, value in service_information:
        ws.cell(row, 1).value = label
        ws.cell(row, 1).font = Font(bold=True)

        ws.cell(row, 2).value = value

        ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=4)

        for column in range(1, 5):
            ws.cell(row, column).border = normal_border

        row += 1

    row += 1

    # =========================================================
    # MINISTRY TEAM
    # =========================================================
    row = section_title(row, "MINISTRY TEAM")

    row = table_header(row,
        [
            "Role",
            "Names",
            "",
            "",
        ],
    )

    ws.merge_cells(
        start_row=row - 1,
        start_column=2,
        end_row=row - 1,
        end_column=4,
    )

    clergy_names = (
        ", ".join(clergy.full_name for clergy in service.clergy.all()) or "None"
    )

    officiant_name = service.officiant.full_name if service.officiant else "None"

    usher_names = ", ".join(usher.full_name for usher in service.ushers.all()) or "None"

    chalice_names = (
        ", ".join(assistant.full_name for assistant in service.chalice_assistants.all())
        or "None"
    )

    ministry = [
        ("Clergy", clergy_names),
        ("Officiant", officiant_name),
        ("Ushers", usher_names),
        ("Chalice Assistants", chalice_names),
    ]

    for role, names in ministry:
        ws.cell(row, 1).value = role

        ws.merge_cells(
            start_row=row,
            start_column=2,
            end_row=row,
            end_column=4,
        )

        ws.cell(row, 2).value = names

        for column in range(1, 5):
            ws.cell(row, column).border = normal_border
            ws.cell(row, column).alignment = Alignment(
                vertical="top",
                wrap_text=True,
            )

        row += 1

    row += 1

    # =========================================================
    # CHURCH OFFICERS
    # =========================================================
    row = section_title(
        row,
        "CHURCH OFFICERS",
    )

    row = table_header(
        row,
        [
            "Office",
            "Holder",
            "",
            "",
        ],
    )

    ws.merge_cells(
        start_row=row - 1,
        start_column=2,
        end_row=row - 1,
        end_column=4,
    )

    officers = [
        (
            "Priest Warden",
            service.priest_warden or "None",
        ),
        (
            "People's Warden",
            service.peoples_warden or "None",
        ),
        (
            "Verger",
            service.verger or "None",
        ),
        (
            "Parish-Clerk",
            service.parish_clerk or "None",
        ),
        (
            "Accounts-Clerk",
            service.accounts_clerk or "None",
        ),
    ]

    for office, holder in officers:
        ws.cell(row, 1).value = office

        ws.merge_cells(
            start_row=row,
            start_column=2,
            end_row=row,
            end_column=4,
        )

        ws.cell(row, 2).value = holder

        for column in range(1, 5):
            ws.cell(row, column).border = normal_border

        row += 1

    row += 1

    # =========================================================
    # PCC
    # =========================================================
    row = section_title(
        row,
        "PCC MEMBERS",
    )

    pcc_names = ", ".join(service.pcc_members) if service.pcc_members else "None"

    ws.merge_cells(
        start_row=row,
        start_column=1,
        end_row=row,
        end_column=4,
    )

    ws.cell(row, 1).value = pcc_names
    ws.cell(row, 1).border = normal_border
    ws.cell(row, 1).alignment = Alignment(
        wrap_text=True,
        vertical="top",
    )

    row += 2

    # =========================================================
    # MAIN COLLECTIONS
    # =========================================================
    row = section_title(
        row,
        "MAIN COLLECTIONS",
    )

    row = table_header(
        row,
        [
            "Collection",
            "GL Code",
            "Amount",
            "",
        ],
    )

    main_collections = [
        (
            "General Offertory",
            "4010",
            service.general_offertory,
        ),
        (
            "Dues",
            "4011",
            service.dues,
        ),
        (
            "Tithes",
            "4012",
            service.tithes,
        ),
    ]

    for name, code, amount in main_collections:
        ws.cell(row, 1).value = name
        ws.cell(row, 2).value = code
        ws.cell(row, 3).value = convert_amount(amount)

        ws.cell(row, 3).number_format = currency_format

        for column in range(1, 5):
            ws.cell(row, column).border = normal_border

        row += 1

    row += 1

    # =========================================================
    # DAY-BORN
    # =========================================================
    row = section_title(
        row,
        "DAY-BORN OFFERINGS",
    )

    row = table_header(
        row,
        [
            "Day",
            "Amount",
            "",
            "",
        ],
    )

    for day, amount in service.ordered_day_born_offerings:
        ws.cell(row, 1).value = day
        ws.cell(row, 2).value = convert_amount(amount)
        ws.cell(row, 2).number_format = currency_format

        for column in range(1, 5):
            ws.cell(row, column).border = normal_border

        row += 1

    ws.cell(row, 1).value = "Total"
    ws.cell(row, 1).font = Font(bold=True)

    ws.cell(row, 2).value = convert_amount(service.day_born_total)
    ws.cell(row, 2).number_format = currency_format

    for column in range(1, 5):
        ws.cell(row, column).border = total_border
        ws.cell(row, column).fill = total_fill
        ws.cell(row, column).font = Font(bold=True)

    row += 2

    # =========================================================
    # GUILD
    # =========================================================
    row = section_title(
        row,
        "GUILD OFFERINGS",
    )

    row = table_header(
        row,
        [
            "Guild",
            "Amount",
            "",
            "",
        ],
    )

    guild_items = service.guild_offerings or []

    if guild_items:
        for item in guild_items:
            ws.cell(row, 1).value = (
                item.get("guild_name") or item.get("name") or "Guild"
            )

            ws.cell(row, 2).value = convert_amount(item.get("amount", 0))

            ws.cell(row, 2).number_format = currency_format

            for column in range(1, 5):
                ws.cell(row, column).border = normal_border

            row += 1
    else:
        ws.cell(row, 1).value = "None"
        ws.cell(row, 2).value = convert_amount(0)
        ws.cell(row, 2).number_format = currency_format

        for column in range(1, 5):
            ws.cell(row, column).border = normal_border

        row += 1

    ws.cell(row, 1).value = "Total"
    ws.cell(row, 1).font = Font(bold=True)

    ws.cell(row, 2).value = convert_amount(service.guild_total)
    ws.cell(row, 2).number_format = currency_format

    for column in range(1, 5):
        ws.cell(row, column).border = total_border
        ws.cell(row, column).fill = total_fill
        ws.cell(row, column).font = Font(bold=True)

    row += 2

    # =========================================================
    # SPECIAL COLLECTIONS
    # =========================================================
    row = section_title(
        row,
        "SPECIAL COLLECTIONS",
    )

    row = table_header(
        row,
        [
            "Collection",
            "Description",
            "Amount",
            "",
        ],
    )

    special_collections = [
        (
            "Special Thanksgiving",
            service.special_thank_offering,
        ),
        (
            "Easter",
            service.easter_offering,
        ),
        (
            "Christmas",
            service.christmas_offering,
        ),
        (
            "Harvest",
            service.harvest_offering,
        ),
        (
            "Other Collections",
            service.other_collections,
        ),
    ]

    for collection_name, items in special_collections:
        items = items or []

        if items:
            for item in items:
                description = (
                    item.get("name") or item.get("description") or collection_name
                )

                ws.cell(row, 1).value = collection_name
                ws.cell(row, 2).value = description
                ws.cell(row, 3).value = convert_amount(item.get("amount", 0))

                ws.cell(row, 3).number_format = currency_format

                for column in range(1, 5):
                    ws.cell(row, column).border = normal_border

                row += 1

        else:
            ws.cell(row, 1).value = collection_name
            ws.cell(row, 2).value = "None"
            ws.cell(row, 3).value = convert_amount(0)
            ws.cell(row, 3).number_format = currency_format

            for column in range(1, 5):
                ws.cell(row, column).border = normal_border

            row += 1

    row += 1

    # =========================================================
    # ACCOUNTING SUMMARY
    # =========================================================
    row = section_title(
        row,
        "ACCOUNTING SUMMARY",
    )

    row = table_header(
        row,
        [
            "Collection",
            "General Ledger Code",
            "Amount",
            "",
        ],
    )

    accounting_summary = [
        (
            "General Offertory",
            "4010",
            service.general_offertory,
        ),
        (
            "Dues",
            "4011",
            service.dues,
        ),
        (
            "Tithes",
            "4012",
            service.tithes,
        ),
        (
            "Day-Born Collection",
            "4013",
            service.day_born_total,
        ),
        (
            "Guild Collection",
            "4014",
            service.guild_total,
        ),
        (
            "Special Thanksgiving",
            "4015",
            service.special_thank_offering_total,
        ),
        (
            "Easter",
            "4016",
            service.easter_total,
        ),
        (
            "Christmas",
            "4017",
            service.christmas_total,
        ),
        (
            "Harvest",
            "4018",
            service.harvest_total,
        ),
        (
            "Other Collections",
            "4019",
            service.other_collections_total,
        ),
    ]

    for name, code, amount in accounting_summary:
        ws.cell(row, 1).value = name
        ws.cell(row, 2).value = code
        ws.cell(row, 3).value = convert_amount(amount)
        ws.cell(row, 3).number_format = currency_format

        for column in range(1, 5):
            ws.cell(row, column).border = normal_border

        row += 1

    # Grand total
    ws.cell(
        row,
        1,
    ).value = "TOTAL COLLECTIONS FOR THE DAY"

    ws.cell(
        row,
        3,
    ).value = convert_amount(service.grand_total)

    ws.cell(
        row,
        3,
    ).number_format = currency_format

    for column in range(1, 5):
        ws.cell(row, column).border = total_border
        ws.cell(row, column).fill = total_fill
        ws.cell(row, column).font = Font(
            bold=True,
            size=11,
        )

    row += 2

    # =========================================================
    # RECORD INFORMATION
    # =========================================================
    row = section_title(
        row,
        "RECORD INFORMATION",
    )

    record_information = [
        (
            "Created",
            service.created_at.strftime("%d %B %Y %H:%M"),
        ),
        (
            "Last Updated",
            service.updated_at.strftime("%d %B %Y %H:%M"),
        ),
        (
            "Status",
            "Posted" if service.posted_to_ledger else "Pending",
        ),
    ]

    for label, value in record_information:
        ws.cell(row, 1).value = label
        ws.cell(row, 1).font = Font(bold=True)

        ws.merge_cells(
            start_row=row,
            start_column=2,
            end_row=row,
            end_column=4,
        )

        ws.cell(row, 2).value = value

        for column in range(1, 5):
            ws.cell(row, column).border = normal_border

        row += 1

    # ---------------------------------------------------------
    # COLUMN WIDTHS
    # ---------------------------------------------------------
    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 30
    ws.column_dimensions["C"].width = 18
    ws.column_dimensions["D"].width = 5

    # ---------------------------------------------------------
    # ALIGNMENT
    # ---------------------------------------------------------
    for current_row in ws.iter_rows(
        min_row=1,
        max_row=row,
        min_col=1,
        max_col=4,
    ):
        for cell in current_row:
            cell.alignment = Alignment(
                vertical="center",
                wrap_text=True,
            )

    # Re-apply centered title alignment
    ws["A1"].alignment = Alignment(
        horizontal="center",
        vertical="center",
    )

    ws["A2"].alignment = Alignment(
        horizontal="center",
        vertical="center",
    )

    ws["A3"].alignment = Alignment(
        horizontal="center",
        vertical="center",
    )

    # ---------------------------------------------------------
    # PRINT AREA / FOOTER
    # ---------------------------------------------------------
    ws.print_area = f"A1:D{row}"
    ws.print_title_rows = "1:5"

    ws.oddFooter.center.text = (
        f"{entity.name} — " f"{service.name_of_service} — " f"Page &P of &N"
    )

    ws.oddFooter.center.size = 8

    # ---------------------------------------------------------
    # RETURN EXCEL FILE
    # ---------------------------------------------------------
    output = BytesIO()

    wb.save(output)
    output.seek(0)

    filename = (
        f"service_activity_" f"{service.id}_" f"{service.date.strftime('%Y%m%d')}.xlsx"
    )

    response = HttpResponse(
        output.getvalue(),
        content_type=(
            "application/vnd.openxmlformats-officedocument." "spreadsheetml.sheet"
        ),
    )

    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    return response


@staff_member_required
def service_pdf(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    service = get_object_or_404(Service, pk=pk, entity=entity)

    # Calculate totals (same as in detail view)
    special_total = sum(
        item.get("amount", 0)
        for item in service.special_thank_offering
        if isinstance(item, dict)
    )
    easter_total = sum(
        item.get("amount", 0)
        for item in service.easter_offering
        if isinstance(item, dict)
    )
    christmas_total = sum(
        item.get("amount", 0)
        for item in service.christmas_offering
        if isinstance(item, dict)
    )
    harvest_total = sum(
        item.get("amount", 0)
        for item in service.harvest_offering
        if isinstance(item, dict)
    )
    other_total = sum(
        item.get("amount", 0)
        for item in service.other_collections
        if isinstance(item, dict)
    )

    context = {
        "entity": entity,
        "service": service,
        "special_total": special_total,
        "easter_total": easter_total,
        "christmas_total": christmas_total,
        "harvest_total": harvest_total,
        "other_total": other_total,
        "title": f"Service Report - {service.name_of_service}",
    }

    template = get_template("ChurchApp/service_pdf.html")
    html = template.render(context)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="service_{service.pk}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("PDF generation error", status=500)
    return response


@staff_member_required
def service_excel(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    service = get_object_or_404(Service, pk=pk, entity=entity)

    # Calculate totals
    special_total = sum(
        item.get("amount", 0)
        for item in service.special_thank_offering
        if isinstance(item, dict)
    )
    easter_total = sum(
        item.get("amount", 0)
        for item in service.easter_offering
        if isinstance(item, dict)
    )
    christmas_total = sum(
        item.get("amount", 0)
        for item in service.christmas_offering
        if isinstance(item, dict)
    )
    harvest_total = sum(
        item.get("amount", 0)
        for item in service.harvest_offering
        if isinstance(item, dict)
    )
    other_total = sum(
        item.get("amount", 0)
        for item in service.other_collections
        if isinstance(item, dict)
    )

    wb = Workbook()
    ws = wb.active
    ws.title = "Service Report"

    # Styles
    bold_font = Font(bold=True)
    center_align = Alignment(horizontal="center", vertical="center")
    right_align = Alignment(horizontal="right")
    thin_border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin"),
    )

    # Header
    ws.merge_cells("A1:C1")
    ws["A1"] = f"Service Report – {service.name_of_service}"
    ws["A1"].font = Font(size=14, bold=True)
    ws["A1"].alignment = center_align

    ws["A3"] = "Date:"
    ws["B3"] = service.date.strftime("%Y-%m-%d")
    ws["A4"] = "Attendance:"
    ws["B4"] = service.attendance
    ws["A5"] = "Communicants:"
    ws["B5"] = service.communicants

    # Ministry Team
    ws["A7"] = "Clergy:"
    ws["B7"] = ", ".join([c.full_name for c in service.clergy.all()]) or "None"
    ws["A8"] = "Officiant:"
    ws["B8"] = service.officiant.full_name if service.officiant else "None"
    ws["A9"] = "Ushers:"
    ws["B9"] = ", ".join([u.full_name for u in service.ushers.all()]) or "None"

    # Finance
    ws["A11"] = "Finance"
    ws["A11"].font = bold_font
    ws["A12"] = "General Offertory:"
    ws["B12"] = float(service.general_offertory)
    ws["C12"] = "₵"
    ws["A13"] = "Dues:"
    ws["B13"] = float(service.dues)
    ws["C13"] = "₵"
    ws["A14"] = "Tithes:"
    ws["B14"] = float(service.tithes)
    ws["C14"] = "₵"

    # DayBorn
    row = 16
    ws["A" + str(row)] = "Day-Born Offerings"
    ws["A" + str(row)].font = bold_font
    row += 1
    for day, amount in service.day_born_offerings.items():
        ws["A" + str(row)] = day
        ws["B" + str(row)] = float(amount)
        ws["C" + str(row)] = "₵"
        row += 1
    ws["A" + str(row)] = "Total Day-Born"
    ws["B" + str(row)] = float(service.day_born_total)
    ws["C" + str(row)] = "₵"
    ws["A" + str(row)].font = bold_font

    # Guilds
    row += 2
    ws["A" + str(row)] = "Guild Offerings"
    ws["A" + str(row)].font = bold_font
    row += 1
    for item in service.guild_offerings:
        ws["A" + str(row)] = item.get("guild_name", "Guild")
        ws["B" + str(row)] = float(item.get("amount", 0))
        ws["C" + str(row)] = "₵"
        row += 1
    ws["A" + str(row)] = "Total Guild"
    ws["B" + str(row)] = float(service.guild_total)
    ws["C" + str(row)] = "₵"
    ws["A" + str(row)].font = bold_font

    # Special Offerings
    row += 2
    ws["A" + str(row)] = "Special Offerings"
    ws["A" + str(row)].font = bold_font
    row += 1

    specials = [
        ("Special Thank", service.special_thank_offering, special_total),
        ("Harvest Thank", service.harvest_offering, harvest_total),
        ("Christmas Thank", service.christmas_offering, christmas_total),
        ("Easter Thank", service.easter_offering, easter_total),
        ("Other Collections", service.other_collections, other_total),
    ]
    for label, items, total in specials:
        ws["A" + str(row)] = label
        row += 1
        for item in items:
            name = item.get("name") or item.get("description") or label
            ws["A" + str(row)] = "  " + name
            ws["B" + str(row)] = float(item.get("amount", 0))
            ws["C" + str(row)] = "₵"
            row += 1
        ws["A" + str(row)] = "  Total " + label
        ws["B" + str(row)] = float(total)
        ws["C" + str(row)] = "₵"
        ws["A" + str(row)].font = bold_font
        row += 1

    # Grand Total
    row += 1
    ws["A" + str(row)] = "GRAND TOTAL"
    ws["A" + str(row)].font = Font(bold=True, size=12)
    ws["B" + str(row)] = float(service.grand_total)
    ws["C" + str(row)] = "₵"
    ws["B" + str(row)].font = Font(bold=True, size=12)

    # Adjust column widths
    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 15
    ws.column_dimensions["C"].width = 10

    # Apply borders to all cells with data
    for row in ws.iter_rows(min_row=1, max_row=ws.max_row, min_col=1, max_col=3):
        for cell in row:
            cell.border = thin_border

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = (
        f'attachment; filename="service_{service.pk}.xlsx"'
    )
    wb.save(response)
    return response


@staff_member_required
def service_list_report(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)

    # Get date range from query params
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')

    # Default: last 30 days
    if not start_date:
        start_date = (timezone.now().date() - timedelta(days=30)).isoformat()
    if not end_date:
        end_date = timezone.now().date().isoformat()

    # Parse dates
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        start = timezone.now().date() - timedelta(days=30)
        end = timezone.now().date()

    # Filter services
    services = Service.objects.filter(
        entity=entity,
        date__gte=start,
        date__lte=end
    ).order_by('date')

    # Paginate (20 per page)
    paginator = Paginator(services, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Compute column totals for the whole filtered set (not just page)
    totals = services.aggregate(
        total_attendance=Sum('attendance'),
        total_communicants=Sum('communicants'),
        total_dues=Sum('dues'),
        total_tithes=Sum('tithes'),
        total_general_offertory=Sum('general_offertory'),
        total_day_born=Sum('day_born_total'),
        total_guild=Sum('guild_total'),
        total_easter=Sum('easter_offering'),  # Can't sum JSON directly; we'll compute in Python
        total_christmas=Sum('christmas_offering'),
        total_harvest=Sum('harvest_offering'),
        total_special=Sum('special_thank_offering'),
        total_other=Sum('other_collections'),
        total_grand=Sum('grand_total'),
    )

    # For JSON fields, we need to sum manually because Sum won't work on JSONField
    # We'll loop through the queryset to compute these totals
    easter_sum = 0
    christmas_sum = 0
    harvest_sum = 0
    special_sum = 0
    other_sum = 0
    for s in services:
        easter_sum += sum(item.get('amount', 0) for item in s.easter_offering if isinstance(item, dict))
        christmas_sum += sum(item.get('amount', 0) for item in s.christmas_offering if isinstance(item, dict))
        harvest_sum += sum(item.get('amount', 0) for item in s.harvest_offering if isinstance(item, dict))
        special_sum += sum(item.get('amount', 0) for item in s.special_thank_offering if isinstance(item, dict))
        other_sum += sum(item.get('amount', 0) for item in s.other_collections if isinstance(item, dict))

    # Compute per-service JSON totals for display in the table (we'll use the model's fields)
    # But the model already has day_born_total, guild_total, etc.

    context = {
        'entity': entity,
        'services': page_obj,
        'start_date': start.isoformat(),
        'end_date': end.isoformat(),
        'totals': {
            'attendance': totals['total_attendance'] or 0,
            'communicants': totals['total_communicants'] or 0,
            'dues': totals['total_dues'] or 0,
            'tithes': totals['total_tithes'] or 0,
            'general_offertory': totals['total_general_offertory'] or 0,
            'day_born': totals['total_day_born'] or 0,
            'guild': totals['total_guild'] or 0,
            'easter': easter_sum,
            'christmas': christmas_sum,
            'harvest': harvest_sum,
            'special': special_sum,
            'other': other_sum,
            'grand_total': totals['total_grand'] or 0,
        },
        'title': f'Service Report – {entity.name}',
    }
    return render(request, 'ChurchApp/service_list_report.html', context)


@staff_member_required
def service_list_report_pdf(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')

    if not start_date:
        start_date = (timezone.now().date() - timedelta(days=30)).isoformat()
    if not end_date:
        end_date = timezone.now().date().isoformat()

    try:
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        start = timezone.now().date() - timedelta(days=30)
        end = timezone.now().date()

    services = Service.objects.filter(
        entity=entity,
        date__gte=start,
        date__lte=end
    ).order_by('date')

    # Compute totals (same as above)
    easter_sum = 0
    christmas_sum = 0
    harvest_sum = 0
    special_sum = 0
    other_sum = 0
    for s in services:
        easter_sum += sum(item.get('amount', 0) for item in s.easter_offering if isinstance(item, dict))
        christmas_sum += sum(item.get('amount', 0) for item in s.christmas_offering if isinstance(item, dict))
        harvest_sum += sum(item.get('amount', 0) for item in s.harvest_offering if isinstance(item, dict))
        special_sum += sum(item.get('amount', 0) for item in s.special_thank_offering if isinstance(item, dict))
        other_sum += sum(item.get('amount', 0) for item in s.other_collections if isinstance(item, dict))

    totals = {
        'attendance': services.aggregate(Sum('attendance'))['attendance__sum'] or 0,
        'communicants': services.aggregate(Sum('communicants'))['communicants__sum'] or 0,
        'dues': services.aggregate(Sum('dues'))['dues__sum'] or 0,
        'tithes': services.aggregate(Sum('tithes'))['tithes__sum'] or 0,
        'general_offertory': services.aggregate(Sum('general_offertory'))['general_offertory__sum'] or 0,
        'day_born': services.aggregate(Sum('day_born_total'))['day_born_total__sum'] or 0,
        'guild': services.aggregate(Sum('guild_total'))['guild_total__sum'] or 0,
        'easter': easter_sum,
        'christmas': christmas_sum,
        'harvest': harvest_sum,
        'special': special_sum,
        'other': other_sum,
        'grand_total': services.aggregate(Sum('grand_total'))['grand_total__sum'] or 0,
    }

    context = {
        'entity': entity,
        'services': services,
        'start_date': start,
        'end_date': end,
        'totals': totals,
        'title': f'Service Report – {entity.name}',
        'now': timezone.now(),
    }

    template = get_template('ChurchApp/service_list_report_pdf.html')
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="service_report_{start}_{end}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('PDF generation error', status=500)
    return response


@staff_member_required
def service_list_report_excel(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')

    if not start_date:
        start_date = (timezone.now().date() - timedelta(days=30)).isoformat()
    if not end_date:
        end_date = timezone.now().date().isoformat()

    try:
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        start = timezone.now().date() - timedelta(days=30)
        end = timezone.now().date()

    services = Service.objects.filter(
        entity=entity,
        date__gte=start,
        date__lte=end
    ).order_by('date')

    # Prepare data for Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Service Report"

    # Headers
    headers = [
        'Date', 'Service Name', 'Clergy', 'Officiant', 'Attendance', 'Communicants',
        'Dues', 'Tithes', 'General Offertory', 'Day-Born Total', 'Guild Total',
        'Easter Total', 'Christmas Total', 'Harvest Total', 'Special Thank Total',
        'Other Collections Total', 'Grand Total'
    ]
    ws.append(headers)

    # Bold header
    for cell in ws[1]:
        cell.font = Font(bold=True)

    # Data rows
    for service in services:
        # Compute JSON totals (already in model fields, but we can also compute)
        easter = sum(item.get('amount', 0) for item in service.easter_offering if isinstance(item, dict))
        christmas = sum(item.get('amount', 0) for item in service.christmas_offering if isinstance(item, dict))
        harvest = sum(item.get('amount', 0) for item in service.harvest_offering if isinstance(item, dict))
        special = sum(item.get('amount', 0) for item in service.special_thank_offering if isinstance(item, dict))
        other = sum(item.get('amount', 0) for item in service.other_collections if isinstance(item, dict))

        clergy_names = ', '.join([c.full_name for c in service.clergy.all()]) or ''
        officiant_name = service.officiant.full_name if service.officiant else ''
        row = [
            service.date.isoformat(),
            service.name_of_service,
            clergy_names,
            officiant_name,
            service.attendance,
            service.communicants,
            float(service.dues),
            float(service.tithes),
            float(service.general_offertory),
            float(service.day_born_total),
            float(service.guild_total),
            float(easter),
            float(christmas),
            float(harvest),
            float(special),
            float(other),
            float(service.grand_total),
        ]
        ws.append(row)

    # Totals row
    total_row = ['TOTALS', '', '', '', '', '']
    # We'll calculate totals in Python
    totals = {
        'attendance': services.aggregate(Sum('attendance'))['attendance__sum'] or 0,
        'communicants': services.aggregate(Sum('communicants'))['communicants__sum'] or 0,
        'dues': services.aggregate(Sum('dues'))['dues__sum'] or 0,
        'tithes': services.aggregate(Sum('tithes'))['tithes__sum'] or 0,
        'general_offertory': services.aggregate(Sum('general_offertory'))['general_offertory__sum'] or 0,
        'day_born': services.aggregate(Sum('day_born_total'))['day_born_total__sum'] or 0,
        'guild': services.aggregate(Sum('guild_total'))['guild_total__sum'] or 0,
    }
    # Compute JSON totals for all services
    easter_sum = sum(sum(item.get('amount', 0) for item in s.easter_offering if isinstance(item, dict)) for s in services)
    christmas_sum = sum(sum(item.get('amount', 0) for item in s.christmas_offering if isinstance(item, dict)) for s in services)
    harvest_sum = sum(sum(item.get('amount', 0) for item in s.harvest_offering if isinstance(item, dict)) for s in services)
    special_sum = sum(sum(item.get('amount', 0) for item in s.special_thank_offering if isinstance(item, dict)) for s in services)
    other_sum = sum(sum(item.get('amount', 0) for item in s.other_collections if isinstance(item, dict)) for s in services)
    grand_total = services.aggregate(Sum('grand_total'))['grand_total__sum'] or 0

    totals_row = [
        'TOTAL',
        '', '', '', '',
        totals['attendance'],
        totals['communicants'],
        totals['dues'],
        totals['tithes'],
        totals['general_offertory'],
        totals['day_born'],
        totals['guild'],
        easter_sum,
        christmas_sum,
        harvest_sum,
        special_sum,
        other_sum,
        grand_total,
    ]
    ws.append(totals_row)
    # Bold the totals row
    for cell in ws[ws.max_row]:
        cell.font = Font(bold=True)

    # Adjust column widths
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except:
                pass
        adjusted_width = min(max_length + 2, 30)
        ws.column_dimensions[column].width = adjusted_width

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="service_report_{start}_{end}.xlsx"'
    wb.save(response)
    return response


# MembersApp/views.py (or wherever your back_to_home is defined)

from djan_led.utils import get_module_home_url
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django_ledger.models import EntityModel


from django.db.models import Q


@login_required
@staff_member_required
def member_images_view(request, slug, pk):
    """Read-only display of a member's passport picture."""
    entity = get_object_or_404(EntityModel, slug=slug)
    member = get_object_or_404(Member, pk=pk, entity=entity, is_deleted=False)

    return render(
        request,
        "ChurchApp/member_images_view.html",
        {
            "entity": entity,
            "member": member,
        },
    )


@login_required
@staff_member_required
def member_images(request, slug, pk=None):
    """
    Manage a church member's passport picture.
    Supports search-first when no pk is given.
    """
    entity = get_object_or_404(EntityModel, slug=slug)
    member = None

    if pk:
        member = get_object_or_404(Member, pk=pk, entity=entity, is_deleted=False)

    # Search
    search_query = request.GET.get("search", "")
    search_results = []
    if search_query:
        search_results = Member.objects.filter(
            entity=entity,
            is_deleted=False,
        ).filter(
            Q(full_name__icontains=search_query)
            | Q(id__icontains=search_query)
            | Q(telephone1__icontains=search_query)
        )[:20]

    # Upload / delete on POST
    if request.method == "POST" and member:
        if "passport_picture" in request.FILES:
            # Replace old file cleanly
            if member.passport_picture:
                member.passport_picture.delete(save=False)
            member.passport_picture = request.FILES["passport_picture"]
            member.save()
            messages.success(request, "Passport picture uploaded.")

        if request.POST.get("action") == "delete":
            if member.passport_picture:
                member.passport_picture.delete(save=False)
                member.passport_picture = None
                member.save()
                messages.success(request, "Passport picture deleted.")
            else:
                messages.warning(request, "No picture to delete.")

        return redirect("ChurchApp:member_images", slug=entity.slug, pk=member.pk)

    context = {
        "entity": entity,
        "member": member,
        "search_query": search_query,
        "search_results": search_results,
    }
    return render(request, "ChurchApp/member_images.html", context)


@login_required
def back_to_home(request, slug=None):
    """
    Universal exit that returns the user to their entity's correct dashboard.
    """
    if slug:
        entity = get_object_or_404(EntityModel, slug=slug)
    else:
        # Fall back to the user's default entity
        entity = (
            EntityModel.objects.filter(admin=request.user).first()
            or EntityModel.objects.first()
        )

    return redirect(get_module_home_url(entity))

from datetime import datetime
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django_ledger.models import EntityModel

from .models import MemberContribution
from services.contributions import (filtered_contributions, summary_by_category, grand_total)


@login_required
def contribution_list(request, slug):
    """
    List of MemberContribution rows with filters.
    Supports ?member=<id>&start=&end=&ledger=&q=  + ?format=pdf|excel
    """
    entity = get_object_or_404(EntityModel, slug=slug)

    # ---- filters ----
    member_id = request.GET.get("member")
    start_str = request.GET.get("start")
    end_str = request.GET.get("end")
    ledger = request.GET.get("ledger")
    q = (request.GET.get("q") or "").strip()

    member = None
    if member_id:
        from .models import Member

        member = Member.objects.filter(pk=member_id, entity=entity).first()

    def _parse(s):
        try:
            return datetime.strptime(s, "%Y-%m-%d").date() if s else None
        except ValueError:
            return None

    start = _parse(start_str)
    end = _parse(end_str)

    # ---- query ----
    qs = filtered_contributions(
        entity, member=member, start=start, end=end, ledger_code=ledger, q=q
    )

    rows = list(qs)
    by_category = summary_by_category(qs)
    total = grand_total(qs)

    # ---- members for the dropdown ----
    from .models import Member

    members = Member.objects.filter(entity=entity, is_deleted=False).order_by(
        "full_name"
    )

    return render(
        request,
        "ChurchApp/contribution_list.html",
        {
            "entity": entity,
            "rows": rows,
            "by_category": by_category,
            "total": total,
            "members": members,
            "member": member,
            "start": start,
            "end": end,
            "ledger": ledger,
            "q": q,
            "total_count": len(rows),
        },
    )

from django.http import HttpResponse
from datetime import datetime


@login_required
def contribution_pdf(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)

    member_id = request.GET.get("member")
    start_str = request.GET.get("start")
    end_str   = request.GET.get("end")
    ledger    = request.GET.get("ledger")
    q         = (request.GET.get("q") or "").strip()

    member = None
    if member_id:
        from .models import Member
        member = Member.objects.filter(pk=member_id, entity=entity).first()

    def _parse(s):
        try:
            return datetime.strptime(s, "%Y-%m-%d").date() if s else None
        except ValueError:
            return None

    from .reports import build_contribution_pdf
    pdf = build_contribution_pdf(
        entity=entity,
        member=member,
        start=_parse(start_str),
        end=_parse(end_str),
        ledger=ledger,
        q=q,
        generated_by=getattr(request.user, "username", ""),
    )

    filename = f"Giving_Report_{entity.slug}.pdf"
    resp = HttpResponse(pdf, content_type="application/pdf")
    resp["Content-Disposition"] = f'inline; filename="{filename}"'
    return resp

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


@login_required
def contribution_excel(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)

    # parse filters (same as list view)
    member_id = request.GET.get("member")
    start_str = request.GET.get("start")
    end_str = request.GET.get("end")
    ledger = request.GET.get("ledger")
    q = (request.GET.get("q") or "").strip()

    member = None
    if member_id:
        from .models import Member

        member = Member.objects.filter(pk=member_id, entity=entity).first()

    def _parse(s):
        try:
            return datetime.strptime(s, "%Y-%m-%d").date() if s else None
        except ValueError:
            return None

    qs = filtered_contributions(
        entity,
        member=member,
        start=_parse(start_str),
        end=_parse(end_str),
        ledger_code=ledger,
        q=q,
    )
    rows = list(qs)
    by_category = summary_by_category(qs)
    total = grand_total(qs)

    wb = Workbook()

    # ---- sheet 1: detail ----
    ws = wb.active
    ws.title = "Giving Detail"

    # header
    ws.append(
        [
            "Date",
            "Member",
            "Ledger Code",
            "Ledger Name",
            "Receipt No",
            "Details",
            "Amount (₵)",
        ]
    )
    for col in range(1, 8):
        c = ws.cell(row=1, column=col)
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="1A56DB")
        c.alignment = Alignment(horizontal="center", vertical="center")

    # rows
    for r in rows:
        ws.append(
            [
                r.date,
                r.member.full_name,
                r.ledger_code,
                r.ledger_name,
                r.receipt_no,
                r.details,
                float(r.amount),
            ]
        )

    # total row
    last = ws.max_row + 1
    ws.cell(row=last, column=6, value="TOTAL").font = Font(bold=True)
    ws.cell(row=last, column=7, value=float(total)).font = Font(bold=True)

    # column widths
    widths = [12, 28, 14, 22, 15, 30, 15]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w

    # number format on amount column
    for row in ws.iter_rows(min_row=2, min_col=7, max_col=7):
        for c in row:
            c.number_format = "#,##0.00"

    ws.freeze_panes = "A2"

    # ---- sheet 2: summary ----
    ws2 = wb.create_sheet("Summary by Category")
    ws2.append(["Ledger Code", "Ledger Name", "Count", "Total (₵)"])
    for col in range(1, 5):
        c = ws2.cell(row=1, column=col)
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="1A56DB")
        c.alignment = Alignment(horizontal="center")

    for cat in by_category:
        ws2.append(
            [
                cat["ledger_code"] or "",
                cat["ledger_name"] or "",
                cat["count"],
                float(cat["total"]),
            ]
        )

    last = ws2.max_row + 1
    ws2.cell(row=last, column=3, value="TOTAL").font = Font(bold=True)
    ws2.cell(row=last, column=4, value=float(total)).font = Font(bold=True)

    for i, w in enumerate([14, 30, 10, 15], start=1):
        ws2.column_dimensions[get_column_letter(i)].width = w
    for row in ws2.iter_rows(min_row=2, min_col=4, max_col=4):
        for c in row:
            c.number_format = "#,##0.00"

    # ---- response ----
    from io import BytesIO

    buf = BytesIO()
    wb.save(buf)

    filename = f"Giving_Report_{entity.slug}.xlsx"
    resp = HttpResponse(
        buf.getvalue(),
        content_type=(
            "application/vnd.openxmlformats-officedocument" ".spreadsheetml.sheet"
        ),
    )
    resp["Content-Disposition"] = f'attachment; filename="{filename}"'
    return resp



# ----------------------------------------------------------------------
# Shared filter helper — used by HTML, PDF, Excel so numbers always match
# ----------------------------------------------------------------------
def _filter_contributions(request, entity):
    """Return (qs, filters_dict, totals_dict)."""
    member_id = request.GET.get("member") or ""
    start_str = request.GET.get("start") or ""
    end_str = request.GET.get("end") or ""
    category = request.GET.get("category") or ""

    start = parse_date(start_str)
    end = parse_date(end_str)

    qs = (
        MemberContribution.objects.filter(entity=entity)
        .select_related("member", "trans")
        .order_by("-date", "member__full_name")
    )

    if member_id and member_id.isdigit():
        qs = qs.filter(member_id=int(member_id))
    if start:
        qs = qs.filter(date__gte=start)
    if end:
        qs = qs.filter(date__lte=end)

    # Category filter — matches ledger_name
    if category:
        qs = qs.filter(ledger_name__iexact=category)

    total = qs.aggregate(s=Sum("amount"))["s"] or 0

    return (
        qs,
        {
            "member_id": member_id,
            "start": start_str,
            "end": end_str,
            "category": category,
            "period_label": for_period_label(start, end),
        },
        {"total": total, "count": qs.count()},
    )


def _category_choices(entity):
    """Distinct ledger_names used on this entity's contributions."""
    names = (
        MemberContribution.objects.filter(entity=entity)
        .values_list("ledger_name", flat=True)
        .distinct()
        .order_by("ledger_name")
    )
    return [n for n in names if n]


# ----------------------------------------------------------------------
# HTML list
# ----------------------------------------------------------------------
@login_required
def member_contributions_list(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)

    qs, filters, totals = _filter_contributions(request, entity)
    members = Member.objects.filter(entity=entity, is_deleted=False).order_by(
        "full_name"
    )
    categories = _category_choices(entity)

    # Group by member for a summary table
    per_member = (
        qs.values("member_id", "member__full_name")
        .annotate(total=Sum("amount"))
        .order_by("member__full_name")
    )

    return render(
        request,
        "ChurchApp/member_contributions_list.html",
        {
            "entity": entity,
            "rows": list(qs),
            "per_member": list(per_member),
            "members": members,
            "categories": categories,
            "filters": filters,
            "totals": totals,
            "now": timezone.now(),
        },
    )


# ----------------------------------------------------------------------
# PDF export
# ----------------------------------------------------------------------
@login_required
def member_contributions_pdf(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    qs, filters, totals = _filter_contributions(request, entity)

    cfg = getattr(entity, "config", None)

    # Header info
    member_label = "All members"
    if filters["member_id"] and filters["member_id"].isdigit():
        m = Member.objects.filter(pk=int(filters["member_id"]), entity=entity).first()
        if m:
            member_label = m.full_name

    category_label = filters["category"] or "All categories"

    columns = [
        Col("Date", 12, "left"),
        Col("Member", 30, "left"),
        Col("Category", 20, "left"),
        Col("Receipt", 15, "left"),
        Col("Details", 30, "left"),
        Col("Amount", 18, "right", currency=True),
    ]

    table_rows = [
        [
            r.date.strftime("%d/%m/%Y"),
            r.member.full_name,
            r.ledger_name or r.ledger_code or "",
            r.receipt_no or "",
            (r.details or "")[:40],
            r.amount,
        ]
        for r in qs
    ]

    totals_row = ["", "", "", "", "TOTAL", totals["total"]]

    pdf_bytes = build_report_pdf(
        entity=entity,
        entity_config=cfg,
        report_title="Member Contributions",
        period_label=f"{filters['period_label']}   {member_label}   {category_label}",
        columns=columns,
        rows=table_rows,
        totals=totals_row,
        filename=f"contributions_{entity.slug}.pdf",
        landscape_mode=True,
    )

    resp = HttpResponse(pdf_bytes, content_type="application/pdf")
    mode = "attachment" if request.GET.get("download") == "1" else "inline"
    resp["Content-Disposition"] = (
        f'{mode}; filename="contributions_{entity.slug}_{timezone.now():%Y%m%d}.pdf"'
    )
    return resp


# ----------------------------------------------------------------------
# Excel export
# ----------------------------------------------------------------------
@login_required
def member_contributions_excel(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    qs, filters, totals = _filter_contributions(request, entity)

    headers = [
        "Date",
        "Member",
        "Member ID",
        "Category",
        "Ledger Code",
        "Receipt No",
        "Details",
        "Amount",
        "Trans Voucher",
    ]

    data = [
        [
            r.date.strftime("%d/%m/%Y"),
            r.member.full_name,
            r.member.pk,
            r.ledger_name or "",
            r.ledger_code or "",
            r.receipt_no or "",
            r.details or "",
            float(r.amount),
            r.trans.rec_vou_no if r.trans else "",
        ]
        for r in qs
    ]
    data.append(["", "", "", "", "", "", "TOTAL", float(totals["total"]), ""])

    cfg = getattr(entity, "config", None)

    return render_excel(
        headers,
        data,
        filename=f"contributions_{entity.slug}_{timezone.now():%Y%m%d}.xlsx",
        sheet_name="Contributions",
        title=(cfg.organization_name if cfg else entity.name),
        subtitle=f"Member Contributions — {filters['period_label']}",
    )
