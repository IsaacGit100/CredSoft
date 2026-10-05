# FixedAssets/views.py

from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from django.utils import timezone
from django_ledger.models import EntityModel
from RecPayApp.models import Trans
from .models import FixedAsset, AssetCategory, DepreciationEntry
from .forms import FixedAssetForm, AssetCategoryForm
from .services import post_depreciation


# FixedAssets/views.py — Fixed Asset views only

@login_required
def fixed_asset_home(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    return render(request, 'FixedAssets/fixed_assets_home.html', {"entity": entity})


@login_required
def fixed_asset_list(request, slug):
    """List all fixed assets."""
    entity = get_object_or_404(EntityModel, slug=slug)

    assets = (
        FixedAsset.objects.filter(entity=entity)
        .select_related("category", "trans")
        .order_by("asset_id")
    )

    search = request.GET.get("search", "").strip()
    category_filter = request.GET.get("category", "")

    if search:
        assets = assets.filter(
            models.Q(asset_id__icontains=search) | models.Q(name__icontains=search)
        )
    if category_filter:
        assets = assets.filter(category_id=category_filter)

    totals = assets.aggregate(
        t_cost=models.Sum("cost"),
        t_accum=models.Sum("accumulated_depreciation"),
        t_nbv=models.Sum("book_value"),
    )

    context = {
        "entity": entity,
        "assets": assets,
        "categories": AssetCategory.objects.filter(entity=entity),
        "total_cost": totals["t_cost"] or 0,
        "total_accum_dep": totals["t_accum"] or 0,
        "total_nbv": totals["t_nbv"] or 0,
        "search": search,
        "category_filter": category_filter,
    }
    return render(request, "FixedAssets/fixed_asset_list.html", context)


@login_required
def fixed_asset_create(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    if request.method == "POST":
        form = FixedAssetForm(request.POST, entity=entity)
        if form.is_valid():
            asset = form.save(commit=False)
            asset.entity = entity
            asset.created_by = request.user
            asset.book_value = asset.cost - (
                asset.accumulated_depreciation or Decimal("0.00")
            )
            asset.save()
            messages.success(request, f"Fixed Asset '{asset.name}' registered.")
            return redirect("FixedAssets:fixed_asset_list", slug=entity.slug)
    else:
        form = FixedAssetForm(
            entity=entity, initial={"acquisition_date": timezone.now().date()}
        )
    return render(
        request,
        "FixedAssets/fixed_asset_form.html",
        {"entity": entity, "form": form, "title": "Register Fixed Asset"},
    )


@login_required
def fixed_asset_update(request, slug, pk):
    """Edit a fixed asset. Only allowed if not posted to Trans."""
    entity = get_object_or_404(EntityModel, slug=slug)
    asset = get_object_or_404(FixedAsset, pk=pk, entity=entity)

    if asset.trans_id:
        messages.error(request, "Cannot edit an asset already posted to Trans.")
        return redirect("FixedAssets:fixed_asset_list", slug=entity.slug)

    if request.method == "POST":
        form = FixedAssetForm(request.POST, instance=asset, entity=entity)
        if form.is_valid():
            asset = form.save(commit=False)
            asset.book_value = asset.cost - (
                asset.accumulated_depreciation or Decimal("0.00")
            )
            asset.save()
            messages.success(request, f" Asset '{asset.name}' updated.")
            return redirect("FixedAssets:fixed_asset_list", slug=entity.slug)
    else:
        form = FixedAssetForm(instance=asset, entity=entity)

    return render(
        request,
        "FixedAssets/fixed_asset_form.html",
        {
            "entity": entity,
            "form": form,
            "asset": asset,
            "title": f"Edit Asset: {asset.asset_id}",
        },
    )


@login_required
def fixed_asset_delete(request, slug, pk):
    """Delete a fixed asset. Only allowed if not posted to Trans."""
    entity = get_object_or_404(EntityModel, slug=slug)
    asset = get_object_or_404(FixedAsset, pk=pk, entity=entity)

    if asset.trans_id:
        messages.error(request, "Cannot delete an asset already posted to Trans.")
        return redirect("FixedAssets:fixed_asset_list", slug=entity.slug)

    if request.method == "POST":
        name = asset.name
        asset.delete()
        messages.success(request, f"Asset '{name}' deleted.")
        return redirect("FixedAssets:fixed_asset_list", slug=entity.slug)

    return render(
        request,
        "FixedAssets/fixed_asset_confirm_delete.html",
        {
            "entity": entity,
            "asset": asset,
        },
    )


@login_required
def fixed_asset_post_to_trans(request, slug, pk):
    """Post a single Fixed Asset to Trans for supervisor approval."""
    entity = get_object_or_404(EntityModel, slug=slug)
    asset = get_object_or_404(FixedAsset, pk=pk, entity=entity)

    if asset.trans_id:
        messages.error(request, "This asset has already been posted to Trans.")
        return redirect("FixedAssets:fixed_asset_list", slug=entity.slug)

    asset_acc = asset.category.asset_account if asset.category else None
    if not asset_acc:
        messages.error(request, "Category has no asset account. Cannot post.")
        return redirect("FixedAssets:fixed_asset_list", slug=entity.slug)

        # Map payment_mode → engine pay_mode + credit account
    PAY_MODE_MAP = {
        "CASH": ("Cash", "1010"),
        "BANK": ("Transfer", "1020"),
        "CHEQUE": ("Cheque", "1020"),
        "MOMO": ("Momo", "1020"),
        "CREDIT": ("None", None),  # handled as Journal below
    }
    mode = (asset.payment_mode or "CASH").upper()
    engine_mode, _credit_code = PAY_MODE_MAP.get(mode, ("Cash", "1010"))

    if mode == "CREDIT":
        # acquisition on credit — post as Journal: Dr Asset / Cr Payable
        trans = Trans.objects.create(
            entity=entity,
            module="fixed_assets",
            sub_module="fixed_asset",
            trans_type="Journal",
            date=asset.acquisition_date,
            amount=asset.cost,
            debit_account_code=asset_acc.code,
            debit_account_name=asset_acc.name,
            credit_account_code="2010",  # ← your payable code; adjust
            credit_account_name="Accounts Payable",
            purpose="Fixed Asset Acquisition (Credit)",
            details=f"Fixed Asset: {asset.asset_id} – {asset.name}",
            journal_status="PENDING",
            status="DRAFT",
            created_by=request.user,
            created_by_name=request.user.username,
            created_by_username=request.user.username,
        )
    else:
        # paid in cash / bank / cheque / momo — engine figures out Cash/Bank from pay_mode
        trans = Trans.objects.create(
            entity=entity,
            module="fixed_assets",
            sub_module="fixed_asset",
            trans_type="Payments",
            date=asset.acquisition_date,
            amount=asset.cost,
            pay_mode=engine_mode,
            ledger_code=asset_acc.code,
            ledger_name=asset_acc.name,
            purpose="Fixed Asset Acquisition",
            details=f"Fixed Asset: {asset.asset_id} – {asset.name}",
            journal_status="PENDING",
            status="DRAFT",
            created_by=request.user,
            created_by_name=request.user.username,
            created_by_username=request.user.username,
        )

    asset.trans = trans
    asset.save(update_fields=["trans"])

    messages.success(
        request,
        f" Asset '{asset.name}' posted to Trans. "
        f"Voucher {trans.rec_vou_no} awaiting supervisor approval.",
    )
    return redirect("FixedAssets:fixed_asset_list", slug=entity.slug)


@login_required
def run_depreciation(request, slug):
    """
    One-click action that:
      1. Posts acquisition Trans for any un-posted Fixed Assets
      2. Runs depreciation for the current month
    Safe to run any number of times — skips already-posted items.
    """
    entity = get_object_or_404(EntityModel, slug=slug)
    today = timezone.now().date()

    posted_acq = 0
    for asset in FixedAsset.objects.filter(entity=entity, trans__isnull=True):
        acc = asset.category.asset_account if asset.category else None
        if not acc:
            continue
        trans = Trans.objects.create(
            entity=entity,
            module="fixed_assets",
            sub_module="fixed_asset",
            trans_type="Payments",
            date=asset.acquisition_date,
            amount=asset.cost,
            pay_mode="Cash",
            ledger_code=acc.code,
            ledger_name=acc.name,
            purpose="Fixed Asset Acquisition",
            details=f"{asset.asset_id} - {asset.name}",
            created_by=request.user,
            created_by_name=request.user.username,
            created_by_username=request.user.username,
        )
        asset.trans = trans
        asset.save(update_fields=["trans"])
        posted_acq += 1

    period_start = today.replace(day=1)
    period_end = today
    result = post_depreciation(entity, period_start, period_end, user=request.user)

    messages.success(
        request,
        f" Posted {posted_acq} new asset(s) and "
        f"{result['created']} depreciation entr{'y' if result['created'] == 1 else 'ies'} "
        f"(₵{result['total']:,.2f}). Pending supervisor approval.",
    )
    if result["skipped"]:
        messages.info(
            request,
            f"ℹ {result['skipped']} asset(s) skipped (already done this month).",
        )
    for err in result["errors"]:
        messages.error(request, err)

    return redirect("FixedAssets:fixed_asset_list", slug=entity.slug)

@login_required
def asset_category_list(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    categories = AssetCategory.objects.filter(entity=entity).order_by("name")
    return render(
        request,
        "FixedAssets/asset_category_list.html",
        {
            "entity": entity,
            "categories": categories,
        },
    )


@login_required
def asset_category_create(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)

    if request.method == "POST":
        form = AssetCategoryForm(request.POST, entity=entity)
        if form.is_valid():
            cat = form.save(commit=False)
            cat.entity = entity
            cat.save()
            messages.success(request, f" Category '{cat.name}' created.")
            return redirect("FixedAssets:asset_category_list", slug=entity.slug)
    else:
        form = AssetCategoryForm(entity=entity)

    return render(
        request,
        "FixedAssets/asset_category_form.html",
        {
            "entity": entity,
            "form": form,
            "title": "Add Asset Category",
        },
    )


@login_required
def asset_category_update(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    cat = get_object_or_404(AssetCategory, pk=pk, entity=entity)

    if request.method == "POST":
        form = AssetCategoryForm(request.POST, instance=cat, entity=entity)
        if form.is_valid():
            form.save()
            messages.success(request, f" Category '{cat.name}' updated.")
            return redirect("FixedAssets:asset_category_list", slug=entity.slug)
    else:
        form = AssetCategoryForm(instance=cat, entity=entity)

    return render(
        request,
        "FixedAssets/asset_category_form.html",
        {
            "entity": entity,
            "form": form,
            "category": cat,
            "title": f"Edit Category: {cat.name}",
        },
    )


@login_required
def asset_category_delete(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    cat = get_object_or_404(AssetCategory, pk=pk, entity=entity)

    if cat.assets.exists():
        messages.error(request, f"Cannot delete '{cat.name}' – it has assets assigned.")
        return redirect("FixedAssets:asset_category_list", slug=entity.slug)

    if request.method == "POST":
        name = cat.name
        cat.delete()
        messages.success(request, f"Category '{name}' deleted.")
        return redirect("FixedAssets:asset_category_list", slug=entity.slug)

    return render(
        request,
        "FixedAssets/asset_category_confirm_delete.html",
        {
            "entity": entity,
            "category": cat,
        },
    )

# FixedAssets/views.py — add these imports at the top
import io
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter


@login_required
def fixed_asset_list_pdf(request, slug):
    """Export the Fixed Assets Register as an A4 PDF."""
    entity = get_object_or_404(EntityModel, slug=slug)

    assets = (
        FixedAsset.objects.filter(entity=entity)
        .select_related("category", "trans", "created_by")
        .order_by("asset_id")
    )

    # Apply the same filters as the list view (optional)
    search = request.GET.get("search", "").strip()
    category_filter = request.GET.get("category", "")
    if search:
        assets = assets.filter(
            models.Q(asset_id__icontains=search) | models.Q(name__icontains=search)
        )
    if category_filter:
        assets = assets.filter(category_id=category_filter)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=1.2 * cm,
        rightMargin=1.2 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.2 * cm,
        title=f"Fixed Asset Register – {entity.name}",
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleX",
        parent=styles["Title"],
        fontSize=14,
        leading=18,
        alignment=TA_CENTER,
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "SubX",
        parent=styles["Normal"],
        fontSize=10,
        leading=12,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#666666"),
        spaceAfter=10,
    )
    cell_style = ParagraphStyle(
        "CellX",
        parent=styles["Normal"],
        fontSize=8,
        leading=10,
    )
    cell_right = ParagraphStyle(
        "CellR",
        parent=styles["Normal"],
        fontSize=8,
        leading=10,
        alignment=TA_RIGHT,
    )

    elements = []
    elements.append(Paragraph(f"{entity.name}", title_style))
    elements.append(Paragraph("Fixed Asset Register", subtitle_style))

    # Columns (A4 portrait  18.6cm usable width)
    headers = [
        "#",
        "Asset ID",
        "Name",
        "Category",
        "Acquired",
        "Cost (₵)",
        "Accum. Dep (₵)",
        "NBV (₵)",
        "Status",
    ]

    data = [[Paragraph(f"<b>{h}</b>", cell_style) for h in headers]]

    total_cost = Decimal("0.00")
    total_accum = Decimal("0.00")
    total_nbv = Decimal("0.00")

    for idx, a in enumerate(assets, 1):
        total_cost += a.cost or Decimal("0.00")
        total_accum += a.accumulated_depreciation or Decimal("0.00")
        total_nbv += a.book_value or Decimal("0.00")

        status = "Active" if a.is_active else "Disposed"

        data.append(
            [
                Paragraph(str(idx), cell_style),
                Paragraph(a.asset_id or "—", cell_style),
                Paragraph((a.name or "—")[:40], cell_style),
                Paragraph(a.category.name if a.category else "—", cell_style),
                Paragraph(
                    (
                        a.acquisition_date.strftime("%Y-%m-%d")
                        if a.acquisition_date
                        else "—"
                    ),
                    cell_style,
                ),
                Paragraph(f"{a.cost:,.2f}", cell_right),
                Paragraph(f"{a.accumulated_depreciation:,.2f}", cell_right),
                Paragraph(f"{a.book_value:,.2f}", cell_right),
                Paragraph(status, cell_style),
            ]
        )

    # Totals row
    data.append(
        [
            "",
            "",
            Paragraph("<b>TOTALS</b>", cell_style),
            "",
            "",
            Paragraph(f"<b>{total_cost:,.2f}</b>", cell_right),
            Paragraph(f"<b>{total_accum:,.2f}</b>", cell_right),
            Paragraph(f"<b>{total_nbv:,.2f}</b>", cell_right),
            "",
        ]
    )

    col_widths = [
        0.8 * cm,  # #
        3.0 * cm,  # Asset ID
        4.5 * cm,  # Name
        3.0 * cm,  # Category
        2.0 * cm,  # Acquired
        2.2 * cm,  # Cost
        2.4 * cm,  # Accum Dep
        2.4 * cm,  # NBV
        1.5 * cm,  # Status
    ]

    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a3a6c")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -2),
                    [colors.white, colors.HexColor("#f5f5f5")],
                ),
                ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e0e8f0")),
            ]
        )
    )

    elements.append(table)
    elements.append(Spacer(1, 6))
    elements.append(
        Paragraph(
            f"Generated: {timezone.now().strftime('%Y-%m-%d %H:%M')} &nbsp;|&nbsp; "
            f"Total records: {assets.count()}",
            ParagraphStyle(
                "Foot",
                parent=styles["Normal"],
                fontSize=7,
                textColor=colors.grey,
                alignment=TA_CENTER,
            ),
        )
    )

    doc.build(elements)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="fixed_assets_{entity.slug}.pdf"'
    )
    return response

