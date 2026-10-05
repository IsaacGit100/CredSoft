"""
ReportLab PDF builder for loan repayment schedules.

Used by:
  - the preview from the application form  (loan is a dict)
  - the saved loan detail / list           (loan is a model instance)

Returns raw PDF bytes.
"""

from io import BytesIO
from decimal import Decimal

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    KeepTogether,
    HRFlowable,
)

BRAND = colors.HexColor("#1a56db")
BRAND_DARK = colors.HexColor("#1e3a5f")
GREY_BG = colors.HexColor("#f3f4f6")
GREY_LINE = colors.HexColor("#d1d5db")
GREEN_BG = colors.HexColor("#ecfdf5")
GREEN_FG = colors.HexColor("#065f46")
RED_BG = colors.HexColor("#fef2f2")
RED_FG = colors.HexColor("#991b1b")
BLUE_BG = colors.HexColor("#eff6ff")
BLUE_FG = colors.HexColor("#1e40af")
AMBER_BG = colors.HexColor("#fef3c7")
AMBER_FG = colors.HexColor("#92400e")


def _money(v):
    try:
        return f"{Decimal(v):,.2f}"
    except Exception:
        return str(v)


def _get(obj, key, default=""):
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#6b7280"))
    canvas.drawString(15 * mm, 10 * mm, doc._footer_text or "")
    canvas.drawRightString(A4[0] - 15 * mm, 10 * mm, f"Page {doc.page}")
    canvas.setStrokeColor(GREY_LINE)
    canvas.setLineWidth(0.4)
    canvas.line(15 * mm, 14 * mm, A4[0] - 15 * mm, 14 * mm)
    canvas.restoreState()


