from django.shortcuts import render

# Create your views here.


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django_ledger.models import (
    EntityModel,
    LedgerModel,
    JournalEntryModel,
    AccountModel,
    TransactionModel,
)
from decimal import Decimal
from django.utils import timezone
from .models import Service, Clergy, Ushers, Guild, Officiant
from .forms import ServiceForm


@login_required
def church_home(request, slug):
    pass


from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count
from django_ledger.models import EntityModel
from .models import Event
from .models import Member
# from .models import Member, Offering, Event, FinancialRecord

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
            return redirect("ChurchApp:member_list", slug=entity.slug)
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


@login_required
def member_edit1(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    member = get_object_or_404(Member, pk=pk, entity=entity)
    if request.method == "POST":
        form = MemberForm(request.POST, instance=member, entity=entity)
        if form.is_valid():
            form.save()
            messages.success(request, f"Member {member.full_name} updated.")
            return redirect("ChurchApp:member_list", slug=slug)
    else:
        form = MemberForm(instance=member, entity=entity)
    return render(
        request,
        "ChurchApp/member_form.html",
        {"form": form, "entity": entity, "member": member},
    )


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
def service_list(request, slug):
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
            return redirect("ChurchApp:clergy_list", slug=entity.slug)
    else:
        form = ClergyForm(entity=entity)
    context = {
        "entity": entity,
        "form": form,
        "title": "Add Clergy",
    }
    return render(request, "ChurchApp/clergy_form.html", context)


@staff_member_required
def clergy_update(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    clergy = get_object_or_404(Clergy, pk=pk, entity=entity)
    if request.method == "POST":
        form = ClergyForm(request.POST, instance=clergy, entity=entity)
        if form.is_valid():
            form.save()
            messages.success(request, f"Clergy {clergy.full_name} updated.")
            return redirect("ChurchApp:clergy_list", slug=entity.slug)
    else:
        form = ClergyForm(instance=clergy, entity=entity)
    context = {
        "entity": entity,
        "form": form,
        "clergy": clergy,
        "title": f"Edit Clergy: {clergy.full_name}",
    }
    return render(request, "ChurchApp/clergy_form.html", context)


@staff_member_required
def clergy_delete(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    clergy = get_object_or_404(Clergy, pk=pk, entity=entity)
    if request.method == "POST":
        clergy.delete()
        messages.success(request, f"Clergy {clergy.full_name} deleted.")
        return redirect("ChurchApp:clergy_list", slug=entity.slug)
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
def clergy_edit(request, slug, pk):
    pass

@login_required
def clergy_view(request, slug, pk):
    pass


## ==================================Ushers =========================
# ChurchApp/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django_ledger.models import EntityModel
from .models import Ushers
from .forms import UsherForm


@staff_member_required
def usher_list_manage(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    ushers = Ushers.objects.filter(entity=entity)
    context = {
        "entity": entity,
        "ushers": ushers,
        "total_ushers": ushers.count(),
    }
    return render(request, "ChurchApp/usher_list_manage.html", context)


@staff_member_required
def usher_create(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    if request.method == "POST":
        form = UsherForm(request.POST, entity=entity)
        if form.is_valid():
            usher = form.save(commit=False)
            usher.entity = entity
            usher.save()
            messages.success(request, f"Usher {usher.name} created successfully.")
            return redirect("ChurchApp:usher_list_manage", slug=entity.slug)
    else:
        form = UsherForm(entity=entity)
    context = {
        "entity": entity,
        "form": form,
        "title": "Add Usher",
    }
    return render(request, "ChurchApp/usher_form.html", context)


@staff_member_required
def usher_update(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    usher = get_object_or_404(Ushers, pk=pk, entity=entity)
    if request.method == "POST":
        form = UsherForm(request.POST, instance=usher, entity=entity)
        if form.is_valid():
            form.save()
            messages.success(request, f"Usher {usher.name} updated successfully.")
            return redirect("ChurchApp:usher_list_manage", slug=entity.slug)
    else:
        form = UsherForm(instance=usher, entity=entity)
    context = {
        "entity": entity,
        "form": form,
        "usher": usher,
        "title": f"Edit Usher: {usher.name}",
    }
    return render(request, "ChurchApp/usher_form.html", context)


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


## =============================== Guilds =========================
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
    guilds = Guild.objects.filter(entity=entity)
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
            return redirect("ChurchApp:guild_lis_manage", slug=entity.slug)
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


## ===============================Officiant ======================
# ChurchApp/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django_ledger.models import EntityModel
from .models import Officiant
from .forms import OfficiantForm


@staff_member_required
def officiant_list_manage(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    officiants = Officiant.objects.filter(entity=entity)
    context = {
        "entity": entity,
        "officiants": officiants,
        "total_officiants": officiants.count(),
    }
    return render(request, "ChurchApp/officiant_list_manage.html", context)


@staff_member_required
def officiant_create(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    if request.method == "POST":
        form = OfficiantForm(request.POST, entity=entity)
        if form.is_valid():
            officiant = form.save(commit=False)
            officiant.entity = entity
            officiant.save()
            messages.success(
                request, f"Officiant '{officiant.name}' created successfully."
            )
            return redirect("ChurchApp:officiant_list", slug=entity.slug)
    else:
        form = OfficiantForm(entity=entity)
    context = {
        "entity": entity,
        "form": form,
        "title": "Add Officiant",
    }
    return render(request, "ChurchApp/officiant_form.html", context)


@staff_member_required
def officiant_update(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    officiant = get_object_or_404(Officiant, pk=pk, entity=entity)
    if request.method == "POST":
        form = OfficiantForm(request.POST, instance=officiant, entity=entity)
        if form.is_valid():
            form.save()
            messages.success(
                request, f"Officiant '{officiant.name}' updated successfully."
            )
            return redirect("ChurchApp:officiant_list", slug=entity.slug)
    else:
        form = OfficiantForm(instance=officiant, entity=entity)
    context = {
        "entity": entity,
        "form": form,
        "officiant": officiant,
        "title": f"Edit Officiant: {officiant.name}",
    }
    return render(request, "ChurchApp/officiant_form.html", context)


@staff_member_required
def officiant_delete(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    officiant = get_object_or_404(Officiant, pk=pk, entity=entity)
    if request.method == "POST":
        officiant.delete()
        messages.success(request, f"Officiant '{officiant.name}' deleted successfully.")
        return redirect("ChurchApp:officiant_list", slug=entity.slug)
    context = {
        "entity": entity,
        "officiant": officiant,
    }
    return render(request, "ChurchApp/officiant_confirm_delete.html", context)


@staff_member_required
def officiant_detail(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    officiant = get_object_or_404(Officiant, pk=pk, entity=entity)
    context = {
        "entity": entity,
        "officiant": officiant,
    }
    return render(request, "ChurchApp/officiant_detail.html", context)


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


@staff_member_required
def service_create(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    if request.method == "POST":
        form = ServiceForm(request.POST, entity=entity)
        if form.is_valid():
            service = form.save(commit=False)
            service.entity = entity
            service.created_by = request.user
            service.created_at = timezone.now()
            service.updated_at = timezone.now()
            # Grand total is computed in model's save()
            service.save()

            # Post to ledger if user checked the box
            if form.cleaned_data.get("post_to_ledger", False):
                try:
                    journal_entry = create_service_journal(service, entity)
                    service.journal_entry_id = str(journal_entry.uuid)
                    service.posted_to_ledger = True
                    service.save(update_fields=["journal_entry_id", "posted_to_ledger"])
                    messages.success(request, "Service saved and posted to ledger.")
                except Exception as e:
                    messages.warning(
                        request, f"Service saved, but journal entry failed: {e}"
                    )
            else:
                messages.info(request, "Service saved without ledger posting.")

            return redirect("ChurchApp:service_list", slug=entity.slug)
    else:
        form = ServiceForm(entity=entity, initial={"date": timezone.now().date()})

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
def service_list(request, slug):
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
