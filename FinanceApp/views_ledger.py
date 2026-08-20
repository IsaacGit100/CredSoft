# FinanceApp/views_ledger.py
from django.shortcuts import render
from .models import ChartOfAccounts, GeneralLedger
import io
from xhtml2pdf import pisa
from openpyxl import Workbook
from django.template.loader import get_template
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import models
from decimal import Decimal
from django.utils import timezone
from django.db.models import Count, Q, Sum

from .models import GeneralLedger, JournalLine
from coa.models import ChartOfAccounts
from RecPayApp.models import Trans

## ============================Helper Functions =====================================
from decimal import Decimal
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils import timezone
from .models import ChartOfAccounts, GeneralLedger

# ----- Helper function -----


def get_ledger_data(request, slug):
    """Common logic to fetch and prepare ledger data for reports."""
    accounts = ChartOfAccounts.objects.filter(
        is_active=True).order_by('accountno')
    ledger_data = []
    total_debit = Decimal('0')
    total_credit = Decimal('0')

    for account in accounts:
        ledger = GeneralLedger.objects.filter(account=account).first()
        balance = ledger.current_balance if ledger else Decimal('0')

        # Determine debit/credit based on account type
        if account.account_type in ['ASSET', 'EXPENSE']:
            debit_balance = balance if balance > 0 else Decimal('0')
            credit_balance = abs(balance) if balance < 0 else Decimal('0')
        else:
            credit_balance = balance if balance > 0 else Decimal('0')
            debit_balance = abs(balance) if balance < 0 else Decimal('0')

        # Include if non-zero or important types
        if balance != 0 or account.account_type in ['ASSET', 'LIABILITY', 'EQUITY']:
            ledger_data.append({
                'account': account,
                'ledger': ledger,
                'balance': balance,
                'debit_balance': debit_balance,
                'credit_balance': credit_balance,
            })
            total_debit += debit_balance
            total_credit += credit_balance

    # Apply filters
    account_type = request.GET.get('account_type')
    if account_type:
        ledger_data = [
            item for item in ledger_data if item['account'].account_type == account_type]

    search = request.GET.get('search')
    if search:
        search_lower = search.lower()
        ledger_data = [
            item for item in ledger_data
            if search_lower in item['account'].accountno.lower()
            or search_lower in item['account'].name.lower()
        ]

    return {
        'ledger_data': ledger_data,
        'total_debit': total_debit,
        'total_credit': total_credit,
        'total_accounts': len(ledger_data),
    }





## ==================================== General Ledger List ==================================
@login_required
def ledger_list(request, slug):
    """Display all general ledger accounts with their balances"""
    
    # Get all active accounts with their ledger balances
    accounts = ChartOfAccounts.objects.filter(is_active=True).order_by('accountno')
    
    ledger_data = []
    total_debit_balance = Decimal('0')
    total_credit_balance = Decimal('0')
    
    for account in accounts:
        # Get ledger record for this account
        ledger = GeneralLedger.objects.filter(account=account).first()
        
        if ledger:
            balance = ledger.current_balance
        else:
            balance = Decimal('0')
        
        # Determine if balance is debit or credit based on account type
        if account.account_type in ['ASSET', 'EXPENSE']:
            # Assets and Expenses normally have debit balance
            debit_balance = balance if balance > 0 else Decimal('0')
            credit_balance = abs(balance) if balance < 0 else Decimal('0')
        else:
            # Liabilities, Equity, Income normally have credit balance
            credit_balance = balance if balance > 0 else Decimal('0')
            debit_balance = abs(balance) if balance < 0 else Decimal('0')
        
        # Only show accounts with non-zero balance or specific types
        if balance != 0 or account.account_type in ['ASSET', 'LIABILITY', 'EQUITY']:
            ledger_data.append({
                'account': account,
                'ledger': ledger,
                'balance': balance,
                'debit_balance': debit_balance,
                'credit_balance': credit_balance,
                'formatted_no': format_account_number(account.accountno),
            })
            
            total_debit_balance += debit_balance
            total_credit_balance += credit_balance
    
    # Pagination
    paginator = Paginator(ledger_data, 50)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    
    # Filters
    account_type = request.GET.get('account_type')
    if account_type:
        page_obj.object_list = [item for item in page_obj.object_list if item['account'].account_type == account_type]
    
    search = request.GET.get('search')
    if search:
        page_obj.object_list = [
            item for item in page_obj.object_list 
            if search.lower() in item['account'].accountno.lower() 
            or search.lower() in item['account'].name.lower()
        ]
    
    context = {
        'page_obj': page_obj,
        'total_debit_balance': total_debit_balance,
        'total_credit_balance': total_credit_balance,
        'total_accounts': len(ledger_data),
        'account_types': ChartOfAccounts.ACCOUNT_TYPES,
        'today': timezone.now(),
    }
    return render(request, 'FinanceApp/ledger_list.html', context)


