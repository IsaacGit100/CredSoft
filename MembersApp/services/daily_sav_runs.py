"""
daily_sav_runs
==============

Daily savings interest accrual. This service ONLY does:

    1. daily_interest = balance * effective_sav_int_rate / 100 / 365
    2. tot_mnth_sav_int_accrued += daily_interest
    3. mnth_int_accrued_days    += 1

It does NOT touch:
    - member.balance
    - member.tot_sav_int
    - Trans / ledger

Those are updated when the supervisor posts the period-end application.

Idempotent per (master, date).
"""

from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction
from django.utils import timezone

from MembersApp.models import Master, SavingsDailyLog

FOUR = Decimal("0.0001")
TWO = Decimal("0.01")


def _d4(x):
    return Decimal(x or 0).quantize(FOUR, rounding=ROUND_HALF_UP)


def _d2(x):
    return Decimal(x or 0).quantize(TWO, rounding=ROUND_HALF_UP)


def is_month_end(d: date) -> bool:
    return (d + timedelta(days=1)).month != d.month


def preview_one(member, today):
    """Read-only projection for the test page — nothing is written."""
    current_balance = _d2(member.balance)
    rate = Decimal(member.effective_sav_int_rate or 0)
    daily_int = _d4(member.sav_interest)

    mnth_accrued = _d2((member.tot_mnth_sav_int_accrued or 0) + daily_int)
    mnth_days = int(member.mnth_int_accrued_days or 0) + 1

    already = SavingsDailyLog.objects.filter(master=member, date=today).exists()

    return {
        "member": member,
        "old_balance": current_balance,
        "effective_rate": rate,
        "daily_interest": daily_int,
        "new_balance": current_balance,  # unchanged — kept for the table column
        "mnth_accrued": mnth_accrued,
        "mnth_days": mnth_days,
        "month_end": is_month_end(today),
        "already": already,
    }


@transaction.atomic
def process_one(member, today):
    """Accrue one day's interest for one member. Writes nothing to balance."""
    if SavingsDailyLog.objects.filter(master=member, date=today).exists():
        return None

    current_balance = _d2(member.balance)  # read-only — for the audit log
    rate = Decimal(member.effective_sav_int_rate or 0)
    daily_int = _d4(member.sav_interest)

    mnth_accrued = _d2((member.tot_mnth_sav_int_accrued or 0) + daily_int)
    mnth_days = int(member.mnth_int_accrued_days or 0) + 1

    # The ONLY writes to Master in this service:
    member.tot_mnth_sav_int_accrued = mnth_accrued
    member.mnth_int_accrued_days = mnth_days
    member.save(
        update_fields=[
            "tot_mnth_sav_int_accrued",
            "mnth_int_accrued_days",
        ]
    )

    return SavingsDailyLog.objects.create(
        date=today,
        entity=member.entity,
        master=member,
        old_balance=current_balance,
        effective_rate=rate,
        daily_interest=daily_int,
        new_balance=current_balance,  # same value — balance doesn't move here
        mnth_accrued_after=mnth_accrued,
        mnth_days_after=mnth_days,
        was_month_end=False,
        applied_amount=Decimal("0.00"),
    )


def run(entity=None, today=None, dry_run=False):
    today = today or timezone.localdate()

    qs = Master.objects.all()
    if entity is not None:
        qs = qs.filter(entity=entity)
    qs = qs.select_related("entity")

    written = skipped = errors = 0
    error_list = []

    for m in qs:
        try:
            if dry_run:
                written += 1
                continue
            log = process_one(m, today)
            written += 1 if log else 0
            skipped += 0 if log else 1
        except Exception as e:
            errors += 1
            error_list.append(f"master {m.pk}: {type(e).__name__}: {e}")

    return {
        "service": "daily_sav_runs",
        "entity": getattr(entity, "slug", "*") if entity else "*",
        "date": str(today),
        "written": written,
        "skipped": skipped,
        "errors": errors,
        "error_list": error_list,
    }
