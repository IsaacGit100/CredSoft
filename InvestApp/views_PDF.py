# views.py
import io
import datetime
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from . models import Investment

from django.db.models import Sum, Q
from decimal import Decimal
from django.template.loader import get_template
from django.http import HttpResponse


def export_investments_pdf(request):
    # Get filtered data (you'll need to implement the same filtering as in your main view)
    investments = get_filtered_investments(request)

    # Calculate totals (similar to your template)
    total_invested = sum(inv.amount for inv in investments)
    total_interest_expected = sum(inv.interest_expected for inv in investments)
    total_interest_earned = sum(inv.interest_earned for inv in investments)

    # Create a file-like buffer to receive PDF data
    buffer = io.BytesIO()

    # Create the PDF object, using landscape orientation to accommodate the wide table
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
    elements = []

    # Add title
    styles = getSampleStyleSheet()
    title = Paragraph("Investment Portfolio Report", styles['Title'])
    elements.append(title)

    # Add date
    today = datetime.date.today().strftime("%d/%m/%Y")
    date_text = Paragraph(f"Report Date: {today}", styles['Normal'])
    elements.append(date_text)

    # Add some space
    elements.append(Paragraph("<br/><br/>", styles['Normal']))

    # Prepare table data
    table_data = []

    # Table headers
    headers = [
        'Date', 'Cert No', 'Bank/Company', 'Branch', 
        'Investment Amount', 'Rate (%)', 'Period', 
        'Interest Expected', 'Interest Earned'
    ]
    table_data.append(headers)

    # Table rows
    for investment in investments:
        row = [
            investment.date.strftime("%d/%m/%Y"),  # Format date as dd/mm/yyyy
            investment.certificate_no,
            investment.get_bank_company_display(),
            investment.branch,
            f"{investment.amount:,.2f}",  # Format with commas
            f"{investment.rate}%",
            investment.get_period_display(),
            f"{investment.interest_expected:,.2f}",  # Format with commas
            f"{investment.interest_earned:,.2f}"  # Format with commas
        ]
        table_data.append(row)

    # Add totals row
    totals_row = [
        '', '', '', 'TOTAL',
        f"{total_invested:,.2f}",
        '', '',
        f"{total_interest_expected:,.2f}",
        f"{total_interest_earned:,.2f}"
    ]
    table_data.append(totals_row)

    # Create table
    table = Table(table_data)

    # Add style to table
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])

    # Apply the style to the table
    table.setStyle(style)

    # Add the table to the elements
    elements.append(table)

    # Build the PDF
    doc.build(elements)

    # FileResponse sets the Content-Disposition header
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="investment_report.pdf")


from xhtml2pdf import pisa
from openpyxl import Workbook
import io

def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)
    if pdf.err:
        return None
    return result.getvalue()

def quarterly_report_pdf(request):
    year = 2026  # or get from request.GET
    quarterly_data = _build_quarterly_data(year)  # reuse the data building logic
    context = {
        'year': year,
        'quarterly_data': quarterly_data,
        'grand_total_expected': sum(q['total_expected'] for q in quarterly_data),
        'grand_total_earned': sum(q['total_earned'] for q in quarterly_data),
        'total_investments': sum(q['count'] for q in quarterly_data),
    }
    pdf = render_to_pdf('InvestApp/invest_quarterly_report.html', context)
    if pdf is None:
        return HttpResponse("Error generating PDF", status=500)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="quarterly_report_{year}.pdf"'
    return response

def _build_quarterly_data(year):
    quarters = [
        {'name': 'Jan – Mar', 'start': f'{year}-01-01', 'end': f'{year}-03-31'},
        {'name': 'Apr – Jun', 'start': f'{year}-04-01', 'end': f'{year}-06-30'},
        {'name': 'Jul – Sep', 'start': f'{year}-07-01', 'end': f'{year}-09-30'},
        {'name': 'Oct – Dec', 'start': f'{year}-10-01', 'end': f'{year}-12-31'},
    ]
    quarterly_data = []
    for q in quarters:
        investments = Investment.objects.filter(maturity_date__range=[q['start'], q['end']]).order_by('maturity_date')
        total_expected = investments.aggregate(Sum('interest_expected'))['interest_expected__sum'] or Decimal('0')
        total_earned = investments.aggregate(Sum('interest_earned'))['interest_earned__sum'] or Decimal('0')
        quarterly_data.append({
            'name': q['name'],
            'investments': investments,
            'total_expected': total_expected,
            'total_earned': total_earned,
            'count': investments.count(),
        })
    return quarterly_data