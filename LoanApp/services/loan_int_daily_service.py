"""
loan_int_daily_service
======================

Runs once per day. For every loan whose next_repayment_date == today,
performs one repayment cycle and writes a LoanDailyTable row.

Core rule:
    new_balance = old_balance + due_interest - amount_paid

Allocation (interest first):
    interest_paid      = min(amount_paid, due_interest)
    interest_shortfall = due_interest - interest_paid
    outstanding_amount = max(old_balance - (amount_paid - interest_paid), 0)
    new_loan_balance   = outstanding_amount + interest_shortfall

Term:
    new_term = max(old_term - 1, 0)
    If new_term == 0 → status = CLOSED.

Interest and repayment formulas come from the Loan @properties
(loan.due_interest / loan.due_repayment) — never duplicated here.

Idempotent per (loan, date).
"""

from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from LoanApp.models import Loan, LoanDailyTable

TWO = Decimal("0.01")
CYCLE_DAYS = 30
ACTIVE_STATUSES = ("ACTIVE", "DISBURSED", "APPROVED")


def _m(x):
    return Decimal(x or 0).quantize(TWO, rounding=ROUND_HALF_UP)


def _paid_on(loan, day) -> Decimal:
    """Sum POSTED Trans amounts for this loan on `day`."""
    try:
        from RecPayApp.models import Trans
    except ImportError:
        return Decimal("0.00")
    total = Trans.objects.filter(
        loan=loan, date=day, journal_status="POSTED"
    ).aggregate(s=Sum("amount"))["s"]
    return _m(total)


@transaction.atomic
def process_one_loan(loan: Loan, today: date) -> LoanDailyTable | None:
    if loan.next_repayment_date != today:
        return None
    if loan.status not in ACTIVE_STATUSES:
        return None
    if LoanDailyTable.objects.filter(loan=loan, date=today).exists():
        return None

    old_balance = _m(loan.loan_balance)
    old_term = int(loan.term_months or 0)
    old_due_int = _m(loan.due_interest)  # @property
    old_due_rep = _m(loan.due_repayment)  # @property
    amount_paid = _paid_on(loan, today)

    interest_paid = min(amount_paid, old_due_int)
    interest_shortfall = _m(old_due_int - interest_paid)

    outstanding_amount = _m(
        max(old_balance - (amount_paid - interest_paid), Decimal("0.00"))
    )
    new_balance = _m(outstanding_amount + interest_shortfall)

    new_term = max(old_term - 1, 0)

    loan.loan_balance = new_balance
    loan.term_months = new_term
    loan.next_repayment_date = today + timedelta(days=CYCLE_DAYS)
    if new_term == 0:
        loan.status = "CLOSED"
    loan.save(
        update_fields=[
            "loan_balance",
            "term_months",
            "next_repayment_date",
            "status",
        ]
    )

    try:
        new_due_int = _m(loan.due_interest)
    except Exception:
        new_due_int = _m(new_balance * Decimal(loan.interest_rate or 0) / 100)

    if new_term <= 0:
        new_due_rep = new_balance
    else:
        try:
            new_due_rep = _m(loan.due_repayment)
        except Exception:
            new_due_rep = _m(new_balance / new_term)

    return LoanDailyTable.objects.create(
        date=today,
        entity=loan.entity,
        member=loan.member,
        loan=loan,
        due_interest=old_due_int,
        due_repayment=old_due_rep,
        amount_paid=amount_paid,
        interest_part=interest_paid,
        repayment_part=_m(amount_paid - interest_paid),
        outstanding_amount=outstanding_amount,
        new_loan_balance=new_balance,
        new_due_interest=new_due_int,
        new_due_repayment=new_due_rep,
    )


def run(entity=None, today=None, dry_run=False) -> dict:
    today = today or timezone.localdate()

    qs = Loan.objects.filter(next_repayment_date=today)
    if entity is not None:
        qs = qs.filter(entity=entity)
    qs = qs.select_related("entity", "member")

    written = skipped = errors = 0
    error_list = []

    for loan in qs:
        try:
            if dry_run:
                written += 1
                continue
            log = process_one_loan(loan, today)
            written += 1 if log else 0
            skipped += 0 if log else 1
        except Exception as e:
            errors += 1
            error_list.append(f"loan {loan.pk}: {type(e).__name__}: {e}")

    return {
        "service": "loan_int_daily",
        "entity": getattr(entity, "slug", "*") if entity else "*",
        "date": str(today),
        "written": written,
        "skipped": skipped,
        "errors": errors,
        "error_list": error_list,
    }
