from django.shortcuts import render
from django.db import models

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, Q, Count, F
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from decimal import Decimal

import re
import io

from django.utils.dateparse import parse_date
from django.contrib import messages
from django.utils import timezone
from datetime import datetime

from django.core.paginator import Paginator

from django import template
register = template.Library()

from django.http import HttpResponse
from django.shortcuts import render
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
import io


from reportlab.lib import colors
from io import BytesIO
from datetime import datetime
from .models import Trans
from django_ledger.models import (
    EntityModel,
    LedgerModel,
    JournalEntryModel,
    AccountModel,
    TransactionModel,
)

import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter

import json

## Import Tables
from .models import Trans
from MembersApp.models import Master
from UserAuth.models import User
from coa.models import ChartOfAccounts
from LoanApp.models import Loan

## Import Views
from . import views
from . import views_pdf
from . import views_excel


def trans_all_pdf(request, slug):
    """Generate PDF for ALL transactions - with clean payment details"""

    # Get all transactions ordered by date
    transactions = Trans.objects.all().order_by("-date", "-id")

    # Calculate totals
    total_receipts = (
        transactions.filter(trans_type="Receipts").aggregate(total=Sum("amount"))[
            "total"
        ]
        or 0
    )
    total_payments = (
        transactions.filter(trans_type="Payments").aggregate(total=Sum("amount"))[
            "total"
        ]
        or 0
    )
    net_balance = total_receipts - total_payments

    # Create buffer
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30,
    )

    elements = []

    # Styles
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "Title",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=14,
        alignment=TA_CENTER,
        spaceAfter=4,
        textColor=colors.black,
    )

    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        alignment=TA_CENTER,
        spaceAfter=8,
        textColor=colors.black,
    )

    normal_style = ParagraphStyle(
        "Normal",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7,
        spaceBefore=1,
        spaceAfter=1,
        leading=9,
        textColor=colors.black,
    )

    bold_style = ParagraphStyle(
        "Bold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7,
        spaceBefore=1,
        spaceAfter=1,
        textColor=colors.black,
    )

    # ===== TITLE SECTION =====
    elements.append(Paragraph("ST. ANDREWS CO-OPERATIVE CREDIT UNION", title_style))
    elements.append(
        Paragraph("COMPREHENSIVE FINANCIAL TRANSACTIONS REPORT", subtitle_style)
    )
    elements.append(
        Paragraph(
            f"Generated: {datetime.now().strftime('%d/%m/%Y %H:%M')}", normal_style
        )
    )
    elements.append(Spacer(1, 0.1 * inch))

    # ===== SUMMARY STATISTICS =====
    summary_data = [
        ["Summary", "Count", "Total (₵)"],
        [
            "Receipts",
            transactions.filter(trans_type="Receipts").count(),
            f"{total_receipts:,.2f}",
        ],
        [
            "Payments",
            transactions.filter(trans_type="Payments").count(),
            f"{total_payments:,.2f}",
        ],
        ["Net Balance", "", f"{net_balance:,.2f}"],
        ["Total Records", transactions.count(), ""],
    ]

    summary_table = Table(summary_data, colWidths=[2 * inch, 1 * inch, 1.5 * inch])
    summary_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("ALIGN", (1, 0), (2, -1), "RIGHT"),
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.black),
                ("LINEABOVE", (0, -1), (-1, -1), 0.5, colors.black),
            ]
        )
    )
    elements.append(summary_table)
    elements.append(Spacer(1, 0.15 * inch))

    # ===== TRANSACTIONS TABLE =====
    elements.append(Paragraph("DETAILED TRANSACTIONS", bold_style))
    elements.append(Spacer(1, 0.05 * inch))

    # TABLE HEADERS
    table_data = [
        [
            "Date",
            "ID",
            "Reference",
            "Mem ID",
            "Member/Name",
            "Code",
            "Ledger",
            "Ln ID",
            "Details",
            "Receipts (₵)",
            "Payments (₵)",
            "Payment Details",
        ]
    ]

    # Add transaction rows
    for t in transactions:
        # Get member/name
        if t.member:
            member_id = t.member.id
            person = t.member_name or f"{t.member.first_name} {t.member.last_name}"
        elif t.non_member_name:
            member_id = "-"
            person = t.non_member_name
        else:
            member_id = "-"
            person = "-"

        # Format amounts
        if t.trans_type == "Receipts":
            receipts = f"{t.amount:,.2f}"
            payments = ""
        else:
            receipts = ""
            payments = f"{t.amount:,.2f}"

        # Get CLEAN payment details - just values separated by colons
        payment_details = ""
        if t.pay_mode == "Cheque":
            details = []
            if t.cheque_no:
                details.append(f"{t.cheque_no}")
            if t.cheque_date:
                details.append(f"{t.cheque_date.strftime('%d/%m/%Y')}")
            if t.bank:
                details.append(f"{t.bank}")
            if t.bank_branch:
                details.append(f"{t.bank_branch}")
            if t.bank_no:
                details.append(f"{t.bank_no}")
            payment_details = " : ".join(details) if details else "CASH"
        elif t.pay_mode == "Transfer":
            details = []
            if t.momo_no:
                details.append(f"{t.momo_no}")
            if t.momo_name:
                details.append(f"{t.momo_name}")
            payment_details = " : ".join(details) if details else "CASH"
        else:  # Cash
            payment_details = "CASH"

        # Truncate long fields
        person_display = person[:22] + ".." if len(person) > 22 else person
        ledger_name_display = (
            (t.ledger_name or "-")[:18] + ".."
            if t.ledger_name and len(t.ledger_name) > 18
            else (t.ledger_name or "-")
        )
        details_display = (
            (t.details or "-")[:18] + ".."
            if t.details and len(t.details) > 18
            else (t.details or "-")
        )

        table_data.append(
            [
                t.date.strftime("%d/%m/%y"),
                t.id,
                t.rec_vou_no or "-",
                member_id,
                person_display,
                t.ledger_code or "-",
                ledger_name_display,
                t.loan_id or "-",
                details_display,
                receipts,
                payments,
                payment_details,
            ]
        )

    # Add totals row
    table_data.append(
        [
            "TOTAL",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            f"{total_receipts:,.2f}",
            f"{total_payments:,.2f}",
            f"NET: ₵{net_balance:,.2f}",
        ]
    )

    # Column widths
    col_widths = [
        0.5 * inch,  # Date
        0.3 * inch,  # ID
        0.7 * inch,  # Reference
        0.4 * inch,  # Mem ID
        1.2 * inch,  # Member/Name
        0.5 * inch,  # Code
        1.0 * inch,  # Ledger
        1.0 * inch,  # Details
        0.8 * inch,  # Receipts
        0.8 * inch,  # Payments
        2.5 * inch,  # Payment Details
    ]

    transaction_table = Table(table_data, colWidths=col_widths, repeatRows=1)

    # Table style
    style = [
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 6),
        ("ALIGN", (0, 1), (3, -2), "CENTER"),
        ("ALIGN", (4, 1), (4, -2), "LEFT"),
        ("ALIGN", (5, 1), (7, -2), "LEFT"),
        ("ALIGN", (8, 1), (9, -2), "RIGHT"),
        ("ALIGN", (10, 1), (10, -2), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.black),
        ("LINEABOVE", (0, -1), (-1, -1), 0.5, colors.black),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
    ]

    # Alternating row backgrounds
    for i in range(1, len(table_data) - 1):
        if i % 2 == 0:
            style.append(
                ("BACKGROUND", (0, i), (-1, i), colors.Color(0.95, 0.95, 0.95))
            )

    transaction_table.setStyle(TableStyle(style))
    elements.append(transaction_table)
    elements.append(Spacer(1, 0.1 * inch))

    # Footer
    elements.append(Paragraph("-" * 130, normal_style))
    elements.append(
        Paragraph(
            f"RECEIPTS: ₵{total_receipts:,.2f} | PAYMENTS: ₵{total_payments:,.2f} | NET: ₵{net_balance:,.2f} | "
            f"COUNT: {transactions.count()}",
            normal_style,
        )
    )

    doc.build(elements)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="transactions_{datetime.now().strftime("%Y%m%d_%H%M")}.pdf"'
    )

    return response


