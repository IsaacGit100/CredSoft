from datetime import datetime
from urllib.parse import urlencode
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone


from django_ledger.models import EntityModel

from Report.pdf_builder import Col, build_report_pdf
from Report.utils import (
    as_at_label,
    for_period_label,
    parse_date,
    render_excel,
)


from .utils import (
    get_church_entities,
    get_consolidated_dashboard_data,
    get_consolidated_income_statement,
    get_consolidated_trial_balance,
    resolve_selected_entities,
)

def _scope_label(entities, selected_slugs):
    """Return 'St Patrick Parish' or 'Consolidated (5 parishes)'."""
    if len(selected_slugs) == 1:
        e = entities.first()
        return e.name if e else "Parish"
    return f"Consolidated ({len(selected_slugs)} parishes)"

def scope_title(base_name, entities, selected_slugs):
    """Return 'St Patrick Parish — Trial Balance' or 'Consolidated Trial Balance'."""
    if len(selected_slugs) == 1:
        e = entities.first()
        return f"{e.name} — {base_name}" if e else base_name
    return f"Consolidated {base_name}"


def scope_subtitle(entities, selected_slugs):
    """Return a subtitle reflecting the scope."""
    if len(selected_slugs) == 1:
        e = entities.first()
        return e.name if e else ""
    return f"Sum of {len(selected_slugs)} parishes"


# ---------------------------------------------------------------------------
# Super admin guard
# ---------------------------------------------------------------------------
def _is_bishop(user):
    try:
        return user.djan_led_profile.role == "super_admin"
    except Exception:
        return False


def _require_bishop(request, require_selection=False):
    """Return a redirect response if not bishop, else None.
    
    If require_selection is True, a bishop who hasn't picked a parish
    or Consolidated yet is redirected to the select screen.
    """
    if not _is_bishop(request.user):
        return redirect("after_login_redirect")
    if require_selection:
        has_single = bool(request.session.get("current_entity_slug"))
        has_consolidated = bool(request.session.get("consolidated_mode"))
        if not (has_single or has_consolidated):
            return redirect("Consolidated:select_context")
    return None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _selection_querystring(request, extra=None):
    """Query string that preserves entities + dates for report links."""
    qs = request.GET.copy()
    qs.pop("format", None)
    qs.pop("download", None)
    if extra:
        for k, v in extra.items():
            qs[k] = v
    return qs.urlencode()


def _period_label(start, end):
    """Bishop view is always for a period, not 'as at'."""
    if start and end:
        return f"for the period {start:%d/%m/%Y} to {end:%d/%m/%Y}"
    if start:
        return f"from {start:%d/%m/%Y}"
    if end:
        return f"up to {end:%d/%m/%Y}"
    return "for all dates"


# ---------------------------------------------------------------------------
# Main dashboard
# ---------------------------------------------------------------------------
@login_required
def consolidated_dashboard(request):
    r = _require_bishop(request, require_selection=True)
    if r:
        return r

    all_churches = get_church_entities()
    entities, selected_slugs = resolve_selected_entities(request)

    start = parse_date(request.GET.get("start"))
    end = parse_date(request.GET.get("end"))

    data = get_consolidated_dashboard_data(entities, start, end)

    context = {
        "all_churches": all_churches,
        "selected_slugs": selected_slugs,
        "selected_count": len(selected_slugs),
        "total_count": all_churches.count(),
        "all_selected": len(selected_slugs) == all_churches.count(),
        "start": request.GET.get("start", ""),
        "end": request.GET.get("end", ""),
        "period_label": _period_label(start, end),
        "per_entity": data["per_entity"],
        "totals": data["totals"],
        "querystring": _selection_querystring(request),
    }
    return render(request, "Consolidated/dashboard.html", context)


# ---------------------------------------------------------------------------
# Consolidated Trial Balance
# ---------------------------------------------------------------------------

@login_required
def consolidated_trial_balance(request):
    r = _require_bishop(request, require_selection=True)
    if r:
        return r

    entities, selected_slugs = resolve_selected_entities(request)
    start = parse_date(request.GET.get("start"))
    end = parse_date(request.GET.get("end"))

    rows, total_dr, total_cr = get_consolidated_trial_balance(entities, start, end)
    p_label = _period_label(start, end)
    balanced = total_dr == total_cr

    if len(selected_slugs) == 1:
        e = entities.first()
        scope_label = (getattr(getattr(e, "config", None), "display_name", "")
                       or (e.name if e else "Parish"))
    else:
        scope_label = f"Consolidated ({len(selected_slugs)} parishes)"

    fmt = request.GET.get("format", "html")

    if fmt == "pdf":
        columns = [
            Col("Code", 12, "left"),
            Col("Account", 48, "left"),
            Col("Debit", 20, "right", currency=True),
            Col("Credit", 20, "right", currency=True),
        ]
        table_rows = [[r["code"], r["name"], r["dr"], r["cr"]] for r in rows]
        totals = ["", "Totals", total_dr, total_cr]

        first_entity = entities.first()
        cfg = getattr(first_entity, "config", None) if first_entity else None
        pdf_bytes = build_report_pdf(
            entity=first_entity,
            entity_config=cfg,
            report_title=f"{scope_label} — Trial Balance",
            period_label=p_label,
            columns=columns,
            rows=table_rows,
            totals=totals,
            filename="consolidated_trial_balance.pdf",
        )
        resp = HttpResponse(pdf_bytes, content_type="application/pdf")
        resp["Content-Disposition"] = (
            f'inline; filename="consolidated_tb_{timezone.now():%Y%m%d}.pdf"'
        )
        return resp

    if fmt == "excel":
        headers = ["Code", "Account", "Debit", "Credit"]
        data_x = [[r["code"], r["name"], float(r["dr"]), float(r["cr"])] for r in rows]
        data_x.append(["", "Totals", float(total_dr), float(total_cr)])
        return render_excel(
            headers, data_x,
            filename=f"consolidated_tb_{timezone.now():%Y%m%d}.xlsx",
            sheet_name="Trial Balance",
            title=f"{scope_label} — Trial Balance",
            subtitle=p_label,
        )

    context = {
        "rows": rows,
        "total_dr": total_dr,
        "total_cr": total_cr,
        "balanced": balanced,
        "period_label": p_label,
        "entity_count": len(selected_slugs),
        "scope_label": scope_label,
        "querystring": _selection_querystring(request),
        "start": request.GET.get("start", ""),
        "end": request.GET.get("end", ""),
        "now": timezone.now(),
    }
    return render(request, "Consolidated/consolidated_trial_balance.html", context)

# ---------------------------------------------------------------------------
# Consolidated Income Statement
# ---------------------------------------------------------------------------

@login_required
def consolidated_income_statement(request):
    r = _require_bishop(request, require_selection=True)
    if r:
        return r

    entities, selected_slugs = resolve_selected_entities(request)
    start = parse_date(request.GET.get("start"))
    end = parse_date(request.GET.get("end"))

    data = get_consolidated_income_statement(entities, start, end)
    p_label = _period_label(start, end)

    if len(selected_slugs) == 1:
        e = entities.first()
        scope_label = (getattr(getattr(e, "config", None), "display_name", "")
                       or (e.name if e else "Parish"))
    else:
        scope_label = f"Consolidated ({len(selected_slugs)} parishes)"

    fmt = request.GET.get("format", "html")

    if fmt == "pdf":
        columns = [
            Col("Code", 15, "left"),
            Col("Account", 55, "left"),
            Col("Amount", 30, "right", currency=True),
        ]
        table_rows = [["", "REVENUE", ""]]
        for r in data["revenue_rows"]:
            table_rows.append([r["code"], r["name"], r["amount"]])
        table_rows.append(["", "Total Revenue", data["total_revenue"]])
        table_rows.append(["", "", ""])
        if data["cogs_rows"]:
            table_rows.append(["", "COST OF GOODS SOLD", ""])
            for r in data["cogs_rows"]:
                table_rows.append([r["code"], r["name"], r["amount"]])
            table_rows.append(["", "Total COGS", data["total_cogs"]])
            table_rows.append(["", "Gross Profit", data["gross_profit"]])
            table_rows.append(["", "", ""])
        table_rows.append(["", "EXPENSES", ""])
        for r in data["expense_rows"]:
            table_rows.append([r["code"], r["name"], r["amount"]])
        table_rows.append(["", "Total Expenses", data["total_expense"]])
        table_rows.append(["", "", ""])
        net_label = "NET INCOME" if data["net_income"] >= 0 else "NET LOSS"
        table_rows.append(["", net_label, data["net_income"]])

        first_entity = entities.first()
        cfg = getattr(first_entity, "config", None) if first_entity else None
        pdf_bytes = build_report_pdf(
            entity=first_entity,
            entity_config=cfg,
            report_title=f"{scope_label} — Income Statement",
            period_label=p_label,
            columns=columns,
            rows=table_rows,
            totals=None,
            filename="consolidated_income_statement.pdf",
        )
        resp = HttpResponse(pdf_bytes, content_type="application/pdf")
        resp["Content-Disposition"] = (
            f'inline; filename="consolidated_income_{timezone.now():%Y%m%d}.pdf"'
        )
        return resp

    if fmt == "excel":
        headers = ["Code", "Account", "Amount"]
        data_x = []
        data_x.append(["", "REVENUE", ""])
        for r in data["revenue_rows"]:
            data_x.append([r["code"], r["name"], float(r["amount"])])
        data_x.append(["", "Total Revenue", float(data["total_revenue"])])
        data_x.append(["", "", ""])
        if data["cogs_rows"]:
            data_x.append(["", "COST OF GOODS SOLD", ""])
            for r in data["cogs_rows"]:
                data_x.append([r["code"], r["name"], float(r["amount"])])
            data_x.append(["", "Total COGS", float(data["total_cogs"])])
            data_x.append(["", "Gross Profit", float(data["gross_profit"])])
            data_x.append(["", "", ""])
        data_x.append(["", "EXPENSES", ""])
        for r in data["expense_rows"]:
            data_x.append([r["code"], r["name"], float(r["amount"])])
        data_x.append(["", "Total Expenses", float(data["total_expense"])])
        data_x.append(["", "", ""])
        net_label = "NET INCOME" if data["net_income"] >= 0 else "NET LOSS"
        data_x.append(["", net_label, float(data["net_income"])])

        return render_excel(
            headers, data_x,
            filename=f"consolidated_income_{timezone.now():%Y%m%d}.xlsx",
            sheet_name="Income Statement",
            title=f"{scope_label} — Income Statement",
            subtitle=p_label,
        )

    context = {
        "data": data,
        "period_label": p_label,
        "entity_count": len(selected_slugs),
        "scope_label": scope_label,
        "querystring": _selection_querystring(request),
        "start": request.GET.get("start", ""),
        "end": request.GET.get("end", ""),
        "now": timezone.now(),
    }
    return render(request, "Consolidated/consolidated_income_statement.html", context)

