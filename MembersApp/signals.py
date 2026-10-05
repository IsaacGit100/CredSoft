"""
Signals for MembersApp.

When a Trans linked to a SavIntApplication is marked POSTED by the
supervisor, credit the member's tot_sav_int and reset the monthly
counters.
"""

from decimal import Decimal

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from RecPayApp.models import Trans
from MembersApp.models import SavIntApplication

TWO = Decimal("0.01")


def _d2(x):
    return Decimal(x or 0).quantize(TWO)


@receiver(post_save, sender=Trans)
def apply_savings_interest_on_post(sender, instance, **kwargs):
    if instance.journal_status != "POSTED":
        return

    try:
        app = SavIntApplication.objects.select_related("master").get(
            trans=instance, status="PENDING"
        )
    except SavIntApplication.DoesNotExist:
        return

    if app.applied_at:
        return

    m = app.master

    m.tot_sav_int = _d2((m.tot_sav_int or 0) + app.amount)
    m.balance = _d2(
        (m.tot_deposits or 0) - (m.tot_deposit_withdrawal or 0) + m.tot_sav_int
    )
    m.tot_mnth_sav_int_accrued = Decimal("0.00")
    m.mnth_int_accrued_days = 0
    m.save(
        update_fields=[
            "tot_sav_int",
            "balance",
            "tot_mnth_sav_int_accrued",
            "mnth_int_accrued_days",
        ]
    )

    app.status = "POSTED"
    app.applied_at = timezone.now()
    app.save(update_fields=["status", "applied_at"])
