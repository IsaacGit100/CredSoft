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
def opening_balance_home(request):
    return render(request, 'FinanceApp/opening_balance_home.html')

@login_required
def finance_reports_home(request, slug):
    return render(request, 'FinanceApp/finance_reports_home.html')

@login_required
def journal_home(request):
    return render(request, 'FinanceApp/journal_home.html')

@login_required
def finance_home(request):
    """Finance module dashboard"""
    
    # Get statistics
    journal_count = JournalEntry.objects.count()
    posted_count = JournalEntry.objects.filter(status='POSTED').count()
    draft_count = JournalEntry.objects.filter(status='DRAFT').count()
    account_count = ChartOfAccounts.objects.filter(is_active=True).count()
    
    context = {
        'journal_count': journal_count,
        'posted_count': posted_count,
        'draft_count': draft_count,
        'account_count': account_count,
        'today': timezone.now(),
    }
    return render(request, 'FinanceApp/finance_home.html', context)

def main_menu(request):
    return render(request, 'main_menu.html')

def trial_balance_print(request):
    pass

def trial_balance_pdf(request):
    pass

def balance_sheet_print(request):
    pass

def balance_sheet_pdf(request):
    pass


def balance_sheet_excel(request):
    pass

from decimal import Decimal
from .models import ChartOfAccounts, GeneralLedger

def get_trial_balance_data(as_at_date=None):
    """
    Build trial balance data: account code, name, debit balance, credit balance.
    Uses opening_balance from GeneralLedger as the base.
    """
    accounts = ChartOfAccounts.objects.filter(is_active=True).order_by('accountno')
    trial_balance = []
    total_debit = Decimal('0.00')
    total_credit = Decimal('0.00')

    for account in accounts:
        ledger = GeneralLedger.objects.filter(account=account).first()
        if ledger:
            # For trial balance, use current_balance (which includes opening + transactions)
            balance = ledger.current_balance
        else:
            balance = Decimal('0.00')

        # Determine if it's a debit or credit balance
        if balance > 0:
            # Assets and Expenses normally have debit balance
            if account.account_type in ['ASSET', 'EXPENSE']:
                debit = balance
                credit = Decimal('0.00')
            else:
                # Liabilities, Equity, Income normally have credit balance
                debit = Decimal('0.00')
                credit = balance
        else:
            debit = Decimal('0.00')
            credit = Decimal('0.00')

        # Only include accounts with non‑zero balance
        if debit != 0 or credit != 0:
            trial_balance.append({
                'account': account,
                'debit': debit,
                'credit': credit,
            })
            total_debit += debit
            total_credit += credit

    difference = total_debit - total_credit
    is_balanced = abs(difference) < Decimal('0.01')

    return {
        'trial_balance': trial_balance,
        'total_debit': total_debit,
        'total_credit': total_credit,
        'difference': difference,
        'is_balanced': is_balanced,
        'as_at_date': as_at_date,
    }
    
    
# FinanceApp/views.py
from django.shortcuts import render
from django.utils import timezone
from .utils import get_trial_balance_data

def trial_balance(request, slug):
    date_str = request.GET.get('as_at_date')
    if date_str:
        from datetime import datetime
        as_at_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        as_at_date = timezone.now().date()

    context = get_trial_balance_data(as_at_date)
    return render(request, 'FinanceApp/trial_balance.html', context)






@login_required
def back_to_home(request, slug):
    """Return to main dashboard"""
    return redirect('/')  # This takes user back to dashboard

# finance/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db import models
from django.db import transaction as db_transaction
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from decimal import Decimal
from datetime import datetime, timedelta
import json

from .models import GeneralLedger, JournalEntry, JournalLine
from coa.models import ChartOfAccounts
from UserAuth.models import User
from RecPayApp.models import Trans as SourceTransaction

# ==================== JOURNAL ENTRY VIEWS ====================

@login_required
@permission_required('finance.view_journalentry')
def journal_entry_list_manage(request, slug):
    """List all journal entries"""
    journals = JournalEntry.objects.select_related('created_by', 'posted_by', 'source_trans').all()
    
    # Filters
    status = request.GET.get('status')
    if status:
        journals = journals.filter(status=status)
    
    date_from = request.GET.get('date_from')
    if date_from:
        journals = journals.filter(entry_date__gte=date_from)
    
    date_to = request.GET.get('date_to')
    if date_to:
        journals = journals.filter(entry_date__lte=date_to)
    
    search = request.GET.get('search')
    if search:
        journals = journals.filter(
            models.Q(entry_number__icontains=search) |
            models.Q(description__icontains=search)
        )
    
    paginator = Paginator(journals.order_by('-entry_date', '-entry_number'), 50)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    
    context = {
        'page_obj': page_obj,
        'status_choices': JournalEntry.STATUS_CHOICES,
        'total_journals': journals.count(),
        'total_draft': journals.filter(status='DRAFT').count(),
        'total_posted': journals.filter(status='POSTED').count(),
        'total_void': journals.filter(status='VOID').count(),
    }
    return render(request, 'FinanceApp/journal_entry_list_manage.html', context)