# ---------------------------------------------------------------------------
# Placeholders for balance sheet / cash flow (same pattern)
# ---------------------------------------------------------------------------
@login_required
def consolidated_balance_sheet(request):
    r = _require_bishop(request, require_selection=True)
    if r:
        return r

    from decimal import Decimal
    from Report.utils import get_balance_sheet, as_at_label

    entities, selected_slugs = resolve_selected_entities(request)
    end = parse_date(request.GET.get("end"))
    p_label = as_at_label(end)

    asset_map = {}
    liability_map = {}
    equity_map = {}
    total_assets = Decimal("0")
    total_liabilities = Decimal("0")
    total_equity_accounts = Decimal("0")
    total_earnings = Decimal("0")

    for entity in entities:
        d = get_balance_sheet(entity, end)

        for row in d["asset_rows"]:
            key = row["code"]
            if key not in asset_map:
                asset_map[key] = {"code": row["code"], "name": row["name"],
                                  "amount": Decimal("0")}
            asset_map[key]["amount"] += row["amount"]

        for row in d["liability_rows"]:
            key = row["code"]
            if key not in liability_map:
                liability_map[key] = {"code": row["code"], "name": row["name"],
                                      "amount": Decimal("0")}
            liability_map[key]["amount"] += row["amount"]

        for row in d["equity_rows"]:
            key = row["code"]
            if key not in equity_map:
                equity_map[key] = {"code": row["code"], "name": row["name"],
                                   "amount": Decimal("0")}
            equity_map[key]["amount"] += row["amount"]

        total_assets += d["total_assets"]
        total_liabilities += d["total_liabilities"]
        total_equity_accounts += d["total_equity_accounts"]
        total_earnings += d["current_earnings"]

    asset_rows = sorted(asset_map.values(), key=lambda x: x["code"])
    liability_rows = sorted(liability_map.values(), key=lambda x: x["code"])
    equity_rows = sorted(equity_map.values(), key=lambda x: x["code"])

    total_equity = total_equity_accounts + total_earnings
    total_liab_eq = total_liabilities + total_equity
    balanced = total_assets == total_liab_eq

    if len(selected_slugs) == 1:
        e = entities.first()
        scope_label = (getattr(getattr(e, "config", None), "display_name", "")
                       or (e.name if e else "Parish"))
    else:
        scope_label = f"Consolidated ({len(selected_slugs)} parishes)"

    fmt = request.GET.get("format", "html")

    if fmt == "pdf":
        columns = [
            Col("Code", 15, "left"),
            Col("Account", 55, "left"),
            Col("Amount", 30, "right", currency=True),
        ]
        table_rows = [["", "ASSETS", ""]]
        for r in asset_rows:
            table_rows.append([r["code"], r["name"], r["amount"]])
        table_rows.append(["", "Total Assets", total_assets])
        table_rows.append(["", "", ""])
        table_rows.append(["", "LIABILITIES", ""])
        for r in liability_rows:
            table_rows.append([r["code"], r["name"], r["amount"]])
        table_rows.append(["", "Total Liabilities", total_liabilities])
        table_rows.append(["", "", ""])
        table_rows.append(["", "EQUITY", ""])
        for r in equity_rows:
            table_rows.append([r["code"], r["name"], r["amount"]])
        if total_earnings:
            table_rows.append(["", "Current Period Earnings", total_earnings])
        table_rows.append(["", "Total Equity", total_equity])
        table_rows.append(["", "", ""])
        table_rows.append(["", "TOTAL LIABILITIES & EQUITY", total_liab_eq])

        first_entity = entities.first()
        cfg = getattr(first_entity, "config", None) if first_entity else None
        pdf_bytes = build_report_pdf(
            entity=first_entity,
            entity_config=cfg,
            report_title=f"{scope_label} — Balance Sheet",
            period_label=p_label,
            columns=columns,
            rows=table_rows,
            totals=None,
            filename="consolidated_balance_sheet.pdf",
        )
        resp = HttpResponse(pdf_bytes, content_type="application/pdf")
        resp["Content-Disposition"] = (
            f'inline; filename="consolidated_bs_{timezone.now():%Y%m%d}.pdf"'
        )
        return resp

    if fmt == "excel":
        headers = ["Section", "Code", "Account", "Amount"]
        data_x = []

        data_x.append(["ASSETS", "", "", ""])
        for r in asset_rows:
            data_x.append(["", r["code"], r["name"], float(r["amount"])])
        data_x.append(["", "", "Total Assets", float(total_assets)])
        data_x.append(["", "", "", ""])

        data_x.append(["LIABILITIES", "", "", ""])
        for r in liability_rows:
            data_x.append(["", r["code"], r["name"], float(r["amount"])])
        data_x.append(["", "", "Total Liabilities", float(total_liabilities)])
        data_x.append(["", "", "", ""])

        data_x.append(["EQUITY", "", "", ""])
        for r in equity_rows:
            data_x.append(["", r["code"], r["name"], float(r["amount"])])
        if total_earnings:
            data_x.append(["", "", "Current Period Earnings", float(total_earnings)])
        data_x.append(["", "", "Total Equity", float(total_equity)])
        data_x.append(["", "", "", ""])
        data_x.append(["", "", "TOTAL LIABILITIES & EQUITY", float(total_liab_eq)])

        return render_excel(
            headers, data_x,
            filename=f"consolidated_bs_{timezone.now():%Y%m%d}.xlsx",
            sheet_name="Balance Sheet",
            title=f"{scope_label} — Balance Sheet",
            subtitle=p_label,
        )

    context = {
        "asset_rows": asset_rows,
        "liability_rows": liability_rows,
        "equity_rows": equity_rows,
        "total_assets": total_assets,
        "total_liabilities": total_liabilities,
        "total_equity_accounts": total_equity_accounts,
        "current_earnings": total_earnings,
        "total_equity": total_equity,
        "total_liab_eq": total_liab_eq,
        "balanced": balanced,
        "period_label": p_label,
        "entity_count": len(selected_slugs),
        "scope_label": scope_label,
        "querystring": _selection_querystring(request),
        "start": request.GET.get("start", ""),
        "end": request.GET.get("end", ""),
        "now": timezone.now(),
    }
    return render(request, "Consolidated/consolidated_balance_sheet.html", context)


@login_required
def consolidated_cash_flow(request):
    r = _require_bishop(request, require_selection=True)
    if r:
        return r

    from decimal import Decimal
    from Report.utils import get_cash_flow

    entities, selected_slugs = resolve_selected_entities(request)
    start = parse_date(request.GET.get("start"))
    end = parse_date(request.GET.get("end"))
    p_label = _period_label(start, end)

    total_operating = Decimal("0")
    total_investing = Decimal("0")
    total_financing = Decimal("0")
    opening = Decimal("0")
    closing = Decimal("0")
    per_entity = []

    # Collect all rows across parishes, keyed by (section, code)
    operating_map = {}
    investing_map = {}
    financing_map = {}

    for entity in entities:
        d = get_cash_flow(entity, start, end)

        per_entity.append({
            "entity": entity,
            "operating": d["total_operating"],
            "investing": d["total_investing"],
            "financing": d["total_financing"],
            "net_change": d["net_change"],
        })

        for row in d["operating"]:
            key = row["account_code"]
            if key not in operating_map:
                operating_map[key] = {
                    "code": row["account_code"],
                    "name": row["account_name"],
                    "amount": Decimal("0"),
                }
            operating_map[key]["amount"] += row["amount"]

        for row in d["investing"]:
            key = row["account_code"]
            if key not in investing_map:
                investing_map[key] = {
                    "code": row["account_code"],
                    "name": row["account_name"],
                    "amount": Decimal("0"),
                }
            investing_map[key]["amount"] += row["amount"]

        for row in d["financing"]:
            key = row["account_code"]
            if key not in financing_map:
                financing_map[key] = {
                    "code": row["account_code"],
                    "name": row["account_name"],
                    "amount": Decimal("0"),
                }
            financing_map[key]["amount"] += row["amount"]

        total_operating += d["total_operating"]
        total_investing += d["total_investing"]
        total_financing += d["total_financing"]
        opening += d["opening_cash"]
        closing += d["closing_cash"]

    operating_rows = sorted(operating_map.values(), key=lambda x: x["code"])
    investing_rows = sorted(investing_map.values(), key=lambda x: x["code"])
    financing_rows = sorted(financing_map.values(), key=lambda x: x["code"])

    net_change = total_operating + total_investing + total_financing
    reconciled = (opening + net_change) == closing

    if len(selected_slugs) == 1:
        e = entities.first()
        scope_label = (getattr(getattr(e, "config", None), "display_name", "")
                       or (e.name if e else "Parish"))
    else:
        scope_label = f"Consolidated ({len(selected_slugs)} parishes)"

    fmt = request.GET.get("format", "html")

    if fmt == "pdf":
        columns = [
            Col("Code", 15, "left"),
            Col("Account", 55, "left"),
            Col("Amount", 30, "right", currency=True),
        ]
        table_rows = [["", "OPERATING ACTIVITIES", ""]]
        for r in operating_rows:
            table_rows.append([r["code"], r["name"], r["amount"]])
        table_rows.append(["", "Net Cash from Operating Activities", total_operating])
        table_rows.append(["", "", ""])
        table_rows.append(["", "INVESTING ACTIVITIES", ""])
        for r in investing_rows:
            table_rows.append([r["code"], r["name"], r["amount"]])
        table_rows.append(["", "Net Cash from Investing Activities", total_investing])
        table_rows.append(["", "", ""])
        table_rows.append(["", "FINANCING ACTIVITIES", ""])
        for r in financing_rows:
            table_rows.append([r["code"], r["name"], r["amount"]])
        table_rows.append(["", "Net Cash from Financing Activities", total_financing])
        table_rows.append(["", "", ""])
        table_rows.append(["", "Net Change in Cash", net_change])
        table_rows.append(["", "Opening Cash Balance", opening])
        table_rows.append(["", "Closing Cash Balance", closing])

        first_entity = entities.first()
        cfg = getattr(first_entity, "config", None) if first_entity else None
        pdf_bytes = build_report_pdf(
            entity=first_entity,
            entity_config=cfg,
            report_title=f"{scope_label} — Cash Flow Statement",
            period_label=p_label,
            columns=columns,
            rows=table_rows,
            totals=None,
            filename="consolidated_cash_flow.pdf",
        )
        resp = HttpResponse(pdf_bytes, content_type="application/pdf")
        resp["Content-Disposition"] = (
            f'inline; filename="consolidated_cf_{timezone.now():%Y%m%d}.pdf"'
        )
        return resp

    if fmt == "excel":
        headers = ["Section", "Code", "Account", "Amount"]
        data_x = []

        data_x.append(["Operating", "", "OPERATING ACTIVITIES", ""])
        for r in operating_rows:
            data_x.append(["", r["code"], r["name"], float(r["amount"])])
        data_x.append(["", "", "Net Cash from Operating", float(total_operating)])
        data_x.append(["", "", "", ""])

        data_x.append(["Investing", "", "INVESTING ACTIVITIES", ""])
        for r in investing_rows:
            data_x.append(["", r["code"], r["name"], float(r["amount"])])
        data_x.append(["", "", "Net Cash from Investing", float(total_investing)])
        data_x.append(["", "", "", ""])

        data_x.append(["Financing", "", "FINANCING ACTIVITIES", ""])
        for r in financing_rows:
            data_x.append(["", r["code"], r["name"], float(r["amount"])])
        data_x.append(["", "", "Net Cash from Financing", float(total_financing)])
        data_x.append(["", "", "", ""])

        data_x.append(["", "", "Net Change in Cash", float(net_change)])
        data_x.append(["", "", "Opening Cash", float(opening)])
        data_x.append(["", "", "Closing Cash", float(closing)])

        return render_excel(
            headers, data_x,
            filename=f"consolidated_cf_{timezone.now():%Y%m%d}.xlsx",
            sheet_name="Cash Flow",
            title=f"{scope_label} — Cash Flow",
            subtitle=p_label,
        )

    context = {
        "operating_rows": operating_rows,
        "investing_rows": investing_rows,
        "financing_rows": financing_rows,
        "total_operating": total_operating,
        "total_investing": total_investing,
        "total_financing": total_financing,
        "net_change": net_change,
        "opening_cash": opening,
        "closing_cash": closing,
        "reconciled": reconciled,
        "period_label": p_label,
        "entity_count": len(selected_slugs),
        "scope_label": scope_label,
        "querystring": _selection_querystring(request),
        "start": request.GET.get("start", ""),
        "end": request.GET.get("end", ""),
        "now": timezone.now(),
    }
    return render(request, "Consolidated/consolidated_cash_flow.html", context)
