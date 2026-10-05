from django.contrib.auth.decorators import login_required
from . models import  OpeningBalanceLine
from FinanceApp.models import GeneralLedger
from coa.models import ChartOfAccounts
from django.utils import timezone
from decimal import Decimal
from . forms import OpeningBalanceLineForm

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django_ledger.models import EntityModel, AccountModel
from RecPayApp.models import Trans

from django.db import transaction
from RecPayApp.models import Trans
from .models import OpeningBalanceLine

from djan_led.utils import get_visible_accounts
from django.core.paginator import Paginator


import json
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django_ledger.models import EntityModel, AccountModel
from RecPayApp.models import Trans


from djan_led.utils import get_visible_accounts

# Create your views here.

@login_required
def open_bal_home(request, slug):
    return render(request, 'OpenBals/open_bal_home.html')

@login_required
@staff_member_required
def open_bal_list(request, slug):
    """
    List all opening balance lines with filters and totals.
    """
    entity = get_object_or_404(EntityModel, slug=slug)

    # Base queryset
    lines = (
        OpeningBalanceLine.objects.filter(entity=entity)
        .select_related("account_code", "trans", "created_by")
        .order_by("-date", "account_code")
    )

    # Filters
    search = request.GET.get("search", "").strip()
    start_date = request.GET.get("start", "").strip()
    end_date = request.GET.get("end", "").strip()
    status_filter = request.GET.get("status", "").strip()

    if search:
        lines = lines.filter(
            models.Q(account_code__icontains=search)
            | models.Q(account_name__icontains=search)
            | models.Q(description__icontains=search)
        )

    if start_date:
        lines = lines.filter(date__gte=start_date)
    if end_date:
        lines = lines.filter(date__lte=end_date)

    if status_filter == "pending":
        lines = lines.filter(trans__journal_status="PENDING")
    elif status_filter == "posted":
        lines = lines.filter(trans__journal_status="POSTED")
    elif status_filter == "approved":
        lines = lines.filter(trans__journal_status="APPROVED")

    # Totals (on filtered set)
    totals = lines.aggregate(
        total_debit=models.Sum("debit_amount"),
        total_credit=models.Sum("credit_amount"),
    )
    total_debit = totals["total_debit"] or 0
    total_credit = totals["total_credit"] or 0
    difference = total_debit - total_credit

    # Pagination
    paginator = Paginator(lines, 50)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "entity": entity,
        "lines": page_obj,
        "total_debit": total_debit,
        "total_credit": total_credit,
        "difference": difference,
        "is_balanced": abs(difference) < 0.01,
        "search": search,
        "start_date": start_date,
        "end_date": end_date,
        "status_filter": status_filter,
        "total_count": lines.count(),
        "pending_count": OpeningBalanceLine.objects.filter(
            entity=entity, status="PENDING"
        ).count(),
        
    }
    return render(request, "OpenBals/open_bal_list.html", context)


@login_required
def open_bal_post_all(request, slug):
    print(">>> RUNNING NEW VERSION OF opening_balance_post_all <<<")
    entity = get_object_or_404(EntityModel, slug=slug)

    # ------------------------------------------------------------
    # GET: Show confirmation page
    # ------------------------------------------------------------
    if request.method == "GET":
        pending_count = OpeningBalanceLine.objects.filter(
            entity=entity, trans__isnull=True
        ).count()

        return render(
            request,
            "OpenBals/open_bal_confirm_post_all.html",
            {
                "entity": entity,
                "pending_count": pending_count,
            },
        )

    # ------------------------------------------------------------
    # POST: Actually post the opening balances
    # ------------------------------------------------------------
    OB_EQUITY_CODE = "3099"
    OB_EQUITY_NAME = "Opening Balance Equity"

    posted = 0
    skipped = 0

    with transaction.atomic():
        for line in OpeningBalanceLine.objects.filter(
            entity=entity, trans__isnull=True
        ):
            # `account_code` is an AccountModel FK — pull out primitives
            account = line.account_code  # AccountModel instance
            line_code = str(account.code)  # '1010'
            line_name = str(line.account_name)  # already a string: 'Cash'

            if line.debit_amount and line.debit_amount > 0:
                dr_code, dr_name = line_code, line_name
                cr_code, cr_name = OB_EQUITY_CODE, OB_EQUITY_NAME
                amount = line.debit_amount
            elif line.credit_amount and line.credit_amount > 0:
                dr_code, dr_name = OB_EQUITY_CODE, OB_EQUITY_NAME
                cr_code, cr_name = line_code, line_name
                amount = line.credit_amount
            else:
                skipped += 1
                continue

            trans = Trans.objects.create(
                entity=entity,
                module="open_balance",
                sub_module="opening_balance",
                trans_type="Journal",
                date=line.date,
                amount=amount,
                pay_mode="None",
                debit_account_code=dr_code,
                debit_account_name=dr_name,
                credit_account_code=cr_code,
                credit_account_name=cr_name,
                purpose="Opening Balance",
                details=f"OB: {line_code} {line_name}",
                journal_status="PENDING",
                status="DRAFT",
                created_by=request.user,
                created_by_name=request.user.username,
                created_by_username=request.user.username,
            )
            line.trans = trans
            line.save(update_fields=["trans"])
            posted += 1

    messages.success(request, f"Posted {posted} line(s). Skipped {skipped}.")
    return redirect("OpenBals:open_bal_list", slug=entity.slug)


