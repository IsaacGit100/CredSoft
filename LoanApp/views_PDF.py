
# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Sum, Count
from django.utils import timezone
from decimal import Decimal
import json
from datetime import date, datetime, timedelta
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse


from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.rl_settings import underlineWidth

from django.http import HttpResponse


# ## Tables
from .models import Loan, Guarantor
from MembersApp.models import Master


@login_required
def generate_loan_PDF(request, slug, loan_id):
    print("isaac1")
    print(f"DEBUG: Entering generate_loan_PDF with loan_id: {loan_id}")
    print(f"DEBUG: Method: {request.method}")
    print(f"DEBUG: Path: {request.path}")
    """Generate PDF acceptance letter with repayment schedule"""
    loan = get_object_or_404(Loan, id=loan_id)

    # Create the HttpResponse object with PDF headers
    response = HttpResponse(content_type='application/pdf')
    filename = f"loan_acceptance_{loan.id}_{loan.master.full_name.replace(' ', '_')}.pdf"
#    filename = f"loan_acceptance_{loan.id}_{loan.borrower.full_name.replace(' ', '_')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # Create the PDF object
    doc = SimpleDocTemplate(response, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Container for the 'Flowable' objects
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
        leading=12,
    )
    
    centered_style = ParagraphStyle(
        'CustomCentered',
        parent=styles['Normal'],
        fontSize=12,
        alignment=1,  # Center
        spaceAfter=6,
        fontName='Helvetica-Bold',
        textColor=colors.darkblue
    )
    
    right_aligned_style = ParagraphStyle(
        'RightAligned',
        parent=styles['Normal'],
        fontSize=10,
        alignment=2,  # Right alignment
        spaceAfter=6,
    )
    
    bold_style = ParagraphStyle(
        'CustomBold',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
        fontName='Helvetica-Bold',
    )
    
    underlined_bold_style = ParagraphStyle(
        'UnderlinedBold',
        parent=styles['Heading2'],
        fontSize=12,
        alignment=1,
        spaceAfter=12,
        textDecoration='underline',
        fontName='Helvetica-Bold',
    )
    
    # CENTERED LETTER HEADING
    story.append(Paragraph("St. Andrews Co-Operative Credit Union", centered_style))
    story.append(Spacer(1, 8))
    
    # Header Section - Right aligned address
    header_data = [
        [Paragraph("", normal_style), Paragraph("C/o St Andrews Ang. Church", right_aligned_style)],
        [Paragraph("", normal_style), Paragraph("Abbosey Okai – Accra", right_aligned_style)],
        [Paragraph("", normal_style), Paragraph(f"{loan.date_approved}", right_aligned_style)],
    ]
    
    header_table = Table(header_data, colWidths=[4*inch, 2*inch])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    story.append(header_table)
    story.append(Spacer(1, 20))
    
    # Recipient Address
    story.append(Paragraph(f"{loan.master.full_name}", normal_style))
    story.append(Paragraph("St Andrews Credit Union", normal_style))
    story.append(Paragraph("Abbosey Okai", normal_style))
    story.append(Spacer(1, 15))
    
    # Title
    story.append(Paragraph("Dear Sir/Madam", normal_style))
    story.append(Paragraph("<u>APPLICATION FOR LOAN</u>", bold_style))
    story.append(Spacer(1, 10))
    
    # Main content
    content_text = f"""
    This is to inform you that an amount of <b>¢{loan.principal:,.2f}</b> has been approved for you on 
    <b>{loan.date_approved}</b> based on the following conditions:
    """
    story.append(Paragraph(content_text, normal_style))
    story.append(Spacer(1, 10))
    
    # Conditions
    conditions = [
        "a. Interest Rate of 3% per month on reducing balance in a straight line method.",
        "b. You will be charged 1% processing fee on the loan amount",
        "c. The balance on your savings, shares will be frozen during the life of the loan.",
        "d. The amount that has been guaranteed for you will be frozen on your guarantors until that portion of the loan is paid.",
        "e. Failure to pay the loan on the schedule dates will attract a penalty.",
    ]
    
    for condition in conditions:
        story.append(Paragraph(condition, normal_style))
    
    story.append(Spacer(1, 10))
    story.append(Paragraph("Details of the approval is as follows:", normal_style))
    story.append(Spacer(1, 10))
    
    # Calculate processing fee (1%)
    processing_fee = loan.principal * Decimal('0.01')
    
    # Calculate monthly interest
    monthly_interest = (loan.principal * loan.interest_rate / 100) / 12
    
    # Get total guaranteed amount
    total_guaranteed = loan.guarantor_data.get('total_guaranteed', 0) if loan.guarantor_data else 0
    
    # Approval details table with BOLD LABELS
    approval_data = [
        [Paragraph('<b>Principal</b>', bold_style), Paragraph(f'¢{loan.principal:,.2f}', right_aligned_style),
        Paragraph('<b>Purpose</b>', bold_style), loan.purpose or 'Not specified'],
        
        
        [Paragraph('<b>Process Fee (1%)</b>', bold_style), Paragraph(f'¢{processing_fee:,.2f}', right_aligned_style),
        Paragraph('<b>Moratorium</b>', bold_style), Paragraph(f'{loan.moratorium} months', right_aligned_style)],
        
        [Paragraph('<b>Monthly Deduction</b>', bold_style), Paragraph(f'¢{loan.monthly_repayment:,.2f}', right_aligned_style),
        Paragraph('<b>Date Applied</b>', bold_style), Paragraph(str(loan.date_applied), right_aligned_style),],
        
        [Paragraph('<b>Interest Rate-Month</b>', bold_style), Paragraph(f'{loan.interest_rate}%', right_aligned_style), 
        Paragraph('<b>Disburse Date</b>', bold_style), Paragraph(str(loan.disbursement_date), right_aligned_style),],
        
        [Paragraph('<b>Monthly Interest</b>', bold_style), Paragraph(f'¢{monthly_interest:,.2f}', right_aligned_style), 
        Paragraph('<b>Next repay date</b>', bold_style), Paragraph(str(loan.next_repayment_date), right_aligned_style),],
        
        [Paragraph('<b>No. Of Months</b>', bold_style), Paragraph(str(loan.loan_term), right_aligned_style), 
        Paragraph('<b>Amount Guaranteed</b>', bold_style), Paragraph(f'¢{total_guaranteed:,.2f}', right_aligned_style),],
    ]
    
    approval_table = Table(approval_data, colWidths=[1.5*inch, 1.5*inch, 1.2*inch, 1.8*inch])
    approval_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    story.append(approval_table)
    story.append(Spacer(1, 20))
    
    # ACCEPTANCE Section
    story.append(Paragraph("ACCEPTANCE", bold_style))
    story.append(Spacer(1, 10))
    
    acceptance_text = f"""
    I .............................................................................................................. 
    have accepted the loan offer with the attendant conditions and repayment schedule.
    """
    story.append(Paragraph(acceptance_text, normal_style))
    story.append(Spacer(1, 15))
    
    # Signature lines
    signature_data = [
        ['Signed .............................................................................', 'Date .............................................'],
        ['Approved By .........................................................', 'Signature ...................................... Date ....................'],
    ]
    
    signature_table = Table(signature_data, colWidths=[3*inch, 3*inch])
    signature_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    story.append(signature_table)
    story.append(Spacer(1, 10))
    
    # Repayment Schedule Section
    story.append(Paragraph("Repayment Schedule attached.", bold_style))
    
    # Generate repayment schedule
    story.append(PageBreak())
    story.append(Paragraph("REPAYMENT SCHEDULE", bold_style))
    story.append(Spacer(1, 10))
    
    # Generate repayment schedule data with BOLD HEADERS
    schedule_data = [[
        Paragraph('<b>Month</b>', bold_style), 
        Paragraph('<b>Date</b>', bold_style), 
        Paragraph('<b>Beginning Balance</b>', bold_style), 
        Paragraph('<b>Principal</b>', bold_style), 
        Paragraph('<b>Interest</b>', bold_style), 
        Paragraph('<b>Total Payment</b>', bold_style), 
        Paragraph('<b>Ending Balance</b>', bold_style)
    ]]
    
    try:
        repayment_schedule = loan.generate_repayment_schedule()
        for payment in repayment_schedule:
            schedule_data.append([
                str(payment['month']),
                str(payment['date']),
                f"¢{payment.get('balance', 0):,.2f}",
                f"¢{payment.get('principal', 0):,.2f}",
                f"¢{payment.get('interest', 0):,.2f}",
                f"¢{payment.get('total_payment', 0):,.2f}",
                f"¢{payment.get('balance', 0) - payment.get('principal', 0):,.2f}",
            ])
           
    except:
        # Fallback if repayment schedule generation fails
        balance = float(loan.principal)
        monthly_rate = float(loan.interest_rate) / 100 / 12
        monthly_payment = float(loan.monthly_repayment)
        current_date = loan.disbursement_date
        
        for month in range(1, loan.loan_term + 1):
            interest = balance * monthly_rate
            principal_payment = monthly_payment - interest
            
            if principal_payment > balance:
                principal_payment = balance
                
            total_payment = principal_payment + interest
            ending_balance = balance - principal_payment
            
            # Calculate next date (approximately 30 days per month)
            from datetime import timedelta
            next_date = current_date + timedelta(days=30*month)
            
            schedule_data.append([
                str(month),
                next_date.strftime('%Y-%m-%d'),
                f"¢{balance:,.2f}",
                f"¢{principal_payment:,.2f}",
                f"¢{interest:,.2f}",
                f"¢{total_payment:,.2f}",
                f"¢{ending_balance:,.2f}",
            ])
            
            balance = ending_balance
            if balance <= 0:
                break
    
    # Create repayment schedule table
    schedule_table = Table(schedule_data, colWidths=[0.5*inch, 1*inch, 1*inch, 0.8*inch, 0.8*inch, 1*inch, 1*inch])
    schedule_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    
    story.append(schedule_table)
    
    # Build PDF
    doc.build(story)
    
    return response




