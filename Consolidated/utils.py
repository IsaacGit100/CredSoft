"""
Consolidated helpers — thin wrappers that reuse Report.utils.

No duplicate calculations. Everything routes through Report/utils.get_*.
"""

from decimal import Decimal

from django_ledger.models import EntityModel

from Report.utils import (
    get_balance_sheet,
    get_cash_flow,
    get_income_statement,
    get_trial_balance,
)


def get_church_entities():
    """
    Churches are entities whose EntityConfig.entity_type == 'church'.
    Falls back to all entities if none are tagged yet.
    """
    qs = EntityModel.objects.filter(config__entity_type="church").order_by("name")
    if not qs.exists():
        qs = EntityModel.objects.all().order_by("name")
    return qs

def resolve_selected_entities(request):
    """
    Decide which entities a report applies to:
      1. ?entities=slug1,slug2 in URL → those
      2. session has consolidated_mode=True → all parishes (sum)
      3. session has current_entity_slug → that single parish
      4. NO selection → empty (nothing to show)
    """
    all_churches = get_church_entities()

    # 1. Explicit URL selection
    raw = request.GET.get("entities", "").strip()
    if raw:
        slugs = [s for s in raw.split(",") if s]
        selected = all_churches.filter(slug__in=slugs)
        return selected, [e.slug for e in selected]

    # 2. Consolidated mode from session
    if request.session.get("consolidated_mode"):
        slugs = list(all_churches.values_list("slug", flat=True))
        return all_churches, slugs

    # 3. Single parish from session
    session_slug = request.session.get("current_entity_slug")
    if session_slug:
        try:
            entity = all_churches.get(slug=session_slug)
            single = all_churches.filter(pk=entity.pk)
            return single, [entity.slug]
        except EntityModel.DoesNotExist:
            pass

    # 4. No selection — return empty
    return all_churches.none(), []


def get_consolidated_dashboard_data(entities, start=None, end=None):
    """
    Loop over entities, call Report.utils functions, return:
        {
          'per_entity':  [ {entity, cash, bank, total_cash, revenue, expense,
                            net_income, assets, liabilities, equity,
                            receipts, payments, net_flow}, ... ],
          'totals':      { same keys, summed },
        }
    """
    per_entity = []
    totals = {
        "cash": Decimal("0"),
        "bank": Decimal("0"),
        "total_cash": Decimal("0"),
        "total_receipts": Decimal("0"),
        "total_payments": Decimal("0"),
        "net_flow": Decimal("0"),
        "total_revenue": Decimal("0"),
        "total_expense": Decimal("0"),
        "net_income": Decimal("0"),
        "total_assets": Decimal("0"),
        "total_liabilities": Decimal("0"),
        "total_equity": Decimal("0"),
    }

    for entity in entities:
        # Income statement
        is_data = get_income_statement(entity, start, end)
        # Balance sheet
        bs_data = get_balance_sheet(entity, end)

        # Cash position (as at end)
        from Report.utils import _cash_balance, CASH_CODES
        from django_ledger.models import TransactionModel
        from django.db.models import Sum

        def _bal(code):
            qs = TransactionModel.objects.filter(
                journal_entry__ledger__entity=entity,
                journal_entry__posted=True,
                account__code=code,
            )
            if end:
                qs = qs.filter(journal_entry__timestamp__date__lte=end)
            dr = qs.filter(tx_type="debit").aggregate(s=Sum("amount"))["s"] or Decimal(
                "0"
            )
            cr = qs.filter(tx_type="credit").aggregate(s=Sum("amount"))["s"] or Decimal(
                "0"
            )
            return dr - cr

        cash = _bal("1010")
        bank = _bal("1020")
        total_cash = cash + bank

        # Trans flows (receipts/payments) for the period
        from RecPayApp.models import Trans

        tq = Trans.objects.filter(entity=entity)
        if start:
            tq = tq.filter(date__gte=start)
        if end:
            tq = tq.filter(date__lte=end)
        receipts = tq.filter(trans_type="Receipts").aggregate(s=Sum("amount"))[
            "s"
        ] or Decimal("0")
        payments = tq.filter(trans_type="Payments").aggregate(s=Sum("amount"))[
            "s"
        ] or Decimal("0")

        row = {
            "entity": entity,
            "cash": cash,
            "bank": bank,
            "total_cash": total_cash,
            "total_receipts": receipts,
            "total_payments": payments,
            "net_flow": receipts - payments,
            "total_revenue": is_data["total_revenue"],
            "total_expense": is_data["total_expense"],
            "net_income": is_data["net_income"],
            "total_assets": bs_data["total_assets"],
            "total_liabilities": bs_data["total_liabilities"],
            "total_equity": bs_data["total_equity"],
        }
        per_entity.append(row)

        for k in totals:
            totals[k] += row[k]

    return {"per_entity": per_entity, "totals": totals}