def trans_view_pdf(request, slug, pk):
    """Using tables for perfect column alignment"""
    transaction = get_object_or_404(Trans, pk=pk)
    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    y = height - 40
    
    # TITLE
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width/2, y, "TRANSACTION DETAILS")
    y -= 25
    p.setFont("Helvetica", 12)
    p.drawCentredString(width/2, y, f"Type: {transaction.trans_type} | Date: {transaction.date.strftime('%d-%b-%Y')}")
    y -= 30
    
    # ===== SECTION 1: TRANSACTION INFORMATION =====
    section_title(p, 50, y, "1. Transaction Information")
    y -= 25
    
    # Create table data
    data1 = [
        ["Transaction ID:", str(transaction.id), "Receipt/Voucher No:", transaction.trans_no or "N/A"],
        ["Transaction Type:", transaction.trans_type, "Member No:", str(transaction.member_no) if transaction.member_no else "N/A"],
        ["Member Name:", transaction.member_name or "N/A", "Non Member Name:", transaction.non_member_name or "N/A"],
        ["Non Member Contact:", transaction.non_member_contact or "N/A", "", ""]
    ]
    
    # Draw table
    col_widths = [100, 150, 100, 150]
    table_height = draw_table(p, 50, y, data1, col_widths, row_height=20)
    y -= table_height + 20
    
    # ===== SECTION 2: FINANCIAL INFORMATION =====
    section_title(p, 50, y, "2. Financial Information")
    y -= 25
    
    data2 = [
        ["Amount:", f"GH₵ {transaction.amount:,.2f}", "Payment Mode:", transaction.pay_mode],
        ["Receipts:", f"GH₵ {transaction.receipts:,.2f}", "Payments:", f"GH₵ {transaction.payments:,.2f}"]
    ]
    
    table_height = draw_table(p, 50, y, data2, col_widths, row_height=20)
    y -= table_height + 20
    
    # ===== SECTION 3: PAYMENT DETAILS =====
    section_title(p, 50, y, "3. Payment Details")
    y -= 25
    
    data3 = []
    if transaction.pay_mode in ['Cheque', 'Transfer']:
        data3.append(["Bank:", transaction.bank or "N/A", "Account/Cheque No:", transaction.bank_no or "N/A"])
        data3.append(["Bank Branch:", transaction.bank_branch or "N/A", "", ""])
    
    if transaction.momo_no:
        data3.append(["MoMo Number:", transaction.momo_no or "N/A", "MoMo Name:", transaction.momo_name or "N/A"])
    
    if data3:
        table_height = draw_table(p, 50, y, data3, col_widths, row_height=20)
        y -= table_height + 20
    else:
        y -= 10
    
    # ===== SECTION 4: PURPOSE AND DETAILS =====
    section_title(p, 50, y, "4. Purpose and Other Details")
    y -= 25
    
    data4 = [
        ["Purpose:", transaction.purpose, "Other Purpose:", transaction.other_purpose or "N/A"],
        ["Details:", transaction.details or "N/A", "", ""],
        ["Ledger ID:", transaction.ledger_id or "N/A", "Ledger Name:", transaction.ledger_name or "N/A"]
    ]
    
    if transaction.account:
        data4.append(["Chart of Account:", str(transaction.account)[:30], "", ""])
    
    table_height = draw_table(p, 50, y, data4, col_widths, row_height=20)
    y -= table_height + 20
    
    # ===== SECTION 5: LOAN DETAILS =====
    section_title(p, 50, y, "5. Loan Details")
    y -= 25
    
    data5 = []
    if transaction.loan_id or transaction.loan_name:
        data5.append(["Loan ID:", str(transaction.loan_id) if transaction.loan_id else "N/A", 
                     "Loan Name:", transaction.loan_name or "N/A"])
    else:
        data5.append(["Loan Details:", "No loan information", "", ""])
    
    table_height = draw_table(p, 50, y, data5, col_widths, row_height=20)
    y -= table_height + 20
    
    # ===== SECTION 6: SYSTEM INFORMATION =====
    section_title(p, 50, y, "6. System Information")
    y -= 25
    
    data6 = [
        ["Created At:", transaction.created_at.strftime('%d-%b-%Y %I:%M %p'), 
         "Updated At:", transaction.updated_at.strftime('%d-%b-%Y %I:%M %p')],
        ["Report Generated:", datetime.now().strftime('%d-%b-%Y %I:%M %p'), "", ""]
    ]
    
    table_height = draw_table(p, 50, y, data6, col_widths, row_height=20)
    
    # FOOTER
    footer_y = 60
    p.line(60, footer_y, 250, footer_y)
    p.setFont("Helvetica", 10)
    p.drawString(60, footer_y - 15, "Authorized Signature")
    
    p.setFont("Helvetica", 8)
    p.drawRightString(width - 50, 40, f"Page 1 of 1 | Ref: TRANS-{transaction.id}")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return FileResponse(buffer, filename=f"Transaction_{transaction.id}.pdf")