@login_required
def gua_list_pdf(request, slug):
    """Export loans list as PDF"""
    # Get loans data
#    loans = Loan.objects.select_related('master').all()
    loans = Loan.objects.all()
    # Create PDF in memory
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    # Add title
    styles = getSampleStyleSheet()
    title = Paragraph("LOAN LIST REPORT", styles['Heading1'])
    elements.append(title)
    
    # Prepare data for table
    data = [['Loan ID', 'Member', 'Principal', 'Int Rate', 'Term', 'Shortfall', 'Guarantors', 'Guarantee Total']]
    
    for loan in loans:
        # Format guarantor info
        guarantor_info = "No guarantors"
        if loan.guarantor_count > 0:
        # Access raw guarantor data
            if hasattr(loan, 'guarantor_data') and loan.guarantor_data:
                guarantors = loan.guarantor_data.get('guarantors', [])
                if guarantors:
                    guarantor_names = [g.get('name', 'Unknown') for g in guarantors[:2]]
                    guarantor_info = f"{len(guarantors)} guarantors"
                    if guarantor_names:
                        guarantor_info += f" ({', '.join(guarantor_names)})"
            else:
                guarantor_info = "No guarantors"
        else:
        # Fallback to the string property
            guarantor_info = loan.guarantee_details  # No parentheses!
        
        data.append([
            loan.id,
            f"{loan.master_name} (ID: {loan.master_id})",
            f"¢{loan.loan_balance}",
            f"{loan.interest_rate}%",
            f"{loan.loan_term} months",
            f"¢{loan.shortfall}",
            guarantor_info,
            f"¢{loan.total_guaranteed}"
        ])
    
    # Create table
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(table)
    
    # Build PDF
    doc.build(elements)
    
    # Create response
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="loan_list.pdf"'
    return response