@login_required
@permission_required('FinanceAdd.add_journalentry')
def journal_create(request, slug):
    """Create a new journal entry"""
    if request.method == 'POST':
        try:
            with db_transaction.atomic():
                # Create journal entry
                entry_date = request.POST.get('entry_date')
                description = request.POST.get('description')
                source_trans_id = request.POST.get('source_trans')
                
                # Generate journal number
                date_str = timezone.now().strftime('%Y%m%d')
                last_journal = JournalEntry.objects.filter(
                    entry_number__startswith=f'JE-{date_str}'
                ).count()
                entry_number = f'JE-{date_str}-{last_journal + 1:04d}'
                
                journal = JournalEntry.objects.create(
                    entry_number=entry_number,
                    entry_date=entry_date,
                    description=description,
                    created_by=request.user,
                    status='DRAFT'
                )
                
                if source_trans_id:
                    journal.source_trans_id = source_trans_id
                    journal.save()
                
                # Create journal lines
                account_ids = request.POST.getlist('account_id[]')
                debit_amounts = request.POST.getlist('debit[]')
                credit_amounts = request.POST.getlist('credit[]')
                descriptions = request.POST.getlist('line_description[]')
                member_ids = request.POST.getlist('member_id[]')
                
                for i, account_id in enumerate(account_ids):
                    if account_id:
                        debit = Decimal(debit_amounts[i]) if debit_amounts[i] else Decimal('0')
                        credit = Decimal(credit_amounts[i]) if credit_amounts[i] else Decimal('0')
                        
                        if debit > 0 or credit > 0:
                            JournalLine.objects.create(
                                journal=journal,
                                account_id=account_id,
                                debit=debit,
                                credit=credit,
                                line_description=descriptions[i] if i < len(descriptions) else '',
                                member_id=member_ids[i] if i < len(member_ids) else None
                            )
                
                messages.success(request, f'Journal entry {journal.entry_number} created as DRAFT!')
                return redirect('FinanceApp:journal_detail', pk=journal.pk)
                
        except Exception as e:
            messages.error(request, f'Error creating journal: {str(e)}')
    
    # GET request - show form
    accounts = ChartOfAccounts.objects.filter(status='ACTIVE').select_related('category')
    source_transactions = SourceTransaction.objects.filter(status='DRAFT')[:20]
    
    context = {
        'accounts': accounts,
        'source_transactions': source_transactions,
        'today': timezone.now().date(),
    }
    return render(request, 'FinanceApp/journal_form.html', context)

@login_required
@permission_required('FinanceApp.view_journalentry')
def journal_detail(request, slug, pk):
    """View journal entry details"""
    journal = get_object_or_404(
        JournalEntry.objects.select_related('created_by', 'posted_by', 'source_trans'),
        pk=pk
    )
    lines = journal.lines.select_related('account', 'member').all()
    
    # Calculate totals
    total_debit = sum(line.debit for line in lines)
    total_credit = sum(line.credit for line in lines)
    
    context = {
        'journal': journal,
        'lines': lines,
        'total_debit': total_debit,
        'total_credit': total_credit,
        'is_balanced': total_debit == total_credit,
        'difference': abs(total_debit - total_credit),
    }
    return render(request, 'FinanceApp/journal_detail.html', context)

@login_required
@permission_required('finance.change_journalentry')
def journal_edit(request, slug, pk):
    """Edit journal entry (only if DRAFT)"""
    journal = get_object_or_404(JournalEntry, pk=pk)
    
    if journal.status != 'DRAFT':
        messages.error(request, 'Only draft journals can be edited!')
        return redirect('FinanceApp:journal_detail', pk=pk)
    
    if request.method == 'POST':
        try:
            with db_transaction.atomic():
                # Update journal header
                journal.entry_date = request.POST.get('entry_date')
                journal.description = request.POST.get('description')
                journal.save()
                
                # Delete existing lines
                journal.lines.all().delete()
                
                # Create new lines
                account_ids = request.POST.getlist('account_id[]')
                debit_amounts = request.POST.getlist('debit[]')
                credit_amounts = request.POST.getlist('credit[]')
                descriptions = request.POST.getlist('line_description[]')
                member_ids = request.POST.getlist('member_id[]')
                
                for i, account_id in enumerate(account_ids):
                    if account_id:
                        debit = Decimal(debit_amounts[i]) if debit_amounts[i] else Decimal('0')
                        credit = Decimal(credit_amounts[i]) if credit_amounts[i] else Decimal('0')
                        
                        if debit > 0 or credit > 0:
                            JournalLine.objects.create(
                                journal=journal,
                                account_id=account_id,
                                debit=debit,
                                credit=credit,
                                line_description=descriptions[i] if i < len(descriptions) else '',
                                member_id=member_ids[i] if i < len(member_ids) else None
                            )
                
                messages.success(request, f'Journal {journal.entry_number} updated successfully!')
                return redirect('FinanceApp:journal_detail', pk=journal.pk)
                
        except Exception as e:
            messages.error(request, f'Error updating journal: {str(e)}')
    
    # GET request
    accounts = ChartOfAccounts.objects.filter(status='ACTIVE').select_related('category')
    lines = journal.lines.select_related('account', 'member').all()
    
    context = {
        'journal': journal,
        'accounts': accounts,
        'lines': lines,
        'today': timezone.now().date(),
    }
    return render(request, 'FinanceApp/journal_edit.html', context)

@login_required
@permission_required('finance.change_journalentry')
def journal_post(request, slug, pk):
    """Post journal to ledger"""
    journal = get_object_or_404(JournalEntry, pk=pk)
    
    if request.method == 'POST':
        if journal.status != 'DRAFT':
            messages.error(request, 'Journal already posted or voided!')
            return redirect('FinanceApp:journal_detail', pk=pk)
        
        # Check if balanced
        if not journal.is_balanced():
            messages.error(request, f'Cannot post unbalanced journal! Debits: {journal.total_debit()}, Credits: {journal.total_credit()}')
            return redirect('FinanceApp:journal_detail', pk=pk)
        
        try:
            journal.post(user=request.user)
            messages.success(request, f'Journal {journal.entry_number} posted to ledger successfully!')
        except Exception as e:
            messages.error(request, f'Error posting journal: {str(e)}')
        
        return redirect('FinanceApp:journal_detail', pk=pk)
    
    context = {'journal': journal}
    return render(request, 'FinanceApp/journal_post_confirm.html', context)