# ---------------------------------------------------------------------------
# Portal (choose a single parish)
# ---------------------------------------------------------------------------
@login_required
def super_admin_portal(request):
    r = _require_bishop(request)
    if r:
        return r
    entities = get_church_entities()
    root = EntityModel.objects.filter(depth=1).first()
    return render(
        request,
        "Consolidated/portal.html",
        {
            "entities": entities,
            "all_entities": entities,  # ← add: match the template's expectation
            "root_entity": root,
        },
    )


@login_required
def select_context(request):
    """Screen 1 — pick a parish or Consolidated."""
    if not _is_bishop(request.user):
        # Non-bishop users skip the select screen
        return redirect("after_login_redirect")

    entities = get_church_entities()
    return render(request, "Consolidated/select.html", {"entities": entities})


@login_required
def set_context(request, slug):
    """Record the choice in session, then redirect to reports home."""
    if not _is_bishop(request.user):
        return redirect("after_login_redirect")

    if slug == "consolidated":
        request.session["current_entity_slug"] = None
        request.session["consolidated_mode"] = True
    else:
        entity = get_object_or_404(EntityModel, slug=slug)
        request.session["current_entity_slug"] = entity.slug
        request.session["consolidated_mode"] = False

    return redirect("Consolidated:reports_home")


@login_required
def set_context_bulk(request):
    if request.method != "POST":
        return redirect("Consolidated:select_context")

    if not _is_bishop(request.user):
        return redirect("after_login_redirect")

    selection = request.POST.get("selection", "").strip()

    if selection == "consolidated":
        request.session["current_entity_slug"] = None
        request.session["consolidated_mode"] = True
    elif selection:
        entity = get_object_or_404(EntityModel, slug=selection)
        request.session["current_entity_slug"] = entity.slug
        request.session["consolidated_mode"] = False
    else:
        messages.error(request, "Please select a parish or Consolidated.")
        return redirect("Consolidated:select_context")

    return redirect("Consolidated:reports_home")


## ==============================Consolidated Reports =============================


@login_required
def reports_home(request):
    """Landing page for the bishop — tiles linking to every consolidated report."""
    r = _require_bishop(request, require_selection=True)
    if r:
        return r

    # Read current selection from session (set by the select screen)
    current_entity = None
    consolidated_mode = request.session.get("consolidated_mode", False)
    slug = request.session.get("current_entity_slug")

    if slug:
        try:
            from django_ledger.models import EntityModel

            current_entity = EntityModel.objects.get(slug=slug)
        except Exception:
            current_entity = None

    entities, selected_slugs = resolve_selected_entities(request)

    return render(
        request,
        "Consolidated/reports_home.html",
        {
            "current_entity": current_entity,
            "consolidated_mode": consolidated_mode,
            "entity_count": entities.count(),
            "selected_count": len(selected_slugs),
        },
    )


@login_required
def report_members(request):
    r = _require_bishop(request, require_selection=True)
    if r:
        return r

    from ChurchApp.models import Member

    entities, selected_slugs = resolve_selected_entities(request)

    qs = (
        Member.objects.filter(entity__in=entities, is_deleted=False)
        .select_related("entity")
        .order_by("last_name", "first_name")
    )

    search = request.GET.get("q", "").strip()
    if search:
        qs = qs.filter(
            Q(id__icontains=search)
            | Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
            | Q(other_names__icontains=search)
            | Q(telephone1__icontains=search)
            | Q(telephone2__icontains=search)
        )

    members = list(qs)

    # ---------- Whole-list PDF ----------
    fmt = request.GET.get("format", "html")

    if fmt == "pdf":
        columns = [
            Col("No", 6, "left"),
            Col("Full Name", 20, "left"),
            Col("Telephone", 13, "left"),
            Col("Date of Birth", 12, "left"),
            Col("Baptised", 12, "left"),
            Col("Confirmed", 12, "left"),
            Col("Res. Address", 25, "left"),
        ]
        rows = [
            [
                i,
                m.full_name or f"{m.last_name or ''} {m.first_name or ''}".strip(),
                m.telephone1 or "",
                m.date_of_birth.strftime("%d/%m/%Y") if m.date_of_birth else "",
                m.date_baptised.strftime("%d/%m/%Y") if m.date_baptised else "",
                m.date_confirmed.strftime("%d/%m/%Y") if m.date_confirmed else "",
                m.res_address or "",
            ]
            for i, m in enumerate(members, start=1)
        ]

        first_entity = entities.first()
        cfg = getattr(first_entity, "config", None) if first_entity else None

        pdf_bytes = build_report_pdf(
            entity=first_entity,
            entity_config=cfg,
            report_title="Consolidated Members List",
            period_label=f"{len(members)} members across {entities.count()} parishes",
            columns=columns,
            rows=rows,
            totals=None,
            filename="consolidated_members.pdf",
            landscape_mode=True,
        )
        resp = HttpResponse(pdf_bytes, content_type="application/pdf")
        resp["Content-Disposition"] = 'inline; filename="consolidated_members.pdf"'
        return resp

    # ---------- Whole-list Excel (all fields) ----------
    if fmt == "excel":
        headers = [
            "No",
            "Parish",
            "Member ID",
            "Title",
            "First Name",
            "Other Names",
            "Last Name",
            "Full Name",
            "Email",
            "Telephone 1",
            "Telephone 2",
            "Ghana Card",
            "Date of Birth",
            "Date Baptised",
            "Date Confirmed",
            "Date Enrolled",
            "Date Expired",
            "Education",
            "Profession",
            "Postal Address",
            "Res. Address",
            "Near Landmark",
            "Father Name",
            "Mother Name",
            "Total Tithe",
            "Total Dues",
        ]
        data = []
        for i, m in enumerate(members, start=1):
            data.append(
                [
                    i,
                    m.entity.name,
                    m.id,
                    m.get_title_display() if m.title else "",
                    m.first_name or "",
                    m.other_names or "",
                    m.last_name or "",
                    m.full_name or "",
                    m.email or "",
                    m.telephone1 or "",
                    m.telephone2 or "",
                    m.ghana_card_no or "",
                    m.date_of_birth.strftime("%d/%m/%Y") if m.date_of_birth else "",
                    m.date_baptised.strftime("%d/%m/%Y") if m.date_baptised else "",
                    m.date_confirmed.strftime("%d/%m/%Y") if m.date_confirmed else "",
                    m.date_enrolled.strftime("%d/%m/%Y") if m.date_enrolled else "",
                    m.date_expired.strftime("%d/%m/%Y") if m.date_expired else "",
                    m.get_education_level_display() if m.education_level else "",
                    m.profession or "",
                    m.postal_address or "",
                    m.res_address or "",
                    m.near_landmark or "",
                    m.father_name or "",
                    m.mother_name or "",
                    float(m.tot_tithe or 0),
                    float(m.tot_dues or 0),
                ]
            )

        first_entity = entities.first()
        cfg = getattr(first_entity, "config", None) if first_entity else None

        return render_excel(
            headers,
            data,
            filename="consolidated_members.xlsx",
            sheet_name="Consolidated Members",
            title=(cfg.organization_name if cfg else "Consolidated Members"),
            subtitle=f"{len(members)} members across {entities.count()} parishes",
        )

    # ---------- HTML ----------
    return render(
        request,
        "Consolidated/reports_members.html",
        {
            "members": members,
            "search": search,
            "entity_count": entities.count(),
            "member_count": len(members),
            "selected_slugs": selected_slugs,
        },
    )


