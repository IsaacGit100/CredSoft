# services/pdf_utils.py

from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from django.http import HttpResponse
from django.utils import timezone

# ---------------- Brand palette ----------------
BRAND_DARK = colors.HexColor("#1a3a6c")
BRAND_GRID = colors.HexColor("#cccccc")
BRAND_BOX = colors.HexColor("#666666")
BRAND_ROW_ALT = colors.HexColor("#f7f9fc")
BRAND_TOTAL = colors.HexColor("#e8eef7")
BRAND_DEBIT = colors.HexColor("#1e40af")
BRAND_CREDIT = colors.HexColor("#166534")
BRAND_DANGER = colors.HexColor("#991b1b")


def money(value):
    """Format a number as currency text."""
    if value is None:
        return "—"
    try:
        return f"{float(value):,.2f}"
    except (TypeError, ValueError):
        return str(value)


def build_title_block(entity_name, title, subtitle=None):
    """Return a list of Paragraphs forming the header."""
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleX",
        parent=styles["Title"],
        fontSize=16,
        textColor=BRAND_DARK,
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "SubX",
        parent=styles["Normal"],
        fontSize=10,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#666"),
        spaceAfter=10,
    )

    blocks = [Paragraph(entity_name, title_style)]
    header_line = title
    if subtitle:
        header_line = f"{header_line} &nbsp;•&nbsp; {subtitle}"
    blocks.append(Paragraph(header_line, subtitle_style))
    return blocks


def build_summary_table(items, total_width):
    """
    items = [(label, value, color_or_None), ...]
    """
    styles = getSampleStyleSheet()
    cell = ParagraphStyle("sumCell", fontSize=10, alignment=TA_CENTER, leading=13)
    label_style = ParagraphStyle(
        "sumLabel",
        fontSize=8,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#666"),
        leading=10,
    )

    top = [Paragraph(lbl.upper(), label_style) for lbl, _, _ in items]
    bottom = []
    for _, val, col in items:
        if col:
            bottom.append(
                Paragraph(f"<font color='{col.hexval()}'><b>{val}</b></font>", cell)
            )
        else:
            bottom.append(Paragraph(f"<b>{val}</b>", cell))

    col_w = total_width / len(items)
    tbl = Table([top, bottom], colWidths=[col_w] * len(items))
    tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0f4fa")),
                ("BOX", (0, 0), (-1, -1), 0.5, BRAND_GRID),
                ("INNERGRID", (0, 0), (-1, -1), 0.3, BRAND_GRID),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return tbl


def build_data_table(headers, rows, col_widths, totals_row=None):
    """
    headers      = ['#', 'Date', ...]
    rows         = list of lists (strings only)
    col_widths   = list of widths in points (cm * 28.35)
    totals_row   = optional list aligned to headers; empty strings allowed
    """
    header_style = ParagraphStyle(
        "hdrX", fontSize=9, textColor=colors.white, leading=11
    )
    cell = ParagraphStyle("cellX", fontSize=9, leading=11)
    cell_right = ParagraphStyle("cellXR", parent=cell, alignment=TA_RIGHT)
    cell_center = ParagraphStyle("cellXC", parent=cell, alignment=TA_CENTER)

    data = [[Paragraph(f"<b>{h}</b>", header_style) for h in headers]]

    for row in rows:
        formatted = []
        for i, cell_val in enumerate(row):
            # Right-align numeric columns (usually the last numeric ones)
            txt = str(cell_val) if cell_val is not None else ""
            # Heuristic: if it looks numeric or is '—', right align
            if (
                txt.replace(",", "")
                .replace(".", "")
                .replace("-", "")
                .replace("₵", "")
                .replace(" ", "")
                .isdigit()
            ):
                formatted.append(Paragraph(txt, cell_right))
            elif txt == "—" or txt == "":
                formatted.append(Paragraph(txt, cell_right))
            else:
                formatted.append(Paragraph(txt, cell))
        data.append(formatted)

    if totals_row:
        totals_cells = []
        for i, val in enumerate(totals_row):
            txt = str(val) if val is not None else ""
            if i == 0:
                totals_cells.append(Paragraph(f"<b>{txt}</b>", cell))
            else:
                totals_cells.append(Paragraph(f"<b>{txt}</b>", cell_right))
        data.append(totals_cells)

    tbl = Table(data, colWidths=col_widths, repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), BRAND_DARK),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.3, BRAND_GRID),
        ("BOX", (0, 0), (-1, -1), 0.6, BRAND_BOX),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]

    # Alternate row shading
    for i in range(1, len(data) - (1 if totals_row else 0)):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), BRAND_ROW_ALT))

    if totals_row:
        style.append(("BACKGROUND", (0, -1), (-1, -1), BRAND_TOTAL))

    tbl.setStyle(TableStyle(style))
    return tbl


def build_pdf_response(
    filename, title_block, summary_table=None, data_table=None, extra_flowables=None
):
    """
    Generic PDF builder.
    Returns an HttpResponse with the generated PDF.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=1.2 * cm,
        rightMargin=1.2 * cm,
        topMargin=1 * cm,
        bottomMargin=1.5 * cm,
        title=filename,
    )

    story = []
    story.extend(title_block)
    if summary_table:
        story.append(summary_table)
        story.append(Spacer(1, 10))
    if data_table:
        story.append(data_table)
    if extra_flowables:
        story.extend(extra_flowables)

    doc.build(story)

    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    response.write(pdf)
    return response