@login_required
def fixed_asset_list_excel(request, slug):
    """Export the Fixed Assets Register as an Excel file with all fields."""
    entity = get_object_or_404(EntityModel, slug=slug)

    assets = (
        FixedAsset.objects.filter(entity=entity)
        .select_related(
            "category",
            "trans",
            "created_by",
            "category__asset_account",
            "category__accumulated_depreciation_account",
            "category__depreciation_expense_account",
        )
        .order_by("asset_id")
    )

    wb = Workbook()
    ws = wb.active
    ws.title = "Fixed Assets"

    
    bold = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill("solid", fgColor="1a3a6c")
    total_fill = PatternFill("solid", fgColor="e0e8f0")
    thin = Side(style="thin", color="999999")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    center = Alignment(horizontal="center", vertical="center")
    right = Alignment(horizontal="right", vertical="center")

    ws.merge_cells("A1:AB1")
    ws["A1"] = f"{entity.name} – Fixed Asset Register"
    ws["A1"].font = Font(bold=True, size=14)
    ws["A1"].alignment = center

    headers = [
        "#",
        # Asset core
        "Asset ID",
        "Name",
        "Description",
        "Category",
        "Category Method",
        "Category Life (yrs)",
        "Category Rate (%)",
        "Category Salvage (%)",
        # Acquisition
        "Acquisition Date",
        "Cost",
        "Salvage Value",
        "Depreciation Method",
        "Useful Life (yrs)",
        "Override Rate (%)",
        # Values
        "Accumulated Depreciation",
        "Book Value (NBV)",
        "Last Depreciation Date",
        # Status
        "Is Active",
        "Disposal Date",
        # GL accounts (from category)
        "Asset Account Code",
        "Asset Account Name",
        "Accum Dep Account Code",
        "Accum Dep Account Name",
        "Dep Expense Account Code",
        "Dep Expense Account Name",
        # Link
        "Voucher No",
        "Journal Status",
        # Audit
        "Created By",
        "Created At",
        "Updated At",
    ]
    ws.append(headers)

    header_row = ws.max_row
    for col_idx, _ in enumerate(headers, start=1):
        cell = ws.cell(row=header_row, column=col_idx)
        cell.font = bold
        cell.fill = header_fill
        cell.alignment = center
        cell.border = border


    for idx, a in enumerate(assets, 1):
        cat = a.category
        row = [
            idx,
            a.asset_id or "",
            a.name or "",
            a.description or "",
            cat.name if cat else "",
            cat.get_depreciation_method_display() if cat else "",
            cat.useful_life_years if cat else "",
            float(cat.depreciation_rate) if cat and cat.depreciation_rate else "",
            (
                float(cat.salvage_value_percent)
                if cat and cat.salvage_value_percent
                else ""
            ),
            a.acquisition_date.strftime("%Y-%m-%d") if a.acquisition_date else "",
            float(a.cost) if a.cost else 0,
            float(a.salvage_value) if a.salvage_value else 0,
            a.get_depreciation_method_display(),
            a.useful_life_years,
            float(a.override_depreciation_rate) if a.override_depreciation_rate else "",
            float(a.accumulated_depreciation) if a.accumulated_depreciation else 0,
            float(a.book_value) if a.book_value else 0,
            (
                a.last_depreciation_date.strftime("%Y-%m-%d")
                if a.last_depreciation_date
                else ""
            ),
            "Yes" if a.is_active else "No",
            a.disposal_date.strftime("%Y-%m-%d") if a.disposal_date else "",
            cat.asset_account.code if cat and cat.asset_account else "",
            cat.asset_account.name if cat and cat.asset_account else "",
            (
                cat.accumulated_depreciation_account.code
                if cat and cat.accumulated_depreciation_account
                else ""
            ),
            (
                cat.accumulated_depreciation_account.name
                if cat and cat.accumulated_depreciation_account
                else ""
            ),
            (
                cat.depreciation_expense_account.code
                if cat and cat.depreciation_expense_account
                else ""
            ),
            (
                cat.depreciation_expense_account.name
                if cat and cat.depreciation_expense_account
                else ""
            ),
            a.trans.rec_vou_no if a.trans else "",
            a.trans.get_journal_status_display() if a.trans else "",
            a.created_by.username if a.created_by else "",
            a.created_at.strftime("%Y-%m-%d %H:%M") if a.created_at else "",
            a.updated_at.strftime("%Y-%m-%d %H:%M") if a.updated_at else "",
        ]
        ws.append(row)

        for c_idx in range(1, len(headers) + 1):
            cell = ws.cell(row=ws.max_row, column=c_idx)
            cell.border = border


    ws.append(
        [
            "",
            "TOTALS",
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
            "",
            "",
            "",
            "",
        ]
    )
    total_row = ws.max_row
    cost_col = headers.index("Cost") + 1
    accum_col = headers.index("Accumulated Depreciation") + 1
    nbv_col = headers.index("Book Value (NBV)") + 1

    ws.cell(row=total_row, column=2).font = Font(bold=True)
    for col in (cost_col, accum_col, nbv_col):
        col_letter = get_column_letter(col)
        c = ws.cell(row=total_row, column=col)
        c.value = f"=SUM({col_letter}2:{col_letter}{total_row - 1})"
        c.font = Font(bold=True)
        c.alignment = right
        c.fill = total_fill
        c.border = border

    for col_idx, header in enumerate(headers, start=1):
        letter = get_column_letter(col_idx)
        ws.column_dimensions[letter].width = max(12, min(len(header) + 4, 30))

    # Freeze header + first two columns
    ws.freeze_panes = "C2"

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = (
        f'attachment; filename="fixed_assets_{entity.slug}.xlsx"'
    )
    wb.save(response)
    return response