@login_required
def report_clergy(request):
    r = _require_bishop(request, require_selection=True)
    if r:
        return r

    from ChurchApp.models import Clergy

    entities, selected_slugs = resolve_selected_entities(request)

    qs = (
        Clergy.objects.filter(entity__in=entities)
        .select_related("entity")
        .order_by("last_name", "first_name")
    )

    search = request.GET.get("q", "").strip()
    if search:
        qs = qs.filter(
            Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
            | Q(other_names__icontains=search)
            | Q(full_name__icontains=search)
            | Q(telephone__icontains=search)
            | Q(clergy_type__icontains=search)
        )

    clergy_list = list(qs)

    fmt = request.GET.get("format", "html")

    # ---------- Whole-list PDF ----------
    if fmt == "pdf":
        columns = [
            Col("No", 5, "left"),
            Col("Title", 8, "left"),
            Col("Full Name", 20, "left"),
            Col("Type", 12, "left"),
            Col("Parish", 18, "left"),
            Col("Telephone", 13, "left"),
            Col("Email", 19, "left"),
            Col("Arrived", 10, "left"),
            Col("Departed", 10, "left"),
        ]
        rows = [
            [
                i,
                c.title or "",
                c.full_name or "",
                c.clergy_type or "",
                c.entity.name,
                c.telephone or "",
                c.email_address or "",
                c.date_arrived.strftime("%d/%m/%Y") if c.date_arrived else "",
                c.date_depart.strftime("%d/%m/%Y") if c.date_depart else "",
            ]
            for i, c in enumerate(clergy_list, start=1)
        ]

        first_entity = entities.first()
        cfg = getattr(first_entity, "config", None) if first_entity else None

        pdf_bytes = build_report_pdf(
            entity=first_entity,
            entity_config=cfg,
            report_title="Consolidated Clergy List",
            period_label=f"{len(clergy_list)} clergy across {entities.count()} parishes",
            columns=columns,
            rows=rows,
            totals=None,
            filename="consolidated_clergy.pdf",
            landscape_mode=True,
        )
        resp = HttpResponse(pdf_bytes, content_type="application/pdf")
        resp["Content-Disposition"] = 'inline; filename="consolidated_clergy.pdf"'
        return resp

    # ---------- Whole-list Excel ----------
    if fmt == "excel":
        headers = [
            "No",
            "Parish",
            "ID",
            "Title",
            "First Name",
            "Other Names",
            "Last Name",
            "Full Name",
            "Type",
            "Telephone",
            "Email",
            "Postal Address",
            "Res. Address",
            "Date Arrived",
            "Date Departed",
        ]
        data = []
        for i, c in enumerate(clergy_list, start=1):
            data.append(
                [
                    i,
                    c.entity.name,
                    c.id,
                    c.title or "",
                    c.first_name or "",
                    c.other_names or "",
                    c.last_name or "",
                    c.full_name or "",
                    c.clergy_type or "",
                    c.telephone or "",
                    c.email_address or "",
                    c.postal_address or "",
                    c.res_address or "",
                    c.date_arrived.strftime("%d/%m/%Y") if c.date_arrived else "",
                    c.date_depart.strftime("%d/%m/%Y") if c.date_depart else "",
                ]
            )

        first_entity = entities.first()
        cfg = getattr(first_entity, "config", None) if first_entity else None

        return render_excel(
            headers,
            data,
            filename="consolidated_clergy.xlsx",
            sheet_name="Consolidated Clergy",
            title=(cfg.organization_name if cfg else "Consolidated Clergy"),
            subtitle=f"{len(clergy_list)} clergy across {entities.count()} parishes",
        )

    return render(
        request,
        "Consolidated/reports_clergy.html",
        {
            "clergy_list": clergy_list,
            "search": search,
            "entity_count": entities.count(),
            "clergy_count": len(clergy_list),
        },
    )


@login_required
def clergy_detail(request, pk):
    """Read-only view of a single clergy member."""
    r = _require_bishop(request, require_selection=True)
    if r:
        return r

    from ChurchApp.models import Clergy

    clergy = get_object_or_404(Clergy, pk=pk)

    return render(request, "Consolidated/clergy_detail.html", {"clergy": clergy})


@login_required
def clergy_pdf(request, pk):
    """Single clergy profile as PDF."""
    r = _require_bishop(request, require_selection=True)
    if r:
        return r

    from ChurchApp.models import Clergy

    clergy = get_object_or_404(Clergy, pk=pk)

    cfg = getattr(clergy.entity, "config", None)

    columns = [
        Col("Field", 35, "left"),
        Col("Value", 65, "left"),
    ]

    fields = [
        ("Full Name", clergy.full_name or ""),
        ("Title", clergy.title or ""),
        ("Clergy Type", clergy.clergy_type or ""),
        ("Parish", clergy.entity.name),
        ("Email", clergy.email_address or ""),
        ("Telephone", clergy.telephone or ""),
        ("Postal Address", clergy.postal_address or ""),
        ("Res. Address", clergy.res_address or ""),
        (
            "Date Arrived",
            clergy.date_arrived.strftime("%d/%m/%Y") if clergy.date_arrived else "",
        ),
        (
            "Date Departed",
            clergy.date_depart.strftime("%d/%m/%Y") if clergy.date_depart else "",
        ),
    ]

    pdf_bytes = build_report_pdf(
        entity=clergy.entity,
        entity_config=cfg,
        report_title=f"Clergy Profile — {clergy.full_name}",
        period_label="",
        columns=columns,
        rows=fields,
        totals=None,
        filename=f"clergy_{clergy.pk}.pdf",
    )

    resp = HttpResponse(pdf_bytes, content_type="application/pdf")
    resp["Content-Disposition"] = f'inline; filename="clergy_{clergy.pk}.pdf"'
    return resp


@login_required
def clergy_excel(request, pk):
    """Single clergy profile as Excel."""
    r = _require_bishop(request, require_selection=True)
    if r:
        return r

    from ChurchApp.models import Clergy

    clergy = get_object_or_404(Clergy, pk=pk)

    cfg = getattr(clergy.entity, "config", None)

    rows = [
        ["Full Name", clergy.full_name or ""],
        ["Title", clergy.title or ""],
        ["Clergy Type", clergy.clergy_type or ""],
        ["Parish", clergy.entity.name],
        ["Email", clergy.email_address or ""],
        ["Telephone", clergy.telephone or ""],
        ["Postal Address", clergy.postal_address or ""],
        ["Res. Address", clergy.res_address or ""],
        [
            "Date Arrived",
            clergy.date_arrived.strftime("%d/%m/%Y") if clergy.date_arrived else "",
        ],
        [
            "Date Departed",
            clergy.date_depart.strftime("%d/%m/%Y") if clergy.date_depart else "",
        ],
    ]

    return render_excel(
        ["Field", "Value"],
        rows,
        filename=f"clergy_{clergy.pk}.xlsx",
        sheet_name="Clergy",
        title=(cfg.organization_name if cfg else "Clergy Profile"),
        subtitle=clergy.full_name or "",
    )


from decimal import Decimal


def _sum_json(j):
    """Sum a JSONField dict of amounts. Handles strings, ints, decimals."""
    if not isinstance(j, dict):
        return Decimal("0")
    total = Decimal("0")
    for v in j.values():
        try:
            total += Decimal(str(v).replace(",", "") or "0")
        except Exception:
            pass
    return total


def _service_amounts(s):
    """Return all amount groups for one service."""
    general = s.general_offertory or Decimal("0")
    dues = s.dues or Decimal("0")
    tithes = s.tithes or Decimal("0")
    day_born = s.day_born_total or _sum_json(s.day_born_offerings)
    guild = s.guild_total or _sum_json(s.guild_offerings)
    special = s.special_total or _sum_json(s.special_thank_offering)
    easter = _sum_json(s.easter_offering)
    christmas = _sum_json(s.christmas_offering)
    harvest = _sum_json(s.harvest_offering)
    other = _sum_json(s.other_collections)

    calc_total = (
        general
        + dues
        + tithes
        + day_born
        + guild
        + special
        + easter
        + christmas
        + harvest
        + other
    )

    # Prefer the stored grand_total when set
    total = s.grand_total or calc_total

    return {
        "general": general,
        "dues": dues,
        "tithes": tithes,
        "day_born": day_born,
        "guild": guild,
        "special": special,
        "easter": easter,
        "christmas": christmas,
        "harvest": harvest,
        "other": other,
        "total": total,
    }


def _clergy_names(s):
    """Return a comma-joined string of clergy on the service."""
    names = []
    for c in s.clergy.all():
        names.append(f"{c.title or ''} {c.full_name}".strip())
    return ", ".join(names) or "—"