@login_required
@permission_required('FinanceApp.change_journalentry')
def journal_void(request, slug, pk):
    """Void a journal entry"""
    journal = get_object_or_404(JournalEntry, pk=pk)
    
    if request.method == 'POST':
        if journal.status == 'POSTED':
            messages.error(request, 'Cannot void a posted journal! Create a reversing entry instead.')
        else:
            journal.status = 'VOID'
            journal.save()
            messages.success(request, f'Journal {journal.entry_number} voided successfully!')
        
        return redirect('FinanceApp:journal_detail', pk=pk)
    
    context = {'journal': journal}
    return render(request, 'FinanceApp/journal_void_confirm.html', context)

# ==================== GENERAL LEDGER VIEWS ====================

@login_required
@permission_required('FinanceApp.view_generalledger')
def ledger_list(request, slug):
    """View general ledger (all accounts)"""
    ledgers = GeneralLedger.objects.select_related('account', 'account__category').all()
    
    # Filter by account type
    account_type = request.GET.get('account_type')
    if account_type:
        ledgers = ledgers.filter(account__account_type=account_type)
    
    # Filter by category
    category = request.GET.get('category')
    if category:
        ledgers = ledgers.filter(account__category_id=category)
    
    # Search
    search = request.GET.get('search')
    if search:
        ledgers = ledgers.filter(
            models.Q(account__account_code__icontains=search) |
            models.Q(account__account_name__icontains=search)
        )
    
    paginator = Paginator(ledgers.order_by('account__account_code'), 50)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    
    # Calculate totals
    total_debit_balance = 0
    total_credit_balance = 0
    
    for ledger in page_obj:
        if ledger.current_balance > 0:
            if ledger.account.account_type in ['ASSET', 'EXPENSE']:
                total_debit_balance += ledger.current_balance
            else:
                total_credit_balance += ledger.current_balance
        else:
            if ledger.account.account_type in ['ASSET', 'EXPENSE']:
                total_credit_balance += abs(ledger.current_balance)
            else:
                total_debit_balance += abs(ledger.current_balance)
    
    context = {
        'page_obj': page_obj,
        'total_debit_balance': total_debit_balance,
        'total_credit_balance': total_credit_balance,
        'is_balanced': total_debit_balance == total_credit_balance,
        'account_types': ChartOfAccounts.ACCOUNT_TYPES,
    }
    return render(request, 'FinanceApp/ledger_list.html', context)

@login_required
@permission_required('FinanceApp.view_generalledger')
def ledger_detail(request, slug, account_code):
    """View ledger details for a specific account"""
    account = get_object_or_404(ChartOfAccounts, account_code=account_code)
    ledger = get_object_or_404(GeneralLedger, account=account)
    
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
    
    paginator = Paginator(journal_lines, 100)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    
    # Calculate running balance
    running_balance = ledger.opening_balance
    for line in page_obj:
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
    
    context = {
        'account': account,
        'ledger': ledger,
        'page_obj': page_obj,
        'date_from': date_from,
        'date_to': date_to,
    }
    return render(request, 'FinanceApp/ledger_detail.html', context)

# ==================== FINANCIAL REPORTS ====================

@login_required
@permission_required('FinanceApp.view_financialreports')
def trial_balance(request, slug):
    """Generate trial balance report"""
    as_at_date = request.GET.get('as_at_date', timezone.now().date())
    
    # Get all active accounts
    accounts = ChartOfAccounts.objects.filter(status='ACTIVE').select_related('category')
    
    trial_balance_data = []
    total_debit = Decimal('0')
    total_credit = Decimal('0')
    
    for account in accounts:
        ledger = GeneralLedger.objects.filter(account=account).first()
        
        if ledger:
            balance = ledger.current_balance
            if account.account_type in ['ASSET', 'EXPENSE']:
                if balance > 0:
                    total_debit += balance
                else:
                    total_credit += abs(balance)
                
                trial_balance_data.append({
                    'account': account,
                    'debit': balance if balance > 0 else 0,
                    'credit': abs(balance) if balance < 0 else 0,
                })
            else:  # LIABILITY, EQUITY, INCOME
                if balance > 0:
                    total_credit += balance
                else:
                    total_debit += abs(balance)
                
                trial_balance_data.append({
                    'account': account,
                    'debit': abs(balance) if balance < 0 else 0,
                    'credit': balance if balance > 0 else 0,
                })
        else:
            trial_balance_data.append({
                'account': account,
                'debit': 0,
                'credit': 0,
            })
    
    # Group by category
    categories = {}
    for item in trial_balance_data:
        cat_name = item['account'].category.name if item['account'].category else 'Uncategorized'
        if cat_name not in categories:
            categories[cat_name] = {
                'accounts': [],
                'total_debit': Decimal('0'),
                'total_credit': Decimal('0'),
            }
        categories[cat_name]['accounts'].append(item)
        categories[cat_name]['total_debit'] += item['debit']
        categories[cat_name]['total_credit'] += item['credit']
    
    context = {
        'categories': categories,
        'total_debit': total_debit,
        'total_credit': total_credit,
        'is_balanced': total_debit == total_credit,
        'as_at_date': as_at_date,
        'difference': abs(total_debit - total_credit),
    }
    return render(request, 'FinanceApp/trial_balance.html', context)

