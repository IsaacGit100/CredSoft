from django.utils import timezone
from .models import ChartOfAccounts, GeneralLedger
from xhtml2pdf import pisa
from openpyxl import Workbook
from django.template.loader import get_template
from decimal import Decimal
from django.db.models import Sum
from django.shortcuts import render

# Create your views here.
# views.py

from django.contrib.admin.views.decorators import staff_member_required

# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Q
from django.http import JsonResponse


from django.contrib.auth.decorators import login_required

# views.py
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
import io
from datetime import datetime



@login_required
@staff_member_required
def income_statement(request):
    """HTML Income Statement (with print styles via @media print)"""
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    if not from_date or not to_date:
        today = timezone.now().date()
        from_date = today.replace(day=1)
        to_date = today

    # Get income and expense accounts (active)
    income_accounts = ChartOfAccounts.objects.filter(
        account_type='INCOME', is_active=True)
    expense_accounts = ChartOfAccounts.objects.filter(
        account_type='EXPENSE', is_active=True)

    income_data = []
    total_income = Decimal('0')
    for account in income_accounts:
        ledger = GeneralLedger.objects.filter(account=account).first()
        if ledger:
            balance = ledger.period_balance if hasattr(
                ledger, 'period_balance') else ledger.current_balance
            if balance > 0:
                total_income += balance
                income_data.append({'account': account, 'amount': balance})

    expense_data = []
    total_expense = Decimal('0')
    for account in expense_accounts:
        ledger = GeneralLedger.objects.filter(account=account).first()
        if ledger:
            balance = ledger.period_balance if hasattr(
                ledger, 'period_balance') else ledger.current_balance
            if balance > 0:
                total_expense += balance
                expense_data.append({'account': account, 'amount': balance})

    net_income = total_income - total_expense

    context = {
        'income_data': income_data,
        'expense_data': expense_data,
        'total_income': total_income,
        'total_expense': total_expense,
        'net_income': net_income,
        'from_date': from_date,
        'to_date': to_date,
    }
    return render(request, 'FinanceApp/income_statement.html', context)


@login_required
@staff_member_required
def inc_state_print(request):
    """Print‑friendly HTML version (uses @media print)"""
    # Same data as the HTML view, but rendered with a print‑optimised template
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    if not from_date or not to_date:
        today = timezone.now().date()
        from_date = today.replace(day=1)
        to_date = today

    income_accounts = ChartOfAccounts.objects.filter(
        account_type='INCOME', is_active=True)
    expense_accounts = ChartOfAccounts.objects.filter(
        account_type='EXPENSE', is_active=True)

    income_data = []
    total_income = Decimal('0')
    for account in income_accounts:
        ledger = GeneralLedger.objects.filter(account=account).first()
        if ledger:
            balance = ledger.period_balance if hasattr(
                ledger, 'period_balance') else ledger.current_balance
            if balance > 0:
                total_income += balance
                income_data.append({'account': account, 'amount': balance})

    expense_data = []
    total_expense = Decimal('0')
    for account in expense_accounts:
        ledger = GeneralLedger.objects.filter(account=account).first()
        if ledger:
            balance = ledger.period_balance if hasattr(
                ledger, 'period_balance') else ledger.current_balance
            if balance > 0:
                total_expense += balance
                expense_data.append({'account': account, 'amount': balance})

    net_income = total_income - total_expense

    context = {
        'income_data': income_data,
        'expense_data': expense_data,
        'total_income': total_income,
        'total_expense': total_expense,
        'net_income': net_income,
        'from_date': from_date,
        'to_date': to_date,
        'generated_date': timezone.now(),
    }
    return render(request, 'FinanceApp/income_statement_print.html', context)


@login_required
@staff_member_required
def inc_state_pdf(request):
    """Generate PDF download"""
    try:
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        if not from_date or not to_date:
            today = timezone.now().date()
            from_date = today.replace(day=1)
            to_date = today

        income_accounts = ChartOfAccounts.objects.filter(
            account_type='INCOME', is_active=True)
        expense_accounts = ChartOfAccounts.objects.filter(
            account_type='EXPENSE', is_active=True)

        income_data = []
        total_income = Decimal('0')
        for account in income_accounts:
            ledger = GeneralLedger.objects.filter(account=account).first()
            if ledger:
                balance = ledger.period_balance if hasattr(
                    ledger, 'period_balance') else ledger.current_balance
                if balance > 0:
                    total_income += balance
                    income_data.append({'account': account, 'amount': balance})

        expense_data = []
        total_expense = Decimal('0')
        for account in expense_accounts:
            ledger = GeneralLedger.objects.filter(account=account).first()
            if ledger:
                balance = ledger.period_balance if hasattr(
                    ledger, 'period_balance') else ledger.current_balance
                if balance > 0:
                    total_expense += balance
                    expense_data.append(
                        {'account': account, 'amount': balance})

        net_income = total_income - total_expense

        context = {
            'income_data': income_data,
            'expense_data': expense_data,
            'total_income': total_income,
            'total_expense': total_expense,
            'net_income': net_income,
            'from_date': from_date,
            'to_date': to_date,
            'generated_date': timezone.now(),
        }

        template = get_template('FinanceApp/income_statement_pdf.html')
        html = template.render(context)
        result = io.BytesIO()
        pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)

        if pdf is None or pdf.err:
            return HttpResponse("PDF generation failed", status=500)

        response = HttpResponse(
            result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="income_statement.pdf"'
        return response

    except Exception as e:
        return HttpResponse(f"Error generating PDF: {str(e)}", status=500)


@login_required
@staff_member_required
def inc_state_excel(request):
    """Generate Excel download"""
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    if not from_date or not to_date:
        today = timezone.now().date()
        from_date = today.replace(day=1)
        to_date = today

    income_accounts = ChartOfAccounts.objects.filter(
        account_type='INCOME', is_active=True)
    expense_accounts = ChartOfAccounts.objects.filter(
        account_type='EXPENSE', is_active=True)

    wb = Workbook()
    ws = wb.active
    ws.title = "Income Statement"
    ws.append(['INCOME STATEMENT'])
    ws.append(['Period:', f'{from_date} to {to_date}'])
    ws.append([])

    ws.append(['INCOME'])
    ws.append(['Account', 'Amount (₵)'])
    total_income = Decimal('0')
    for account in income_accounts:
        ledger = GeneralLedger.objects.filter(account=account).first()
        if ledger:
            balance = ledger.period_balance if hasattr(
                ledger, 'period_balance') else ledger.current_balance
            if balance > 0:
                total_income += balance
                ws.append([account.name, float(balance)])
    ws.append(['Total Income', float(total_income)])

    ws.append([])
    ws.append(['EXPENSES'])
    ws.append(['Account', 'Amount (₵)'])
    total_expense = Decimal('0')
    for account in expense_accounts:
        ledger = GeneralLedger.objects.filter(account=account).first()
        if ledger:
            balance = ledger.period_balance if hasattr(
                ledger, 'period_balance') else ledger.current_balance
            if balance > 0:
                total_expense += balance
                ws.append([account.name, float(balance)])
    ws.append(['Total Expenses', float(total_expense)])

    net_income = total_income - total_expense
    ws.append([])
    ws.append(['NET INCOME (LOSS)', float(net_income)])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="income_statement.xlsx"'
    wb.save(response)
    return response