@login_required
def report_services(request):
    r = _require_bishop(request, require_selection=True)
    if r:
        return r

    from ChurchApp.models import Service
    from Report.utils import parse_date

    entities, selected_slugs = resolve_selected_entities(request)
    start = parse_date(request.GET.get("start"))
    end = parse_date(request.GET.get("end"))

    qs = (
        Service.objects.filter(entity__in=entities)
        .select_related("entity", "officiant")
        .prefetch_related("clergy")
        .order_by("-date", "-id")
    )
    if start:
        qs = qs.filter(date__gte=start)
    if end:
        qs = qs.filter(date__lte=end)

    search = request.GET.get("q", "").strip()
    if search:
        qs = qs.filter(
            Q(name_of_service__icontains=search)
            | Q(entity__name__icontains=search)
            | Q(clergy__full_name__icontains=search)
            | Q(officiant__full_name__icontains=search)
        ).distinct()

    services = list(qs)

    # Aggregate totals for footer
    from decimal import Decimal

    grand = {
        k: Decimal("0")
        for k in [
            "general",
            "dues",
            "tithes",
            "day_born",
            "guild",
            "special",
            "easter",
            "christmas",
            "harvest",
            "other",
            "total",
        ]
    }
    total_attendance = 0
    total_communicants = 0
    for s in services:
        amt = _service_amounts(s)
        for k in grand:
            grand[k] += amt[k]
        total_attendance += s.attendance or 0
        total_communicants += s.communicants or 0

    fmt = request.GET.get("format", "html")

    # ---------- PDF ----------
    if fmt == "pdf":
        columns = [
            Col("No", 4, "left"),
            Col("Date", 10, "left"),
            Col("Service", 17, "left"),
            Col("Parish", 15, "left"),
            Col("Officiant", 15, "left"),
            Col("Clergy", 19, "left"),
            Col("Att.", 5, "right"),
            Col("Comm.", 6, "right"),
            Col("Posted", 5, "left"),
        ]
        rows = []
        for i, s in enumerate(services, start=1):
            rows.append(
                [
                    i,
                    s.date.strftime("%d/%m/%Y") if s.date else "",
                    s.name_of_service or "",
                    s.entity.name,
                    str(s.officiant) if s.officiant else "",
                    _clergy_names(s),
                    s.attendance or 0,
                    s.communicants or 0,
                    "Yes" if s.posted_to_ledger else "No",
                ]
            )

        first_entity = entities.first()
        cfg = getattr(first_entity, "config", None) if first_entity else None

        pdf_bytes = build_report_pdf(
            entity=first_entity,
            entity_config=cfg,
            report_title="Consolidated Services List",
            period_label=f"{len(services)} services across {entities.count()} parishes",
            columns=columns,
            rows=rows,
            totals=None,
            filename="consolidated_services.pdf",
            landscape_mode=True,
        )
        resp = HttpResponse(pdf_bytes, content_type="application/pdf")
        resp["Content-Disposition"] = 'inline; filename="consolidated_services.pdf"'
        return resp

    # ---------- Excel ----------
    if fmt == "excel":
        headers = [
            "No",
            "Date",
            "Parish",
            "Service",
            "Officiant",
            "Clergy",
            "Attendance",
            "Communicants",
            "General Offertory",
            "Dues",
            "Tithes",
            "Day Born",
            "Guild",
            "Special Thank",
            "Easter",
            "Christmas",
            "Harvest",
            "Other",
            "Total",
            "Posted to Ledger",
        ]
        data = []
        for i, s in enumerate(services, start=1):
            a = _service_amounts(s)
            data.append(
                [
                    i,
                    s.date.strftime("%d/%m/%Y") if s.date else "",
                    s.entity.name,
                    s.name_of_service or "",
                    str(s.officiant) if s.officiant else "",
                    _clergy_names(s),
                    s.attendance or 0,
                    s.communicants or 0,
                    float(a["general"]),
                    float(a["dues"]),
                    float(a["tithes"]),
                    float(a["day_born"]),
                    float(a["guild"]),
                    float(a["special"]),
                    float(a["easter"]),
                    float(a["christmas"]),
                    float(a["harvest"]),
                    float(a["other"]),
                    float(a["total"]),
                    "Yes" if s.posted_to_ledger else "No",
                ]
            )
        # Grand total
        data.append(
            [
                "",
                "",
                "",
                "TOTAL",
                "",
                "",
                total_attendance,
                total_communicants,
                float(grand["general"]),
                float(grand["dues"]),
                float(grand["tithes"]),
                float(grand["day_born"]),
                float(grand["guild"]),
                float(grand["special"]),
                float(grand["easter"]),
                float(grand["christmas"]),
                float(grand["harvest"]),
                float(grand["other"]),
                float(grand["total"]),
                "",
            ]
        )

        first_entity = entities.first()
        cfg = getattr(first_entity, "config", None) if first_entity else None

        return render_excel(
            headers,
            data,
            filename="consolidated_services.xlsx",
            sheet_name="Consolidated Services",
            title=(cfg.organization_name if cfg else "Consolidated Services"),
            subtitle=f"{len(services)} services across {entities.count()} parishes",
        )

    return render(
        request,
        "Consolidated/reports_services.html",
        {
            "services": services,
            "grand": grand,
            "total_attendance": total_attendance,
            "total_communicants": total_communicants,
            "search": search,
            "start": request.GET.get("start", ""),
            "end": request.GET.get("end", ""),
            "entity_count": entities.count(),
            "service_count": len(services),
        },
    )


@login_required
def service_detail(request, pk):
    r = _require_bishop(request, require_selection=True)
    if r:
        return r

    from ChurchApp.models import Service

    s = get_object_or_404(Service, pk=pk)

    return render(
        request,
        "Consolidated/service_detail.html",
        {
            "service": s,
            "amounts": _service_amounts(s),
        },
    )


@login_required
def service_pdf(request, pk):
    r = _require_bishop(request, require_selection=True)
    if r:
        return r

    from ChurchApp.models import Service

    s = get_object_or_404(Service, pk=pk)
    a = _service_amounts(s)
    cfg = getattr(s.entity, "config", None)

    columns = [Col("Field", 40, "left"), Col("Value", 60, "left")]
    clergy_names = (
        ", ".join(f"{c.title or ''} {c.full_name}".strip() for c in s.clergy.all())
        or "—"
    )

    fields = [
        ("Parish", s.entity.name),
        ("Date", s.date.strftime("%d/%m/%Y") if s.date else ""),
        ("Service Name", s.name_of_service or ""),
        ("Officiant", str(s.officiant) if s.officiant else ""),
        ("Priest's Warden", s.priest_warden or ""),
        ("People's Warden", s.peoples_warden or ""),
        ("Verger", s.verger or ""),
        ("Parish Clerk", s.parish_clerk or ""),
        ("Accounts Clerk", s.accounts_clerk or ""),
        ("Attendance", s.attendance or 0),
        ("Communicants", s.communicants or 0),
        ("Clergy", clergy_names),
        ("General Offertory", f"{a['general']:,.2f}"),
        ("Dues", f"{a['dues']:,.2f}"),
        ("Tithes", f"{a['tithes']:,.2f}"),
        ("Day Born", f"{a['day_born']:,.2f}"),
        ("Guild", f"{a['guild']:,.2f}"),
        ("Special Thank", f"{a['special']:,.2f}"),
        ("Easter", f"{a['easter']:,.2f}"),
        ("Christmas", f"{a['christmas']:,.2f}"),
        ("Harvest", f"{a['harvest']:,.2f}"),
        ("Other", f"{a['other']:,.2f}"),
        ("GRAND TOTAL", f"{a['total']:,.2f}"),
        ("Posted to Ledger", "Yes" if s.posted_to_ledger else "No"),
    ]

    pdf_bytes = build_report_pdf(
        entity=s.entity,
        entity_config=cfg,
        report_title="Service Details",
        period_label=s.date.strftime("%d/%m/%Y") if s.date else "",
        columns=columns,
        rows=fields,
        totals=None,
        filename=f"service_{s.pk}.pdf",
    )
    resp = HttpResponse(pdf_bytes, content_type="application/pdf")
    resp["Content-Disposition"] = f'inline; filename="service_{s.pk}.pdf"'
    return resp


@login_required
def service_excel(request, pk):
    r = _require_bishop(request, require_selection=True)
    if r:
        return r

    from ChurchApp.models import Service

    s = get_object_or_404(Service, pk=pk)
    a = _service_amounts(s)
    cfg = getattr(s.entity, "config", None)

    clergy_names = (
        ", ".join(f"{c.title or ''} {c.full_name}".strip() for c in s.clergy.all())
        or ""
    )

    rows = [
        ["Parish", s.entity.name],
        ["Date", s.date.strftime("%d/%m/%Y") if s.date else ""],
        ["Service Name", s.name_of_service or ""],
        ["Officiant", str(s.officiant) if s.officiant else ""],
        ["Priest's Warden", s.priest_warden or ""],
        ["People's Warden", s.peoples_warden or ""],
        ["Verger", s.verger or ""],
        ["Parish Clerk", s.parish_clerk or ""],
        ["Accounts Clerk", s.accounts_clerk or ""],
        ["Attendance", s.attendance or 0],
        ["Communicants", s.communicants or 0],
        ["Clergy", clergy_names],
        ["General Offertory", float(a["general"])],
        ["Dues", float(a["dues"])],
        ["Tithes", float(a["tithes"])],
        ["Day Born", float(a["day_born"])],
        ["Guild", float(a["guild"])],
        ["Special Thank", float(a["special"])],
        ["Easter", float(a["easter"])],
        ["Christmas", float(a["christmas"])],
        ["Harvest", float(a["harvest"])],
        ["Other", float(a["other"])],
        ["GRAND TOTAL", float(a["total"])],
        ["Posted to Ledger", "Yes" if s.posted_to_ledger else "No"],
    ]

    return render_excel(
        ["Field", "Value"],
        rows,
        filename=f"service_{s.pk}.xlsx",
        sheet_name="Service",
        title=(cfg.organization_name if cfg else "Service Details"),
        subtitle=s.date.strftime("%d/%m/%Y") if s.date else "",
    )


def _asset_category_name(a):
    """Safely get the category name (FK or None)."""
    if a.category:
        return getattr(a.category, "name", str(a.category))
    return "—"


def _asset_status(a):
    if not a.is_active:
        return "Disposed" if a.disposal_date else "Inactive"
    return "Active"