# Existing ledger_list view (HTML)


@login_required
def ledger_list(request, slug):
    data = get_ledger_data(request)
    # Paginate
    from django.core.paginator import Paginator
    paginator = Paginator(data['ledger_data'], 50)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)

    context = {
        'page_obj': page_obj,
        'total_debit_balance': data['total_debit'],
        'total_credit_balance': data['total_credit'],
        'total_accounts': data['total_accounts'],
        'account_types': ChartOfAccounts.ACCOUNT_TYPES,
        'today': timezone.now(),
    }
    return render(request, 'FinanceApp/ledger_list.html', context)


@login_required
def ledger_list_print(request, slug):
    """Print‑friendly version (with @media print)"""
    data = get_ledger_data(request)
    context = {
        'ledger_data': data['ledger_data'],
        'total_debit': data['total_debit'],
        'total_credit': data['total_credit'],
        'total_accounts': data['total_accounts'],
        'generated_date': timezone.now(),
    }
    return render(request, 'FinanceApp/ledger_list_print.html', context)


@login_required
def ledger_list_pdf(request, slug):
    """Generate PDF download"""
    try:
        data = get_ledger_data(request)
        context = {
            'ledger_data': data['ledger_data'],
            'total_debit': data['total_debit'],
            'total_credit': data['total_credit'],
            'total_accounts': data['total_accounts'],
            'generated_date': timezone.now(),
        }
        template = get_template('FinanceApp/ledger_list_pdf.html')
        html = template.render(context)
        result = io.BytesIO()
        pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)

        if pdf is None or pdf.err:
            return HttpResponse("PDF generation failed", status=500)

        response = HttpResponse(
            result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="general_ledger.pdf"'
        return response

    except Exception as e:
        return HttpResponse(f"Error generating PDF: {str(e)}", status=500)


@login_required
def ledger_list_excel(request, slug):
    """Generate Excel download"""
    data = get_ledger_data(request)
    wb = Workbook()
    ws = wb.active
    ws.title = "General Ledger"

    # Headers
    ws.append(['Account Code', 'Account Name', 'Account Type',
              'Debit (₵)', 'Credit (₵)', 'Balance (₵)'])

    for item in data['ledger_data']:
        ws.append([
            item['account'].accountno,
            item['account'].name,
            item['account'].account_type,
            float(item['debit_balance']),
            float(item['credit_balance']),
            float(item['balance']),
        ])

    ws.append([])
    ws.append(['TOTAL', '', '', float(data['total_debit']),
              float(data['total_credit']), ''])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="general_ledger.xlsx"'
    wb.save(response)
    return response





from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

def ledger_account_detail(request, slug, account_id):
    try:
        account = ChartOfAccounts.objects.get(id=account_id)
    except ChartOfAccounts.DoesNotExist:
        messages.error(request, "Account not found.")
        return redirect('FinanceApp:ledger_opening_balance')
    ledger = GeneralLedger.objects.filter(account=account).first()
    context = {
        'account': account,
        'ledger': ledger,
    }
    return render(request, 'FinanceApp/ledger_account_detail.html', context)

@login_required
def ledger_account_detail9(request, slug, account_code):
    """View detailed ledger entries for a specific account"""
    
    account = get_object_or_404(ChartOfAccounts, accountno=account_code)
    ledger = GeneralLedger.objects.filter(account=account).first()
    
    # Get all journal lines for this account
    journal_lines = JournalLine.objects.filter(
        account=account
    ).select_related('journal', 'member').order_by('-journal__entry_date', '-created_at')
    
    # Date filters
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if date_from:
        journal_lines = journal_lines.filter(journal__entry_date__gte=date_from)
    if date_to:
        journal_lines = journal_lines.filter(journal__entry_date__lte=date_to)
    
    # Calculate running balance
    running_balance = ledger.opening_balance if ledger else Decimal('0')
    
    for line in journal_lines:
        if line.debit > 0:
            if account.account_type in ['ASSET', 'EXPENSE']:
                running_balance += line.debit
            else:
                running_balance -= line.debit
        else:
            if account.account_type in ['ASSET', 'EXPENSE']:
                running_balance -= line.credit
            else:
                running_balance += line.credit
        line.running_balance = running_balance
    
    paginator = Paginator(journal_lines, 100)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    
    context = {
        'account': account,
        'ledger': ledger,
        'page_obj': page_obj,
        'date_from': date_from,
        'date_to': date_to,
        'formatted_no': format_account_number(account.accountno),
    }
    return render(request, 'FinanceApp/ledger_account_detail.html', context)


def format_account_number(accountno):
    """Format 8-digit account number to X-XX-XX-XXX format"""
    if len(accountno) == 8:
        return f"{accountno[0]}-{accountno[1:3]}-{accountno[3:5]}-{accountno[5:8]}"
    return accountno

def ledger_balances(request, slug):
    ledgers = GeneralLedger.objects.select_related('account').all()
    context = {'ledgers': ledgers}
    return render(request, 'FinanceApp/ledger_balances.html', context)

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods
from .models import ChartOfAccounts, GeneralLedger
from .forms import LedgerOpeningBalanceForm


from django.contrib import messages

@staff_member_required
def ledger_opening_balance(request, slug):
    account = None
    ledger = None
    form = None
    message = None

    # GET parameter for account selection
    if 'account_id' in request.GET:
        account_id = request.GET.get('account_id')
        try:
            account = ChartOfAccounts.objects.get(id=account_id)
            ledger, created = GeneralLedger.objects.get_or_create(account=account)
        except ChartOfAccounts.DoesNotExist:
            messages.error(request, "Account not found. Please select a valid account.")
            return redirect('FinanceApp:ledger_opening_balance')

    # POST request (form submission)
    if request.method == 'POST':
        account_id = request.POST.get('account_id')
        if not account_id:
            messages.error(request, "No account selected.")
            return redirect('FinanceApp:ledger_opening_balance')
        try:
            account = ChartOfAccounts.objects.get(id=account_id)
            ledger, created = GeneralLedger.objects.get_or_create(account=account)
        except ChartOfAccounts.DoesNotExist:
            messages.error(request, "Invalid account. Please select a valid account.")
            return redirect('FinanceApp:ledger_opening_balance')

        form = LedgerOpeningBalanceForm(request.POST, instance=ledger)
        if form.is_valid():
            form.save()
            messages.success(request, f"Opening balance for {account.name} updated successfully.")
            # Optionally redirect to the detail page of the same account
            return redirect('FinanceApp:ledger_account_detail', account_id=account.id)
        else:
            messages.error(request, "Please correct the errors below.")

    # If we have an account and ledger but no form yet (GET after selection)
    if account and ledger and not form:
        form = LedgerOpeningBalanceForm(instance=ledger)

    context = {
        'account': account,
        'form': form,
        'account_id': account.id if account else None,
    }
    return render(request, 'FinanceApp/ledger_open_bal.html', context)





@staff_member_required
def account_autocomplete(request, slug):
    """Return JSON list of accounts matching the search term (for autocomplete)."""
    q = request.GET.get('q', '')
    if len(q) < 2:
        return JsonResponse([], safe=False)
    accounts = ChartOfAccounts.objects.filter(
        name__icontains=q
    )[:20].values('id', 'name', 'accountno')
    return JsonResponse(list(accounts), safe=False)

from django.db.models import Q
from django.utils import timezone
from .models import GeneralLedger, ChartOfAccounts
from decimal import Decimal

def ledger_statement(request):
    ledgers = GeneralLedger.objects.select_related('account').all().order_by('account__accountno')

    # Filters
    account_type = request.GET.get('account_type', '')
    if account_type:
        ledgers = ledgers.filter(account__account_type=account_type)

    min_balance = request.GET.get('min_balance', '')
    if min_balance:
        try:
            ledgers = ledgers.filter(current_balance__gte=Decimal(min_balance))
        except:
            pass

    max_balance = request.GET.get('max_balance', '')
    if max_balance:
        try:
            ledgers = ledgers.filter(current_balance__lte=Decimal(max_balance))
        except:
            pass

    search = request.GET.get('search', '')
    if search:
        ledgers = ledgers.filter(
            Q(account__accountno__icontains=search) |
            Q(account__name__icontains=search)
        )

    # Totals
    total_debit_balance = ledgers.filter(account__account_type='ASSET').aggregate(total=Sum('current_balance'))['total'] or Decimal('0')
    total_credit_balance = ledgers.filter(account__account_type='LIABILITY').aggregate(total=Sum('current_balance'))['total'] or Decimal('0')
    net_balance = total_debit_balance - total_credit_balance

    context = {
        'ledgers': ledgers,
        'total_debit_balance': total_debit_balance,
        'total_credit_balance': total_credit_balance,
        'net_balance': net_balance,
        'account_types': ChartOfAccounts.account_type,  # if defined in model
    }
    return render(request, 'FinanceApp/ledger_statement.html', context)


## ==================================Trans JournalLine JournalEntry List =======================

from django.db.models import Q
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from openpyxl import Workbook


def trans_journ_report(request):
    # Base queryset: only POSTED transactions that have a journal entry
    trans_list = Trans.objects.filter(status='POSTED', journal_entries__isnull=False).distinct()
    
    
    # Filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    batch = request.GET.get('batch')
    
    if start_date:
        trans_list = trans_list.filter(date__gte=start_date)
    if end_date:
        trans_list = trans_list.filter(date__lte=end_date)
    if batch:
        trans_list = trans_list.filter(batch_number=batch)
    
    # Order by date
    trans_list = trans_list.order_by('-date', '-id')
    
    # Build flattened data: each row = one journal line
    report_lines = []
    for trans in trans_list:
        # Each trans has exactly one journal entry (source_trans)
        journal = trans.journal_entries.first()  # use related_name
        try:
            account = ChartOfAccounts.objects.get(accountno=trans.ledger_code)
            ledger = GeneralLedger.objects.filter(account=account).first()
            if ledger:
                ledger_bal = ledger.current_balance
            else:
                ledger_bal = Decimal('0.00')
        except ChartOfAccounts.DoesNotExist:
            ledger_bal = Decimal('0.00')
        
        if not journal:
            continue
        for line in journal.lines.all():
            report_lines.append({
                'trans_voucher': trans.rec_vou_no,
                'trans_date': trans.date,
                'trans_amount': trans.amount,
                'trans_ledger': trans.ledger_name or trans.ledger_code,
                'trans_batch_no': trans.batch_number,
                'journal_entry': journal.entry_number,
                'account_code': line.account.accountno,
                'account_name': line.account.name,
                'debit': line.debit,
                'credit': line.credit,
                'ledger_bal': ledger_bal
            })
    
    context = {
        'report_lines': report_lines,
        'start_date': start_date,
        'end_date': end_date,
        'batch': batch,
        'total_debit': sum(l['debit'] for l in report_lines),
        'total_credit': sum(l['credit'] for l in report_lines),
    }
    return render(request, 'FinanceApp/trans_journ_report.html', context)


def trans_journ_report_pdf(request):
    # Same logic as above, then render PDF
    # ... (copy filtering logic)
    # (We'll refactor to a common function later)
    # Base queryset: only POSTED transactions that have a journal entry
    trans_list = Trans.objects.filter(status='POSTED', journal_entries__isnull=False).distinct()
    
    
    # Filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    batch = request.GET.get('batch')
    
    if start_date:
        trans_list = trans_list.filter(date__gte=start_date)
    if end_date:
        trans_list = trans_list.filter(date__lte=end_date)
    if batch:
        trans_list = trans_list.filter(batch_number=batch)
    
    # Order by date
    trans_list = trans_list.order_by('-date', '-id')
    
    # Build flattened data: each row = one journal line
    report_lines = []
    for trans in trans_list:
        # Each trans has exactly one journal entry (source_trans)
        journal = trans.journal_entries.first()  # use related_name
        if not journal:
            continue
        for line in journal.lines.all():
            report_lines.append({
                'trans_voucher': trans.rec_vou_no,
                'trans_date': trans.date,
                'trans_amount': trans.amount,
                'trans_ledger': trans.ledger_name or trans.ledger_code,
                'journal_entry': journal.entry_number,
                'account_code': line.account.accountno,
                'account_name': line.account.name,
                'debit': line.debit,
                'credit': line.credit,
            })

    
    
    
    
    
    context = {
        'report_lines': report_lines,
        'total_debit': sum(l['debit'] for l in report_lines),
        'total_credit': sum(l['credit'] for l in report_lines),
        
        'start_date': start_date,
        'end_date': end_date,
        'batch': batch,
    }
    
    template = get_template('FinanceApp/trans_journ_report_pdf.html')
    html = template.render(context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="transaction_journal_report.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('PDF error', status=500)
    return response


def trans_journ_report_excel(request):
    # Get filtered trans_list (same as HTML view)
    trans_list = Trans.objects.filter(status='POSTED', journal_entries__isnull=False).distinct()
    # Apply filters (start_date, end_date, batch) as needed...
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Transaction Journal Report"
    ws.append(['Voucher', 'Date', 'Amount', 'Ledger', 'Journal Entry', 'Account Code', 'Account Name', 'Debit', 'Credit'])
    
    total_debit = 0
    total_credit = 0
    
    for trans in trans_list:
        journal = trans.journal_entries.first()
        if not journal:
            continue
        for line in journal.lines.all():
            debit = float(line.debit)
            credit = float(line.credit)
            total_debit += debit
            total_credit += credit
            ws.append([
                trans.rec_vou_no,
                trans.date.strftime('%Y-%m-%d'),
                float(trans.amount),
                trans.ledger_name or trans.ledger_code,
                journal.entry_number,
                line.account.accountno,
                line.account.name,
                debit,
                credit,
            ])
    
    ws.append(['', '', '', '', '', '', 'TOTALS', total_debit, total_credit])
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="transaction_journal_report.xlsx"'
    wb.save(response)
    return response

def get_transaction_journal_lines(request):
    qs = Trans.objects.filter(status='POSTED', journal_entries__isnull=False).distinct()
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    batch = request.GET.get('batch')
    if start_date:
        qs = qs.filter(date__gte=start_date)
    if end_date:
        qs = qs.filter(date__lte=end_date)
    if batch:
        qs = qs.filter(batch_number=batch)
    qs = qs.order_by('-date', '-id')
    lines = []
    for trans in qs:
        journal = trans.journal_entries.first()
        if not journal:
            continue
        for line in journal.lines.all():
            lines.append({
                'trans_voucher': trans.rec_vou_no,
                'trans_date': trans.date,
                'trans_amount': trans.amount,
                'trans_ledger': trans.ledger_name or trans.ledger_code,
                'journal_entry': journal.entry_number,
                'account_code': line.account.accountno,
                'account_name': line.account.name,
                'debit': line.debit,
                'credit': line.credit,
            })
    return lines, (start_date, end_date, batch)



