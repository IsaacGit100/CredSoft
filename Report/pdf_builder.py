"""
Shared ReportLab PDF builder for all Report app reports.
Clean layout: no colored backgrounds, thin rule lines only.
"""

import os
from datetime import datetime
from decimal import Decimal, InvalidOperation
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

FONT = "Helvetica"
FONT_BOLD = "Helvetica-Bold"


def _try_dejavu():
    global FONT, FONT_BOLD
    candidates = [
        ("C:/Windows/Fonts/DejaVuSans.ttf", "C:/Windows/Fonts/DejaVuSans-Bold.ttf"),
        (
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ),
    ]
    for regular, bold in candidates:
        if os.path.exists(regular) and os.path.exists(bold):
            pdfmetrics.registerFont(TTFont("DejaVuSans", regular))
            pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", bold))
            FONT = "DejaVuSans"
            FONT_BOLD = "DejaVuSans-Bold"
            return


_try_dejavu()
CURRENCY = "₵" if FONT.startswith("DejaVu") else "GHS "

ALIGN_MAP = {"left": TA_LEFT, "center": TA_CENTER, "right": TA_RIGHT}

# Neutral palette
DARK_NAVY = colors.HexColor("#1e3a5f")
RULE_GRAY = colors.HexColor("#cccccc")
TOTALS_BG = colors.HexColor("#f5f5f5")
TOTALS_RULE = colors.HexColor("#888888")


class Col:
    def __init__(self, label, width_pct, align="left", currency=False):
        self.label = label
        self.width_pct = width_pct
        self.align = align
        self.currency = currency


def _fmt_number(value, currency=False):
    if value is None or value == "":
        return ""
    try:
        d = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return str(value)
    if d == 0:
        return ""
    s = f"{d:,.2f}"
    return f"{CURRENCY}{s}" if currency else s


def _cell(text, align="left", bold=False, size=9.0, color=None):
    """Wrap text in a Paragraph so long values wrap inside their cell."""
    if text is None or text == "":
        return ""
    style = ParagraphStyle(
        "cell",
        fontName=FONT_BOLD if bold else FONT,
        fontSize=size,
        leading=size + 2.5,
        alignment=ALIGN_MAP[align],
        textColor=color or colors.black,
    )
    return Paragraph(str(text), style)


def _make_footer(org_name):
    def _footer(canvas, doc):
        canvas.saveState()
        canvas.setFont(FONT, 8)
        canvas.setFillColor(colors.HexColor("#666666"))
        w, _ = doc.pagesize
        canvas.drawCentredString(
            w / 2, 1.0 * cm, f"Generated {datetime.now():%d/%m/%Y %H:%M}  —  {org_name}"
        )
        canvas.drawRightString(w - 1.5 * cm, 1.0 * cm, f"Page {doc.page}")
        canvas.restoreState()

    return _footer


def build_report_pdf(
    *,
    entity,
    entity_config,
    report_title,
    period_label,
    columns,
    rows,
    totals=None,
    filename="report.pdf",
    landscape_mode=False,
):
    buf = BytesIO()

    pagesize = landscape(A4) if landscape_mode else A4
    doc = SimpleDocTemplate(
        buf,
        pagesize=pagesize,
        leftMargin=1.2 * cm,
        rightMargin=1.2 * cm,
        topMargin=1.2 * cm,
        bottomMargin=1.5 * cm,
        title=report_title,
        author=(entity_config.organization_name if entity_config else "Report"),
    )

    styles = {
        "org": ParagraphStyle(
            "org",
            fontName=FONT_BOLD,
            fontSize=16,
            alignment=TA_CENTER,
            textColor=DARK_NAVY,
        ),
        "subtitle": ParagraphStyle(
            "subtitle",
            fontName=FONT,
            fontSize=9,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#666666"),
        ),
        "entity": ParagraphStyle(
            "entity",
            fontName=FONT_BOLD,
            fontSize=11,
            alignment=TA_CENTER,
            textColor=DARK_NAVY,
            spaceBefore=6,
        ),
        "title": ParagraphStyle(
            "title", fontName=FONT_BOLD, fontSize=12, alignment=TA_CENTER, spaceBefore=2
        ),
        "period": ParagraphStyle(
            "period",
            fontName=FONT,
            fontSize=9,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#666666"),
            spaceBefore=2,
            spaceAfter=12,
        ),
    }

    story = []

    org_name = entity_config.organization_name if entity_config else "Organization"
    subtitle = entity_config.report_subtitle if entity_config else ""
    ent_name = (
        entity_config.display_name
        if entity_config and entity_config.display_name
        else entity.name
    )

    story.append(Paragraph(org_name, styles["org"]))
    if subtitle:
        story.append(Paragraph(subtitle, styles["subtitle"]))
    story.append(Paragraph(ent_name, styles["entity"]))
    story.append(Paragraph(report_title, styles["title"]))
    if period_label:
        story.append(Paragraph(period_label, styles["period"]))
    else:
        story.append(Spacer(1, 12))

    # ---- Header row ----
    header = [
        _cell(c.label, align="center", bold=True, size=9.0, color=DARK_NAVY)
        for c in columns
    ]
    data = [header]

    # ---- Body rows ----
    for r in rows:
        row_data = []
        for i, v in enumerate(r):
            c = columns[i]
            if c.align == "left":
                row_data.append(_cell(v, align="left", size=9.0))
            else:
                row_data.append(_fmt_number(v, currency=c.currency))
        data.append(row_data)

    # ---- Totals row ----
    if totals:
        totals_row = []
        for i, v in enumerate(totals):
            c = columns[i]
            if c.align == "left":
                totals_row.append(_cell(v, align="left", bold=True, size=9.0))
            else:
                totals_row.append(_fmt_number(v, currency=c.currency))
        data.append(totals_row)

    # Column widths
    avail_width = doc.width
    col_widths = [(c.width_pct / 100.0) * avail_width for c in columns]

    table = Table(data, colWidths=col_widths, repeatRows=1)

    # ---- Clean style: no fills, only thin rule lines ----
    style_cmds = [
        # Header row: dark text, bold, thin dark rule underneath
        ("TEXTCOLOR", (0, 0), (-1, 0), DARK_NAVY),
        ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("TOPPADDING", (0, 0), (-1, 0), 6),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("LINEBELOW", (0, 0), (-1, 0), 0.75, DARK_NAVY),
        # Body: thin light rule between rows
        ("FONTNAME", (0, 1), (-1, -1), FONT),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("TOPPADDING", (0, 1), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
        ("LINEBELOW", (0, 1), (-1, -2), 0.25, RULE_GRAY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]

    # Per-column alignment
    for i, c in enumerate(columns):
        style_cmds.append(("ALIGN", (i, 0), (i, -1), c.align.upper()))

    # Totals row: bold, light gray fill, darker rule on top
    if totals:
        style_cmds += [
            ("FONTNAME", (0, -1), (-1, -1), FONT_BOLD),
            ("LINEABOVE", (0, -1), (-1, -1), 1, TOTALS_RULE),
            ("BACKGROUND", (0, -1), (-1, -1), TOTALS_BG),
        ]

    table.setStyle(TableStyle(style_cmds))
    story.append(table)

    footer = _make_footer(org_name)
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return buf.getvalue()
