from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django_ledger.models import (
    EntityModel,
    JournalEntryModel,
    TransactionModel,
    AccountModel,
    LedgerModel,
)
from djan_led.models import UserProfile
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
@login_required
def tech_dashboard(request):
    # Ensure user is technical or super_admin (optional)
    #    entity = get_object_or_404(EntityModel, slug=slug)
    #    if not user_can_access_entity(request.user, entity):
    #        return render(request, 'djan_led/access_denied.html', {'entity': entity})
    try:
        profile = request.user.djan_led_profile
        if profile.role not in ["technical", "super_admin"]:
            return redirect("djan_led:after_login_redirect")
    except:
        return redirect("djan_led:after_login_redirect")

    return render(request, "Tech/tech_dashboard.html", {"user": request.user})



@login_required
def user_management(request):
    # Only technical and super_admin can access
    try:
        profile = request.user.djan_led_profile
        if profile.role not in ["technical", "super_admin"]:
            messages.error(request, "Access denied. You are not authorised.")
            return redirect("after_login_redirect")
    except:
        messages.error(request, "Profile not found.")
        return redirect("after_login_redirect")

    users = User.objects.all().order_by("username")
    user_data = []

    for u in users:
        try:
            profile = u.djan_led_profile
            role = profile.role
            default_entity = (
                profile.default_entity.name if profile.default_entity else "—"
            )
            allowed = ", ".join([e.name for e in profile.allowed_entities.all()]) or "—"
        except:
            role = "—"
            default_entity = "—"
            allowed = "—"

        user_data.append(
            {
                "user": u,
                "role": role,
                "default_entity": default_entity,
                "allowed_entities": allowed,
            }
        )

    context = {
        "user_data": user_data,
    }
    return render(request, "Tech/user_management.html", context)

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django_ledger.models import EntityModel

@staff_member_required
def entity_management(request):
    """View to manage entities (list, create, edit)"""
    entities = EntityModel.objects.all()
    context = {
        'entities': entities,
        'title': 'Entity Management',
    }
    return render(request, 'Tech/entity_management.html', context)


@login_required
def coa_management(request):
    entities = EntityModel.objects.all().order_by("name")
    #    if not user_can_access_entity(request.user, entity):
    #        return render(request, 'djan_led/access_denied.html', {'entity': entity})
    return render(request, "Tech/coa_management.html", {"entities": entities})



@login_required
def create_entity(request):
    if request.method == "POST":
        # Handle entity creation
        pass
    return render(request, "Tech/create_entity.html")


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.crypto import get_random_string

User = get_user_model()


@staff_member_required
def reset_user_password(request, user_id):
    if request.method != "POST":
        return redirect("Tech:user_management")

    user = get_object_or_404(User, id=user_id)
    new_password = get_random_string(
        length=12,
        allowed_chars="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*",
    )
    user.set_password(new_password)
    user.save()

    messages.success(
        request, f"Password for {user.username} has been reset to: {new_password}"
    )
    return redirect("Tech:user_management")


from django.utils.crypto import get_random_string

import secrets
import string


def generate_random_password(length=12):
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(secrets.choice(alphabet) for _ in range(length))


# Tech/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django_ledger.models import EntityModel
from .forms import EntityForm


@staff_member_required
def edit_entity(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    if request.method == "POST":
        form = EntityForm(request.POST, instance=entity)
        if form.is_valid():
            form.save()
            messages.success(request, f"Entity '{entity.name}' updated successfully.")
            return redirect("Tech:entity_management")
    else:
        form = EntityForm(instance=entity)

    context = {
        "form": form,
        "entity": entity,
        "title": f"Edit Entity: {entity.name}",
    }
    return render(request, "Tech/edit_entity.html", context)