@login_required
def report_assets(request):
    r = _require_bishop(request, require_selection=True)
    if r:
        return r

    from FixedAssets.models import FixedAsset
    from Report.utils import parse_date

    entities, selected_slugs = resolve_selected_entities(request)
    start = parse_date(request.GET.get("start"))
    end = parse_date(request.GET.get("end"))

    qs = (
        FixedAsset.objects.filter(entity__in=entities)
        .select_related("entity", "category")
        .order_by("entity__name", "category__name", "name")
    )
    if start:
        qs = qs.filter(acquisition_date__gte=start)
    if end:
        qs = qs.filter(acquisition_date__lte=end)

    search = request.GET.get("q", "").strip()
    if search:
        qs = qs.filter(
            Q(name__icontains=search)
            | Q(asset_id__icontains=search)
            | Q(description__icontains=search)
            | Q(category__name__icontains=search)
            | Q(entity__name__icontains=search)
        )

    status = request.GET.get("status", "").strip()
    if status == "active":
        qs = qs.filter(is_active=True)
    elif status == "inactive":
        qs = qs.filter(is_active=False)

    assets = list(qs)

    # Totals
    total_cost = sum((a.cost or Decimal("0")) for a in assets)
    total_accum = sum((a.accumulated_depreciation or Decimal("0")) for a in assets)
    total_nbv = sum((a.book_value or Decimal("0")) for a in assets)

    fmt = request.GET.get("format", "html")

    # ---------- PDF ----------
    if fmt == "pdf":
        columns = [
            Col("No", 4, "left"),
            Col("Category", 12, "left"),
            Col("Asset", 20, "left"),
            Col("Code", 9, "left"),
            Col("Parish", 14, "left"),
            Col("Acquired", 10, "left"),
            Col("Cost", 10, "right"),
            Col("Acc. Dep", 10, "right"),
            Col("NBV", 11, "right"),
        ]
        rows = []
        for i, a in enumerate(assets, start=1):
            rows.append(
                [
                    i,
                    _asset_category_name(a),
                    a.name or "",
                    a.asset_id or "",
                    a.entity.name,
                    (
                        a.acquisition_date.strftime("%d/%m/%Y")
                        if a.acquisition_date
                        else ""
                    ),
                    f"{(a.cost or 0):,.2f}",
                    f"{(a.accumulated_depreciation or 0):,.2f}",
                    f"{(a.book_value or 0):,.2f}",
                ]
            )

        first_entity = entities.first()
        cfg = getattr(first_entity, "config", None) if first_entity else None

        totals = [
            "",
            "",
            "TOTAL",
            "",
            "",
            "",
            f"{total_cost:,.2f}",
            f"{total_accum:,.2f}",
            f"{total_nbv:,.2f}",
        ]

        pdf_bytes = build_report_pdf(
            entity=first_entity,
            entity_config=cfg,
            report_title="Consolidated Fixed Assets",
            period_label=f"{len(assets)} assets across {entities.count()} parishes",
            columns=columns,
            rows=rows,
            totals=totals,
            filename="consolidated_assets.pdf",
            landscape_mode=True,
        )
        resp = HttpResponse(pdf_bytes, content_type="application/pdf")
        resp["Content-Disposition"] = 'inline; filename="consolidated_assets.pdf"'
        return resp

    # ---------- Excel ----------
    if fmt == "excel":
        headers = [
            "No",
            "Parish",
            "Category",
            "Asset ID",
            "Name",
            "Description",
            "Acquisition Date",
            "Cost",
            "Salvage Value",
            "Useful Life (yrs)",
            "Depreciation Method",
            "Override Rate",
            "Accumulated Depreciation",
            "Book Value",
            "Last Depreciation Date",
            "Status",
            "Disposal Date",
        ]
        data = []
        for i, a in enumerate(assets, start=1):
            data.append(
                [
                    i,
                    a.entity.name,
                    _asset_category_name(a),
                    a.asset_id or "",
                    a.name or "",
                    a.description or "",
                    (
                        a.acquisition_date.strftime("%d/%m/%Y")
                        if a.acquisition_date
                        else ""
                    ),
                    float(a.cost or 0),
                    float(a.salvage_value or 0),
                    a.useful_life_years or 0,
                    a.depreciation_method or "",
                    float(a.override_depreciation_rate or 0),
                    float(a.accumulated_depreciation or 0),
                    float(a.book_value or 0),
                    (
                        a.last_depreciation_date.strftime("%d/%m/%Y")
                        if a.last_depreciation_date
                        else ""
                    ),
                    _asset_status(a),
                    a.disposal_date.strftime("%d/%m/%Y") if a.disposal_date else "",
                ]
            )
        data.append(
            [
                "",
                "",
                "",
                "",
                "TOTAL",
                "",
                "",
                float(total_cost),
                "",
                "",
                "",
                "",
                float(total_accum),
                float(total_nbv),
                "",
                "",
                "",
            ]
        )

        first_entity = entities.first()
        cfg = getattr(first_entity, "config", None) if first_entity else None

        return render_excel(
            headers,
            data,
            filename="consolidated_assets.xlsx",
            sheet_name="Consolidated Assets",
            title=(cfg.organization_name if cfg else "Consolidated Fixed Assets"),
            subtitle=f"{len(assets)} assets across {entities.count()} parishes",
        )

    return render(
        request,
        "Consolidated/reports_assets.html",
        {
            "assets": assets,
            "total_cost": total_cost,
            "total_accum": total_accum,
            "total_nbv": total_nbv,
            "search": search,
            "status": status,
            "start": request.GET.get("start", ""),
            "end": request.GET.get("end", ""),
            "entity_count": entities.count(),
            "asset_count": len(assets),
        },
    )


@login_required
def asset_detail(request, pk):
    r = _require_bishop(request, require_selection=True)
    if r:
        return r

    from FixedAssets.models import FixedAsset

    asset = get_object_or_404(FixedAsset, pk=pk)

    return render(request, "Consolidated/asset_detail.html", {"asset": asset})


@login_required
def asset_pdf(request, pk):
    r = _require_bishop(request, require_selection=True)
    if r:
        return r

    from FixedAssets.models import FixedAsset

    asset = get_object_or_404(FixedAsset, pk=pk)
    cfg = getattr(asset.entity, "config", None)

    columns = [Col("Field", 40, "left"), Col("Value", 60, "left")]
    fields = [
        ("Parish", asset.entity.name),
        ("Category", _asset_category_name(asset)),
        ("Asset ID", asset.asset_id or ""),
        ("Name", asset.name or ""),
        ("Description", asset.description or ""),
        (
            "Acquisition Date",
            (
                asset.acquisition_date.strftime("%d/%m/%Y")
                if asset.acquisition_date
                else ""
            ),
        ),
        ("Cost", f"{(asset.cost or 0):,.2f}"),
        ("Salvage Value", f"{(asset.salvage_value or 0):,.2f}"),
        ("Useful Life (years)", asset.useful_life_years or 0),
        ("Depreciation Method", asset.depreciation_method or ""),
        ("Override Rate", f"{(asset.override_depreciation_rate or 0):,.2f}"),
        ("Accumulated Depreciation", f"{(asset.accumulated_depreciation or 0):,.2f}"),
        ("Book Value (NBV)", f"{(asset.book_value or 0):,.2f}"),
        (
            "Last Depreciation Date",
            (
                asset.last_depreciation_date.strftime("%d/%m/%Y")
                if asset.last_depreciation_date
                else ""
            ),
        ),
        ("Status", _asset_status(asset)),
        (
            "Disposal Date",
            asset.disposal_date.strftime("%d/%m/%Y") if asset.disposal_date else "",
        ),
    ]

    pdf_bytes = build_report_pdf(
        entity=asset.entity,
        entity_config=cfg,
        report_title=f"Fixed Asset — {asset.name}",
        period_label="",
        columns=columns,
        rows=fields,
        totals=None,
        filename=f"asset_{asset.pk}.pdf",
    )
    resp = HttpResponse(pdf_bytes, content_type="application/pdf")
    resp["Content-Disposition"] = f'inline; filename="asset_{asset.pk}.pdf"'
    return resp


@login_required
def asset_excel(request, pk):
    r = _require_bishop(request, require_selection=True)
    if r:
        return r

    from FixedAssets.models import FixedAsset

    asset = get_object_or_404(FixedAsset, pk=pk)
    cfg = getattr(asset.entity, "config", None)

    rows = [
        ["Parish", asset.entity.name],
        ["Category", _asset_category_name(asset)],
        ["Asset ID", asset.asset_id or ""],
        ["Name", asset.name or ""],
        ["Description", asset.description or ""],
        [
            "Acquisition Date",
            (
                asset.acquisition_date.strftime("%d/%m/%Y")
                if asset.acquisition_date
                else ""
            ),
        ],
        ["Cost", float(asset.cost or 0)],
        ["Salvage Value", float(asset.salvage_value or 0)],
        ["Useful Life (years)", asset.useful_life_years or 0],
        ["Depreciation Method", asset.depreciation_method or ""],
        ["Override Rate", float(asset.override_depreciation_rate or 0)],
        ["Accumulated Depreciation", float(asset.accumulated_depreciation or 0)],
        ["Book Value (NBV)", float(asset.book_value or 0)],
        [
            "Last Depreciation Date",
            (
                asset.last_depreciation_date.strftime("%d/%m/%Y")
                if asset.last_depreciation_date
                else ""
            ),
        ],
        ["Status", _asset_status(asset)],
        [
            "Disposal Date",
            asset.disposal_date.strftime("%d/%m/%Y") if asset.disposal_date else "",
        ],
    ]

    return render_excel(
        ["Field", "Value"],
        rows,
        filename=f"asset_{asset.pk}.xlsx",
        sheet_name="Fixed Asset",
        title=(cfg.organization_name if cfg else "Fixed Asset"),
        subtitle=asset.name or "",
    )
    def report_dues_tithe_summary(request):
        pass


@login_required
def report_dues_tithe_summary(request):
    """Summary of dues + tithes per parish."""
    r = _require_bishop(request, require_selection=True)
    if r:
        return r

    from django.db.models import Sum
    from RecPayApp.models import Trans

    entities, selected_slugs = resolve_selected_entities(request)

    rows = []
    grand_dues = 0
    grand_tithes = 0

    for entity in entities:
        qs = Trans.objects.filter(entity=entity, sub_module="dues_tithe")
        dues = qs.filter(ledger_code="4013").aggregate(s=Sum("amount"))["s"] or 0
        tithes = qs.filter(ledger_code="4014").aggregate(s=Sum("amount"))["s"] or 0
        rows.append([entity.name, float(dues), float(tithes), float(dues + tithes)])
        grand_dues += dues
        grand_tithes += tithes

    rows.append(
        [
            "TOTAL",
            float(grand_dues),
            float(grand_tithes),
            float(grand_dues + grand_tithes),
        ]
    )

    if request.GET.get("format") == "excel":
        return render_excel(
            ["Parish", "Dues", "Tithes", "Total"],
            rows,
            filename="consolidated_dues_tithe.xlsx",
            sheet_name="Dues & Tithes",
            title="Consolidated Dues & Tithes",
            subtitle=f"{len(selected_slugs)} parishes",
        )

    # Minimal HTML fallback — reuse the reports_home layout
    columns = ["Parish", "Dues", "Tithes", "Total"]
    return render(
        request,
        "Consolidated/reports_generic.html",
        {
            "title": "Consolidated Dues & Tithes",
            "columns": columns,
            "rows": rows,
            "querystring": _selection_querystring(request),
        },
    )

## ===================================Consolidated (Sum) (Bishop) Diocese======================================


@login_required
def diocese_reports_home(request):
    """Landing page for Diocese reports — all parishes, no selection."""
    r = _require_bishop(request)
    if r:
        return r

    entities = get_church_entities()

    return render(
        request,
        "Consolidated/diocese_reports_home.html",
        {
            "entity_count": entities.count(),
        },
    )


@login_required
def diocese_trial_balance(request):
    r = _require_bishop(request)
    if r:
        return r

    # Always ALL church parishes — no session filter
    entities = get_church_entities()
    start = parse_date(request.GET.get("start"))
    end = parse_date(request.GET.get("end"))

    rows, total_dr, total_cr = get_consolidated_trial_balance(entities, start, end)
    p_label = _period_label(start, end)
    balanced = total_dr == total_cr

    scope_label = f"Diocese of Accra — {entities.count()} Parishes"

    fmt = request.GET.get("format", "html")

    if fmt == "pdf":
        columns = [
            Col("Code", 12, "left"),
            Col("Account", 48, "left"),
            Col("Debit", 20, "right", currency=True),
            Col("Credit", 20, "right", currency=True),
        ]
        table_rows = [[r["code"], r["name"], r["dr"], r["cr"]] for r in rows]
        totals = ["", "Totals", total_dr, total_cr]

        first_entity = entities.first()
        cfg = getattr(first_entity, "config", None) if first_entity else None
        pdf_bytes = build_report_pdf(
            entity=first_entity,
            entity_config=cfg,
            report_title="Bishop's Trial Balance — Diocese Total",
            period_label=p_label,
            columns=columns,
            rows=table_rows,
            totals=totals,
            filename="bishop_trial_balance.pdf",
        )
        resp = HttpResponse(pdf_bytes, content_type="application/pdf")
        resp["Content-Disposition"] = (
            f'inline; filename="bishop_tb_{timezone.now():%Y%m%d}.pdf"'
        )
        return resp

    if fmt == "excel":
        headers = ["Code", "Account", "Debit", "Credit"]
        data_x = [[r["code"], r["name"], float(r["dr"]), float(r["cr"])] for r in rows]
        data_x.append(["", "Totals", float(total_dr), float(total_cr)])
        return render_excel(
            headers, data_x,
            filename=f"bishop_tb_{timezone.now():%Y%m%d}.xlsx",
            sheet_name="Bishop TB",
            title="Bishop's Trial Balance — Diocese Total",
            subtitle=p_label,
        )

    context = {
        "rows": rows,
        "total_dr": total_dr,
        "total_cr": total_cr,
        "balanced": balanced,
        "period_label": p_label,
        "entity_count": entities.count(),
        "scope_label": scope_label,
        "querystring": _selection_querystring(request),
        "start": request.GET.get("start", ""),
        "end": request.GET.get("end", ""),
        "now": timezone.now(),
    }
    return render(request, "Consolidated/diocese_trial_balance.html", context)


