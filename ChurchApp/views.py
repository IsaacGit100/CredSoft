from django.shortcuts import render

# Create your views here.


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django_ledger.models import (EntityModel, LedgerModel, JournalEntryModel, AccountModel, TransactionModel)
from decimal import Decimal
from django.utils import timezone
from .models import Service, Member, Event
from .forms import ServiceForm
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count
from django_ledger.models import EntityModel
from LoanApp.models import Loan

# from .models import Member, Offering, Event, FinancialRecord
@login_required
def church_home(request, slug):
    pass

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
#        "total_income": finances.filter(transaction_type="Income").aggregate(
#            total=Sum("amount")
#        )["total"]
#        or 0,
#        "total_expenses": finances.filter(transaction_type="Expense").aggregate(
#            total=Sum("amount")
#        )["total"]
#        or 0,
    }
    return render(request, "ChurchApp/church_dashboard.html", context)


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django_ledger.models import EntityModel
from .models import Member
from .forms import MemberForm


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


def member_edit(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    member = get_object_or_404(Member, pk=pk, entity=entity)
    if request.method == "POST":
        form = MemberForm(request.POST, instance=member, entity=entity)
        if form.is_valid():
            form.save()
            messages.success(request, "Member updated.")
            return redirect("ChurchApp:member_list", slug=entity.slug)
    else:
        form = MemberForm(instance=member, entity=entity)
    return render(request, 'ChurchApp/member_edit.html', {'form': form, 'entity': entity})


# ChurchApp/views.py

from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django_ledger.models import EntityModel
from .models import Member

@login_required
@staff_member_required
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
def member_delete(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    member = get_object_or_404(Member, pk=pk, entity=entity)

    if request.method == "POST":
        member.is_deleted = True
        member.save()
        messages.success(request, f"Member {member.full_name} soft deleted.")
        return redirect("ChurchApp:member_list", slug=slug)

    return render(
        request,
        "ChurchApp/member_confirm_delete.html",
        {"entity": entity, "member": member},
    )


@login_required
def member_restore(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    member = get_object_or_404(Member, pk=pk, entity=entity, is_deleted=True)

    if request.method == "POST":
        member.is_deleted = False
        member.save()
        messages.success(request, f"Member {member.full_name} restored.")
        return redirect("ChurchApp:member_list", slug=slug)

    return render(
        request,
        "ChurchApp/member_confirm_restore.html",
        {"entity": entity, "member": member},
    )


@login_required
def service_create(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    if request.method == "POST":
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.entity = entity
            service.created_by = request.user
            service.save()
            messages.success(request, "Service recorded.")
            return redirect("ChurchApp:service_list", slug=slug)
    else:
        form = ServiceForm()
    context = {
        "form": form,
        "entity": entity,
        "clergy_list": Clergy.objects.filter(entity=entity),
        "usher_list": Usher.objects.filter(entity=entity),
        "guild_list": Guild.objects.filter(entity=entity),
        "officiant_list": Officiant.objects.filter(entity=entity),
    }
    return render(request, "ChurchApp/service_form.html", context)


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
    return render(request, "ChurchApp/service_list.html", context)


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


# ChurchApp/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django_ledger.models import EntityModel
from .models import Clergy
from .forms import ClergyForm

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


@staff_member_required
def clergy_create(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    if request.method == "POST":
        form = ClergyForm(request.POST, entity=entity)
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


## ===============================Sunday Service ==============================
# ChurchApp/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django_ledger.models import EntityModel
from .models import Service
from .forms import ServiceForm
from services.journal_engine import JournalEngine  # adjust import path


# ChurchApp/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django_ledger.models import EntityModel
from RecPayApp.models import Trans  # Import Trans model
from .models import Service
from .forms import ServiceForm
import json

# ChurchApp/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django_ledger.models import EntityModel
from RecPayApp.models import Trans  # Import Trans model
from .models import Service
from .forms import ServiceForm
import json


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


# List, detail, delete views (keep as before)
@staff_member_required
def service_list_manage(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    services = Service.objects.filter(entity=entity).order_by("-date")
    context = {
        "entity": entity,
        "services": services,
        "total_services": services.count(),
    }
    return render(request, "ChurchApp/service_list.html", context)


@staff_member_required
def service_detail(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    service = get_object_or_404(Service, pk=pk, entity=entity)
    context = {
        "entity": entity,
        "service": service,
    }
    return render(request, "ChurchApp/service_detail.html", context)


@staff_member_required
def service_delete(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    service = get_object_or_404(Service, pk=pk, entity=entity)
    if request.method == "POST":
        service.delete()
        messages.success(request, f"Service '{service.name_of_service}' deleted.")
        return redirect("ChurchApp:service_list", slug=entity.slug)
    context = {
        "entity": entity,
        "service": service,
    }
    return render(request, "ChurchApp/service_confirm_delete.html", context)


# ChurchApp/views.py

from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django_ledger.models import EntityModel
from .models import Clergy, Member
from .forms import ClergyForm


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


# ChurchApp/views.py


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

# ChurchApp/views.py


@staff_member_required
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


# ChurchApp/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django_ledger.models import EntityModel
from .models import Member, Role, MemberRole
from .forms import RoleAssignmentForm


@staff_member_required
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
    }
    return render(request, "ChurchApp/role_management.html", context)


@staff_member_required
def member_roles_edit(request, slug, pk):
    """
    Edit roles for a specific member.
    """
    entity = get_object_or_404(EntityModel, slug=slug)
    member = get_object_or_404(Member, pk=pk, entity=entity)

    if request.method == "POST":
        form = RoleAssignmentForm(request.POST, entity=entity, member=member)
        if form.is_valid():
            form.save(member)
            messages.success(request, f"Roles updated for {member.full_name}")
            return redirect("ChurchApp:role_management", slug=entity.slug)
    else:
        form = RoleAssignmentForm(entity=entity, member=member)

    context = {
        "entity": entity,
        "member": member,
        "form": form,
        "title": f"Manage Roles: {member.full_name}",
    }
    return render(request, "ChurchApp/member_roles_edit.html", context)


@staff_member_required
def role_create(request, slug):
    """
    Create a new role.
    """
    entity = get_object_or_404(EntityModel, slug=slug)

    if request.method == "POST":
        name = request.POST.get("name")
        display_name = request.POST.get("display_name")
        description = request.POST.get("description", "")

        if name and display_name:
            role, created = Role.objects.get_or_create(
                entity=entity,
                name=name,
                defaults={
                    "display_name": display_name,
                    "description": description,
                    "is_active": True,
                },
            )
            if created:
                messages.success(request, f"Role '{display_name}' created.")
            else:
                messages.warning(request, f"Role '{display_name}' already exists.")
        else:
            messages.error(request, "Please provide both name and display name.")

        return redirect("ChurchApp:role_management", slug=entity.slug)

    context = {
        "entity": entity,
        "title": "Create Role",
    }
    return render(request, "ChurchApp/role_create.html", context)


# ChurchApp/views.py

from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django_ledger.models import EntityModel
from .models import Member


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


# ChurchApp/views.py
### ============================== Dues and Tithes ==============================

@staff_member_required
def dues_tithe_create(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    members = Member.objects.filter(entity=entity, is_deleted=False).order_by("full_name")

    if request.method == "POST":
        form = DuesTitheForm(request.POST, entity=entity)
        if form.is_valid():
            dues_tithe = form.save(commit=False)
            dues_tithe.entity = entity
            dues_tithe.created_by = request.user
            dues_tithe.save()

            # Create Trans record
            ledger_code = "4011" if dues_tithe.payment_type == "dues" else "4012"
            trans = create_trans(
                entity=entity,
                trans_type="Receipts",
                amount=dues_tithe.amount,
                date=dues_tithe.date_paid,
                pay_mode="Cash",
                ledger_code=ledger_code,
                ledger_name=dues_tithe.get_payment_type_display(),
                details=f"{dues_tithe.get_payment_type_display()} - {dues_tithe.month.strftime('%B %Y')}",
                source=dues_tithe,
                member=dues_tithe.member,
                created_by=request.user,
                purpose=f"{dues_tithe.get_payment_type_display()} Payment",
                module="church",
            )

            dues_tithe.trans = trans
            dues_tithe.save()

            messages.success(
                request,
                f"{dues_tithe.get_payment_type_display()} saved for {dues_tithe.member.full_name}",
            )
            return redirect("ChurchApp:dues_tithe_list", slug=entity.slug)
    else:
        form = DuesTitheForm(entity=entity, initial={"month": timezone.now().date()})

    context = {
        "entity": entity,
        "form": form,
        "title": "Add Dues/Tithe Payment",
    }
    return render(request, "ChurchApp/dues_tithe_form.html", context)


# ChurchApp/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db import models
from django.utils import timezone
from django_ledger.models import EntityModel
from RecPayApp.models import Trans
from MembersApp.models import Master
from .forms import DuesTitheTransactionForm
# from services.trans_helper import create_trans


@login_required
@staff_member_required
def dues_tithe_list(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)

    # Debug: Check total transactions
    print("Total Trans records:", Trans.objects.count())
    print("Church module records:", Trans.objects.filter(module="church").count())
    print(
        "Dues/Tithe records:",
        Trans.objects.filter(ledger_code__in=["4011", "4012"]).count(),
    )

    # Get all church transactions for dues and tithes
    transactions = (
        Trans.objects.filter(entity=entity, module="church", trans_type="Receipts")
        .filter(
            models.Q(ledger_code__in=["4011", "4012"])
            | models.Q(purpose__in=["Dues", "Tithe"])
        )
        .order_by("-date", "-created_at")
    )

    print("Found transactions:", transactions.count())
    for t in transactions:
        print(
            f"  {t.rec_vou_no}: purpose={t.purpose}, ledger_code={t.ledger_code}, amount={t.amount}"
        )

    # ... rest of view
# ChurchApp/views.py

@login_required
@staff_member_required
def dues_tithe_list_manage6(request, slug):
    """
    Display all dues/tithe transactions.
    """
    entity = get_object_or_404(EntityModel, slug=slug)

    # Debug: Check what's actually in the database
    print("=== DEBUG: All Trans records ===")
    for t in Trans.objects.all()[:20]:
        print(f"ID: {t.id}, rec_vou_no: {t.rec_vou_no}, module: {t.module}, purpose: {t.purpose}, ledger_code: {t.ledger_code}, entity: {t.entity}")

    # Get all transactions that are dues or tithes (more flexible query)
    transactions = Trans.objects.filter(
        entity=entity,
        trans_type='Receipts'
    ).filter(
        models.Q(ledger_code__in=['4011', '4012']) | 
        models.Q(purpose__in=['Dues', 'Tithe']) |
        models.Q(ledger_name__in=['Dues', 'Tithe'])
    ).order_by('-date', '-created_at')

    print(f"Found transactions: {transactions.count()}")
    for t in transactions:
        print(f"  {t.rec_vou_no}: module={t.module}, purpose={t.purpose}, ledger_code={t.ledger_code}, ledger_name={t.ledger_name}")

    # Apply filters
    payment_type = request.GET.get('type')
    if payment_type == 'dues':
        transactions = transactions.filter(ledger_code='4011')
    elif payment_type == 'tithe':
        transactions = transactions.filter(ledger_code='4012')

    # Search by member name
    search = request.GET.get('search')
    if search:
        transactions = transactions.filter(
            models.Q(church_member__full_name__icontains=search) |
            models.Q(member__full_name__icontains=search) |
            models.Q(non_member_name__icontains=search) |
            models.Q(rec_vou_no__icontains=search)
        )

    # Calculate totals
    total_dues = Trans.objects.filter(
        entity=entity,
        ledger_code='4011'
    ).aggregate(total=models.Sum('amount'))['total'] or 0

    total_tithes = Trans.objects.filter(
        entity=entity,
        ledger_code='4012'
    ).aggregate(total=models.Sum('amount'))['total'] or 0

    total_amount = total_dues + total_tithes

    context = {
        'entity': entity,
        'transactions': transactions,
        'total_dues': total_dues,
        'total_tithes': total_tithes,
        'total_amount': total_amount,
        'payment_type': payment_type,
        'search': search,
    }
    return render(request, 'ChurchApp/dues_tithe_list.html', context)


# ChurchApp/views.py


@login_required
@staff_member_required
def dues_tithe_list_manage(request, slug):
    """
    Display all dues/tithe transactions.
    """
    entity = get_object_or_404(EntityModel, slug=slug)

    # DEBUG: Check what's in the database
    print("=== DEBUG: All church transactions ===")
    all_church = Trans.objects.filter(module="church")
    print(f"Total church transactions: {all_church.count()}")
    for t in all_church:
        print(
            f"  {t.rec_vou_no}: module={t.module}, purpose={t.purpose}, ledger_code={t.ledger_code}, entity={t.entity}, entity_id={t.entity_id}"
        )

    # Get all transactions for this entity that are dues or tithes
    # Use a simpler query first
    transactions = (
        Trans.objects.filter(module="church", trans_type="Receipts")
        .filter(
            models.Q(ledger_code__in=["4011", "4012"])
            | models.Q(purpose__in=["Dues", "Tithe"])
        )
        .order_by("-date", "-created_at")
    )

    print(f"Found transactions (without entity filter): {transactions.count()}")

    # If entity filter is needed, apply it separately
    # transactions = transactions.filter(entity=entity)

    # Apply filters
    payment_type = request.GET.get("type")
    if payment_type == "dues":
        transactions = transactions.filter(ledger_code="4011")
    elif payment_type == "tithe":
        transactions = transactions.filter(ledger_code="4012")

    # Search by member name
    search = request.GET.get("search")
    if search:
        transactions = transactions.filter(
            models.Q(church_member__full_name__icontains=search)
            | models.Q(member__full_name__icontains=search)
            | models.Q(non_member_name__icontains=search)
            | models.Q(rec_vou_no__icontains=search)
        )

    # Calculate totals
    total_dues = (
        Trans.objects.filter(module="church", ledger_code="4011").aggregate(
            total=models.Sum("amount")
        )["total"]
        or 0
    )

    total_tithes = (
        Trans.objects.filter(module="church", ledger_code="4012").aggregate(
            total=models.Sum("amount")
        )["total"]
        or 0
    )

    total_amount = total_dues + total_tithes

    context = {
        "entity": entity,
        "transactions": transactions,
        "total_dues": total_dues,
        "total_tithes": total_tithes,
        "total_amount": total_amount,
        "payment_type": payment_type,
        "search": search,
    }
    return render(request, "ChurchApp/dues_tithe_list.html", context)


@login_required
@staff_member_required
def dues_tithe_list_manage10(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
     # Debug: Check total transactions
    print("Total Trans records:", Trans.objects.count())
    print("Church module records:", Trans.objects.filter(module="church").count())
    print("Dues/Tithe records:", Trans.objects.filter(ledger_code__in=["4011", "4012"]).count())
    
     # Get all church transactions for dues and tithes
    transactions = Trans.objects.filter(
        entity=entity,
        module='church',
        trans_type='Receipts'
    ).filter(
        models.Q(ledger_code__in=['4011', '4012']) | 
        models.Q(purpose__in=['Dues', 'Tithe'])
    ).order_by('-date', '-created_at')
    
    print("Found transactions:", transactions.count())
    for t in transactions:
        print(f"  {t.rec_vou_no}: purpose={t.purpose}, ledger_code={t.ledger_code}, amount={t.amount}")

    # Update the display to show church_member
    for trans in transactions:
        if trans.church_member:
            trans.display_member = trans.church_member.full_name
        else:
            trans.display_member = trans.non_member_name or "—"

    context = {
        "entity": entity,
        "transactions": transactions,
        "total_dues": transactions.filter(ledger_code="4011").aggregate(
            total=models.Sum("amount")
        )["total"]
        or 0,
        "total_tithes": transactions.filter(ledger_code="4012").aggregate(
            total=models.Sum("amount")
        )["total"]
        or 0,
    }
    return render(request, "ChurchApp/dues_tithe_list.html", context)


@staff_member_required
def dues_tithe_list_manage2(request, slug):
    """
    Display all dues/tithe transactions with CRUD actions.
    """
    entity = get_object_or_404(EntityModel, slug=slug)

    # Get all dues/tithe transactions
    transactions = (
        Trans.objects.filter(entity=entity, module="church", trans_type="Receipts")
        .filter(
            models.Q(ledger_code__in=["4011", "4012"])
            | models.Q(purpose__in=["Dues", "Tithe"])
        )
        .order_by("-date", "-created_at")
    )

    # Filter by payment type if specified
    payment_type = request.GET.get("type")
    if payment_type == "dues":
        transactions = transactions.filter(ledger_code="4011")
    elif payment_type == "tithe":
        transactions = transactions.filter(ledger_code="4012")

    # Search by member name
    search = request.GET.get("search")
    if search:
        transactions = transactions.filter(
            models.Q(member__full_name__icontains=search)
            | models.Q(non_member_name__icontains=search)
            | models.Q(rec_vou_no__icontains=search)
        )

    # Summary
    total_dues = (
        Trans.objects.filter(
            entity=entity, module="church", ledger_code="4011"
        ).aggregate(total=models.Sum("amount"))["total"]
        or 0
    )

    total_tithes = (
        Trans.objects.filter(
            entity=entity, module="church", ledger_code="4012"
        ).aggregate(total=models.Sum("amount"))["total"]
        or 0
    )

    context = {
        "entity": entity,
        "transactions": transactions,
        "total_dues": total_dues,
        "total_tithes": total_tithes,
        "total_amount": total_dues + total_tithes,
        "payment_type": payment_type,
        "search": search,
        "title": "Dues & Tithes Management",
    }
    return render(request, "ChurchApp/dues_tithe_list.html", context)

@login_required
@staff_member_required
def dues_tithe_create2(request, slug):
    """
    Create a new dues/tithe transaction.
    """
    entity = get_object_or_404(EntityModel, slug=slug) 

    if request.method == "POST":
        form = DuesTitheTransactionForm(request.POST, entity=entity, user=request.user)
        if form.is_valid():
            trans = form.save()

            # Update member's totals if member selected
            if trans.member:
                member = trans.member
                if trans.purpose and trans.purpose.lower() == "tithe":
                    member.tot_tithe = (
                        getattr(member, "tot_tithe", 0) or 0
                    ) + trans.amount
                else:
                    member.tot_dues = (
                        getattr(member, "tot_dues", 0) or 0
                    ) + trans.amount
                member.save()

            messages.success(
                request,
                f"{trans.purpose} recorded. Transaction {trans.rec_vou_no} pending approval.",
            )
            return redirect("ChurchApp:dues_tithe_list", slug=entity.slug)
    else:
        # Determine default purpose from GET param
        purpose = request.GET.get("purpose", "Dues")
        form = DuesTitheTransactionForm(
            entity=entity,
            user=request.user,
            initial={
                "date": timezone.now().date(),
                "purpose": purpose,
                "pay_mode": "Cash",
                "ledger_code": "4011" if purpose == "Dues" else "4012",
                "ledger_name": purpose,
            },
        )

    context = {
        "entity": entity,
        "form": form,
        "title": f'Record {request.GET.get("purpose", "Dues")} Payment',
    }
    return render(request, "ChurchApp/dues_tithe_form.html", context)

# ChurchApp/views.py

# ChurchApp/views.py


@login_required
@staff_member_required
def dues_tithe_create(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)

    if request.method == "POST":
        form = DuesTitheTransactionForm(request.POST, entity=entity, user=request.user)

        # Debug: Print form data
        print("POST data:", request.POST)
        print("Form errors:", form.errors)

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


@staff_member_required
def dues_tithe_update(request, slug, pk):
    """
    Update an existing dues/tithe transaction.
    Only allowed if not yet posted to journals.
    """
    entity = get_object_or_404(EntityModel, slug=slug)
    trans = get_object_or_404(Trans, pk=pk, entity=entity)

    # Only allow editing if not posted
    if trans.journal_status == "POSTED":
        messages.error(
            request, "Cannot edit a transaction that has been posted to journals."
        )
        return redirect("ChurchApp:dues_tithe_list", slug=entity.slug)

    if request.method == "POST":
        # Store old amount for member adjustment
        old_amount = trans.amount
        old_purpose = trans.purpose
        old_member = trans.member

        form = DuesTitheTransactionForm(
            request.POST, instance=trans, entity=entity, user=request.user
        )
        if form.is_valid():
            updated_trans = form.save()

            # Adjust member's totals if member changed or amount changed
            if (
                old_member != updated_trans.member
                or old_amount != updated_trans.amount
                or old_purpose != updated_trans.purpose
            ):
                # Remove old amount from old member
                if old_member:
                    if old_purpose and old_purpose.lower() == "tithe":
                        old_member.tot_tithe = (
                            getattr(old_member, "tot_tithe", 0) or 0
                        ) - old_amount
                    else:
                        old_member.tot_dues = (
                            getattr(old_member, "tot_dues", 0) or 0
                        ) - old_amount
                    old_member.save()

                # Add new amount to new member
                if updated_trans.member:
                    member = updated_trans.member
                    if (
                        updated_trans.purpose
                        and updated_trans.purpose.lower() == "tithe"
                    ):
                        member.tot_tithe = (
                            getattr(member, "tot_tithe", 0) or 0
                        ) + updated_trans.amount
                    else:
                        member.tot_dues = (
                            getattr(member, "tot_dues", 0) or 0
                        ) + updated_trans.amount
                    member.save()

            messages.success(
                request, f"Transaction {updated_trans.rec_vou_no} updated successfully."
            )
            return redirect("ChurchApp:dues_tithe_list", slug=entity.slug)
    else:
        form = DuesTitheTransactionForm(
            instance=trans, entity=entity, user=request.user
        )

    context = {
        "entity": entity,
        "form": form,
        "trans": trans,
        "title": f"Edit {trans.purpose}: {trans.rec_vou_no}",
    }
    return render(request, "ChurchApp/dues_tithe_form.html", context)


@staff_member_required
def dues_tithe_delete(request, slug, pk):
    """
    Delete a dues/tithe transaction.
    Only allowed if not yet posted to journals.
    """
    entity = get_object_or_404(EntityModel, slug=slug)
    trans = get_object_or_404(Trans, pk=pk, entity=entity)

    if trans.journal_status == "POSTED":
        messages.error(
            request, "Cannot delete a transaction that has been posted to journals."
        )
        return redirect("ChurchApp:dues_tithe_list", slug=entity.slug)

    if request.method == "POST":
        # Remove from member's totals
        if trans.member:
            member = trans.member
            if trans.purpose and trans.purpose.lower() == "tithe":
                member.tot_tithe = (getattr(member, "tot_tithe", 0) or 0) - trans.amount
            else:
                member.tot_dues = (getattr(member, "tot_dues", 0) or 0) - trans.amount
            member.save()

        trans.delete()
        messages.success(
            request, f"Transaction {trans.rec_vou_no} deleted successfully."
        )
        return redirect("ChurchApp:dues_tithe_list", slug=entity.slug)

    context = {
        "entity": entity,
        "trans": trans,
        "title": f"Delete {trans.purpose}: {trans.rec_vou_no}",
    }
    return render(request, "ChurchApp/dues_tithe_confirm_delete.html", context)


@staff_member_required
def dues_tithe_detail(request, slug, pk):
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
    return render(request, "ChurchApp/dues_tithe_detail.html", context)


# RecPayApp/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.core.paginator import Paginator
from django.utils import timezone
from decimal import Decimal
from datetime import datetime
from django_ledger.models import EntityModel, AccountModel
from MembersApp.models import Master
from ChurchApp.models import Member  # Import Church Member


@login_required
def trans_create(request, slug):
    """
    Create receipts and payments transactions.
    Handles both Credit Union (Master) and Church (Member) members.
    """
    entity = get_object_or_404(EntityModel, slug=slug)

    # Get Chart of Accounts
    try:
        coa = entity.get_default_coa()
    except:
        messages.error(
            request,
            "This entity does not have a Chart of Accounts. Please create one first.",
        )
        return redirect("djan_led:chart_of_accounts", slug=entity.slug)

    if not coa:
        messages.error(request, "No Chart of Accounts found for this entity.")
        return redirect("djan_led:chart_of_accounts", slug=entity.slug)

    # Get accounts for dropdown
    accounts = AccountModel.objects.filter(
        coa_model=coa, active=True, depth__gt=1
    ).order_by("code")

    # ============================================
    # MEMBERS (Both Master and Member)
    # ============================================
    # Credit Union members (Master)
    master_members = Master.objects.filter(is_deleted=False).order_by(
        "last_name", "first_name"
    )

    # Church members (Member)
    church_members = Member.objects.filter(entity=entity, is_deleted=False).order_by(
        "full_name"
    )

    # Combine for display - we'll use a combined list
    members = list(master_members) + list(church_members)

    # Get selected member
    selected_member_id = request.GET.get("member_id") or request.POST.get("member_id")
    selected_member = None
    selected_member_type = None  # 'master' or 'member'
    active_loans = []

    if selected_member_id and selected_member_id.isdigit():
        # Try Master first
        try:
            selected_member = Master.objects.get(id=int(selected_member_id))
            selected_member_type = "master"
            # Get active loans for Master
            active_loans = Loan.objects.filter(
                master=selected_member, status__in=["Active", "New Loan"]
            ).order_by("-disbursement_date")
        except Master.DoesNotExist:
            # Try Church Member
            try:
                selected_member = Member.objects.get(id=int(selected_member_id))
                selected_member_type = "member"
                # Church members don't have loans in this context
                active_loans = []
            except Member.DoesNotExist:
                selected_member = None
                active_loans = []

    # ============================================
    # GET ALL TRANSACTIONS
    # ============================================
    transactions = Trans.objects.filter(entity=entity).order_by("-date", "-id")

    # Calculate statistics
    total_records = transactions.count()
    receipts = transactions.filter(trans_type="Receipts")
    payments = transactions.filter(trans_type="Payments")

    receipts_count = receipts.count()
    payments_count = payments.count()
    receipts_total = receipts.aggregate(Sum("amount"))["amount__sum"] or Decimal("0.00")
    payments_total = payments.aggregate(Sum("amount"))["amount__sum"] or Decimal("0.00")
    net_balance = receipts_total - payments_total

    # Pagination
    paginator = Paginator(transactions, 50)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # ============================================
    # PROCESS POST REQUEST
    # ============================================
    if request.method == "POST":
        if "close" in request.POST:
            return redirect("ChurchApp:church_dashboard", entity.slug)

        if "save" in request.POST:
            try:
                # Debug print all POST data
                print("\n=== POST DATA ===")
                for key, value in request.POST.items():
                    print(f"{key}: {value}")

                # ====================
                # 1. GET FORM DATA
                # ====================
                date_str = request.POST.get("date", "").strip()
                trans_no = request.POST.get("trans_no", "").strip()
                trans_type = request.POST.get("trans_type", "")
                amount_str = request.POST.get("amount", "0").strip()
                pay_mode = request.POST.get("pay_mode", "")
                name_type = request.POST.get("name_type", "")
                details = request.POST.get("details", "").strip()

                # Generate Receipt / Voucher No
                if trans_type == "Receipts":
                    rec_vou_no = f"REC:{trans_no}"
                else:
                    rec_vou_no = f"VOU:{trans_no}"

                # ====================
                # 2. PARSE AMOUNT
                # ====================
                amount_clean = amount_str.replace(",", "").replace(" ", "")
                try:
                    amount = Decimal(amount_clean)
                except:
                    messages.error(request, "Invalid amount format")
                    return redirect("ChurchApp:trans_create", entity.slug)

                # ====================
                # 3. PARSE DATE
                # ====================
                date = None
                for fmt in ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"]:
                    try:
                        date = datetime.strptime(date_str, fmt).date()
                        break
                    except ValueError:
                        continue

                if not date:
                    messages.error(request, "Invalid date format. Use DD/MM/YYYY")
                    return redirect("ChurchApp:trans_create", entity.slug)

                # ====================
                # 4. PARSE CHEQUE DATE
                # ====================
                cheque_date = None
                cheque_date_str = request.POST.get("cheque_date", "").strip()
                if cheque_date_str:
                    for fmt in ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"]:
                        try:
                            cheque_date = datetime.strptime(cheque_date_str, fmt).date()
                            break
                        except ValueError:
                            continue

                # ====================
                # 5. HANDLE MEMBER/NON-MEMBER
                # ====================
                master_obj = None
                church_member_obj = None
                member_no = None
                member_name = ""

                if name_type == "Member":
                    member_id = request.POST.get("member_id", "")
                    member_type = request.POST.get(
                        "member_type", "master"
                    )  # hidden field

                    if member_id and member_id.isdigit():
                        # Try Master first
                        try:
                            master_obj = Master.objects.get(id=int(member_id))
                            member_no = master_obj.id
                            member_name = master_obj.full_name
                        except Master.DoesNotExist:
                            # Try Church Member
                            try:
                                church_member_obj = Member.objects.get(
                                    id=int(member_id)
                                )
                                member_name = church_member_obj.full_name
                            except Member.DoesNotExist:
                                pass

                # Get non-member data
                non_member_name = request.POST.get("non_member_name", "").strip()
                non_member_contact = request.POST.get("non_member_contact", "").strip()

                # ====================
                # 6. HANDLE LEDGER
                # ====================
                chart_account_value = request.POST.get("chart_account", "").strip()
                ledger_id = ""
                ledger_code = ""
                ledger_name = ""

                if chart_account_value:
                    parts = chart_account_value.split(",")
                    if len(parts) == 3:
                        ledger_id = parts[0].strip()
                        ledger_code = parts[1].strip()
                        ledger_name = parts[2].strip()

                # ====================
                # 7. HANDLE LOAN
                # ====================
                loan_obj = None
                if ledger_name and (
                    "loan repayments" in ledger_name.lower()
                    or "loan disbursements" in ledger_name.lower()
                ):
                    loan_id_value = request.POST.get("loan_id", "")
                    if loan_id_value and loan_id_value.isdigit():
                        try:
                            loan_obj = Loan.objects.get(id=int(loan_id_value))
                            print(
                                f"Selected loan ID: {loan_obj.id}, Balance: {loan_obj.loan_balance}"
                            )
                        except Loan.DoesNotExist:
                            loan_obj = None

                # ====================
                # 8. HANDLE USERS
                # ====================
                username = request.user.username
                user_full_name = request.user.get_full_name()
                user_id = request.user.id

                # ====================
                # 9. HANDLE PAYMENT METHOD
                # ====================
                bank = request.POST.get("bank", "").strip()
                bank_no = request.POST.get("bank_no", "").strip()
                bank_branch = request.POST.get("bank_branch", "").strip()
                momo_no = request.POST.get("momo_no", "").strip()
                momo_name = request.POST.get("momo_name", "").strip()
                cheque_no = request.POST.get("cheque_no", "").strip()

                if pay_mode == "Cheque":
                    # Keep cheque fields
                    momo_no = ""
                    momo_name = ""
                elif pay_mode == "Cash":
                    # Clear ALL payment fields
                    bank = ""
                    bank_no = ""
                    bank_branch = ""
                    cheque_no = ""
                    cheque_date = None
                    momo_no = ""
                    momo_name = ""
                elif pay_mode == "Transfer":
                    bank = ""
                    bank_no = ""
                    bank_branch = ""
                    cheque_no = ""
                    cheque_date = None

                # ====================
                # 10. CREATE TRANSACTION
                # ====================
                trans = Trans.objects.create(
                    # Basic Info
                    entity=entity,
                    date=date,
                    trans_no=trans_no,
                    rec_vou_no=rec_vou_no,
                    trans_type=trans_type,
                    amount=amount,
                    pay_mode=pay_mode,
                    purpose=ledger_name,
                    details=details,
                    # Credit Union Member (Master)
                    member=master_obj,
                    member_no=member_no if master_obj else 0,
                    member_name=member_name,
                    # Church Member (Member)
                    church_member=church_member_obj,
                    # Non-Member Info
                    non_member_name=(
                        non_member_name if name_type == "Non Member" else ""
                    ),
                    non_member_contact=(
                        non_member_contact if name_type == "Non Member" else ""
                    ),
                    # Loan Info
                    loan=loan_obj,
                    # Payment Method Info
                    bank=bank,
                    bank_no=bank_no,
                    bank_branch=bank_branch,
                    momo_no=momo_no,
                    momo_name=momo_name,
                    cheque_no=cheque_no,
                    cheque_date=cheque_date,
                    # Account Info
                    ledger_id=ledger_id,
                    ledger_code=ledger_code,
                    ledger_name=ledger_name,
                    # Module
                    module="church",  # Default to church, can be dynamic
                    # User Info
                    created_by_id=user_id,
                    created_by_name=user_full_name,
                    created_by_username=username,
                )

                messages.success(request, f"Transaction {trans_no} saved successfully!")
                return redirect("ChurchApp:trans_create", entity.slug)

            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
                import traceback

                traceback.print_exc()

    # ============================================
    # CONTEXT
    # ============================================
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

    return render(request, "ChurchApp/trans_create.html", context)


# ChurchApp/views.py

import json
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.db import models
from django_ledger.models import EntityModel
from RecPayApp.models import Trans
from .models import Service, Clergy, Member, Guild
from .forms import ServiceActivityForm
# from services.trans_helper import create_trans


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


# ChurchApp/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from decimal import Decimal
import json
from django_ledger.models import EntityModel
from RecPayApp.models import Trans
from .models import Service, Clergy, Member, Guild
from .forms import ServiceActivityForm


@login_required
def service_activity_create(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)

    # Get data for dropdowns
    clergy_list = Clergy.objects.filter(entity=entity).order_by('full_name')
    officiants = Member.objects.filter(
        entity=entity,
        is_deleted=False
    ).order_by('full_name')
    ushers = Member.objects.filter(
        entity=entity,
        is_deleted=False,
        member_roles__role__name='usher',
        member_roles__is_active=True
    ).order_by('full_name').distinct()
    guilds = Guild.objects.filter(entity=entity, is_active=True).order_by('name')

    if request.method == 'POST':
        # Get basic data
        date = request.POST.get('date')
        service_name = request.POST.get('service_name', '')
        attendance = request.POST.get('attendance', 0)
        communicants = request.POST.get('communicants', 0)

        # Create service record
        service = Service.objects.create(
            entity=entity,
            date=date,
            name_of_service=service_name,
            attendance=attendance,
            communicants=communicants,
            created_by=request.user,
        )

        # Add clergy
        clergy_ids = request.POST.getlist('clergy_ids[]')
        if clergy_ids:
            service.clergy.set(clergy_ids)

        # Add officiant
        officiant_id = request.POST.get('officiant')
        if officiant_id:
            service.officiant_id = officiant_id

        # Add ushers
        usher_ids = request.POST.getlist('usher_ids[]')
        if usher_ids:
            service.ushers.set(usher_ids)

        # Finance fields
        service.general_offertory = request.POST.get('general_offertory', 0) or 0
        service.dues = request.POST.get('dues', 0) or 0
        service.tithes = request.POST.get('tithes', 0) or 0

        # Day Born Offerings
        day_born = {}
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for day in days:
            val = request.POST.get(f'day_born_{day}', '0').replace(',', '')
            try:
                amount = Decimal(val) if val else Decimal('0')
                if amount > 0:
                    day_born[day.capitalize()] = float(amount)
            except:
                pass
        service.day_born_offerings = day_born

        # Guild Offerings
        guild_data = []
        guild_ids = request.POST.getlist('guild_ids[]')
        guild_amounts = request.POST.getlist('guild_amounts[]')
        for i, guild_id in enumerate(guild_ids):
            if guild_id:
                try:
                    guild = Guild.objects.get(id=int(guild_id))
                    amount = Decimal(guild_amounts[i]) if i < len(guild_amounts) else Decimal('0')
                    if amount > 0:
                        guild_data.append({
                            'guild_id': guild.id,
                            'guild_name': guild.name,
                            'amount': float(amount)
                        })
                except:
                    pass
        service.guild_offerings = guild_data

        # Special Thank Offering
        special_amount = request.POST.get('special_thank_amount', '0').replace(',', '')
        service.special_thank_offering = [{
            'name': 'Special Thank Offering',
            'amount': float(special_amount) if special_amount else 0
        }] if special_amount and float(special_amount) > 0 else []

        # Harvest Thank Offering
        harvest_amount = request.POST.get('harvest_thank_amount', '0').replace(',', '')
        service.harvest_thank_offering = [{
            'name': 'Harvest Thank Offering',
            'amount': float(harvest_amount) if harvest_amount else 0
        }] if harvest_amount and float(harvest_amount) > 0 else []

        # Christmas Thank Offering
        christmas_names = request.POST.getlist('christmas_names[]')
        christmas_amounts = request.POST.getlist('christmas_amounts[]')
        christmas_data = []
        for i, name in enumerate(christmas_names):
            if name.strip():
                amount = Decimal(christmas_amounts[i]) if i < len(christmas_amounts) else Decimal('0')
                if amount > 0:
                    christmas_data.append({
                        'name': name.strip(),
                        'amount': float(amount)
                    })
        service.christmas_thank_offering = christmas_data

        # Easter Offerings
        easter_names = request.POST.getlist('easter_names[]')
        easter_amounts = request.POST.getlist('easter_amounts[]')
        easter_data = []
        for i, name in enumerate(easter_names):
            if name.strip():
                amount = Decimal(easter_amounts[i]) if i < len(easter_amounts) else Decimal('0')
                if amount > 0:
                    easter_data.append({
                        'name': name.strip(),
                        'amount': float(amount)
                    })
        service.easter_offering = easter_data

        # Other Thank Offerings
        other_names = request.POST.getlist('other_names[]')
        other_amounts = request.POST.getlist('other_amounts[]')
        other_data = []
        for i, name in enumerate(other_names):
            if name.strip():
                amount = Decimal(other_amounts[i]) if i < len(other_amounts) else Decimal('0')
                if amount > 0:
                    other_data.append({
                        'name': name.strip(),
                        'amount': float(amount)
                    })
        service.other_thank_offerings = other_data

        # Calculate totals and save
        service.save()

        # Create Trans record
        if service.grand_total > 0:
            trans = create_trans(
                entity=entity,
                trans_type='Receipts',
                amount=service.grand_total,
                date=service.date,
                pay_mode='Cash',
                ledger_code='4010',
                ledger_name='Service Offerings',
                details=f"Service: {service.name_of_service or 'Sunday Service'} on {service.date}",
                source=service,
                created_by=request.user,
                purpose='Church Service',
                module='church',
            )
            service.trans = trans
            service.save(update_fields=['trans'])
            messages.success(request, f"Service saved. Transaction {trans.rec_vou_no} created for approval.")
        else:
            messages.info(request, "Service saved with no offerings.")

        return redirect('ChurchApp:service_activity_list', slug=entity.slug)

    context = {
        'entity': entity,
        'clergy_list': clergy_list,
        'officiants': officiants,
        'ushers': ushers,
        'guilds': guilds,
        'today': timezone.now().date(),
        'title': 'Sunday Service Activity',
    }
    return render(request, 'ChurchApp/service_activity_form.html', context)

# ChurchApp/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django_ledger.models import EntityModel
from .models import ChurchConfig
from .forms import ChurchConfigForm


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


# ChurchApp/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django_ledger.models import EntityModel
from .models import Guild
from .forms import GuildForm


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
            return redirect("ChurchApp:guild_list_mange", slug=entity.slug)
    else:
        form = GuildForm()
    context = {
        "entity": entity,
        "form": form,
        "title": "Add Guild",
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
