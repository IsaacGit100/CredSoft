"""
sav_int_application_service
===========================

At period end (monthly / quarterly / yearly), for each member with
tot_mnth_sav_int_accrued > 0:

    1. Create a PENDING Trans:
         DR  interest_expense_account_code
         CR  savings_interest_payable_account_code
    2. Create SavIntApplication (audit link to the Trans).
    3. Do NOT change Master — that happens when the supervisor posts.

Idempotent: one SavIntApplication per (master, period_end, frequency).
"""

from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction
from django.utils import timezone

from MembersApp.models import Master, SavIntApplication

TWO = Decimal("0.01")


def _d2(x):
    return Decimal(x or 0).quantize(TWO, rounding=ROUND_HALF_UP)


def _period_bounds(today, frequency):
    end = today
    if frequency == "MONTHLY":
        start = end.replace(day=1)
    elif frequency == "QUARTERLY":
        q_start = ((end.month - 1) // 3) * 3 + 1
        start = end.replace(month=q_start, day=1)
    elif frequency == "YEARLY":
        start = end.replace(month=1, day=1)
    else:
        start = end
    return start, end


def _should_apply(today, frequency):
    nxt = today + timedelta(days=1)
    if frequency == "DAILY":
        return True
    if frequency == "MONTHLY":
        return nxt.month != today.month
    if frequency == "QUARTERLY":
        return (nxt.month != today.month) and today.month in (3, 6, 9, 12)
    if frequency == "YEARLY":
        return today.month == 12 and today.day == 31
    return False


@transaction.atomic
def apply_one(member, today, frequency, config, Trans):
    accrued = _d2(member.tot_mnth_sav_int_accrued)
    if accrued <= 0:
        return None

    period_start, period_end = _period_bounds(today, frequency)

    if SavIntApplication.objects.filter(
        master=member, period_end=period_end, frequency=frequency
    ).exists():
        return None

    trans = Trans.objects.create(
        entity=member.entity,
        date=today,
        amount=accrued,
        member=member,  # link to the member
        member_no=getattr(member, "member_no", None) or None,
        member_name=member.full_name,
        debit_account_code=config.interest_expense_account_code,
        credit_account_code=config.savings_interest_payable_account_code,
        purpose=f"Savings interest {frequency.lower()} — {member.full_name}",
        journal_status="PENDING",
        module="Savings",  # adjust to your convention
        sub_module="Interest Application",
    )

    return SavIntApplication.objects.create(
        entity=member.entity,
        master=member,
        trans=trans,
        period_start=period_start,
        period_end=period_end,
        frequency=frequency,
        amount=accrued,
        days=int(member.mnth_int_accrued_days or 0),
        status="PENDING",
    )


def run(entity=None, today=None, dry_run=False, force=False):
    from django_ledger.models import EntityModel
    from RecPayApp.models import Trans

    today = today or timezone.localdate()
    entities = EntityModel.objects.all()
    if entity is not None:
        entities = entities.filter(pk=entity.pk)

    written = skipped = errors = 0
    error_list = []

    for e in entities:
        config = getattr(e, "cu_config", None)
        if not config:
            continue
        freq = config.savings_interest_application or "MONTHLY"
        if not (force or _should_apply(today, freq)):
            continue

        for m in Master.objects.filter(entity=e):
            try:
                if dry_run:
                    eligible = _d2(m.tot_mnth_sav_int_accrued) > 0
                    written += 1 if eligible else 0
                    skipped += 0 if eligible else 1
                    continue
                app = apply_one(m, today, freq, config, Trans)
                if app:
                    written += 1
                else:
                    skipped += 1
            except Exception as ex:
                errors += 1
                error_list.append(f"master {m.pk}: {type(ex).__name__}: {ex}")

    return {
        "service": "sav_int_application",
        "entity": getattr(entity, "slug", "*") if entity else "*",
        "date": str(today),
        "written": written,
        "skipped": skipped,
        "errors": errors,
        "error_list": error_list,
    }