@login_required
@permission_required('FinanceApp.view_financialreports')
def income_statement(request, slug):
    """Generate income statement (Profit & Loss)"""
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    
    if not from_date or not to_date:
        # Default to current month
        today = timezone.now().date()
        from_date = today.replace(day=1)
        to_date = today
    
    # Get income accounts
    income_accounts = ChartOfAccounts.objects.filter(
        account_type='INCOME',
        status='ACTIVE'
    ).select_related('category')
    
    # Get expense accounts
    expense_accounts = ChartOfAccounts.objects.filter(
        account_type='EXPENSE',
        status='ACTIVE'
    ).select_related('category')
    
    # Calculate income totals
    income_data = []
    total_income = Decimal('0')
    
    for account in income_accounts:
        ledger = GeneralLedger.objects.filter(account=account).first()
        if ledger:
            balance = ledger.period_balance if hasattr(ledger, 'period_balance') else ledger.current_balance
            if balance > 0:
                total_income += balance
                income_data.append({
                    'account': account,
                    'amount': balance,
                })
    
    # Calculate expense totals
    expense_data = []
    total_expense = Decimal('0')
    
    for account in expense_accounts:
        ledger = GeneralLedger.objects.filter(account=account).first()
        if ledger:
            balance = ledger.period_balance if hasattr(ledger, 'period_balance') else ledger.current_balance
            if balance > 0:
                total_expense += balance
                expense_data.append({
                    'account': account,
                    'amount': balance,
                })
    
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
@permission_required('FinanceApp.view_financialreports')
def balance_sheet(request, slug):
    """Generate balance sheet"""
    as_at_date = request.GET.get('as_at_date', timezone.now().date())
    
    # Get asset accounts
    asset_accounts = ChartOfAccounts.objects.filter(
        account_type='ASSET',
        status='ACTIVE'
    ).select_related('category')
    
    # Get liability accounts
    liability_accounts = ChartOfAccounts.objects.filter(
        account_type='LIABILITY',
        status='ACTIVE'
    ).select_related('category')
    
    # Get equity accounts
    equity_accounts = ChartOfAccounts.objects.filter(
        account_type='EQUITY',
        status='ACTIVE'
    ).select_related('category')
    
    # Calculate totals
    total_assets = Decimal('0')
    assets_data = []
    
    for account in asset_accounts:
        ledger = GeneralLedger.objects.filter(account=account).first()
        if ledger:
            balance = ledger.current_balance
            if balance > 0:
                total_assets += balance
                assets_data.append({
                    'account': account,
                    'amount': balance,
                })
    
    total_liabilities = Decimal('0')
    liabilities_data = []
    
    for account in liability_accounts:
        ledger = GeneralLedger.objects.filter(account=account).first()
        if ledger:
            balance = ledger.current_balance
            if balance > 0:
                total_liabilities += balance
                liabilities_data.append({
                    'account': account,
                    'amount': balance,
                })
    
    total_equity = Decimal('0')
    equity_data = []
    
    for account in equity_accounts:
        ledger = GeneralLedger.objects.filter(account=account).first()
        if ledger:
            balance = ledger.current_balance
            if balance > 0:
                total_equity += balance
                equity_data.append({
                    'account': account,
                    'amount': balance,
                })
    
    # Assets should equal Liabilities + Equity
    check = total_assets - (total_liabilities + total_equity)
    
    context = {
        'assets_data': assets_data,
        'liabilities_data': liabilities_data,
        'equity_data': equity_data,
        'total_assets': total_assets,
        'total_liabilities': total_liabilities,
        'total_equity': total_equity,
        'as_at_date': as_at_date,
        'is_balanced': check == 0,
        'difference': check,
    }
    return render(request, 'FinanceApp/balance_sheet.html', context)

# ==================== API ENDPOINTS ====================

