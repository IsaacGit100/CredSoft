"""
Entity data reset.

DANGEROUS. Used only during testing.

Deletes all transactional data for one entity, in dependency order,
leaving the entity itself (and its config) intact.

Wrapped in a single transaction — any failure rolls back everything.
"""
import json
from django.db import transaction
from django.utils import timezone

# These imports are local so the module is importable without
# forcing every app to be installed.
def _import_all():
    from RecPayApp.models import Trans
    from MembersApp.models import Master, SavingsDailyLog, SavIntApplication
    from LoanApp.models import Loan, LoanDailyTable
    from AutoServices.models import ServiceRun, ServiceGate

    return {
        "Trans":              Trans,
        "SavIntApplication":  SavIntApplication,
        "SavingsDailyLog":    SavingsDailyLog,
        "LoanDailyTable":     LoanDailyTable,
        "Loan":               Loan,
        "Master":             Master,
        "ServiceRun":         ServiceRun,
        "ServiceGate":        ServiceGate,
    }


def preview(entity):
    """Return a dict of counts — what would be deleted."""
    m = _import_all()
    return {
        "Master":            m["Master"].objects.filter(entity=entity).count(),
        "Loan":              m["Loan"].objects.filter(entity=entity).count(),
        "Trans":             m["Trans"].objects.filter(entity=entity).count(),
        "SavingsDailyLog":   m["SavingsDailyLog"].objects.filter(entity=entity).count(),
        "SavIntApplication": m["SavIntApplication"].objects.filter(entity=entity).count(),
        "LoanDailyTable":    m["LoanDailyTable"].objects.filter(entity=entity).count(),
        "ServiceRun":        m["ServiceRun"].objects.filter(entity=entity).count(),
        "ServiceGate":       m["ServiceGate"].objects.filter(run_date__isnull=False).count(),
    }


@transaction.atomic
def reset_entity_data(entity, user, notes=""):
    """
    Delete all transactional data for `entity`.
    Returns a dict of what was deleted.
    """
    from AutoServices.models import EntityResetLog

    m = _import_all()

    deleted = {}

    # --- order matters: children before parents ---

    # 1. SavIntApplication (references Trans and Master)
    deleted["SavIntApplication"] = (
        m["SavIntApplication"].objects.filter(entity=entity).delete()[0]
    )

    # 2. SavingsDailyLog (references Master)
    deleted["SavingsDailyLog"] = (
        m["SavingsDailyLog"].objects.filter(entity=entity).delete()[0]
    )

    # 3. LoanDailyTable (references Loan and Master)
    deleted["LoanDailyTable"] = (
        m["LoanDailyTable"].objects.filter(entity=entity).delete()[0]
    )

    # 4. Trans (references Loan and Master)
    deleted["Trans"] = (
        m["Trans"].objects.filter(entity=entity).delete()[0]
    )

    # 5. Loan (references Master)
    deleted["Loan"] = (
        m["Loan"].objects.filter(entity=entity).delete()[0]
    )

    # 6. Master (references entity)
    deleted["Master"] = (
        m["Master"].objects.filter(entity=entity).delete()[0]
    )

    # 7. ServiceRun (references entity)
    deleted["ServiceRun"] = (
        m["ServiceRun"].objects.filter(entity=entity).delete()[0]
    )

    # 8. Note: ServiceGate is global (one per date), so we don't delete it
    #    — it's cleared by the preflight/main flow naturally.

    # --- audit ---
    EntityResetLog.objects.create(
        entity=entity,
        entity_name=entity.name,
        entity_slug=entity.slug,
        reset_by=user,
        summary=json.dumps(deleted),
        notes=notes,
    )

    return deleted