def get_consolidated_trial_balance(entities, start=None, end=None):
    """Sum trial-balance rows across entities by account code."""
    combined = {}
    total_dr = Decimal("0")
    total_cr = Decimal("0")

    for entity in entities:
        rows, e_dr, e_cr = get_trial_balance(entity, start, end)
        for r in rows:
            key = r["code"]
            if key not in combined:
                combined[key] = {
                    "code": r["code"],
                    "name": r["name"],
                    "dr": Decimal("0"),
                    "cr": Decimal("0"),
                }
            combined[key]["dr"] += r["dr"]
            combined[key]["cr"] += r["cr"]
        total_dr += e_dr
        total_cr += e_cr

    rows = sorted(combined.values(), key=lambda r: r["code"])
    return rows, total_dr, total_cr


def get_consolidated_income_statement(entities, start=None, end=None):
    """
    Return the FULL consolidated income statement:
    one row per account code, summed across all selected parishes.
    """
    from decimal import Decimal
    from Report.utils import get_income_statement

    revenue_map = {}
    cogs_map = {}
    expense_map = {}
    total_revenue = Decimal("0")
    total_cogs = Decimal("0")
    total_expense = Decimal("0")
    per_entity = []

    for entity in entities:
        d = get_income_statement(entity, start, end)

        per_entity.append(
            {
                "entity": entity,
                "revenue": d["total_revenue"],
                "expense": d["total_expense"],
                "net_income": d["net_income"],
            }
        )

        for r in d["revenue_rows"]:
            key = r["code"]
            if key not in revenue_map:
                revenue_map[key] = {
                    "code": r["code"],
                    "name": r["name"],
                    "amount": Decimal("0"),
                }
            revenue_map[key]["amount"] += r["amount"]

        for r in d["cogs_rows"]:
            key = r["code"]
            if key not in cogs_map:
                cogs_map[key] = {
                    "code": r["code"],
                    "name": r["name"],
                    "amount": Decimal("0"),
                }
            cogs_map[key]["amount"] += r["amount"]

        for r in d["expense_rows"]:
            key = r["code"]
            if key not in expense_map:
                expense_map[key] = {
                    "code": r["code"],
                    "name": r["name"],
                    "amount": Decimal("0"),
                }
            expense_map[key]["amount"] += r["amount"]

        total_revenue += d["total_revenue"]
        total_cogs += d["total_cogs"]
        total_expense += d["total_expense"]

    revenue_rows = sorted(revenue_map.values(), key=lambda x: x["code"])
    cogs_rows = sorted(cogs_map.values(), key=lambda x: x["code"])
    expense_rows = sorted(expense_map.values(), key=lambda x: x["code"])

    gross_profit = total_revenue - total_cogs
    net_income = gross_profit - total_expense

    return {
        "revenue_rows": revenue_rows,
        "cogs_rows": cogs_rows,
        "expense_rows": expense_rows,
        "total_revenue": total_revenue,
        "total_cogs": total_cogs,
        "total_expense": total_expense,
        "gross_profit": gross_profit,
        "net_income": net_income,
        "per_entity": per_entity,
    }


def scope_title(base_name, entities, selected_slugs):
    """Return e.g. 'St Patrick Parish Accounts' or 'Consolidated ...'."""
    if len(selected_slugs) == 1:
        entity = entities.first()
        return f"{entity.name} — {base_name}"
    return f"Consolidated {base_name}"


def scope_subtitle(entities, selected_slugs):
    if len(selected_slugs) == 1:
        return entities.first().name
    return f"Sum of {len(selected_slugs)} parishes"