@login_required
def diocese_trial_balance(request):
    r = _require_bishop(request, require_selection=True)
    if r:
        return r

    entities, selected_slugs = resolve_selected_entities(request)
    start = parse_date(request.GET.get("start"))
    end = parse_date(request.GET.get("end"))

    rows, total_dr, total_cr = get_consolidated_trial_balance(entities, start, end)
    p_label = _period_label(start, end)
    balanced = total_dr == total_cr

    if len(selected_slugs) == 1:
        e = entities.first()
        scope_label = getattr(getattr(e, "config", None), "display_name", "") or (
            e.name if e else "Parish"
        )
    else:
        scope_label = f"Consolidated ({len(selected_slugs)} parishes)"

    fmt = request.GET.get("format", "html")

    if fmt == "pdf":
        columns = [
            Col("Code", 12, "left"),
            Col("Account", 48, "left"),
            Col("Debit", 20, "right", currency=True),
            Col("Credit", 20, "right", currency=True),
        ]
        table_rows = [[r["code"], r["name"], r["dr"], r["cr"]] for r in rows]
        totals = ["", "Totals", total_dr, total_cr]

        first_entity = entities.first()
        cfg = getattr(first_entity, "config", None) if first_entity else None
        pdf_bytes = build_report_pdf(
            entity=first_entity,
            entity_config=cfg,
            report_title=f"{scope_label} — Trial Balance",
            period_label=p_label,
            columns=columns,
            rows=table_rows,
            totals=totals,
            filename="consolidated_trial_balance.pdf",
        )
        resp = HttpResponse(pdf_bytes, content_type="application/pdf")
        resp["Content-Disposition"] = (
            f'inline; filename="consolidated_tb_{timezone.now():%Y%m%d}.pdf"'
        )
        return resp

    if fmt == "excel":
        headers = ["Code", "Account", "Debit", "Credit"]
        data_x = [[r["code"], r["name"], float(r["dr"]), float(r["cr"])] for r in rows]
        data_x.append(["", "Totals", float(total_dr), float(total_cr)])
        return render_excel(
            headers,
            data_x,
            filename=f"consolidated_tb_{timezone.now():%Y%m%d}.xlsx",
            sheet_name="Trial Balance",
            title=f"{scope_label} — Trial Balance",
            subtitle=p_label,
        )

    context = {
        "rows": rows,
        "total_dr": total_dr,
        "total_cr": total_cr,
        "balanced": balanced,
        "period_label": p_label,
        "entity_count": len(selected_slugs),
        "scope_label": scope_label,
        "querystring": _selection_querystring(request),
        "start": request.GET.get("start", ""),
        "end": request.GET.get("end", ""),
        "now": timezone.now(),
    }
    return render(request, "Consolidated/diocese_trial_balance.html", context)


# ---------------------------------------------------------------------------
# Consolidated Income Statement
# ---------------------------------------------------------------------------


@login_required
def diocese_income_statement(request):
    r = _require_bishop(request, require_selection=True)
    if r:
        return r

    entities, selected_slugs = resolve_selected_entities(request)
    start = parse_date(request.GET.get("start"))
    end = parse_date(request.GET.get("end"))

    data = get_consolidated_income_statement(entities, start, end)
    p_label = _period_label(start, end)

    if len(selected_slugs) == 1:
        e = entities.first()
        scope_label = getattr(getattr(e, "config", None), "display_name", "") or (
            e.name if e else "Parish"
        )
    else:
        scope_label = f"Consolidated ({len(selected_slugs)} parishes)"

    fmt = request.GET.get("format", "html")

    if fmt == "pdf":
        columns = [
            Col("Code", 15, "left"),
            Col("Account", 55, "left"),
            Col("Amount", 30, "right", currency=True),
        ]
        table_rows = [["", "REVENUE", ""]]
        for r in data["revenue_rows"]:
            table_rows.append([r["code"], r["name"], r["amount"]])
        table_rows.append(["", "Total Revenue", data["total_revenue"]])
        table_rows.append(["", "", ""])
        if data["cogs_rows"]:
            table_rows.append(["", "COST OF GOODS SOLD", ""])
            for r in data["cogs_rows"]:
                table_rows.append([r["code"], r["name"], r["amount"]])
            table_rows.append(["", "Total COGS", data["total_cogs"]])
            table_rows.append(["", "Gross Profit", data["gross_profit"]])
            table_rows.append(["", "", ""])
        table_rows.append(["", "EXPENSES", ""])
        for r in data["expense_rows"]:
            table_rows.append([r["code"], r["name"], r["amount"]])
        table_rows.append(["", "Total Expenses", data["total_expense"]])
        table_rows.append(["", "", ""])
        net_label = "NET INCOME" if data["net_income"] >= 0 else "NET LOSS"
        table_rows.append(["", net_label, data["net_income"]])

        first_entity = entities.first()
        cfg = getattr(first_entity, "config", None) if first_entity else None
        pdf_bytes = build_report_pdf(
            entity=first_entity,
            entity_config=cfg,
            report_title=f"{scope_label} — Income Statement",
            period_label=p_label,
            columns=columns,
            rows=table_rows,
            totals=None,
            filename="consolidated_income_statement.pdf",
        )
        resp = HttpResponse(pdf_bytes, content_type="application/pdf")
        resp["Content-Disposition"] = (
            f'inline; filename="consolidated_income_{timezone.now():%Y%m%d}.pdf"'
        )
        return resp

    if fmt == "excel":
        headers = ["Code", "Account", "Amount"]
        data_x = []
        data_x.append(["", "REVENUE", ""])
        for r in data["revenue_rows"]:
            data_x.append([r["code"], r["name"], float(r["amount"])])
        data_x.append(["", "Total Revenue", float(data["total_revenue"])])
        data_x.append(["", "", ""])
        if data["cogs_rows"]:
            data_x.append(["", "COST OF GOODS SOLD", ""])
            for r in data["cogs_rows"]:
                data_x.append([r["code"], r["name"], float(r["amount"])])
            data_x.append(["", "Total COGS", float(data["total_cogs"])])
            data_x.append(["", "Gross Profit", float(data["gross_profit"])])
            data_x.append(["", "", ""])
        data_x.append(["", "EXPENSES", ""])
        for r in data["expense_rows"]:
            data_x.append([r["code"], r["name"], float(r["amount"])])
        data_x.append(["", "Total Expenses", float(data["total_expense"])])
        data_x.append(["", "", ""])
        net_label = "NET INCOME" if data["net_income"] >= 0 else "NET LOSS"
        data_x.append(["", net_label, float(data["net_income"])])

        return render_excel(
            headers,
            data_x,
            filename=f"consolidated_income_{timezone.now():%Y%m%d}.xlsx",
            sheet_name="Income Statement",
            title=f"{scope_label} — Income Statement",
            subtitle=p_label,
        )

    context = {
        "data": data,
        "period_label": p_label,
        "entity_count": len(selected_slugs),
        "scope_label": scope_label,
        "querystring": _selection_querystring(request),
        "start": request.GET.get("start", ""),
        "end": request.GET.get("end", ""),
        "now": timezone.now(),
    }
    return render(request, "Consolidated/diocese_income_statement.html", context)


