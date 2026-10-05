from django_ledger.models import EntityModel


def current_context(request):
    """Expose current parish + consolidated-mode to every template."""
    if not request.user.is_authenticated:
        return {"current_entity": None, "consolidated_mode": False}

    slug = request.session.get("current_entity_slug")
    mode = request.session.get("consolidated_mode", False)

    entity = None
    if slug:
        try:
            entity = EntityModel.objects.get(slug=slug)
        except EntityModel.DoesNotExist:
            pass

    return {
        "current_entity": entity,
        "consolidated_mode": mode,
    }
