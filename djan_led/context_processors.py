
from .models import UserProfile

def current_entity(request):
    from django_ledger.models import EntityModel
    if request.user.is_authenticated:
        try:
            profile = request.user.djan_led_profile
            if profile.default_entity:
                return {'entity': profile.default_entity}
        except UserProfile.DoesNotExist:
            pass
    return {'entity': None}


def current_entity(request):
    from django_ledger.models import EntityModel
    """
    Adds the user's default entity to every template context.
    If the user is not authenticated or has no default entity, returns None.
    """
    entity = None
    if request.user.is_authenticated:
        try:
            profile = request.user.djan_led_profile
            if profile.default_entity:
                entity = profile.default_entity
        except:
            pass
    return {'entity': entity}