def build_loan_schedule_pdf(
    *, entity, member, loan, rows, totals, generated_on, currency="₵", footer_text=None
):
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=20 * mm,
        title=f"Loan Schedule {_get(loan, 'loan_no', 'PREVIEW')}",
        author=_get(entity, "name", ""),
    )
    doc._footer_text = footer_text or (
        f"Generated {generated_on:%d %b %Y %H:%M} "
        f"{_get(entity, 'name', '')} computer-generated document"
    )

    styles = getSampleStyleSheet()
    h1 = ParagraphStyle(
        "h1",
        parent=styles["Heading1"],
        fontSize=16,
        leading=20,
        textColor=BRAND_DARK,
        spaceAfter=0,
    )
    h2 = ParagraphStyle(
        "h2", parent=styles["Normal"], fontSize=10, textColor=colors.HexColor("#6b7280")
    )
    right = ParagraphStyle(
        "right",
        parent=styles["Normal"],
        alignment=TA_RIGHT,
        fontSize=9,
        textColor=colors.HexColor("#4b5563"),
    )
    small = ParagraphStyle("small", parent=styles["Normal"], fontSize=9)
    center = ParagraphStyle(
        "center",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=8,
        textColor=colors.HexColor("#6b7280"),
    )

    story = []

    # header
    header_left = [
        Paragraph(_get(entity, "name", "Credit Union"), h1),
        Paragraph("Loan Repayment Schedule", h2),
    ]
    header_right = [
        Paragraph(f"Loan No.: <b>{_get(loan, 'loan_no', 'PREVIEW')}</b>", right),
        Paragraph(f"Generated: {generated_on:%d %b %Y %H:%M}", right),
    ]
    header = Table([[header_left, header_right]], colWidths=[110 * mm, 70 * mm])
    header.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    story.append(header)
    story.append(Spacer(1, 3 * mm))
    story.append(
        HRFlowable(width="100%", thickness=1.2, color=BRAND, spaceAfter=4 * mm)
    )

    # member / terms
    terms_data = [
        [
            "Member",
            f"{_get(member, 'full_name', '')}"
            + (
                f"  ({_get(member, 'member_no', '')})"
                if _get(member, "member_no", "")
                else ""
            ),
            "Date Applied",
            f"{_get(loan, 'date_applied', '')}",
        ],
        [
            "Principal",
            f"{currency}{_money(_get(loan, 'principal', 0))}",
            "Interest Rate",
            f"{_get(loan, 'interest_rate', 0)} % / month",
        ],
        [
            "Term",
            f"{_get(loan, 'term_months', 0)} months",
            "Purpose",
            f"{_get(loan, 'purpose', '') or '—'}",
        ],
    ]
    terms = Table(terms_data, colWidths=[25 * mm, 65 * mm, 25 * mm, 65 * mm])
    terms.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.4, GREY_LINE),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, GREY_LINE),
                ("BACKGROUND", (0, 0), (0, -1), GREY_BG),
                ("BACKGROUND", (2, 0), (2, -1), GREY_BG),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(terms)
    story.append(Spacer(1, 5 * mm))

    # summary tiles
    def tile(label, value, fg):
        return [
            Paragraph(
                f'<font size="7" color="{fg.hexval()}"><b>{label.upper()}</b></font>',
                small,
            ),
            Paragraph(
                f'<font size="11" color="{fg.hexval()}"><b>{value}</b></font>', small
            ),
        ]

    monthly = totals.get("installment", 0)
    payable = totals.get("total_payable", 0)
    interest = totals.get("total_interest", 0)
    count = totals.get("count", 0)

    tiles = Table(
        [
            [
                Table(
                    [
                        tile(
                            "Monthly Installment",
                            f"{currency}{_money(monthly)}",
                            BLUE_FG,
                        )
                    ],
                    colWidths=[44 * mm],
                ),
                Table(
                    [tile("Total Payable", f"{currency}{_money(payable)}", GREEN_FG)],
                    colWidths=[44 * mm],
                ),
                Table(
                    [tile("Total Interest", f"{currency}{_money(interest)}", RED_FG)],
                    colWidths=[44 * mm],
                ),
                Table(
                    [tile("Installments", str(count), AMBER_FG)], colWidths=[44 * mm]
                ),
            ]
        ],
        colWidths=[44 * mm] * 4,
    )
    tiles.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, 0), BLUE_BG),
                ("BACKGROUND", (1, 0), (1, 0), GREEN_BG),
                ("BACKGROUND", (2, 0), (2, 0), RED_BG),
                ("BACKGROUND", (3, 0), (3, 0), AMBER_BG),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(tiles)
    story.append(Spacer(1, 5 * mm))

    # amortization
    data = [
        ["#", "Due Date", "Opening", "Principal", "Interest", "Installment", "Closing"]
    ]
    for r in rows:
        due = r["due_date"]
        due_str = due.strftime("%d %b %Y") if hasattr(due, "strftime") else str(due)
        data.append(
            [
                str(r["no"]),
                due_str,
                _money(r["opening"]),
                _money(r["principal"]),
                _money(r["interest"]),
                _money(r["installment"]),
                _money(r["closing"]),
            ]
        )
    data.append(
        [
            "",
            "",
            "",
            _money(totals.get("total_principal", 0)),
            _money(totals.get("total_interest", 0)),
            _money(totals.get("total_payable", 0)),
            "",
        ]
    )

    col_widths = [10 * mm, 26 * mm, 26 * mm, 26 * mm, 24 * mm, 28 * mm, 26 * mm]
    tbl = Table(data, colWidths=col_widths, repeatRows=1)
    tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), GREY_BG),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
                ("ALIGN", (0, 0), (1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.35, GREY_LINE),
                ("FONTSIZE", (0, 1), (-1, -1), 8.5),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("BACKGROUND", (0, -1), (-1, -1), GREY_BG),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ]
        )
    )
    story.append(tbl)
    story.append(Spacer(1, 6 * mm))

    # signatures
    sign = ParagraphStyle(
        "sign",
        parent=styles["Normal"],
        fontSize=8,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#374151"),
    )
    sig = Table(
        [
            [
                Paragraph(
                    "__________________________<br/>Member's Signature / Date", sign
                ),
                Paragraph("__________________________<br/>Witness / Date", sign),
                Paragraph("__________________________<br/>Loan Officer / Date", sign),
            ]
        ],
        colWidths=[60 * mm, 60 * mm, 60 * mm],
    )
    sig.setStyle(
        TableStyle(
            [("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 18)]
        )
    )
    story.append(KeepTogether(sig))
    story.append(Spacer(1, 3 * mm))
    story.append(
        Paragraph(
            "This schedule is computer-generated and is subject to the terms "
            f"of the loan agreement. Amounts shown in {currency}.",
            center,
        )
    )

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return buf.getvalue()
