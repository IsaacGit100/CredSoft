"""
Context processors for djan_led.

Exposes two values to every template:

    entity         — the logged-in user's default entity (fallback only;
                     views may override by passing their own `entity`)
    entity_config  — the EntityConfig for the entity in the current URL
                     (identified by the `slug` kwarg), or None
"""

from django_ledger.models import EntityModel

from .models import EntityConfig, UserProfile


def current_entity(request):
    """
    Add the user's default entity to every template context.

    A view that passes its own `entity` in the context will override this,
    which is intentional — the URL slug is the source of truth for the
    entity currently being viewed.
    """
    if not request.user.is_authenticated:
        return {"entity": None}

    try:
        profile = request.user.djan_led_profile
    except UserProfile.DoesNotExist:
        return {"entity": None}

    return {"entity": profile.default_entity}


def entity_config(request):
    """
    Add the EntityConfig for the entity in the current URL to the context.

    Uses the `slug` kwarg from the URL resolver. Returns None if:
      - the URL has no slug
      - the entity does not exist
      - the entity has no EntityConfig row yet
    """
    match = getattr(request, "resolver_match", None)
    slug = match.kwargs.get("slug") if match else None

    if not slug:
        return {"entity_config": None}

    try:
        entity = EntityModel.objects.get(slug=slug)
    except EntityModel.DoesNotExist:
        return {"entity_config": None}

    try:
        config = EntityConfig.objects.get(entity=entity)
    except EntityConfig.DoesNotExist:
        config = None

    return {"entity_config": config}