import pandas as pd
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
from .models import Loan

@login_required
def loan_list_financials_pdf(request, slug):
    """Generate PDF of all loans"""
    loans = Loan.objects.select_related('master').all()
    
    # Calculate totals
    total_principal = sum(loan.principal for loan in loans)
    total_interest = sum(loan.tot_int or 0 for loan in loans)
    total_repayable = sum(loan.tot_ded or 0 for loan in loans)
    total_balance = sum(loan.loan_balance or 0 for loan in loans)
    total_due_interest = sum(loan.due_interest or 0 for loan in loans)
    total_due_repayment = sum(loan.due_repayment or 0 for loan in loans)
    total_monthly_repayment = sum(loan.monthly_repayment or 0 for loan in loans)
    
    context = {
        'loans': loans,
        'total_principal': total_principal,
        'total_interest': total_interest,
        'total_repayable': total_repayable,
        'total_balance': total_balance,
        'total_due_interest': total_due_interest,
        'total_due_repayment': total_due_repayment,
        'total_monthly_repayment': total_monthly_repayment,
        'generated_date': datetime.now(),
        'user': request.user,
    }
    
    template = get_template('LoanApp/loan_list_financials_pdf.html')
    html = template.render(context)
    
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="loans_report.pdf"'
        return response
    
    return HttpResponse('Error generating PDF', status=400)