@login_required
def asset_category_list_pdf(request, slug):
    """Export asset categories as an A4 landscape PDF."""
    entity = get_object_or_404(EntityModel, slug=slug)

    categories = (
        AssetCategory.objects.filter(entity=entity)
        .select_related(
            "asset_account",
            "accumulated_depreciation_account",
            "depreciation_expense_account",
        )
        .order_by("name")
    )

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),  # ← landscape
        leftMargin=1.0 * cm,
        rightMargin=1.0 * cm,
        topMargin=1.2 * cm,
        bottomMargin=1.0 * cm,
        title=f"Asset Categories - {entity.name}",
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleX",
        parent=styles["Title"],
        fontSize=14,
        leading=18,
        alignment=TA_CENTER,
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "SubX",
        parent=styles["Normal"],
        fontSize=10,
        leading=12,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#666666"),
        spaceAfter=10,
    )
    cell_style = ParagraphStyle(
        "CellX",
        parent=styles["Normal"],
        fontSize=8,
        leading=10,
    )
    cell_right = ParagraphStyle(
        "CellR",
        parent=styles["Normal"],
        fontSize=8,
        leading=10,
        alignment=TA_RIGHT,
    )
    cell_center = ParagraphStyle(
        "CellC",
        parent=styles["Normal"],
        fontSize=8,
        leading=10,
        alignment=TA_CENTER,
    )

    elements = []
    elements.append(Paragraph(f"{entity.name}", title_style))
    elements.append(Paragraph("Asset Categories — GL Account Mapping", subtitle_style))

    # A4 landscape usable width  27.7 cm
    headers = [
        "#",
        "Category",
        "Method",
        "Life (yrs)",
        "Rate (%)",
        "Salvage (%)",
        "Asset Account",
        "Accumulated Depreciation",
        "Depreciation Expense",
        "# Assets",
    ]

    data = [[Paragraph(f"<b>{h}</b>", cell_style) for h in headers]]

    for idx, cat in enumerate(categories, 1):
        asset_acc = cat.asset_account
        accum_acc = cat.accumulated_depreciation_account
        exp_acc = cat.depreciation_expense_account

        data.append(
            [
                Paragraph(str(idx), cell_center),
                Paragraph(cat.name or "—", cell_style),
                Paragraph(cat.get_depreciation_method_display() or "—", cell_center),
                Paragraph(str(cat.useful_life_years or "—"), cell_center),
                Paragraph(
                    f"{cat.depreciation_rate:.2f}" if cat.depreciation_rate else "—",
                    cell_right,
                ),
                Paragraph(
                    (
                        f"{cat.salvage_value_percent:.2f}"
                        if cat.salvage_value_percent
                        else "—"
                    ),
                    cell_right,
                ),
                Paragraph(
                    (
                        f"<b>{asset_acc.code}</b><br/>{asset_acc.name}"
                        if asset_acc
                        else "<i>Not set</i>"
                    ),
                    cell_style,
                ),
                Paragraph(
                    (
                        f"<b>{accum_acc.code}</b><br/>{accum_acc.name}"
                        if accum_acc
                        else "<i>Not set</i>"
                    ),
                    cell_style,
                ),
                Paragraph(
                    (
                        f"<b>{exp_acc.code}</b><br/>{exp_acc.name}"
                        if exp_acc
                        else "<i>Not set</i>"
                    ),
                    cell_style,
                ),
                Paragraph(str(cat.assets.count()), cell_center),
            ]
        )

    # Column widths (sums to ~27.5 cm)
    col_widths = [
        0.8 * cm,  # #
        3.2 * cm,  # Category
        2.0 * cm,  # Method
        1.6 * cm,  # Life
        1.6 * cm,  # Rate
        1.8 * cm,  # Salvage
        4.5 * cm,  # Asset Account
        4.5 * cm,  # Accum Dep
        4.5 * cm,  # Dep Expense
        1.5 * cm,  # # Assets
    ]

    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a3a6c")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#f5f5f5")],
                ),
            ]
        )
    )

    elements.append(table)
    elements.append(Spacer(1, 6))
    elements.append(
        Paragraph(
            f"Generated: {timezone.now().strftime('%Y-%m-%d %H:%M')} &nbsp;|&nbsp; "
            f"Total categories: {categories.count()}",
            ParagraphStyle(
                "Foot",
                parent=styles["Normal"],
                fontSize=7,
                textColor=colors.grey,
                alignment=TA_CENTER,
            ),
        )
    )

    doc.build(elements)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="asset_categories_{entity.slug}.pdf"'
    )
    return response

