from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django_ledger.models import EntityModel

from .pdf_builder import Col, build_report_pdf

from .utils import (
    as_at_label,
    clean_querystring,
    for_period_label,
    get_balance_sheet,
    get_income_statement,
    get_journal_list,
    get_trial_balance,
    get_cash_flow,
    parse_date,
    period_label,
    render_excel,
    get_trans_records,
    get_journal_records,
    get_dashboard_data,
)

@login_required
def finance_reports(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    return render(request, 'Report/finance_reports.html', {"entity": entity})


@login_required
def report_index(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    return render(request, "Report/index.html", {"entity": entity})


@login_required
def trial_balance(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    cfg = getattr(entity, "config", None)

    start = parse_date(request.GET.get("start"))
    end = parse_date(request.GET.get("end"))

    rows, total_dr, total_cr = get_trial_balance(entity, start, end)
    p_label = as_at_label(end)

    ctx = {
        "entity": entity,
        "rows": rows,
        "total_dr": total_dr,
        "total_cr": total_cr,
        "balanced": total_dr == total_cr,
        "start": request.GET.get("start", ""),
        "end": request.GET.get("end", ""),
        "period_label": p_label,
        "querystring": clean_querystring(request),
        "now": timezone.now(),
    }

    fmt = request.GET.get("format", "html")

    # ---------- PDF ----------
    if fmt == "pdf":
        columns = [
            Col("Code", 10, "left"),
            Col("Account", 55, "left"),
            Col("Debit", 17.5, "right", currency=True),
            Col("Credit", 17.5, "right", currency=True),
        ]
        table_rows = [[r["code"], r["name"], r["dr"], r["cr"]] for r in rows]
        totals = ["", "Totals", total_dr, total_cr]

        pdf_bytes = build_report_pdf(
            entity=entity,
            entity_config=cfg,
            report_title="Trial Balance",
            period_label=p_label,                  # ← "as at 30/09/2026"
            columns=columns,
            rows=table_rows,
            totals=totals,
            filename=f"trial_balance_{entity.slug}.pdf",
        )

        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        mode = "attachment" if request.GET.get("download") == "1" else "inline"
        response["Content-Disposition"] = (
            f'{mode}; filename="trial_balance_{entity.slug}_{timezone.now():%Y%m%d}.pdf"'
        )
        return response

    # ---------- Excel ----------
    if fmt == "excel":
        headers = ["Code", "Account", "Balance Type", "Debit", "Credit", "Balance"]
        data = [
            [
                r["code"],
                r["name"],
                r["balance_type"],
                float(r["dr"]),
                float(r["cr"]),
                float(r["balance"]),
            ]
            for r in rows
        ]
        data.append(["", "Totals", "", float(total_dr), float(total_cr), ""])
        return render_excel(
            headers,
            data,
            filename=f"trial_balance_{entity.slug}_{timezone.now():%Y%m%d}.xlsx",
            sheet_name="Trial Balance",
            title=(cfg.organization_name if cfg else ""),
            subtitle=f"Trial Balance {p_label} — {entity.name}",
        )

    # ---------- HTML ----------
    return render(request, "Report/trial_balance.html", ctx)


@login_required
def journal_list(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    cfg = getattr(entity, "config", None)

    start = parse_date(request.GET.get("start"))
    end = parse_date(request.GET.get("end"))

    lines, total_dr, total_cr = get_journal_list(entity, start, end)
    p_label = for_period_label(start, end)

    ctx = {
        "entity": entity,
        "lines": lines,
        "total_dr": total_dr,
        "total_cr": total_cr,
        "balanced": total_dr == total_cr,
        "start": request.GET.get("start", ""),
        "end": request.GET.get("end", ""),
        "period_label": p_label,
        "querystring": clean_querystring(request),
        "now": timezone.now(),
    }

    fmt = request.GET.get("format", "html")

    # ---------- PDF ----------
    if fmt == "pdf":
        columns = [
            Col("Date", 9, "left"),
            Col("Ref", 13, "left"),
            Col("Code", 7, "left"),
            Col("Account", 20, "left"),
            Col("Description", 23, "left"),
            Col("Debit", 14, "right", currency=True),
            Col("Credit", 14, "right", currency=True),
        ]
        table_rows = [
            [
                ln["date"].strftime("%d/%m/%y"),
                ln["je_number"],
                ln["account_code"],
                ln["account_name"],
                ln["description"],
                ln["dr"] or "",
                ln["cr"] or "",
            ]
            for ln in lines
        ]
        totals = ["", "", "", "", "Totals", total_dr, total_cr]

        pdf_bytes = build_report_pdf(
            entity=entity,
            entity_config=cfg,
            report_title="Journal List",
            period_label=p_label,
            columns=columns,
            rows=table_rows,
            totals=totals,
            filename=f"journal_list_{entity.slug}.pdf",
            landscape_mode=True,
        )
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        mode = "attachment" if request.GET.get("download") == "1" else "inline"
        response["Content-Disposition"] = (
            f'{mode}; filename="journal_list_{entity.slug}_{timezone.now():%Y%m%d}.pdf"'
        )
        return response

    # ---------- Excel ----------
    if fmt == "excel":
        headers = [
            "Date",
            "JE No.",
            "Account Code",
            "Account Name",
            "Description",
            "Debit",
            "Credit",
            "Type",
            "JE UUID",
        ]
        data = [
            [
                ln["date"].strftime("%d/%m/%Y"),
                ln["je_number"],
                ln["account_code"],
                ln["account_name"],
                ln["description"],
                float(ln["dr"]) if ln["dr"] else "",
                float(ln["cr"]) if ln["cr"] else "",
                "Debit" if ln["is_debit"] else "Credit",
                ln["je_uuid"],
            ]
            for ln in lines
        ]
        data.append(
            ["", "", "", "", "Totals", float(total_dr), float(total_cr), "", ""]
        )
        return render_excel(
            headers,
            data,
            filename=f"journal_list_{entity.slug}_{timezone.now():%Y%m%d}.xlsx",
            sheet_name="Journal List",
            title=(cfg.organization_name if cfg else ""),
            subtitle=f"Journal List {p_label} — {entity.name}",
        )

    return render(request, "Report/journal_list.html", ctx)


@login_required
def income_statement(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    cfg = getattr(entity, "config", None)

    start = parse_date(request.GET.get("start"))
    end = parse_date(request.GET.get("end"))

    data = get_income_statement(entity, start, end)
    p_label = for_period_label(start, end)

    ctx = {
        "entity": entity,
        "data": data,
        "start": request.GET.get("start", ""),
        "end": request.GET.get("end", ""),
        "period_label": p_label,
        "querystring": clean_querystring(request),
        "now": timezone.now(),
    }

    fmt = request.GET.get("format", "html")

    # ---------- PDF ----------
    if fmt == "pdf":
        columns = [
            Col("Code", 15, "left"),
            Col("Account", 55, "left"),
            Col("Amount", 30, "right", currency=True),
        ]

        table_rows = []

        # Revenue section
        table_rows.append(["", "REVENUE", ""])
        for r in data["revenue_rows"]:
            table_rows.append([r["code"], r["name"], r["amount"]])
        table_rows.append(["", "Total Revenue", data["total_revenue"]])
        table_rows.append(["", "", ""])

        # COGS section (only if any)
        if data["cogs_rows"]:
            table_rows.append(["", "COST OF GOODS SOLD", ""])
            for r in data["cogs_rows"]:
                table_rows.append([r["code"], r["name"], r["amount"]])
            table_rows.append(["", "Total Cost of Goods Sold", data["total_cogs"]])
            table_rows.append(["", "Gross Profit", data["gross_profit"]])
            table_rows.append(["", "", ""])

        # Expense section
        table_rows.append(["", "EXPENSES", ""])
        for r in data["expense_rows"]:
            table_rows.append([r["code"], r["name"], r["amount"]])
        table_rows.append(["", "Total Expenses", data["total_expense"]])
        table_rows.append(["", "", ""])

        # Net income
        net_label = "NET INCOME" if data["net_income"] >= 0 else "NET LOSS"
        table_rows.append(["", net_label, data["net_income"]])

        # No totals row — sections already have their own
        pdf_bytes = build_report_pdf(
            entity=entity,
            entity_config=cfg,
            report_title="Income Statement",
            period_label=p_label,
            columns=columns,
            rows=table_rows,
            totals=None,
            filename=f"income_statement_{entity.slug}.pdf",
        )
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        mode = "attachment" if request.GET.get("download") == "1" else "inline"
        response["Content-Disposition"] = (
            f'{mode}; filename="income_statement_{entity.slug}_{timezone.now():%Y%m%d}.pdf"'
        )
        return response

    # ---------- Excel ----------
    if fmt == "excel":
        headers = ["Section", "Code", "Account", "Amount"]
        rows = []

        for r in data["revenue_rows"]:
            rows.append(["Revenue", r["code"], r["name"], float(r["amount"])])
        rows.append(["Revenue", "", "Total Revenue", float(data["total_revenue"])])

        if data["cogs_rows"]:
            for r in data["cogs_rows"]:
                rows.append(["COGS", r["code"], r["name"], float(r["amount"])])
            rows.append(["COGS", "", "Total COGS", float(data["total_cogs"])])
            rows.append(["", "", "Gross Profit", float(data["gross_profit"])])

        for r in data["expense_rows"]:
            rows.append(["Expense", r["code"], r["name"], float(r["amount"])])
        rows.append(["Expense", "", "Total Expenses", float(data["total_expense"])])

        net_label = "Net Income" if data["net_income"] >= 0 else "Net Loss"
        rows.append(["", "", net_label, float(data["net_income"])])

        return render_excel(
            headers,
            rows,
            filename=f"income_statement_{entity.slug}_{timezone.now():%Y%m%d}.xlsx",
            sheet_name="Income Statement",
            title=(cfg.organization_name if cfg else ""),
            subtitle=f"Income Statement {p_label} — {entity.name}",
        )

    return render(request, "Report/income_statement.html", ctx)


@login_required
def balance_sheet(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    cfg = getattr(entity, "config", None)

    end = parse_date(request.GET.get("end"))
    p_label = as_at_label(end)

    data = get_balance_sheet(entity, end)

    ctx = {
        "entity": entity,
        "data": data,
        "start": request.GET.get("start", ""),
        "end": request.GET.get("end", ""),
        "period_label": p_label,
        "querystring": clean_querystring(request),
        "now": timezone.now(),
    }

    fmt = request.GET.get("format", "html")

    # ---------- PDF ----------
    if fmt == "pdf":
        columns = [
            Col("Code", 15, "left"),
            Col("Account", 55, "left"),
            Col("Amount", 30, "right", currency=True),
        ]

        table_rows = []

        # ASSETS
        table_rows.append(["", "ASSETS", ""])
        for r in data["asset_rows"]:
            table_rows.append([r["code"], r["name"], r["amount"]])
        table_rows.append(["", "Total Assets", data["total_assets"]])
        table_rows.append(["", "", ""])

        # LIABILITIES
        table_rows.append(["", "LIABILITIES", ""])
        for r in data["liability_rows"]:
            table_rows.append([r["code"], r["name"], r["amount"]])
        table_rows.append(["", "Total Liabilities", data["total_liabilities"]])
        table_rows.append(["", "", ""])

        # EQUITY
        table_rows.append(["", "EQUITY", ""])
        for r in data["equity_rows"]:
            table_rows.append([r["code"], r["name"], r["amount"]])
        if data["current_earnings"] != 0:
            table_rows.append(["", "Current Period Earnings", data["current_earnings"]])
        table_rows.append(["", "Total Equity", data["total_equity"]])
        table_rows.append(["", "", ""])

        # LIABILITIES + EQUITY
        table_rows.append(
            ["", "TOTAL LIABILITIES & EQUITY", data["total_liabilities_equity"]]
        )

        pdf_bytes = build_report_pdf(
            entity=entity,
            entity_config=cfg,
            report_title="Balance Sheet",
            period_label=p_label,
            columns=columns,
            rows=table_rows,
            totals=None,
            filename=f"balance_sheet_{entity.slug}.pdf",
        )
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        mode = "attachment" if request.GET.get("download") == "1" else "inline"
        response["Content-Disposition"] = (
            f'{mode}; filename="balance_sheet_{entity.slug}_{timezone.now():%Y%m%d}.pdf"'
        )
        return response

    # ---------- Excel ----------
    if fmt == "excel":
        headers = ["Section", "Code", "Account", "Amount"]
        rows = []

        for r in data["asset_rows"]:
            rows.append(["Asset", r["code"], r["name"], float(r["amount"])])
        rows.append(["Asset", "", "Total Assets", float(data["total_assets"])])

        for r in data["liability_rows"]:
            rows.append(["Liability", r["code"], r["name"], float(r["amount"])])
        rows.append(
            ["Liability", "", "Total Liabilities", float(data["total_liabilities"])]
        )

        for r in data["equity_rows"]:
            rows.append(["Equity", r["code"], r["name"], float(r["amount"])])
        if data["current_earnings"] != 0:
            rows.append(
                [
                    "Equity",
                    "",
                    "Current Period Earnings",
                    float(data["current_earnings"]),
                ]
            )
        rows.append(["Equity", "", "Total Equity", float(data["total_equity"])])

        rows.append(
            [
                "",
                "",
                "Total Liabilities & Equity",
                float(data["total_liabilities_equity"]),
            ]
        )

        return render_excel(
            headers,
            rows,
            filename=f"balance_sheet_{entity.slug}_{timezone.now():%Y%m%d}.xlsx",
            sheet_name="Balance Sheet",
            title=(cfg.organization_name if cfg else ""),
            subtitle=f"Balance Sheet {p_label} — {entity.name}",
        )

    return render(request, "Report/balance_sheet.html", ctx)


@login_required
def account_details(request, slug, code):
    """Show a single account's info, current balance, and all journal lines."""
    entity = get_object_or_404(EntityModel, slug=slug)

    # Find the account in this entity's COA
    coa = entity.get_default_coa()
    account = get_object_or_404(AccountModel, coa_model=coa, code=code)

    start = parse_date(request.GET.get("start"))
    end = parse_date(request.GET.get("end"))

    qs = (
        TransactionModel.objects.filter(
            journal_entry__ledger__entity=entity,
            journal_entry__posted=True,
            account=account,
        )
        .select_related("journal_entry")
        .order_by("journal_entry__timestamp", "journal_entry__je_number")
    )
    if start:
        qs = qs.filter(journal_entry__timestamp__date__gte=start)
    if end:
        qs = qs.filter(journal_entry__timestamp__date__lte=end)

    lines = []
    run_dr = Decimal("0")
    run_cr = Decimal("0")
    for tx in qs:
        amount = tx.amount or Decimal("0")
        if tx.tx_type == "debit":
            run_dr += amount
        else:
            run_cr += amount
        lines.append(
            {
                "date": tx.journal_entry.timestamp.date(),
                "je_number": tx.journal_entry.je_number,
                "description": tx.description or tx.journal_entry.description or "",
                "dr": amount if tx.tx_type == "debit" else None,
                "cr": amount if tx.tx_type == "credit" else None,
            }
        )

    # Signed balance
    if account.balance_type == "debit":
        balance = run_dr - run_cr
    else:
        balance = run_cr - run_dr

    ctx = {
        "code": code,
        "entity": entity,
        "account": account,
        "lines": lines,
        "total_dr": run_dr,
        "total_cr": run_cr,
        "balance": balance,
        "period_label": period_label(start, end),
        "start": request.GET.get("start", ""),
        "end": request.GET.get("end", ""),
        "now": timezone.now(),
    }
    return render(request, "Report/account_details.html", ctx)


@login_required
def cash_flow(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    cfg = getattr(entity, "config", None)

    start = parse_date(request.GET.get("start"))
    end = parse_date(request.GET.get("end"))

    data = get_cash_flow(entity, start, end)
    p_label = for_period_label(start, end)

    ctx = {
        "entity": entity,
        "data": data,
        "start": request.GET.get("start", ""),
        "end": request.GET.get("end", ""),
        "period_label": p_label,
        "querystring": clean_querystring(request),
        "now": timezone.now(),
    }

    fmt = request.GET.get("format", "html")

    # ---------- PDF ----------
    if fmt == "pdf":
        columns = [
            Col("Date", 10, "left"),
            Col("Ref", 13, "left"),
            Col("Description", 47, "left"),
            Col("Amount", 30, "right", currency=True),
        ]

        table_rows = []

        def _section(title, rows, total, total_label):
            table_rows.append(["", "", title, ""])
            for e in rows:
                table_rows.append(
                    [
                        e["date"].strftime("%d/%m/%y"),
                        e["je_number"],
                        e["description"] or e["account_name"],
                        e["amount"],
                    ]
                )
            table_rows.append(["", "", total_label, total])
            table_rows.append(["", "", "", ""])

        _section(
            "OPERATING ACTIVITIES",
            data["operating"],
            data["total_operating"],
            "Net Cash from Operating Activities",
        )
        _section(
            "INVESTING ACTIVITIES",
            data["investing"],
            data["total_investing"],
            "Net Cash from Investing Activities",
        )
        _section(
            "FINANCING ACTIVITIES",
            data["financing"],
            data["total_financing"],
            "Net Cash from Financing Activities",
        )

        table_rows.append(
            ["", "", "Net Increase / (Decrease) in Cash", data["net_change"]]
        )
        table_rows.append(["", "", "Opening Cash Balance", data["opening_cash"]])
        table_rows.append(["", "", "Closing Cash Balance", data["closing_cash"]])

        pdf_bytes = build_report_pdf(
            entity=entity,
            entity_config=cfg,
            report_title="Cash Flow Statement",
            period_label=p_label,
            columns=columns,
            rows=table_rows,
            totals=None,
            filename=f"cash_flow_{entity.slug}.pdf",
        )
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        mode = "attachment" if request.GET.get("download") == "1" else "inline"
        response["Content-Disposition"] = (
            f'{mode}; filename="cash_flow_{entity.slug}_{timezone.now():%Y%m%d}.pdf"'
        )
        return response

    # ---------- Excel ----------
    if fmt == "excel":
        headers = ["Section", "Date", "JE No.", "Account", "Description", "Amount"]
        rows = []

        def _xsection(name, items):
            for e in items:
                rows.append(
                    [
                        name,
                        e["date"].strftime("%d/%m/%Y"),
                        e["je_number"],
                        f"{e['account_code']} {e['account_name']}",
                        e["description"],
                        float(e["amount"]),
                    ]
                )

        _xsection("Operating", data["operating"])
        rows.append(
            [
                "Operating",
                "",
                "",
                "",
                "Net Cash from Operations",
                float(data["total_operating"]),
            ]
        )
        _xsection("Investing", data["investing"])
        rows.append(
            [
                "Investing",
                "",
                "",
                "",
                "Net Cash from Investing",
                float(data["total_investing"]),
            ]
        )
        _xsection("Financing", data["financing"])
        rows.append(
            [
                "Financing",
                "",
                "",
                "",
                "Net Cash from Financing",
                float(data["total_financing"]),
            ]
        )

        rows.append(["", "", "", "", "Net Change in Cash", float(data["net_change"])])
        rows.append(["", "", "", "", "Opening Cash", float(data["opening_cash"])])
        rows.append(["", "", "", "", "Closing Cash", float(data["closing_cash"])])

        return render_excel(
            headers,
            rows,
            filename=f"cash_flow_{entity.slug}_{timezone.now():%Y%m%d}.xlsx",
            sheet_name="Cash Flow",
            title=(cfg.organization_name if cfg else ""),
            subtitle=f"Cash Flow {p_label} — {entity.name}",
        )

    return render(request, "Report/cash_flow.html", ctx)


@login_required
def trans_records(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    cfg = getattr(entity, "config", None)

    start = parse_date(request.GET.get("start"))
    end = parse_date(request.GET.get("end"))
    trans_type = request.GET.get("trans_type", "").strip()
    sub_module = request.GET.get("sub_module", "").strip()

    data = get_trans_records(
        entity, start, end, trans_type=trans_type or None, sub_module=sub_module or None
    )
    p_label = for_period_label(start, end)

    ctx = {
        "entity": entity,
        "data": data,
        "start": request.GET.get("start", ""),
        "end": request.GET.get("end", ""),
        "trans_type": trans_type,
        "sub_module": sub_module,
        "sub_module_choices": [
            ("", "All sub-modules"),
            ("receipts_payments", "Receipts & Payments"),
            ("dues_tithe", "Dues / Tithe"),
            ("service", "Service"),
            ("opening_balance", "Opening Balance"),
        ],
        "period_label": p_label,
        "querystring": clean_querystring(request),
        "now": timezone.now(),
    }

    fmt = request.GET.get("format", "html")

    # -------- PDF --------
    if fmt == "pdf":
        columns = [
            Col("Date", 9, "left"),
            Col("Ref", 12, "left"),
            Col("Type", 9, "left"),
            Col("Party", 18, "left"),
            Col("Code", 7, "left"),
            Col("Ledger", 18, "left"),
            Col("Mode", 8, "left"),
            Col("Amount", 19, "right", currency=True),
        ]

        table_rows = [
            [
                ln["date"].strftime("%d/%m/%y"),
                ln["rec_vou_no"] or ln["trans_no"],
                ln["trans_type"],
                ln["party"],
                ln["ledger_code"],
                ln["ledger_name"],
                ln["pay_mode"],
                ln["amount"],
            ]
            for ln in data["lines"]
        ]

        totals = [
            "",
            "",
            "",
            "",
            "",
            "",
            "Totals",
            data["total_receipts"] - data["total_payments"],
        ]

        pdf_bytes = build_report_pdf(
            entity=entity,
            entity_config=cfg,
            report_title="Transaction Records",
            period_label=p_label,
            columns=columns,
            rows=table_rows,
            totals=totals,
            filename=f"trans_records_{entity.slug}.pdf",
            landscape_mode=True,
        )
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        mode = "attachment" if request.GET.get("download") == "1" else "inline"
        response["Content-Disposition"] = (
            f'{mode}; filename="trans_records_{entity.slug}_{timezone.now():%Y%m%d}.pdf"'
        )
        return response

    # -------- Excel --------
    if fmt == "excel":
        headers = [
            "ID",
            "Date",
            "Trans No",
            "Ref",
            "Type",
            "Module",
            "Sub-module",
            "Party",
            "Ledger Code",
            "Ledger Name",
            "Purpose",
            "Details",
            "Pay Mode",
            "Amount",
            "Journal Status",
            "JE UUID",
        ]
        rows = [
            [
                ln["id"],
                ln["date"].strftime("%d/%m/%Y"),
                ln["trans_no"],
                ln["rec_vou_no"],
                ln["trans_type"],
                ln["module"],
                ln["sub_module"],
                ln["party"],
                ln["ledger_code"],
                ln["ledger_name"],
                ln["purpose"],
                ln["details"],
                ln["pay_mode"],
                float(ln["amount"]),
                ln["journal_status"],
                ln["journal_entry_id"],
            ]
            for ln in data["lines"]
        ]
        rows.append(
            [
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "Totals",
                float(data["total_receipts"] - data["total_payments"]),
                "",
                "",
            ]
        )

        return render_excel(
            headers,
            rows,
            filename=f"trans_records_{entity.slug}_{timezone.now():%Y%m%d}.xlsx",
            sheet_name="Trans Records",
            title=(cfg.organization_name if cfg else ""),
            subtitle=f"Transaction Records {p_label} — {entity.name}",
        )

    return render(request, "Report/trans_records.html", ctx)


@login_required
def journal_records(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    cfg = getattr(entity, "config", None)

    start = parse_date(request.GET.get("start"))
    end = parse_date(request.GET.get("end"))
    account_query = request.GET.get("account", "").strip()

    data = get_journal_records(entity, start, end, account_query=account_query or None)
    p_label = for_period_label(start, end)

    ctx = {
        "entity": entity,
        "data": data,
        "start": request.GET.get("start", ""),
        "end": request.GET.get("end", ""),
        "account_query": account_query,
        "period_label": p_label,
        "querystring": clean_querystring(request),
        "now": timezone.now(),
    }

    fmt = request.GET.get("format", "html")

    # -------- PDF --------
    if fmt == "pdf":
        columns = [
            Col("Date", 9, "left"),
            Col("Ref", 13, "left"),
            Col("Code", 8, "left"),
            Col("Account", 25, "left"),
            Col("Description", 25, "left"),
            Col("Debit", 10, "right", currency=True),
            Col("Credit", 10, "right", currency=True),
        ]

        table_rows = [
            [
                ln["date"].strftime("%d/%m/%y"),
                ln["je_number"],
                ln["account_code"],
                ln["account_name"],
                ln["description"],
                ln["dr"] or "",
                ln["cr"] or "",
            ]
            for ln in data["lines"]
        ]
        totals = ["", "", "", "", "Totals", data["total_dr"], data["total_cr"]]

        pdf_bytes = build_report_pdf(
            entity=entity,
            entity_config=cfg,
            report_title="Journal Records",
            period_label=p_label,
            columns=columns,
            rows=table_rows,
            totals=totals,
            filename=f"journal_records_{entity.slug}.pdf",
            landscape_mode=True,
        )
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        mode = "attachment" if request.GET.get("download") == "1" else "inline"
        response["Content-Disposition"] = (
            f'{mode}; filename="journal_records_{entity.slug}_{timezone.now():%Y%m%d}.pdf"'
        )
        return response

    # -------- Excel --------
    if fmt == "excel":
        headers = [
            "Date",
            "JE No.",
            "Account Code",
            "Account Name",
            "Account Role",
            "Balance Type",
            "Description",
            "Debit",
            "Credit",
            "Type",
            "JE UUID",
        ]
        rows = [
            [
                ln["date"].strftime("%d/%m/%Y"),
                ln["je_number"],
                ln["account_code"],
                ln["account_name"],
                ln["account_role"],
                ln["account_balance_type"],
                ln["description"],
                float(ln["dr"]) if ln["dr"] else "",
                float(ln["cr"]) if ln["cr"] else "",
                "Debit" if ln["is_debit"] else "Credit",
                ln["je_uuid"],
            ]
            for ln in data["lines"]
        ]
        rows.append(
            [
                "",
                "",
                "",
                "",
                "",
                "",
                "Totals",
                float(data["total_dr"]),
                float(data["total_cr"]),
                "",
                "",
            ]
        )

        return render_excel(
            headers,
            rows,
            filename=f"journal_records_{entity.slug}_{timezone.now():%Y%m%d}.xlsx",
            sheet_name="Journal Records",
            title=(cfg.organization_name if cfg else ""),
            subtitle=f"Journal Records {p_label} — {entity.name}",
        )

    return render(request, "Report/journal_records.html", ctx)


@login_required
def finance_dashboard(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    cfg = getattr(entity, "config", None)

    start = parse_date(request.GET.get("start"))
    end = parse_date(request.GET.get("end"))

    data = get_dashboard_data(entity, start, end)
    p_label = for_period_label(start, end)

    return render(
        request,
        "Report/finance_dashboard.html",
        {
            "entity": entity,
            "data": data,
            "start": request.GET.get("start", ""),
            "end": request.GET.get("end", ""),
            "period_label": p_label,
            "querystring": clean_querystring(request),
            "now": timezone.now(),
        },
    )