# ---------------------------------------------------------------------------
# Placeholders for balance sheet / cash flow (same pattern)
# ---------------------------------------------------------------------------
@login_required
def diocese_balance_sheet(request):
    r = _require_bishop(request, require_selection=True)
    if r:
        return r

    from decimal import Decimal
    from Report.utils import get_balance_sheet, as_at_label

    entities, selected_slugs = resolve_selected_entities(request)
    end = parse_date(request.GET.get("end"))
    p_label = as_at_label(end)

    asset_map = {}
    liability_map = {}
    equity_map = {}
    total_assets = Decimal("0")
    total_liabilities = Decimal("0")
    total_equity_accounts = Decimal("0")
    total_earnings = Decimal("0")

    for entity in entities:
        d = get_balance_sheet(entity, end)

        for row in d["asset_rows"]:
            key = row["code"]
            if key not in asset_map:
                asset_map[key] = {
                    "code": row["code"],
                    "name": row["name"],
                    "amount": Decimal("0"),
                }
            asset_map[key]["amount"] += row["amount"]

        for row in d["liability_rows"]:
            key = row["code"]
            if key not in liability_map:
                liability_map[key] = {
                    "code": row["code"],
                    "name": row["name"],
                    "amount": Decimal("0"),
                }
            liability_map[key]["amount"] += row["amount"]

        for row in d["equity_rows"]:
            key = row["code"]
            if key not in equity_map:
                equity_map[key] = {
                    "code": row["code"],
                    "name": row["name"],
                    "amount": Decimal("0"),
                }
            equity_map[key]["amount"] += row["amount"]

        total_assets += d["total_assets"]
        total_liabilities += d["total_liabilities"]
        total_equity_accounts += d["total_equity_accounts"]
        total_earnings += d["current_earnings"]

    asset_rows = sorted(asset_map.values(), key=lambda x: x["code"])
    liability_rows = sorted(liability_map.values(), key=lambda x: x["code"])
    equity_rows = sorted(equity_map.values(), key=lambda x: x["code"])

    total_equity = total_equity_accounts + total_earnings
    total_liab_eq = total_liabilities + total_equity
    balanced = total_assets == total_liab_eq

    if len(selected_slugs) == 1:
        e = entities.first()
        scope_label = getattr(getattr(e, "config", None), "display_name", "") or (
            e.name if e else "Parish"
        )
    else:
        scope_label = f"Consolidated ({len(selected_slugs)} parishes)"

    fmt = request.GET.get("format", "html")

    if fmt == "pdf":
        columns = [
            Col("Code", 15, "left"),
            Col("Account", 55, "left"),
            Col("Amount", 30, "right", currency=True),
        ]
        table_rows = [["", "ASSETS", ""]]
        for r in asset_rows:
            table_rows.append([r["code"], r["name"], r["amount"]])
        table_rows.append(["", "Total Assets", total_assets])
        table_rows.append(["", "", ""])
        table_rows.append(["", "LIABILITIES", ""])
        for r in liability_rows:
            table_rows.append([r["code"], r["name"], r["amount"]])
        table_rows.append(["", "Total Liabilities", total_liabilities])
        table_rows.append(["", "", ""])
        table_rows.append(["", "EQUITY", ""])
        for r in equity_rows:
            table_rows.append([r["code"], r["name"], r["amount"]])
        if total_earnings:
            table_rows.append(["", "Current Period Earnings", total_earnings])
        table_rows.append(["", "Total Equity", total_equity])
        table_rows.append(["", "", ""])
        table_rows.append(["", "TOTAL LIABILITIES & EQUITY", total_liab_eq])

        first_entity = entities.first()
        cfg = getattr(first_entity, "config", None) if first_entity else None
        pdf_bytes = build_report_pdf(
            entity=first_entity,
            entity_config=cfg,
            report_title=f"{scope_label} — Balance Sheet",
            period_label=p_label,
            columns=columns,
            rows=table_rows,
            totals=None,
            filename="consolidated_balance_sheet.pdf",
        )
        resp = HttpResponse(pdf_bytes, content_type="application/pdf")
        resp["Content-Disposition"] = (
            f'inline; filename="consolidated_bs_{timezone.now():%Y%m%d}.pdf"'
        )
        return resp

    if fmt == "excel":
        headers = ["Section", "Code", "Account", "Amount"]
        data_x = []

        data_x.append(["ASSETS", "", "", ""])
        for r in asset_rows:
            data_x.append(["", r["code"], r["name"], float(r["amount"])])
        data_x.append(["", "", "Total Assets", float(total_assets)])
        data_x.append(["", "", "", ""])

        data_x.append(["LIABILITIES", "", "", ""])
        for r in liability_rows:
            data_x.append(["", r["code"], r["name"], float(r["amount"])])
        data_x.append(["", "", "Total Liabilities", float(total_liabilities)])
        data_x.append(["", "", "", ""])

        data_x.append(["EQUITY", "", "", ""])
        for r in equity_rows:
            data_x.append(["", r["code"], r["name"], float(r["amount"])])
        if total_earnings:
            data_x.append(["", "", "Current Period Earnings", float(total_earnings)])
        data_x.append(["", "", "Total Equity", float(total_equity)])
        data_x.append(["", "", "", ""])
        data_x.append(["", "", "TOTAL LIABILITIES & EQUITY", float(total_liab_eq)])

        return render_excel(
            headers,
            data_x,
            filename=f"consolidated_bs_{timezone.now():%Y%m%d}.xlsx",
            sheet_name="Balance Sheet",
            title=f"{scope_label} — Balance Sheet",
            subtitle=p_label,
        )

    context = {
        "asset_rows": asset_rows,
        "liability_rows": liability_rows,
        "equity_rows": equity_rows,
        "total_assets": total_assets,
        "total_liabilities": total_liabilities,
        "total_equity_accounts": total_equity_accounts,
        "current_earnings": total_earnings,
        "total_equity": total_equity,
        "total_liab_eq": total_liab_eq,
        "balanced": balanced,
        "period_label": p_label,
        "entity_count": len(selected_slugs),
        "scope_label": scope_label,
        "querystring": _selection_querystring(request),
        "start": request.GET.get("start", ""),
        "end": request.GET.get("end", ""),
        "now": timezone.now(),
    }
    return render(request, "Consolidated/diocese_balance_sheet.html", context)


@login_required
def diocese_cash_flow(request):
    r = _require_bishop(request, require_selection=True)
    if r:
        return r

    from decimal import Decimal
    from Report.utils import get_cash_flow

    entities, selected_slugs = resolve_selected_entities(request)
    start = parse_date(request.GET.get("start"))
    end = parse_date(request.GET.get("end"))
    p_label = _period_label(start, end)

    total_operating = Decimal("0")
    total_investing = Decimal("0")
    total_financing = Decimal("0")
    opening = Decimal("0")
    closing = Decimal("0")
    per_entity = []

    # Collect all rows across parishes, keyed by (section, code)
    operating_map = {}
    investing_map = {}
    financing_map = {}

    for entity in entities:
        d = get_cash_flow(entity, start, end)

        per_entity.append(
            {
                "entity": entity,
                "operating": d["total_operating"],
                "investing": d["total_investing"],
                "financing": d["total_financing"],
                "net_change": d["net_change"],
            }
        )

        for row in d["operating"]:
            key = row["account_code"]
            if key not in operating_map:
                operating_map[key] = {
                    "code": row["account_code"],
                    "name": row["account_name"],
                    "amount": Decimal("0"),
                }
            operating_map[key]["amount"] += row["amount"]

        for row in d["investing"]:
            key = row["account_code"]
            if key not in investing_map:
                investing_map[key] = {
                    "code": row["account_code"],
                    "name": row["account_name"],
                    "amount": Decimal("0"),
                }
            investing_map[key]["amount"] += row["amount"]

        for row in d["financing"]:
            key = row["account_code"]
            if key not in financing_map:
                financing_map[key] = {
                    "code": row["account_code"],
                    "name": row["account_name"],
                    "amount": Decimal("0"),
                }
            financing_map[key]["amount"] += row["amount"]

        total_operating += d["total_operating"]
        total_investing += d["total_investing"]
        total_financing += d["total_financing"]
        opening += d["opening_cash"]
        closing += d["closing_cash"]

    operating_rows = sorted(operating_map.values(), key=lambda x: x["code"])
    investing_rows = sorted(investing_map.values(), key=lambda x: x["code"])
    financing_rows = sorted(financing_map.values(), key=lambda x: x["code"])

    net_change = total_operating + total_investing + total_financing
    reconciled = (opening + net_change) == closing

    if len(selected_slugs) == 1:
        e = entities.first()
        scope_label = getattr(getattr(e, "config", None), "display_name", "") or (
            e.name if e else "Parish"
        )
    else:
        scope_label = f"Consolidated ({len(selected_slugs)} parishes)"

    fmt = request.GET.get("format", "html")

    if fmt == "pdf":
        columns = [
            Col("Code", 15, "left"),
            Col("Account", 55, "left"),
            Col("Amount", 30, "right", currency=True),
        ]
        table_rows = [["", "OPERATING ACTIVITIES", ""]]
        for r in operating_rows:
            table_rows.append([r["code"], r["name"], r["amount"]])
        table_rows.append(["", "Net Cash from Operating Activities", total_operating])
        table_rows.append(["", "", ""])
        table_rows.append(["", "INVESTING ACTIVITIES", ""])
        for r in investing_rows:
            table_rows.append([r["code"], r["name"], r["amount"]])
        table_rows.append(["", "Net Cash from Investing Activities", total_investing])
        table_rows.append(["", "", ""])
        table_rows.append(["", "FINANCING ACTIVITIES", ""])
        for r in financing_rows:
            table_rows.append([r["code"], r["name"], r["amount"]])
        table_rows.append(["", "Net Cash from Financing Activities", total_financing])
        table_rows.append(["", "", ""])
        table_rows.append(["", "Net Change in Cash", net_change])
        table_rows.append(["", "Opening Cash Balance", opening])
        table_rows.append(["", "Closing Cash Balance", closing])

        first_entity = entities.first()
        cfg = getattr(first_entity, "config", None) if first_entity else None
        pdf_bytes = build_report_pdf(
            entity=first_entity,
            entity_config=cfg,
            report_title=f"{scope_label} — Cash Flow Statement",
            period_label=p_label,
            columns=columns,
            rows=table_rows,
            totals=None,
            filename="consolidated_cash_flow.pdf",
        )
        resp = HttpResponse(pdf_bytes, content_type="application/pdf")
        resp["Content-Disposition"] = (
            f'inline; filename="consolidated_cf_{timezone.now():%Y%m%d}.pdf"'
        )
        return resp

    if fmt == "excel":
        headers = ["Section", "Code", "Account", "Amount"]
        data_x = []

        data_x.append(["Operating", "", "OPERATING ACTIVITIES", ""])
        for r in operating_rows:
            data_x.append(["", r["code"], r["name"], float(r["amount"])])
        data_x.append(["", "", "Net Cash from Operating", float(total_operating)])
        data_x.append(["", "", "", ""])

        data_x.append(["Investing", "", "INVESTING ACTIVITIES", ""])
        for r in investing_rows:
            data_x.append(["", r["code"], r["name"], float(r["amount"])])
        data_x.append(["", "", "Net Cash from Investing", float(total_investing)])
        data_x.append(["", "", "", ""])

        data_x.append(["Financing", "", "FINANCING ACTIVITIES", ""])
        for r in financing_rows:
            data_x.append(["", r["code"], r["name"], float(r["amount"])])
        data_x.append(["", "", "Net Cash from Financing", float(total_financing)])
        data_x.append(["", "", "", ""])

        data_x.append(["", "", "Net Change in Cash", float(net_change)])
        data_x.append(["", "", "Opening Cash", float(opening)])
        data_x.append(["", "", "Closing Cash", float(closing)])

        return render_excel(
            headers,
            data_x,
            filename=f"consolidated_cf_{timezone.now():%Y%m%d}.xlsx",
            sheet_name="Cash Flow",
            title=f"{scope_label} — Cash Flow",
            subtitle=p_label,
        )

    context = {
        "operating_rows": operating_rows,
        "investing_rows": investing_rows,
        "financing_rows": financing_rows,
        "total_operating": total_operating,
        "total_investing": total_investing,
        "total_financing": total_financing,
        "net_change": net_change,
        "opening_cash": opening,
        "closing_cash": closing,
        "reconciled": reconciled,
        "period_label": p_label,
        "entity_count": len(selected_slugs),
        "scope_label": scope_label,
        "querystring": _selection_querystring(request),
        "start": request.GET.get("start", ""),
        "end": request.GET.get("end", ""),
        "now": timezone.now(),
    }
    return render(request, "Consolidated/diocese_cash_flow.html", context)