@login_required
def api_account_balance(request, slug, account_code):
    """API endpoint to get account balance"""
    try:
        account = ChartOfAccounts.objects.get(account_code=account_code)
        ledger = GeneralLedger.objects.filter(account=account).first()
        
        return JsonResponse({
            'success': True,
            'account_code': account.account_code,
            'account_name': account.account_name,
            'balance': float(ledger.current_balance) if ledger else 0,
            'account_type': account.account_type,
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def api_journal_validate(request, slug):
    """Validate journal entry before saving"""
    if request.method == 'POST':
        data = json.loads(request.body)
        total_debit = Decimal(str(data.get('total_debit', 0)))
        total_credit = Decimal(str(data.get('total_credit', 0)))
        
        return JsonResponse({
            'balanced': total_debit == total_credit,
            'difference': float(abs(total_debit - total_credit)),
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

# ==================== EXPORT FUNCTIONS ====================

@login_required
def export_ledger_csv(request, slug, account_code):
    """Export ledger to CSV"""
    import csv
    from django.http import HttpResponse
    
    account = get_object_or_404(ChartOfAccounts, account_code=account_code)
    journal_lines = JournalLine.objects.filter(
        account=account
    ).select_related('journal').order_by('journal__entry_date')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="ledger_{account_code}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date', 'Journal No', 'Description', 'Debit', 'Credit', 'Member'])
    
    for line in journal_lines:
        writer.writerow([
            line.journal.entry_date,
            line.journal.entry_number,
            line.line_description or line.journal.description,
            float(line.debit),
            float(line.credit),
            line.member.name if line.member else ''
        ])
    
    return response




# ##################################
#   BATCH POSTING VIEWS
# ###################################

# finance/views_batch.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db import models
from django.db import transaction as db_transaction
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from decimal import Decimal
import json
from datetime import datetime

from .models import JournalEntry, JournalLine, GeneralLedger
from coa.models import ChartOfAccounts
from RecPayApp.models import Trans as SourceTransaction

# ==================== BATCH POSTING VIEWS ====================

@login_required
@permission_required('FinanceApp:change_journalentry')
def batch_posting_queue(request, slug):
    """View all pending transactions ready for batch posting"""
    
    # Get all draft journals
    pending_journals = JournalEntry.objects.filter(
        status='DRAFT'
    ).select_related('created_by', 'source_trans').order_by('entry_date', 'created_at')
    
    # Get unposted source transactions (if not yet converted to journals)
    pending_transactions = SourceTransaction.objects.filter(
        status='DRAFT',
        journal_entries__isnull=True  # Not yet converted to journal
    ).select_related('member', 'loan', 'created_by').order_by('transaction_date')
    
    # Summary statistics
    summary = {
        'total_journals': pending_journals.count(),
        'total_transactions': pending_transactions.count(),
        'total_amount': pending_journals.aggregate(total=models.Sum('lines__debit'))['total'] or Decimal('0'),
        'total_journal_amount': pending_journals.aggregate(total=models.Sum('lines__debit'))['total'] or Decimal('0'),
        'total_transaction_amount': pending_transactions.aggregate(total=models.Sum('amount'))['total'] or Decimal('0'),
    }
    
    # Calculate total debit/credit for each journal
    for journal in pending_journals:
        journal.total_debit = journal.lines.aggregate(total=models.Sum('debit'))['total'] or Decimal('0')
        journal.total_credit = journal.lines.aggregate(total=models.Sum('credit'))['total'] or Decimal('0')
        journal.is_balanced = journal.total_debit == journal.total_credit
    
    context = {
        'pending_journals': pending_journals,
        'pending_transactions': pending_transactions,
        'summary': summary,
    }
    return render(request, 'FinanceApp/batch_posting_queue.html', context)

@login_required
@permission_required('finance.change_journalentry')
def batch_posting_review(request, slug):
    """Review all items before batch posting"""
    
    if request.method == 'POST':
        selected_journal_ids = request.POST.getlist('selected_journals[]')
        selected_transaction_ids = request.POST.getlist('selected_transactions[]')
        
        # Get selected items
        selected_journals = JournalEntry.objects.filter(
            id__in=selected_journal_ids,
            status='DRAFT'
        ).select_related('created_by')
        
        selected_transactions = SourceTransaction.objects.filter(
            id__in=selected_transaction_ids,
            status='DRAFT'
        ).select_related('member', 'loan', 'created_by')
        
        # Store in session for posting
        request.session['batch_journal_ids'] = selected_journal_ids
        request.session['batch_transaction_ids'] = selected_transaction_ids
        
        # Prepare review data
        review_data = []
        
        # Add journals
        for journal in selected_journals:
            total_debit = journal.lines.aggregate(total=models.Sum('debit'))['total'] or Decimal('0')
            total_credit = journal.lines.aggregate(total=models.Sum('credit'))['total'] or Decimal('0')
            
            review_data.append({
                'type': 'journal',
                'id': journal.id,
                'number': journal.entry_number,
                'date': journal.entry_date,
                'description': journal.description,
                'amount': total_debit,
                'is_balanced': total_debit == total_credit,
                'lines_count': journal.lines.count(),
            })
        
        # Add transactions
        for transaction in selected_transactions:
            review_data.append({
                'type': 'transaction',
                'id': transaction.id,
                'number': transaction.transaction_number,
                'date': transaction.transaction_date,
                'description': transaction.description,
                'amount': transaction.amount,
                'payment_method': transaction.get_payment_method_display(),
                'transaction_type': transaction.get_transaction_type_display(),
            })
        
        context = {
            'review_data': review_data,
            'total_items': len(review_data),
            'total_amount': sum(item['amount'] for item in review_data),
        }
        return render(request, 'FinanceApp/batch_posting_review.html', context)
    
    return redirect('FinanceApp:batch_posting_queue')

@login_required
@permission_required('FinanceApp.change_journalentry')
def batch_posting_execute(request, slug):
    """Execute batch posting"""
    
    if request.method != 'POST':
        return redirect('FinanceApp:batch_posting_queue')
    
    journal_ids = request.session.get('batch_journal_ids', [])
    transaction_ids = request.session.get('batch_transaction_ids', [])
    
    results = {
        'successful': 0,
        'failed': 0,
        'errors': [],
        'posted_journals': [],
        'posted_transactions': [],
    }
    
    with db_transaction.atomic():
        # Post selected journals
        for journal_id in journal_ids:
            try:
                journal = JournalEntry.objects.get(id=journal_id, status='DRAFT')
                
                # Check if balanced
                total_debit = journal.lines.aggregate(total=models.Sum('debit'))['total'] or Decimal('0')
                total_credit = journal.lines.aggregate(total=models.Sum('credit'))['total'] or Decimal('0')
                
                if total_debit != total_credit:
                    results['failed'] += 1
                    results['errors'].append(f"Journal {journal.entry_number}: Unbalanced (Debit: {total_debit}, Credit: {total_credit})")
                    continue
                
                # Post the journal
                journal.post(user=request.user)
                results['successful'] += 1
                results['posted_journals'].append(journal.entry_number)
                
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"Journal ID {journal_id}: {str(e)}")
        
        # Process transactions (create journals if needed)
        for transaction_id in transaction_ids:
            try:
                transaction = SourceTransaction.objects.get(id=transaction_id, status='DRAFT')
                
                # Check if journal already exists
                if hasattr(transaction, 'journal_entries') and transaction.journal_entries.exists():
                    results['errors'].append(f"Transaction {transaction.transaction_number}: Already has journal")
                    results['failed'] += 1
                    continue
                
                # Create journal from transaction
                journal = create_journal_from_transaction(transaction, request.user)
                
                if journal:
                    results['successful'] += 1
                    results['posted_transactions'].append(transaction.transaction_number)
                else:
                    results['failed'] += 1
                    results['errors'].append(f"Transaction {transaction.transaction_number}: Failed to create journal")
                    
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"Transaction ID {transaction_id}: {str(e)}")
    
    # Clear session data
    request.session.pop('batch_journal_ids', None)
    request.session.pop('batch_transaction_ids', None)
    
    # Store results in session for display
    request.session['batch_results'] = results
    
    return redirect('FinanceApp:batch_posting_results')

@login_required
def batch_posting_results(request, slug):
    """Show batch posting results"""
    results = request.session.get('batch_results', None)
    
    if not results:
        return redirect('FinanceApp:batch_posting_queue')
    
    # Clear results from session after viewing
    request.session.pop('batch_results', None)
    
    context = {
        'results': results,
    }
    return render(request, 'FinanceApp/batch_posting_results.html', context)

@login_required
def create_journal_from_transaction(transaction, slug, user):
    """Helper function to create journal from a transaction"""
    
    # Determine account mappings based on transaction type
    if transaction.transaction_type == 'RECEIPT':
        # Receipt: Debit Cash/Bank, Credit Income or Liability
        return create_receipt_journal(transaction, user)
    
    elif transaction.transaction_type == 'PAYMENT':
        # Payment: Debit Expense/Asset, Credit Cash/Bank
        return create_payment_journal(transaction, user)
    
    elif transaction.transaction_type == 'TRANSFER':
        # Transfer: Debit Destination, Credit Source
        return create_transfer_journal(transaction, user)
    
    return None

def create_receipt_journal(transaction, slug, user):
    """Create journal for receipt transaction"""
    
    # Generate journal number
    date_str = transaction.transaction_date.strftime('%Y%m%d')
    last_journal = JournalEntry.objects.filter(
        entry_number__startswith=f'RCPT-{date_str}'
    ).count()
    entry_number = f'RCPT-{date_str}-{last_journal + 1:04d}'
    
    # Create journal
    journal = JournalEntry.objects.create(
        entry_number=entry_number,
        entry_date=transaction.transaction_date,
        description=f"Receipt: {transaction.description}",
        source_trans=transaction,
        created_by=user,
        status='DRAFT'
    )
    
    # Get accounts based on payment method
    if transaction.payment_method == 'CASH':
        cash_account = ChartOfAccounts.objects.filter(account_code='1111').first()  # Cash on Hand
    elif transaction.payment_method == 'BANK':
        cash_account = ChartOfAccounts.objects.filter(account_code='1112').first()  # Cash at Bank
    elif transaction.payment_method == 'MOMO':
        cash_account = ChartOfAccounts.objects.filter(account_code='1115').first()  # Mobile Money
    else:
        cash_account = ChartOfAccounts.objects.filter(account_code='1111').first()
    
    # Credit account (Member Savings by default)
    credit_account = ChartOfAccounts.objects.filter(account_code='2111').first()  # Member Savings
    
    if cash_account:
        JournalLine.objects.create(
            journal=journal,
            account=cash_account,
            debit=transaction.amount,
            credit=0,
            line_description=f"Received from {transaction.member.name if transaction.member else 'Member'}",
            member=transaction.member
        )
    
    if credit_account:
        JournalLine.objects.create(
            journal=journal,
            account=credit_account,
            debit=0,
            credit=transaction.amount,
            line_description=f"Credit to {credit_account.account_name}",
            member=transaction.member
        )
    
    return journal

def create_payment_journal(transaction, slug, user):
    """Create journal for payment transaction"""
    
    # Generate journal number
    date_str = transaction.transaction_date.strftime('%Y%m%d')
    last_journal = JournalEntry.objects.filter(
        entry_number__startswith=f'PYMT-{date_str}'
    ).count()
    entry_number = f'PYMT-{date_str}-{last_journal + 1:04d}'
    
    # Create journal
    journal = JournalEntry.objects.create(
        entry_number=entry_number,
        entry_date=transaction.transaction_date,
        description=f"Payment: {transaction.description}",
        source_trans=transaction,
        created_by=user,
        status='DRAFT'
    )
    
    # Get cash account based on payment method
    if transaction.payment_method == 'CASH':
        cash_account = ChartOfAccounts.objects.filter(account_code='1111').first()
    elif transaction.payment_method == 'BANK':
        cash_account = ChartOfAccounts.objects.filter(account_code='1112').first()
    elif transaction.payment_method == 'MOMO':
        cash_account = ChartOfAccounts.objects.filter(account_code='1115').first()
    else:
        cash_account = ChartOfAccounts.objects.filter(account_code='1111').first()
    
    # Debit account (Expense by default)
    debit_account = ChartOfAccounts.objects.filter(account_code='5999').first()  # General Expenses
    
    if debit_account:
        JournalLine.objects.create(
            journal=journal,
            account=debit_account,
            debit=transaction.amount,
            credit=0,
            line_description=f"Payment for {transaction.description}",
            member=transaction.member
        )
    
    if cash_account:
        JournalLine.objects.create(
            journal=journal,
            account=cash_account,
            debit=0,
            credit=transaction.amount,
            line_description=f"Paid from {cash_account.account_name}",
            member=transaction.member
        )
    
    return journal

def create_transfer_journal(transaction, slug, user):
    """Create journal for transfer transaction"""
    
    # Generate journal number
    date_str = transaction.transaction_date.strftime('%Y%m%d')
    last_journal = JournalEntry.objects.filter(
        entry_number__startswith=f'TRF-{date_str}'
    ).count()
    entry_number = f'TRF-{date_str}-{last_journal + 1:04d}'
    
    # Create journal
    journal = JournalEntry.objects.create(
        entry_number=entry_number,
        entry_date=transaction.transaction_date,
        description=f"Transfer: {transaction.description}",
        source_trans=transaction,
        created_by=user,
        status='DRAFT'
    )
    
    # For transfers, you'd have source and destination accounts
    # This is a simplified example
    source_account = ChartOfAccounts.objects.filter(account_code='1111').first()  # Cash
    dest_account = ChartOfAccounts.objects.filter(account_code='1112').first()  # Bank
    
    if source_account:
        JournalLine.objects.create(
            journal=journal,
            account=source_account,
            debit=0,
            credit=transaction.amount,
            line_description=f"Transfer from {source_account.account_name}"
        )
    
    if dest_account:
        JournalLine.objects.create(
            journal=journal,
            account=dest_account,
            debit=transaction.amount,
            credit=0,
            line_description=f"Transfer to {dest_account.account_name}"
        )
    
    return journal

# ==================== BULK ACTIONS ====================

@login_required
@permission_required('finance.change_journalentry')
def batch_delete_journals(request, slug):
    """Delete multiple draft journals at once"""
    if request.method == 'POST':
        journal_ids = request.POST.getlist('journal_ids[]')
        
        deleted_count = 0
        errors = []
        
        for journal_id in journal_ids:
            try:
                journal = JournalEntry.objects.get(id=journal_id, status='DRAFT')
                journal.delete()
                deleted_count += 1
            except Exception as e:
                errors.append(str(e))
        
        if deleted_count > 0:
            messages.success(request, f'Successfully deleted {deleted_count} journal(s)')
        if errors:
            messages.error(request, f'Errors: {", ".join(errors)}')
        
        return redirect('FinanceApp:batch_posting_queue')
    
    return redirect('FinanceApp:batch_posting_queue')

@login_required
@permission_required('FinanceApp.change_journalentry')
def batch_validate_all(request, slug):
    """Validate all pending journals before batch posting"""
    
    pending_journals = JournalEntry.objects.filter(status='DRAFT')
    
    validation_results = {
        'total': pending_journals.count(),
        'balanced': 0,
        'unbalanced': 0,
        'has_lines': 0,
        'no_lines': 0,
        'unbalanced_list': [],
    }
    
    for journal in pending_journals:
        total_debit = journal.lines.aggregate(total=models.Sum('debit'))['total'] or Decimal('0')
        total_credit = journal.lines.aggregate(total=models.Sum('credit'))['total'] or Decimal('0')
        
        if journal.lines.count() == 0:
            validation_results['no_lines'] += 1
            validation_results['unbalanced_list'].append({
                'id': journal.id,
                'number': journal.entry_number,
                'issue': 'No journal lines'
            })
        elif total_debit == total_credit:
            validation_results['balanced'] += 1
        else:
            validation_results['unbalanced'] += 1
            validation_results['unbalanced_list'].append({
                'id': journal.id,
                'number': journal.entry_number,
                'debit': float(total_debit),
                'credit': float(total_credit),
                'difference': float(abs(total_debit - total_credit)),
                'issue': 'Unbalanced'
            })
    
    return JsonResponse(validation_results)

@login_required
def batch_posting_status(request, slug):
    """Get real-time status of batch posting"""
    pending_journals = JournalEntry.objects.filter(status='DRAFT').count()
    pending_transactions = SourceTransaction.objects.filter(status='DRAFT').count()
    
    return JsonResponse({
        'pending_journals': pending_journals,
        'pending_transactions': pending_transactions,
        'can_post': pending_journals > 0 or pending_transactions > 0,
    })

from django.shortcuts import render, get_object_or_404
from RecPayApp.models import Trans


def trans_detail(request, slug, pk):
    """View transaction details"""
    transaction = get_object_or_404(Trans, pk=pk)
    context = {
        'transaction': transaction,
    }
    return render(request, 'RecPayApp/transaction_detail.html', context)


# FinanceApp/views.py - Add this to your existing views
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import JournalEntry
from coa.models import ChartOfAccounts

@login_required
def finance_fin_home(request, slug):
    """Finance module home/dashboard page"""
    
    # Get statistics
    journal_count = JournalEntry.objects.count()
    posted_count = JournalEntry.objects.filter(status='POSTED').count()
    draft_count = JournalEntry.objects.filter(status='DRAFT').count()
    account_count = ChartOfAccounts.objects.filter(is_active=True).count()
    
    context = {
        'journal_count': journal_count,
        'posted_count': posted_count,
        'draft_count': draft_count,
        'account_count': account_count,
        'today': timezone.now(),
    }
    return render(request, 'FinanceApp/finance_fin_home.html', context)

# finance/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import JournalEntry
from coa.models import ChartOfAccounts

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import FinancialIndicator

@login_required
def indicators_dashboard(request, slug):
    latest = FinancialIndicator.objects.first()
    context = {'indicator': latest}
    return render(request, 'FinanceApp/indicators.html', context)


from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum

from decimal import Decimal
from datetime import datetime
from calendar import monthrange

@login_required
def monthly_income_statement(request, slug):
    from django_ledger.models import EntityModel, AccountModel, TransactionModel
    entity = get_object_or_404(EntityModel, slug=slug)

    today = datetime.today()
    selected_month = int(request.GET.get('month', today.month))
    selected_year = int(request.GET.get('year', today.year))
    
    months = list(range(1, 13))
    current_year = today.year
    years = list(range(current_year - 5, current_year + 5))  # 5 years back and forward

    # Permission check (same as other views)
    try:
        profile = request.user.djan_led_profile
        if entity not in profile.allowed_entities.all() and entity != profile.default_entity:
            return render(request, 'FinanceApp/access_denied.html', {'entity': entity})
    except:
        pass

    # Get month and year from GET, default to current month
    today = datetime.today()
    selected_month = int(request.GET.get('month', today.month))
    selected_year = int(request.GET.get('year', today.year))

    # Create date range for the selected month
    first_day = datetime(selected_year, selected_month, 1)
    last_day = datetime(selected_year, selected_month, monthrange(selected_year, selected_month)[1])

    # Get all revenue and expense accounts for this entity
    revenue_accounts = AccountModel.objects.filter(
        coa_model__entity=entity,
        role='revenue'
    )
    expense_accounts = AccountModel.objects.filter(
        coa_model__entity=entity,
        role='expense'
    )

    # Compute totals for revenue (credit transactions)
    revenue_total = TransactionModel.objects.filter(
        account__in=revenue_accounts,
        tx_type='credit',
        journal_entry__timestamp__range=[first_day, last_day]
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')

    # Compute totals for expenses (debit transactions)
    expense_total = TransactionModel.objects.filter(
        account__in=expense_accounts,
        tx_type='debit',
        journal_entry__timestamp__range=[first_day, last_day]
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')

    net_income = revenue_total - expense_total

    # For detailed breakdown, get individual account balances
    revenue_breakdown = []
    for acc in revenue_accounts:
        total = TransactionModel.objects.filter(
            account=acc,
            tx_type='credit',
            journal_entry__timestamp__range=[first_day, last_day]
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        if total:
            revenue_breakdown.append({'name': acc.name, 'amount': total})

    expense_breakdown = []
    for acc in expense_accounts:
        total = TransactionModel.objects.filter(
            account=acc,
            tx_type='debit',
            journal_entry__timestamp__range=[first_day, last_day]
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        if total:
            expense_breakdown.append({'name': acc.name, 'amount': total})

    # Prepare month/year for the template
    month_name = first_day.strftime('%B %Y')

    
    
    context = {
        'entity': entity,
        'month_name': first_day.strftime('%B %Y'),
        'selected_month': selected_month,
        'selected_year': selected_year,
        'months': months,
        'years': years,
        'revenue_total': revenue_total,
        'expense_total': expense_total,
        'net_income': net_income,
        'revenue_breakdown': revenue_breakdown,
        'expense_breakdown': expense_breakdown,
        
        
        # ... other context ...
    }
    return render(request, 'FinanceApp/monthly_income_statement.html', context)

from django.db.models import Sum
from datetime import datetime
from dateutil.relativedelta import relativedelta

@login_required
def finance_dashboard(request, slug):
    from django_ledger.models import EntityModel, AccountModel, TransactionModel
    entity = get_object_or_404(EntityModel, slug=slug)

    # Permission check
    try:
        profile = request.user.djan_led_profile
        if entity not in profile.allowed_entities.all() and entity != profile.default_entity:
            return render(request, 'FinanceApp/access_denied.html', {'entity': entity})
    except:
        pass

    # Calculate totals for current month
    today = datetime.today()
    first_day = today.replace(day=1)
    last_day = today

    revenue_accounts = AccountModel.objects.filter(coa_model__entity=entity, role='revenue')
    expense_accounts = AccountModel.objects.filter(coa_model__entity=entity, role='expense')

    revenue_total = TransactionModel.objects.filter(
        account__in=revenue_accounts,
        tx_type='credit',
        journal_entry__timestamp__range=[first_day, last_day]
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')

    expense_total = TransactionModel.objects.filter(
        account__in=expense_accounts,
        tx_type='debit',
        journal_entry__timestamp__range=[first_day, last_day]
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')

    net_income = revenue_total - expense_total

    # Year-to-date (YTD) totals
    ytd_first = today.replace(month=1, day=1)
    ytd_revenue = TransactionModel.objects.filter(
        account__in=revenue_accounts,
        tx_type='credit',
        journal_entry__timestamp__range=[ytd_first, last_day]
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')

    ytd_expense = TransactionModel.objects.filter(
        account__in=expense_accounts,
        tx_type='debit',
        journal_entry__timestamp__range=[ytd_first, last_day]
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')

    ytd_net = ytd_revenue - ytd_expense

    # Transaction count for current month
    transaction_count = TransactionModel.objects.filter(
        journal_entry__ledger__entity=entity,
        journal_entry__timestamp__range=[first_day, last_day]
    ).count()

    context = {
        'entity': entity,
        'month_name': today.strftime('%B %Y'),
        'revenue_total': revenue_total,
        'expense_total': expense_total,
        'net_income': net_income,
        'ytd_revenue': ytd_revenue,
        'ytd_expense': ytd_expense,
        'ytd_net': ytd_net,
        'transaction_count': transaction_count,
    }
    return render(request, 'FinanceApp/finance_dashboard.html', context)