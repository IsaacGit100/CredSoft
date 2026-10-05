# FixedAssets/services.py

from decimal import Decimal
from django.utils import timezone
from django.db import transaction as db_transaction

from RecPayApp.models import Trans
from .models import FixedAsset, DepreciationEntry

def calculate_period_depreciation(asset, period_start, period_end):
    """Calculate depreciation for a period. No DB writes."""
    if not asset.is_active or asset.disposal_date:
        return Decimal("0.00")

    days = (period_end - period_start).days + 1
    if days <= 0:
        return Decimal("0.00")

    cost = asset.cost or Decimal("0.00")
    salvage = asset.salvage_value or Decimal("0.00")
    life = asset.useful_life_years or 1

    if asset.depreciation_method == "straight_line":
        annual = (cost - salvage) / Decimal(life)
    else:  # declining_balance
        rate = asset.override_depreciation_rate or asset.category.depreciation_rate
        annual = asset.book_value * (Decimal(rate) / Decimal("100"))

    daily = annual / Decimal("365")
    period_amount = (daily * Decimal(days)).quantize(Decimal("0.01"))

    max_depreciable = (
        cost - salvage - (asset.accumulated_depreciation or Decimal("0.00"))
    )
    return max(Decimal("0.00"), min(period_amount, max_depreciable))


@db_transaction.atomic
def post_depreciation(entity, period_start=None, period_end=None, user=None):
    """
    Calculate depreciation for all active assets; create DepreciationEntry
    + Trans (Journal, PENDING). Does NOT post to the journal.
    """
    today = timezone.now().date()
    period_start = period_start or today.replace(day=1)
    period_end = period_end or today

    assets = FixedAsset.objects.filter(
        entity=entity,
        is_active=True,
        disposal_date__isnull=True,
    ).select_related("category")

    created, skipped, total, errors = 0, 0, Decimal("0.00"), []

    for asset in assets:
        if DepreciationEntry.objects.filter(
            asset=asset,
            period_end__gte=period_start,
            period_start__lte=period_end,
        ).exists():
            skipped += 1
            continue

        amount = calculate_period_depreciation(asset, period_start, period_end)
        if amount <= 0:
            skipped += 1
            continue

        expense_acc = asset.category.depreciation_expense_account
        accum_acc = asset.category.accumulated_depreciation_account
        if not expense_acc or not accum_acc:
            errors.append(f"{asset.asset_id}: category missing GL accounts.")
            continue

        entry = DepreciationEntry.objects.create(
            entity=entity,
            asset=asset,
            period_start=period_start,
            period_end=period_end,
            amount=amount,
            created_by=user,
        )

        # FixedAssets/services.py — inside post_depreciation

        trans = Trans.objects.create(
            entity=entity,
            module='fixed_assets',
            sub_module='depreciation',        # ← ensure this line exists
            trans_type='Journal',
            date=period_end,
            amount=amount,
            pay_mode='None',
            purpose='Depreciation',
            details=f"Depreciation: {asset.asset_id} – {asset.name} ({period_start} → {period_end})",
            debit_account_code=expense_acc.code,
            debit_account_name=expense_acc.name,
            credit_account_code=accum_acc.code,
            credit_account_name=accum_acc.name,
            journal_status='PENDING',
            status='DRAFT',
            created_by=user,
            created_by_name=user.username if user else '',
            created_by_username=user.username if user else '',
        )
                
    
        entry.trans = trans
        entry.save(update_fields=["trans"])

        created += 1
        total += amount

    return {
        "created": created,
        "skipped": skipped,
        "total": total,
        "errors": errors,
        "period_start": period_start,
        "period_end": period_end,
    }


def apply_posted_depreciation(trans):
    """
    Called by TransactionPostingService after a Depreciation Trans is posted.
    Updates the asset's accumulated depreciation + book value.
    """
    for entry in trans.depreciation_entries.all():
        asset = entry.asset
        asset.accumulated_depreciation = (
            asset.accumulated_depreciation or Decimal("0.00")
        ) + entry.amount
        asset.book_value = (
            asset.cost or Decimal("0.00")
        ) - asset.accumulated_depreciation
        asset.last_depreciation_date = entry.period_end
        asset.save(
            update_fields=[
                "accumulated_depreciation",
                "book_value",
                "last_depreciation_date",
            ]
        )