# OpenBals/views.py

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side
from django.db import models


# OpenBals/views.py

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from django.http import HttpResponse
from django.utils import timezone
from django.db import models


@staff_member_required
def open_bal_pdf(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)

    lines = (
        OpeningBalanceLine.objects.filter(entity=entity, status="PENDING")
        .select_related("account_code")
        .order_by("date", "account_code__code")
    )

    totals = lines.aggregate(
        total_debit=models.Sum("debit_amount"),
        total_credit=models.Sum("credit_amount"),
    )
    total_debit = float(totals["total_debit"] or 0)
    total_credit = float(totals["total_credit"] or 0)
    difference = total_debit - total_credit
    is_balanced = abs(difference) < 0.01

    # ---- Build PDF ----
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="pending_ob_{entity.slug}.pdf"'
    )

    doc = SimpleDocTemplate(
        response,
        pagesize=landscape(A4),
        leftMargin=1.2 * cm,
        rightMargin=1.2 * cm,
        topMargin=1 * cm,
        bottomMargin=1.5 * cm,
        title="Pending Opening Balances",
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "title",
        parent=styles["Title"],
        fontSize=16,
        textColor=colors.HexColor("#1a3a6c"),
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "subtitle",
        parent=styles["Normal"],
        fontSize=10,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#666"),
        spaceAfter=10,
    )
    cell_style = ParagraphStyle("cell", fontSize=9, leading=11)
    cell_right = ParagraphStyle("cell_r", parent=cell_style, alignment=TA_RIGHT)
    header_style = ParagraphStyle("hdr", fontSize=9, textColor=colors.white, leading=11)

    story = []
    story.append(Paragraph(entity.name, title_style))
    story.append(
        Paragraph(
            f"Pending Opening Balances &nbsp;•&nbsp; {lines.count()} line(s) &nbsp;•&nbsp; "
            f"Generated {timezone.now().strftime('%Y-%m-%d %H:%M')}",
            subtitle_style,
        )
    )

    # ---- Summary table ----
    summary_data = [
        [
            Paragraph("<b>Total Debit</b>", cell_style),
            Paragraph("<b>Total Credit</b>", cell_style),
            Paragraph("<b>Difference</b>", cell_style),
            Paragraph("<b>Status</b>", cell_style),
        ],
        [
            Paragraph(f"<font color='#1e40af'>₵{total_debit:,.2f}</font>", cell_style),
            Paragraph(f"<font color='#166534'>₵{total_credit:,.2f}</font>", cell_style),
            Paragraph(f"₵{difference:,.2f}", cell_style),
            Paragraph(
                (
                    "<font color='#166534'>BALANCED</font>"
                    if is_balanced
                    else "<font color='#991b1b'>UNBALANCED</font>"
                ),
                cell_style,
            ),
        ],
    ]
    summary_table = Table(
        summary_data, colWidths=[6.2 * cm, 6.2 * cm, 6.2 * cm, 6.2 * cm]
    )
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0f4fa")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
                ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#dddddd")),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(summary_table)
    story.append(Spacer(1, 10))

    # ---- Data table ----
    header_row = [
        Paragraph("<b>#</b>", header_style),
        Paragraph("<b>Date</b>", header_style),
        Paragraph("<b>Code</b>", header_style),
        Paragraph("<b>Account</b>", header_style),
        Paragraph("<b>Debit (₵)</b>", header_style),
        Paragraph("<b>Credit (₵)</b>", header_style),
        Paragraph("<b>Description</b>", header_style),
    ]

    data = [header_row]
    for idx, line in enumerate(lines, start=1):
        data.append(
            [
                Paragraph(str(idx), cell_style),
                Paragraph(
                    line.date.strftime("%Y-%m-%d") if line.date else "", cell_style
                ),
                Paragraph(
                    line.account_code.code if line.account_code else "", cell_style
                ),
                Paragraph(line.account_name or "", cell_style),
                Paragraph(
                    f"{line.debit_amount:,.2f}" if line.debit_amount else "—",
                    cell_right,
                ),
                Paragraph(
                    f"{line.credit_amount:,.2f}" if line.credit_amount else "—",
                    cell_right,
                ),
                Paragraph(line.description or "—", cell_style),
            ]
        )

    # Totals row
    data.append(
        [
            Paragraph("<b>TOTALS</b>", cell_style),
            "",
            "",
            "",
            Paragraph(f"<b>{total_debit:,.2f}</b>", cell_right),
            Paragraph(f"<b>{total_credit:,.2f}</b>", cell_right),
            "",
        ]
    )

    col_widths = [
        1.0 * cm,  # #
        2.3 * cm,  # Date
        2.3 * cm,  # Code
        6.5 * cm,  # Account
        2.8 * cm,  # Debit
        2.8 * cm,  # Credit
        9.0 * cm,  # Description
    ]

    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                # Header
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a3a6c")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (0, 0), (-1, 0), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                # Grid
                ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#cccccc")),
                ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#666666")),
                # Padding
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                # Alignment for numeric columns
                ("ALIGN", (4, 1), (5, -1), "RIGHT"),
                ("ALIGN", (0, 1), (0, -1), "CENTER"),
                # Totals row
                ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e8eef7")),
                ("SPAN", (0, -1), (3, -1)),
            ]
        )
    )
    story.append(table)

    doc.build(story)
    return response