@login_required
def asset_category_list_excel(request, slug):
    """Export asset categories as Excel with all fields."""
    entity = get_object_or_404(EntityModel, slug=slug)

    categories = (
        AssetCategory.objects.filter(entity=entity)
        .select_related(
            "asset_account",
            "accumulated_depreciation_account",
            "depreciation_expense_account",
        )
        .order_by("name")
    )

    wb = Workbook()
    ws = wb.active
    ws.title = "Asset Categories"

    bold = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill("solid", fgColor="1a3a6c")
    thin = Side(style="thin", color="999999")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    center = Alignment(horizontal="center", vertical="center")
    right = Alignment(horizontal="right", vertical="center")

    
    ws.merge_cells("A1:N1")
    ws["A1"] = f"{entity.name} – Asset Categories"
    ws["A1"].font = Font(bold=True, size=14)
    ws["A1"].alignment = center

    #
    headers = [
        "#",
        "Category Name",
        "Depreciation Method",
        "Useful Life (Years)",
        "Salvage Value (%)",
        "Depreciation Rate (%)",
        "Asset Account Code",
        "Asset Account Name",
        "Accum. Dep Account Code",
        "Accum. Dep Account Name",
        "Dep. Expense Account Code",
        "Dep. Expense Account Name",
        "Number of Assets",
        "Total Asset Cost (₵)",
    ]
    ws.append(headers)

    header_row = ws.max_row
    for col_idx, _ in enumerate(headers, start=1):
        cell = ws.cell(row=header_row, column=col_idx)
        cell.font = bold
        cell.fill = header_fill
        cell.alignment = center
        cell.border = border

    # 
    for idx, cat in enumerate(categories, 1):
        asset_acc = cat.asset_account
        accum_acc = cat.accumulated_depreciation_account
        exp_acc = cat.depreciation_expense_account

        total_cost = cat.assets.aggregate(t=models.Sum("cost"))["t"] or 0

        ws.append(
            [
                idx,
                cat.name or "",
                cat.get_depreciation_method_display() or "",
                cat.useful_life_years or 0,
                float(cat.salvage_value_percent) if cat.salvage_value_percent else 0,
                float(cat.depreciation_rate) if cat.depreciation_rate else 0,
                asset_acc.code if asset_acc else "",
                asset_acc.name if asset_acc else "",
                accum_acc.code if accum_acc else "",
                accum_acc.name if accum_acc else "",
                exp_acc.code if exp_acc else "",
                exp_acc.name if exp_acc else "",
                cat.assets.count(),
                float(total_cost),
            ]
        )

        for c_idx in range(1, len(headers) + 1):
            ws.cell(row=ws.max_row, column=c_idx).border = border

    # 
    ws.append(
        [
            "",
            "TOTALS",
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
            f"=SUM(M2:M{ws.max_row})",
            f"=SUM(N2:N{ws.max_row})",
        ]
    )
    total_row = ws.max_row
    for c_idx in (2, 13, 14):
        cell = ws.cell(row=total_row, column=c_idx)
        cell.font = Font(bold=True)
        cell.fill = PatternFill("solid", fgColor="e0e8f0")
        cell.border = border
        if c_idx >= 13:
            cell.alignment = right

    # 
    for col_idx, header in enumerate(headers, start=1):
        letter = get_column_letter(col_idx)
        ws.column_dimensions[letter].width = max(14, min(len(header) + 4, 32))

    # Freeze header + first column
    ws.freeze_panes = "B2"

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = (
        f'attachment; filename="asset_categories_{entity.slug}.xlsx"'
    )
    wb.save(response)
    return response
