# FinanceApp/views_journal.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from django.core.paginator import Paginator
from django.utils import timezone
from decimal import Decimal
#from .models import JournalEntry, JournalLine
#from django_ledger.models import JournalEntryModel
from coa.models import ChartOfAccounts
from MembersApp.models import Master
#from django_ledger.models import AccountModel, EntityModel

# ============================================================
# JOURNAL ENTRY MANAGEMENT (Header)
# ============================================================

@login_required
def journal_entry_manage(request):
    """Manage all journal entries - List view with filters"""
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
    
    # Statistics
    stats = {
        'total': journals.count(),
        'draft': journals.filter(status='DRAFT').count(),
        'posted': journals.filter(status='POSTED').count(),
        'void': journals.filter(status='VOID').count(),
    }
    
    context = {
        'page_obj': page_obj,
        'stats': stats,
        'status_choices': JournalEntry.STATUS_CHOICES,
    }
    return render(request, 'FinanceApp/journal_entry_manage.html', context)


@login_required
def journal_entry_create(request):
    """Create a new journal entry header"""
    if request.method == 'POST':
        try:
            # Generate entry number if not provided
            entry_number = request.POST.get('entry_number')
            if not entry_number:
                from datetime import datetime
                date_str = datetime.now().strftime('%Y%m%d')
                last = JournalEntry.objects.filter(
                    entry_number__startswith=f'JE-{date_str}'
                ).count()
                entry_number = f'JE-{date_str}-{last + 1:04d}'
            
            journal = JournalEntry.objects.create(
                entry_number=entry_number,
                entry_date=request.POST.get('entry_date'),
                description=request.POST.get('description'),
                status=request.POST.get('status', 'DRAFT'),
                created_by=request.user
            )
            
            messages.success(request, f'Journal Entry {journal.entry_number} created!')
            return redirect('FinanceApp:journal_entry_edit', pk=journal.pk)
            
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    context = {
        'today': timezone.now().date(),
        'status_choices': JournalEntry.STATUS_CHOICES,
    }
    return render(request, 'FinanceApp/journal_entry_create.html', context)


@login_required
def journal_entry_detail(request, pk):
    """View journal entry details"""
    journal = get_object_or_404(JournalEntry, pk=pk)
    lines = journal.lines.select_related('account', 'member').all()
    
    total_debit = sum(line.debit for line in lines)
    total_credit = sum(line.credit for line in lines)
    difference = abs(total_debit - total_credit)
    
    context = {
        'journal': journal,
        'lines': lines,
        'total_debit': total_debit,
        'total_credit': total_credit,
        'is_balanced': total_debit == total_credit,
        'difference': difference,
    }
    return render(request, 'FinanceApp/journal_entry_detail.html', context)


@login_required
def journal_entry_edit(request, pk):
    """Edit journal entry header only (not lines)"""
    journal = get_object_or_404(JournalEntry, pk=pk)
    
    if request.method == 'POST':
        journal.entry_date = request.POST.get('entry_date')
        journal.description = request.POST.get('description')
        journal.status = request.POST.get('status')
        journal.save()
        
        messages.success(request, f'Journal {journal.entry_number} updated!')
        return redirect('finance:journal_entry_detail', pk=journal.pk)
    
    context = {
        'journal': journal,
        'status_choices': JournalEntry.STATUS_CHOICES,
    }
    return render(request, 'FinanceApp/journal_entry_edit.html', context)


@login_required
def journal_entry_delete(request, pk):
    """Delete journal entry (only if DRAFT)"""
    journal = get_object_or_404(JournalEntry, pk=pk)
    
    if request.method == 'POST':
        if journal.status != 'DRAFT':
            messages.error(request, 'Only draft journals can be deleted!')
        else:
            entry_number = journal.entry_number
            journal.delete()
            messages.success(request, f'Journal {entry_number} deleted!')
        return redirect('finance:journal_entry_manage')
    
    context = {'journal': journal}
    return render(request, 'FinanceApp/journal_entry_confirm_delete.html', context)


@login_required
def journal_entry_post(request, pk):
    """Post journal to ledger"""
    journal = get_object_or_404(JournalEntry, pk=pk)
    
    if request.method == 'POST':
        if journal.status != 'DRAFT':
            messages.error(request, 'Journal already posted!')
        elif not journal.is_balanced():
            messages.error(request, 'Cannot post unbalanced journal!')
        else:
            try:
                journal.post(user=request.user)
                messages.success(request, f'Journal {journal.entry_number} posted!')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        
        return redirect('FinanceApp:journal_entry_detail', pk=journal.pk)
    
    context = {'journal': journal}
    return render(request, 'FinanceApp/journal_entry_post_confirm.html', context)