@login_required
def trans_pdf(request, slug, pk):
    """Export single transaction as PDF"""
    
    transaction = get_object_or_404(Trans, pk=pk)
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1.5*cm, bottomMargin=1.5*cm)
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=10)
    label_style = ParagraphStyle('Label', parent=styles['Normal'], fontSize=10, fontName='Helvetica-Bold')
    
    elements = []
    
    # Header
    elements.append(Paragraph("ST. ANDREWS CO-OPERATIVE CREDIT UNION", title_style))
    elements.append(Paragraph("Transaction Receipt", title_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Transaction Details
    data = [
        ["Transaction Number:", transaction.trans_no],
        ["Receipt/Voucher No:", transaction.rec_vou_no],
        ["Date:", transaction.date.strftime('%d/%m/%Y')],
        ["Type:", transaction.trans_type],
        ["Amount:", f"₵{transaction.amount:,.2f}"],
        ["Payment Mode:", transaction.pay_mode],
        ["Status:", transaction.status],
    ]
    
    table = Table(data, colWidths=[4*cm, 8*cm])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Party Information
    party_data = [
        ["Party Information", ""],
        ["Name Type:", "Member" if transaction.member else "Non-Member"],
        ["Name:", transaction.member.full_name if transaction.member else transaction.non_member_name],
    ]
    
    if transaction.member:
        party_data.append(["Member ID:", transaction.member.id])
        party_data.append(["Phone:", transaction.member.telephone1 or "-"])
    
    party_table = Table(party_data, colWidths=[4*cm, 8*cm])
    party_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
    ]))
    elements.append(party_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Accounting Information
    accounting_data = [
        ["Accounting Information", ""],
        ["Ledger Account:", f"{transaction.ledger_code} - {transaction.ledger_name}"],
        ["Description:", transaction.details or "-"],
    ]
    
    accounting_table = Table(accounting_data, colWidths=[4*cm, 8*cm])
    accounting_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
    ]))
    elements.append(accounting_table)
    
    # Footer
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", normal_style))
    
    doc.build(elements)
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Transaction_{transaction.trans_no}_{datetime.now().strftime("%Y%m%d")}.pdf"'
    return response
