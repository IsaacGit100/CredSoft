# views.py
import xlwt
import urllib.parse
from django.http import HttpResponse
from datetime import datetime
from django.http import HttpResponse
from . models import Investment

from django.db.models import Sum, Q
from decimal import Decimal
from django.template.loader import get_template
from django.http import HttpResponse
from openpyxl import Workbook

def invest_export_excel(request):
    # Get filtered data
    investments = get_filtered_investments(request)

    # Create the HttpResponse object with the appropriate Excel header
    response = HttpResponse(content_type='application/ms-excel')
    filename = urllib.parse.quote('investment_report.xls')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # Create a workbook and add a worksheet
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Investment Report')

    # Set up styles
    header_style = xlwt.easyxf(
        'font: bold on; align: vert centre, horiz center; pattern: pattern solid, fore-color yellow;'
    )
    date_style = xlwt.easyxf(num_format_str='DD/MM/YYYY')
    currency_style = xlwt.easyxf(num_format_str='#,##0.00')
    bold_currency_style = xlwt.easyxf(num_format_str='#,##0.00')
    #bold_currency_style = xlwt.easyxf(num_format_str='#,##0.00', font='bold on')
    # Write headers
    headers = [
        'Date', 'Cert No', 'Bank/Company', 'Branch', 
        'Investment Amount', 'Rate (%)', 'Period', 
        'Interest Expected', 'Interest Earned'
    ]

    for col, header in enumerate(headers):
        ws.write(0, col, header, header_style)
        # Set column width
        ws.col(col).width = 256 * 15  # 15 characters wide

    # Write data rows
    for row, investment in enumerate(investments, start=1):
        ws.write(row, 0, investment.date, date_style)
        ws.write(row, 1, investment.certificate_no)
        ws.write(row, 2, investment.get_bank_company_display())
        ws.write(row, 3, investment.branch)
        ws.write(row, 4, investment.amount, currency_style)
        ws.write(row, 5, investment.rate)
        ws.write(row, 6, investment.get_period_display())
        ws.write(row, 7, investment.interest_expected, currency_style)
        ws.write(row, 8, investment.interest_earned, currency_style)

    # Write totals row
    total_invested = sum(inv.amount for inv in investments)
    total_interest_expected = sum(inv.interest_expected for inv in investments)
    total_interest_earned = sum(inv.interest_earned for inv in investments)

    last_row = len(investments) + 1
    ws.write(last_row, 3, 'TOTAL', header_style)
    ws.write(last_row, 4, total_invested, bold_currency_style)
    ws.write(last_row, 7, total_interest_expected, bold_currency_style)
    ws.write(last_row, 8, total_interest_earned, bold_currency_style)

    # Save the workbook to the HttpResponse
    wb.save(response)
    return response


def quarterly_report_excel(request):
    year = 2026
    quarterly_data = _build_quarterly_data(year)
    wb = Workbook()
    ws = wb.active
    ws.title = f"Quarterly Report {year}"
    ws.append(['Quarter', 'Cert No', 'Bank/Company', 'Branch', 'Amount', 'Maturity Date', 'Interest Expected', 'Interest Earned'])
    for q in quarterly_data:
        for inv in q['investments']:
            ws.append([q['name'], inv.certificate_no, inv.get_bank_company_display(), inv.branch, 
                       float(inv.amount), inv.maturity_date.strftime('%d/%m/%Y'), 
                       float(inv.interest_expected), float(inv.interest_earned)])
        ws.append([f"Total for {q['name']}", '', '', '', '', '', float(q['total_expected']), float(q['total_earned'])])
        ws.append([])  # blank row
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="quarterly_report_{year}.xlsx"'
    wb.save(response)
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