"""
Shared runner used by both preflight and main commands.
"""

import json, logging
from datetime import datetime, timedelta

from django.utils import timezone
from AutoServices.models import ServiceRun, ServiceGate

from LoanApp.services import loan_int_daily_service
from MembersApp.services import daily_sav_runs
from MembersApp.services import sav_int_application_service

logger = logging.getLogger("AutoServices")

SERVICES = [
    daily_sav_runs,  # 1. accrue daily savings interest
    loan_int_daily_service,  # 2. process due loans
    sav_int_application_service,  # 3. at period end, create PENDING Trans
    
]


def latest_runs_for(entity, run_date=None, kind="main"):
    """
    Return a list of the latest ServiceRun rows for this entity on `run_date`.
    Defaults to today's main run.
    """
    from AutoServices.models import ServiceRun

    if run_date is None:
        run_date = timezone.localdate()

    rows = ServiceRun.objects.filter(
        entity=entity,
        kind=kind,
        run_date=run_date,
    ).order_by("service_name")

    result = {
        "run_date": run_date,
        "kind": kind,
        "services": [],
        "status": "UNKNOWN",
        "ran_at": None,
        "total_written": 0,
        "total_errors": 0,
    }

    if not rows:
        return result

    for r in rows:
        result["services"].append(
            {
                "name": r.service_name.replace("_", " ").title(),
                "written": r.written,
                "skipped": r.skipped,
                "errors": r.errors,
                "status": r.status,
            }
        )
        result["total_written"] += r.written
        result["total_errors"] += r.errors
        if r.started_at and (not result["ran_at"] or r.started_at > result["ran_at"]):
            result["ran_at"] = r.started_at

    # overall verdict
    if result["total_errors"]:
        result["status"] = "PARTIAL"
    elif all(s["status"] == "SUCCESS" for s in result["services"]):
        result["status"] = "SUCCESS"
    else:
        result["status"] = "PARTIAL"

    return result


def get_gate(today):
    return ServiceGate.objects.filter(run_date=today).first()


def run_one_service(svc, entity, today, kind, dry_run):
    name = svc.__name__.rsplit(".", 1)[-1]
    started = timezone.now()

    # Gate check for main runs
    if kind == "main":
        gate = get_gate(today)
        if gate and gate.action == "ABORT":
            ServiceRun.objects.update_or_create(
                service_name=name,
                kind=kind,
                run_date=today,
                defaults=dict(
                    status="BLOCKED",
                    started_at=started,
                    finished_at=timezone.now(),
                    error_detail="Aborted by human decision",
                ),
            )
            return {
                "service": name,
                "status": "BLOCKED",
                "written": 0,
                "skipped": 0,
                "errors": 0,
                "error_list": [],
            }

    try:
        result = svc.run(entity=entity, today=today, dry_run=dry_run)
    except Exception as e:
        result = {
            "service": name,
            "entity": getattr(entity, "slug", "*"),
            "date": str(today),
            "written": 0,
            "skipped": 0,
            "errors": 1,
            "error_list": [f"{type(e).__name__}: {e}"],
        }

    errs = result.get("errors", 0)
    status = "SUCCESS" if errs == 0 else "PARTIAL"

    ServiceRun.objects.update_or_create(
        entity=entity,
        service_name=name,
        kind=kind,
        run_date=today,
        defaults=dict(
            status=status,
            started_at=started,
            finished_at=timezone.now(),
            written=result.get("written", 0),
            skipped=result.get("skipped", 0),
            errors=errs,
            error_detail=json.dumps(result.get("error_list", [])[:50]),
            triggered_by=kind,
        ),
    )

    if errs:
        logger.error(
            "[%s] %s on %s: %d errors. First: %s",
            kind.upper(),
            name,
            today,
            errs,
            result["error_list"][:3],
        )
    return result
