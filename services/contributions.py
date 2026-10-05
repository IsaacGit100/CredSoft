"""
Shared query helpers for MemberContribution reporting.

All three reports (list, PDF, Excel) use the same filtering logic,
so the numbers always match.
"""

from datetime import date
from django.db.models import Sum, Q
from ChurchApp.models import MemberContribution


def filtered_contributions(
    entity, *, member=None, start=None, end=None, ledger_code=None, q=""
):
    """
    Return a filtered queryset of MemberContribution for one entity.

    Params (all optional except entity):
        member      : ChurchApp.Member instance
        start, end  : date boundaries (inclusive)
        ledger_code : exact match (e.g. "4011" for Dues)
        q           : free-text search on member name / receipt / details
    """
    qs = MemberContribution.objects.filter(entity=entity).select_related(
        "member", "trans"
    )

    if member:
        qs = qs.filter(member=member)
    if start:
        qs = qs.filter(date__gte=start)
    if end:
        qs = qs.filter(date__lte=end)
    if ledger_code:
        qs = qs.filter(ledger_code=ledger_code)
    if q:
        qs = qs.filter(
            Q(member__full_name__icontains=q)
            | Q(member__member_no__icontains=q)
            | Q(receipt_no__icontains=q)
            | Q(details__icontains=q)
        )

    return qs.order_by("date", "id")


def summary_by_category(qs):
    """Return [{ledger_code, ledger_name, total, count}, ...]."""
    rows = (
        qs.values("ledger_code", "ledger_name")
        .annotate(total=Sum("amount"), count=Sum("id"))
        .order_by("ledger_code")
    )
    # Sum("id") counts non-null ids — same as Count("id")
    from django.db.models import Count

    rows = (
        qs.values("ledger_code", "ledger_name")
        .annotate(total=Sum("amount"), count=Count("id"))
        .order_by("ledger_code")
    )
    return list(rows)


def grand_total(qs):
    return qs.aggregate(t=Sum("amount"))["t"] or 0