@staff_member_required
def open_bal_excel(request, slug):
    """Excel export of all PENDING opening balance lines."""
    entity = get_object_or_404(EntityModel, slug=slug)

    lines = (
        OpeningBalanceLine.objects.filter(entity=entity, status="PENDING")
        .select_related("account_code")
        .order_by("date", "account_code__code")
    )

    wb = Workbook()
    ws = wb.active
    ws.title = "Pending Opening Balances"

    bold = Font(bold=True)
    thin = Side(style="thin")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    right_align = Alignment(horizontal="right")
    center_align = Alignment(horizontal="center")

    # Title
    ws.merge_cells("A1:G1")
    ws["A1"] = f"{entity.name} – Pending Opening Balances"
    ws["A1"].font = Font(size=14, bold=True)
    ws["A1"].alignment = center_align

    ws.merge_cells("A2:G2")
    ws["A2"] = f"Generated: {timezone.now().strftime('%Y-%m-%d %H:%M')}"
    ws["A2"].font = Font(italic=True, color="666666")
    ws["A2"].alignment = center_align

    # Headers
    ws.append([])
    headers = ["#", "Date", "Code", "Account", "Debit (₵)", "Credit (₵)", "Description"]
    ws.append(headers)
    header_row = ws.max_row
    for cell in ws[header_row]:
        cell.font = bold
        cell.border = border
        cell.alignment = center_align

    # Data rows
    for idx, line in enumerate(lines, start=1):
        ws.append(
            [
                idx,
                line.date.strftime("%Y-%m-%d") if line.date else "",
                line.account_code.code if line.account_code else "",
                line.account_name or "",
                float(line.debit_amount) if line.debit_amount else 0,
                float(line.credit_amount) if line.credit_amount else 0,
                line.description or "",
            ]
        )
        for cell in ws[ws.max_row]:
            cell.border = border
        ws.cell(row=ws.max_row, column=5).alignment = right_align
        ws.cell(row=ws.max_row, column=6).alignment = right_align

    # Totals
    totals = lines.aggregate(
        total_debit=models.Sum("debit_amount"),
        total_credit=models.Sum("credit_amount"),
    )
    total_debit = float(totals["total_debit"] or 0)
    total_credit = float(totals["total_credit"] or 0)

    ws.append([])
    ws.append(["", "", "", "TOTALS:", total_debit, total_credit, ""])
    for cell in ws[ws.max_row]:
        cell.font = bold
        cell.border = border
    ws.cell(row=ws.max_row, column=5).alignment = right_align
    ws.cell(row=ws.max_row, column=6).alignment = right_align

    # Balance row
    diff = total_debit - total_credit
    ws.append([])
    ws.append(
        [
            "",
            "",
            "",
            "Difference:",
            abs(diff),
            "",
            " Balanced" if abs(diff) < 0.01 else f" Out of balance",
        ]
    )
    for cell in ws[ws.max_row]:
        cell.font = bold
        cell.border = border

    # Column widths
    widths = {"A": 5, "B": 12, "C": 10, "D": 30, "E": 15, "F": 15, "G": 30}
    for col, w in widths.items():
        ws.column_dimensions[col].width = w

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = (
        f'attachment; filename="pending_opening_balances_{entity.slug}.xlsx"'
    )
    wb.save(response)
    return response