@login_required
def journal_entry_void(request, pk):
    """Void a journal entry"""
    journal = get_object_or_404(JournalEntry, pk=pk)
    
    if request.method == 'POST':
        if journal.status == 'POSTED':
            messages.error(request, 'Cannot void a posted journal!')
        else:
            journal.status = 'VOID'
            journal.save()
            messages.success(request, f'Journal {journal.entry_number} voided!')
        return redirect('FinanceApp:journal_entry_detail', pk=journal.pk)
    
    context = {'journal': journal}
    return render(request, 'FinanceApp/journal_entry_void_confirm.html', context)


# ============================================================
# JOURNAL LINE MANAGEMENT (Details)
# ============================================================

@login_required
def journal_line_manage(request, journal_pk):
    """Manage lines for a specific journal entry"""
    journal = get_object_or_404(JournalEntry, pk=journal_pk)
    lines = journal.lines.select_related('account', 'member').all()
    
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
    return render(request, 'FinanceApp/journal_line_manage.html', context)


@login_required
def journal_line_create(request, journal_pk):
    """Add a new line to journal entry"""
    journal = get_object_or_404(JournalEntry, pk=journal_pk)
    
    if request.method == 'POST':
        debit = Decimal(request.POST.get('debit', 0))
        credit = Decimal(request.POST.get('credit', 0))
        
        if debit == 0 and credit == 0:
            messages.error(request, 'Debit or credit amount required!')
        elif debit > 0 and credit > 0:
            messages.error(request, 'Cannot have both debit and credit!')
        else:
            JournalLine.objects.create(
                journal=journal,
                account_id=request.POST.get('account'),
                member_id=request.POST.get('member') or None,
                debit=debit,
                credit=credit,
                line_description=request.POST.get('line_description', '')
            )
            messages.success(request, 'Journal line added!')
        
        return redirect('FinanceApp:journal_line_manage', journal_pk=journal.pk)
    
    accounts = ChartOfAccounts.objects.filter(is_active=True).order_by('accountno')
    members = Master.objects.filter(is_active=True).order_by('name')
    
    context = {
        'journal': journal,
        'accounts': accounts,
        'members': members,
    }
    return render(request, 'FinanceApp/journal_line_create.html', context)


@login_required
def journal_line_edit(request, journal_pk, line_pk):
    """Edit a specific journal line"""
    journal = get_object_or_404(JournalEntry, pk=journal_pk)
    line = get_object_or_404(JournalLine, pk=line_pk, journal=journal)
    
    if request.method == 'POST':
        debit = Decimal(request.POST.get('debit', 0))
        credit = Decimal(request.POST.get('credit', 0))
        
        if debit == 0 and credit == 0:
            messages.error(request, 'Debit or credit amount required!')
        elif debit > 0 and credit > 0:
            messages.error(request, 'Cannot have both debit and credit!')
        else:
            line.account_id = request.POST.get('account')
            line.member_id = request.POST.get('member') or None
            line.debit = debit
            line.credit = credit
            line.line_description = request.POST.get('line_description', '')
            line.save()
            messages.success(request, 'Journal line updated!')
        
        return redirect('FinanceApp:journal_line_manage', journal_pk=journal.pk)
    
    accounts = ChartOfAccounts.objects.filter(is_active=True).order_by('accountno')
    members = Master.objects.filter(is_active=True).order_by('name')
    
    context = {
        'journal': journal,
        'line': line,
        'accounts': accounts,
        'members': members,
    }
    return render(request, 'FinanceApp/journal_line_edit.html', context)


@login_required
def journal_line_delete(request, journal_pk, line_pk):
    """Delete a journal line"""
    journal = get_object_or_404(JournalEntry, pk=journal_pk)
    line = get_object_or_404(JournalLine, pk=line_pk, journal=journal)
    
    if request.method == 'POST':
        line.delete()
        messages.success(request, 'Journal line deleted!')
        return redirect('FinanceApp:journal_line_manage', journal_pk=journal.pk)
    
    context = {
        'journal': journal,
        'line': line,
    }
    return render(request, 'FinanceApp/journal_line_confirm_delete.html', context)


def journal_entry_detail(request, pk):
    journal = get_object_or_404(JournalEntry, pk=pk)
    
    # journal.source_trans is already a Trans object from RecPayApp
    # No additional code needed!
    
    context = {
        'journal': journal,
        # source_trans is automatically available
    }
    return render(request, 'FinanceApp/journal_entry_detail.html', context)