@staff_member_required
def open_bal_create(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    accounts = get_visible_accounts(request.user, entity).order_by("code")

    if request.method == "POST":
        date_str = request.POST.get("date", "").strip()
        try:
            date = timezone.datetime.strptime(date_str, "%Y-%m-%d").date()
        except (ValueError, AttributeError):
            date = timezone.now().date()

        lines_json = request.POST.get("lines_json", "[]")
        try:
            lines = json.loads(lines_json)
        except json.JSONDecodeError:
            lines = []

        if not lines:
            messages.error(request, "Please add at least one opening balance line.")
            return redirect("OpenBals:open_bal_create", slug=entity.slug)

        # Balance check
        total_debit = sum(Decimal(str(line.get("debit", 0) or 0)) for line in lines)
        total_credit = sum(Decimal(str(line.get("credit", 0) or 0)) for line in lines)

        if total_debit != total_credit:
            messages.error(
                request,
                f"Debit (₵{total_debit}) must equal Credit (₵{total_credit}). "
                f"Difference: ₵{abs(total_debit - total_credit)}",
            )
            return redirect("OpenBals:open_bal_create", slug=entity.slug)

        saved = 0
        failed = []

        for line in lines:
            try:
                account_id = line.get("account_id")
                account = accounts.filter(pk=account_id).first()
                if not account:
                    failed.append(f"Account not found: {account_id}")
                    continue

                debit = Decimal(str(line.get("debit", 0) or 0))
                credit = Decimal(str(line.get("credit", 0) or 0))
                if debit == 0 and credit == 0:
                    continue

                OpeningBalanceLine.objects.create(
                    entity=entity,
                    date=date,
                    account_code=account,
                    account_name=account.name,
                    debit_amount=debit,
                    credit_amount=credit,
                    description=line.get("description", "").strip(),
                    status="PENDING",  # ← Not posted yet
                    created_by=request.user,
                )
                saved += 1

            except Exception as e:
                failed.append(f"Line failed: {e}")

        if saved:
            messages.success(
                request,
                f" {saved} opening balance line(s) saved. "
                f"Review the list and click 'Post to Trans' when ready.",
            )
        for f in failed:
            messages.error(request, f)

        return redirect("OpenBals:open_bal_list", slug=entity.slug)

    context = {
        "entity": entity,
        "accounts": accounts,
        "today": timezone.now().date(),
        "title": "Opening Balance Entry",
    }
    return render(request, "Openbals/open_bal_form.html", context)


@login_required
def export_pdf(request, slug):
    lines = OpeningBalanceLine.objects.select_related('account').all()
    template = get_template('OpenBals/open_bal_pdf_export.html')
    html = template.render({'lines': lines, 'user': request.user})  #  pass user
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=opening_balances.pdf'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter
from .models import OpeningBalanceLine

@login_required
def export_excel(request, slug):
    wb = Workbook()
    ws = wb.active
    ws.title = "Opening Balances"

    # Headers
    headers = ['Account', 'Debit', 'Credit', 'Date', 'Status', 'Created By']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="007BFF", end_color="007BFF", fill_type="solid")
        cell.alignment = Alignment(horizontal="center", vertical="center")

    lines = OpeningBalanceLine.objects.select_related('account', 'created_by').all()

    for row_idx, line in enumerate(lines, 2):
        ws.cell(row=row_idx, column=1, value=str(line.account))
        ws.cell(row=row_idx, column=2, value=float(line.debit) if line.debit else 0)
        ws.cell(row=row_idx, column=3, value=float(line.credit) if line.credit else 0)
        #  Safe date handling
        ws.cell(row=row_idx, column=4, value=line.date.strftime("%Y-%m-%d") if line.date else "")
        ws.cell(row=row_idx, column=5, value=line.get_status_display())
        #  Safe created_by handling
        if line.created_by:
            ws.cell(row=row_idx, column=6, value=line.created_by.get_full_name() or line.created_by.username)
        else:
            ws.cell(row=row_idx, column=6, value="System")

    # Auto-width
    for col in range(1, len(headers) + 1):
        col_letter = get_column_letter(col)
        ws.column_dimensions[col_letter].width = 20

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=opening_balances.xlsx'
    wb.save(response)
    return response

from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone
