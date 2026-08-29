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
from django.utils.dateparse import parse_date
from django.contrib import messages
from django.utils import timezone
from datetime import datetime

from django.core.paginator import Paginator

from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa

import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from MembersApp.models import Master
from . forms import BaseTransForm
from djan_led.utils import get_visible_accounts

from django_ledger.models.entity import EntityModelValidationError


# Or import everything
# Import Services
# from services.services_trans_posting import TransactionProcessor, process_transaction

from django import template
register = template.Library()

import json

## Import Tables
from .models import Trans
from MembersApp.models import Master
from UserAuth.models import User
from coa.models import ChartOfAccounts
from LoanApp.models import Loan
from django_ledger.models import EntityModel, LedgerModel, JournalEntryModel, AccountModel, TransactionModel

## Import Views
from . import views
from . import views_pdf
from . import views_excel

# ==================== API ENDPOINTS ====================

# RecPayApp/views.py
@ login_required
def recpay_home(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    return render(request, "RecPayApp/recpay_home.html", {"entity": entity})

@ login_required
def trans_view_pending(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    pass


@ login_required
def trans_home(request, slug):
    """ Return To Trans Menu """
    return render(request, 'RecPayApp/trans_home.html')


@login_required
def back_to_home(request, slug):
    """Return to main dashboard"""
    return redirect('/')  # This takes user back to dashboard


@login_required
def api_member_loans(request, slug, member_id):
    """AJAX endpoint to get member's active loans"""
    
    try:
        member = Master.objects.get(id=member_id)
        
        # Get active loans (status = 'New Loan' or 'Active')
        loans = Loan.objects.filter(
            master=member,
            status__in=['New Loan', 'Active']
        )
        
        loan_list = []
        for loan in loans:
            loan_list.append({
                'id': loan.id,  # ← Use 'id' as the identifier
                'loan_display': f"Loan #{loan.id}",  # ← Display text
                'principal': float(loan.principal),
                'balance': float(loan.loan_balance),  # ← Use loan_balance
                'interest_rate': float(loan.interest_rate) if loan.interest_rate else 0,
                'disbursement_date': loan.disbursement_date.strftime('%Y-%m-%d') if loan.disbursement_date else None,
            })
        
        return JsonResponse({
            'success': True,
            'loans': loan_list
        })
    except Master.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Member not found'}, status=404)

@login_required 
def api_member_info(request, slug, member_id):
    """AJAX endpoint to get member information"""
    
    try:
        member = Master.objects.get(id=member_id)
        return JsonResponse({
            'success': True,
            'id': member.id,
            'name': member.full_name,
            'balance': float(member.available_balance),
            'phone': member.telephone1 or '',
            'email': member.email_address or '',
        })
    except Master.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Member not found'}, status=404)

# ## ============================================ Trans Create =============================
@login_required
def trans_create(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    accounts = get_visible_accounts(request.user, entity)
    
    try:
        coa = entity.get_default_coa()
    except EntityModelValidationError:
        messages.error(request, "This entity does not have a Chart of Accounts. Please create one first.")
        return redirect('djan_led:chart_of_accounts', slug=entity.slug)

    accounts = get_visible_accounts(request.user, entity)
    
    if not coa:
        messages.error(request, "No Chart of Accounts found for this entity. Please autofill first.")
        return redirect('chart_of_accounts', slug=entity.slug)
    accounts = AccountModel.objects.filter(coa_model=coa, active=True, depth__gt=1).order_by('code')

    # accounts = AccountModel.objects.filter(coa_model=coa, active=True).exclude(role='root').order_by('code')

    members = Master.objects.filter(is_deleted=False).order_by('last_name', 'first_name')

    selected_member_id = request.GET.get('member_id') or request.POST.get('member_id')
    selected_member = None
    active_loans = []

    if selected_member_id and selected_member_id.isdigit():
        try:
            selected_member = Master.objects.get(id=int(selected_member_id))

            #  CORRECT: Get loans with status 'Active' OR 'New Loan'
            active_loans = Loan.objects.filter(
                master=selected_member,
                status__in=['Active', 'New Loan']  # ← This is the key!
            ).order_by('-disbursement_date')

            print(f"Found {active_loans.count()} active/new loans for {selected_member.full_name}")
            for loan in active_loans:
                print(f"  Loan: {loan.id}, Status: {loan.status}, Balance: {loan.loan_balance}")

        except Master.DoesNotExist:
            print(f"Member with ID {selected_member_id} not found")
            active_loans = []

    # ... rest of your code
    else:
        print("No valid member ID selected")

    # Get all transactions for display
    transactions = Trans.objects.all().order_by('-date', '-id')

    # Calculate statistics
    total_records = transactions.count()
    receipts = transactions.filter(trans_type='Receipts')
    payments = transactions.filter(trans_type='Payments')

    receipts_count = receipts.count()
    payments_count = payments.count()
    receipts_total = receipts.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    payments_total = payments.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

    # Pagination
    paginator = Paginator(transactions, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == 'POST':
        if 'close' in request.POST:
            return redirect('RecPayApp:trans_home', entity.slug)

        if 'save' in request.POST:
            try:
                # Debug print all POST data
                print("\n=== POST DATA ===")
                for key, value in request.POST.items():
                    print(f"{key}: {value}")

                # ====================
                # 1. GET FORM DATA
                # ====================
                date_str = request.POST.get('date', '').strip()
                trans_no = request.POST.get('trans_no', '').strip()
                trans_type = request.POST.get('trans_type', '')
                amount_str = request.POST.get('amount', '0').strip()
                pay_mode = request.POST.get('pay_mode', '')
                name_type = request.POST.get('name_type', '')
                details = request.POST.get('details', '').strip()

                # Generate Receipt / Voucher No
                if trans_type == "Receipts":
                    rec_vou_no = f"REC:{trans_no}"
                else:
                    rec_vou_no = f"VOU:{trans_no}"

                # ====================
                # 2. PARSE AMOUNT
                # ====================
                amount_clean = amount_str.replace(',', '').replace(' ', '')
                try:
                    amount = Decimal(amount_clean)
                except:
                    messages.error(request, "Invalid amount format")
                    return redirect('RecPayApp:trans_create', entity.slug)

                # ====================
                # 3. PARSE DATE
                # ====================
                date = None
                for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d']:
                    try:
                        date = datetime.strptime(date_str, fmt).date()
                        break
                    except ValueError:
                        continue

                if not date:
                    messages.error(request, "Invalid date format. Use DD/MM/YYYY")
                    return redirect('RecPayApp:trans_create', entity.slug)

                # ====================
                # 4. PARSE CHEQUE DATE (if provided)
                # ====================
                cheque_date = None
                cheque_date_str = ''
                cheque_date_str = request.POST.get('cheque_date', '').strip()
                if cheque_date_str:
                    for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d']:
                        try:
                            cheque_date = datetime.strptime(cheque_date_str, fmt).date()
                            break
                        except ValueError:
                            continue

                # ====================
                # 5. HANDLE MEMBER/NON-MEMBER
                # ====================
                member_obj = None
                member_no = None
                member_name = ""

                if name_type == 'Member':
                    member_id = request.POST.get('member_id', '')
                    if member_id and member_id.isdigit():
                        try:
                            member_obj = Master.objects.get(id=int(member_id))
                            member_no = member_obj.id
                            member_name = f"{member_obj.first_name} {member_obj.last_name}"
                        except Master.DoesNotExist:
                            member_no = None

                # Get non-member data
                non_member_name = request.POST.get('non_member_name', '').strip()
                non_member_contact = request.POST.get('non_member_contact', '').strip()

                # ====================
                # 6. HANDLE LEDGER
                # ====================
                chart_account_value = request.POST.get('chart_account', '').strip()
                ledger_id = ""
                ledger_code = ""
                ledger_name = ""

                if chart_account_value:
                    parts = chart_account_value.split(',')
                    if len(parts) == 3:
                        ledger_id = parts[0].strip()
                        ledger_code = parts[1].strip()
                        ledger_name = parts[2].strip()

                # ====================
                # 7. HANDLE LOAN
                # ====================
                # In your trans_create view
                # Get the loan ID from POST

                loan_obj = None  

                if ledger_name and ('loan repayments' in ledger_name.lower() or 'loan disbursements' in ledger_name.lower()):
                    loan_id_value = request.POST.get('loan_id', '')
                    loan_obj = None

                    if loan_id_value and loan_id_value.isdigit():
                        try:
                            loan_obj = Loan.objects.get(id=int(loan_id_value))
                            print(f"Selected loan ID: {loan_obj.id}, Balance: {loan_obj.loan_balance}")
                        except Loan.DoesNotExist:
                            print(f"Loan with ID {loan_id_value} not found")
                            loan_obj = None

                # ====================
                # 8. HANDLE USERS
                # ====================
                # Record created by User

                username = request.user.username
                user_full_name = request.user.get_full_name()
                user_id = request.user.id

                # ====================
                # 8. HANDLE PAYMENT METHOD - COMPLETE FIX
                # ====================
                # Get all payment fields
                bank = request.POST.get('bank', '').strip()
                bank_no = request.POST.get('bank_no', '').strip()
                bank_branch = request.POST.get('bank_branch', '').strip()
                momo_no = request.POST.get('momo_no', '').strip()
                momo_name = request.POST.get('momo_name', '').strip()
                cheque_no = request.POST.get('cheque_no', '').strip()
                cheque_date = None

                # Debug print
                print(f"DEBUG - Pay Mode selected: {pay_mode}")

                # ONLY populate fields based on payment mode
                if pay_mode == 'Cheque':
                    # Parse cheque date ONLY for Cheque transactions
                    cheque_date_str = request.POST.get('cheque_date', '').strip()
                    if cheque_date_str:
                        for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d']:
                            try:
                                cheque_date = datetime.strptime(cheque_date_str, fmt).date()
                                print(f"DEBUG - Cheque date parsed: {cheque_date}")
                                break
                            except ValueError:
                                continue

                    # Keep cheque fields, clear transfer fields
                    momo_no = ''
                    momo_name = ''
                    print("DEBUG - Cheque mode: Keeping cheque fields")

                elif pay_mode == 'Cash':
                    # Clear ALL payment fields for Cash
                    bank = ''
                    bank_no = ''
                    bank_branch = ''
                    cheque_no = ''
                    cheque_date = None
                    momo_no = ''
                    momo_name = ''
                    print("DEBUG - Cash mode: All payment fields cleared")

                elif pay_mode == 'Transfer':
                    # Keep transfer fields, clear cheque fields
                    bank = ''
                    bank_no = ''
                    bank_branch = ''
                    cheque_no = ''
                    cheque_date = None
                    # Keep momo_no, momo_name
                    print("DEBUG - Transfer mode: Transfer fields kept, cheque fields cleared")

                print(f"DEBUG - Final cheque_date: {cheque_date}")

                # ====================
                # 9. CREATE TRANSACTION
                # ====================
                trans = Trans.objects.create(
                    # Basic Info
                    entity=entity,
                    date=date,
                    trans_no=trans_no,
                    rec_vou_no=rec_vou_no,
                    trans_type=trans_type,
                    amount=amount,
                    pay_mode=pay_mode,
                    purpose=ledger_name,
                    details=details,
                    
                    # Member Info
                    member=member_obj,
                    member_no=member_no,
                    member_name=member_name,
                    
                    # Non-Member Info
                    non_member_name=non_member_name if name_type == 'Non Member' else '',
                    non_member_contact=non_member_contact if name_type == 'Non Member' else '',
                    
                    # Loan Info
                    loan=loan_obj,
                 #   loan_id=loan_id_value,
                    
                    # Payment Method Info
                    bank=bank,
                    bank_no=bank_no,
                    bank_branch=bank_branch,
                    momo_no=momo_no,
                    momo_name=momo_name,
                    cheque_no=cheque_no,
                    cheque_date=cheque_date, 
                    
                    # Account Info
                    ledger_id=ledger_id,
                    ledger_code=ledger_code,
                    ledger_name=ledger_name,
                    
                    # User Info
                    created_by_id=user_id,
                    created_by_name=user_full_name,
                    created_by_username=username,
                )

                messages.success(request, f" Transaction {trans_no} saved successfully!")
                return redirect('RecPayApp:trans_create', entity.slug)

            except Exception as e:
                messages.error(request, f"❌ Error: {str(e)}")
                import traceback
                traceback.print_exc()

    context = {
        'tran': page_obj,
        'members': members,
        'loans': active_loans,
        'accounts': accounts,
        'selected_member': selected_member,
        'selected_member_id': selected_member_id,
        'total_records': total_records,
        'receipts_count': receipts_count,
        'payments_count': payments_count,
        'receipts_total': receipts_total,
        'payments_total': payments_total,
        'today': datetime.now().date(),
    }

    return render(request, 'RecPayApp/trans_create.html', context)     

# # ============================= Trans List Manage ===========================
@login_required
def trans_list_manage(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)

    """List all transactions with search and summary"""
    query = request.GET.get('q', '')

    # Get all transactions
    if query:
        transactions = Trans.objects.filter(
            Q(rec_vou_no__icontains=query) |
            Q(member_name__icontains=query) |
            Q(non_member_name__icontains=query) |
            Q(details__icontains=query) |
            Q(ledger_name__icontains=query)
        ).order_by('-date', '-id')
    else:
        transactions = Trans.objects.all().order_by('-id')

    # Calculate ledger summaries
    ledger_summaries = []
    ledgers = transactions.values('ledger_name').distinct()

    for ledger in ledgers:
        ledger_name = ledger['ledger_name']
        if ledger_name:  # Skip empty ledger names
            ledger_trans = transactions.filter(ledger_name=ledger_name)
            count = ledger_trans.count()
            total = ledger_trans.aggregate(total=Sum('amount'))['total'] or 0
            ledger_summaries.append({
                'ledger_name': ledger_name,
                'count': count,
                'total': total
            })

    # Calculate grand total
    grand_total = transactions.aggregate(total=Sum('amount'))['total'] or 0

    # Pagination
    paginator = Paginator(transactions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'transactions': page_obj,
        'ledger_summaries': ledger_summaries,
        'grand_total': grand_total,
    }

    return render(request, 'RecPayApp/trans_list_manage.html', context) 


def trans_view(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    """View a single transaction in detail"""
    transaction = get_object_or_404(Trans, pk=pk)
    return render(request, "RecPayApp/trans_view.html", {"transaction": transaction})


@login_required
def trans_list(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    
    query = request.GET.get('q', '')
    
    # Get all transactions
    if query:
        transactions = Trans.objects.filter(
            Q(rec_vou_no__icontains=query) |
            Q(member_name__icontains=query) |
            Q(non_member_name__icontains=query) |
            Q(details__icontains=query) |
            Q(ledger_name__icontains=query)
        ).order_by('-date', '-id')
    else:
        transactions = Trans.objects.all().order_by('-id')
    
    # Calculate ledger summaries
    ledger_summaries = []
    ledgers = transactions.values('ledger_name').distinct()
    
    for ledger in ledgers:
        ledger_name = ledger['ledger_name']
        if ledger_name:  # Skip empty ledger names
            ledger_trans = transactions.filter(ledger_name=ledger_name)
            count = ledger_trans.count()
            total = ledger_trans.aggregate(total=Sum('amount'))['total'] or 0
            ledger_summaries.append({
                'ledger_name': ledger_name,
                'count': count,
                'total': total
            })
    
    # Calculate grand total
    grand_total = transactions.aggregate(total=Sum('amount'))['total'] or 0
    
    # Pagination
    paginator = Paginator(transactions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'transactions': page_obj,
        'ledger_summaries': ledger_summaries,
        'grand_total': grand_total,
    }
    
    return render(request, 'RecPayApp/trans_list_manage.html', context) 


# ## =========================Trans Edit =========================

@login_required
def trans_edit(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    """Edit transaction"""

    transaction = get_object_or_404(Trans, pk=pk)

    # Only allow editing of DRAFT transactions
    if transaction.status == 'POSTED':
        messages.error(request, "Posted transactions cannot be edited!")
        return redirect('RecPayApp:trans_view', entity.slug, pk=transaction.pk)

    members = Master.objects.filter(is_deleted=False).order_by('last_name', 'first_name')
    accounts = ChartOfAccounts.objects.filter(
        is_active=True,
        is_data_entry=True,
        is_data_view=True
    ).order_by('accountno')

    if request.method == 'POST':
        if 'save' in request.POST:
            try:
                # Update basic info
                transaction.amount = Decimal(request.POST.get('amount', 0))
                transaction.details = request.POST.get('details', '')
                transaction.pay_mode = request.POST.get('pay_mode', 'Cash')
                transaction.trans_type = request.POST.get('trans_type', 'Receipts')

                # Update date
                date_str = request.POST.get('date', '')
                for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d']:
                    try:
                        transaction.date = datetime.strptime(date_str, fmt).date()
                        break
                    except ValueError:
                        continue

                # Update party info
                name_type = request.POST.get('name_type', 'Member')
                if name_type == 'Member':
                    member_id = request.POST.get('member_id', '')
                    if member_id:
                        transaction.member = Master.objects.get(id=member_id)
                        transaction.member_name = transaction.member.full_name
                        transaction.non_member_name = ''
                        transaction.non_member_contact = ''
                    else:
                        transaction.member = None
                        transaction.member_name = ''
                else:
                    transaction.member = None
                    transaction.member_name = ''
                    transaction.non_member_name = request.POST.get('non_member_name', '')
                    transaction.non_member_contact = request.POST.get('non_member_contact', '')

                # Update ledger info
                chart_account = request.POST.get('chart_account', '')
                if chart_account:
                    parts = chart_account.split(',')
                    if len(parts) == 3:
                        transaction.ledger_id = parts[0]
                        transaction.ledger_code = parts[1]
                        transaction.ledger_name = parts[2]

                # Update payment details
                if transaction.pay_mode == 'Cheque':
                    transaction.cheque_date = None
                    cheque_date_str = request.POST.get('cheque_date', '')
                    if cheque_date_str:
                        for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d']:
                            try:
                                transaction.cheque_date = datetime.strptime(cheque_date_str, fmt).date()
                                break
                            except ValueError:
                                continue
                    transaction.cheque_no = request.POST.get('cheque_no', '')
                    transaction.bank = request.POST.get('bank', '')
                    transaction.bank_branch = request.POST.get('bank_branch', '')
                    transaction.bank_no = request.POST.get('bank_no', '')
                    transaction.momo_no = ''
                    transaction.momo_name = ''
                elif transaction.pay_mode == 'Transfer':
                    transaction.momo_no = request.POST.get('momo_no', '')
                    transaction.momo_name = request.POST.get('momo_name', '')
                    transaction.cheque_no = ''
                    transaction.cheque_date = None
                    transaction.bank = ''
                    transaction.bank_branch = ''
                    transaction.bank_no = ''
                else:  # Cash
                    transaction.cheque_no = ''
                    transaction.cheque_date = None
                    transaction.bank = ''
                    transaction.bank_branch = ''
                    transaction.bank_no = ''
                    transaction.momo_no = ''
                    transaction.momo_name = ''

                # Update loan
                loan_id = request.POST.get('loan_id', '')
                if loan_id:
                    transaction.loan_id = loan_id
                else:
                    transaction.loan = None

                transaction.save()
                messages.success(request, "Transaction updated successfully!")
                return redirect('RecPayApp:trans_view', entity.slug, pk=transaction.pk)

            except Exception as e:
                messages.error(request, f"Error updating transaction: {str(e)}")

    context = {
        'transaction': transaction,
        'members': members,
        'accounts': accounts,
    }
    return render(request, 'RecPayApp/trans_edit.html', context)  


# ===============================Trans Delete ===========================


@login_required
def trans_delete(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    """Delete a transaction"""

    transaction = get_object_or_404(Trans, pk=pk)

    # Check if transaction can be deleted
    if transaction.status == 'POSTED':
        messages.error(request, "Posted transactions cannot be deleted! Consider creating a reversing entry.")
        return redirect('RecPayApp:trans_view', entity.slug, pk=transaction.pk)

    if request.method == 'POST':
        confirm = request.POST.get('confirm', '')

        if confirm == 'DELETE':
            trans_number = transaction.trans_no
            transaction.delete()
            messages.success(request, f"Transaction {trans_number} has been deleted successfully!")
            return redirect('RecPayApp:trans_list_manage', entity.slug)
        else:
            messages.error(request, "Please type 'DELETE' to confirm deletion.")
            return redirect('RecPayApp:trans_delete', entity.slug, pk=transaction.pk)

    context = {
        'transaction': transaction,
    }
    return render(request, 'RecPayApp/trans_delete.html', context)

# ## ====================================Trans All Delete ==============================

@login_required    
def trans_all_delete(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    """
    View to confirm and delete all Trans records
    """
    # Get count of records
    record_count = Trans.objects.count()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'confirm':
            # User confirmed deletion
            deleted_count, _ = Trans.objects.all().delete()

            messages.success(
                request, 
                f'Successfully deleted {deleted_count} transaction records.'
            )
            return redirect('RecPayApp:trans_list_manage')  # Redirect to transaction list

        elif action == 'cancel':
            # User cancelled
            messages.info(request, 'Deletion cancelled.')
            return redirect('RecPayApp:trans_list_manage', entity.slug)

    # GET request - show confirmation page
    context = {
        'record_count': record_count,
        'page_title': 'Delete All Transactions'
    }
    return render(request, 'RecPayApp/trans_delete_all_confirm.html', context)

# ## ============================= Trans List Manage =================================


@login_required
def trans_list_manage1(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    """Transaction list management"""

    transactions = Trans.objects.all().order_by('-date', '-id')

    # Search functionality
    search_query = request.GET.get('q', '')
    if search_query:
        transactions = transactions.filter(
            Q(rec_vou_no__icontains=search_query) |
            Q(member_name__icontains=search_query) |
            Q(non_member_name__icontains=search_query) |
            Q(details__icontains=search_query) |
            Q(ledger_name__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(transactions, 50)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)

    # Calculate totals
    receipts = transactions.filter(trans_type='Receipts')
    payments = transactions.filter(trans_type='Payments')

    receipts_total = receipts.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    payments_total = payments.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    net_total = receipts_total - payments_total

    # Ledger summaries
    ledger_summaries = transactions.values('ledger_name').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')[:10]

    context = {
        'transactions': page_obj,
        'receipts_total': receipts_total,
        'payments_total': payments_total,
        'net_total': net_total,
        'receipts_count': receipts.count(),
        'payments_count': payments.count(),
        'total_records': transactions.count(),
        'ledger_summaries': ledger_summaries,
    }
    return render(request, 'RecPayApp/trans_list_manage.html', context)

# # ====================================Ajax Posting Supper ===================================

# RecPayApp/views.py - Add this for AJAX support (Optional)
from django.http import JsonResponse

@login_required
def post_transaction_api(request, slug, pk):
    """API endpoint to post transaction via AJAX"""
    entity = get_object_or_404(EntityModel, slug=slug)
    if request.method == 'POST':
        transaction = get_object_or_404(Trans, pk=pk)

        if transaction.status == 'POSTED':
            return JsonResponse({'success': False, 'error': 'Transaction already posted'})

        service = TransactionPostingService(transaction, request.user)
        result = service.process()

        if result['success']:
            return JsonResponse({
                'success': True,
                'message': 'Transaction posted successfully',
                'journal_number': result['journal_number']
            })
        else:
            return JsonResponse({
                'success': False,
                'error': ', '.join(result['errors'])
            })

    return JsonResponse({'success': False, 'error': 'Invalid request method'})    


@login_required 
def number_to_words_simple(amount):
    """Simple function to format amount for display"""
    # You can replace this with a proper number-to-words function later
    # For now, just return the formatted number
    return f"{amount:,.2f}"

@login_required 
def number_to_words(amount):
    """Convert number to words (simplified version)"""
    # You can implement a full number-to-words function here
    # For now, return a simple string
    return f"{amount:,.2f}"

##   End Of Trans PDF ##############################################################


def master_list(request, pk):
    master = Master.objects.all()
    return render(request, 'master_list_manage.html', {'master': master})


# ==================== TRANSACTION VIEWS ====================


# views.py
from django.db.models import Sum, Count, Q

def journal_view(request, trans_id):
    journals = Journal.objects.filter(trans_id=trans_id).order_by('id')
    j = journals
    journal_count = journals.count()
    
    # Initialize validation flags
    validation = {
        'has_records': journal_count > 0,
        'has_two_entries': journal_count == 2,
        'is_balanced': False,
        'has_debit': False,
        'has_credit': False,
        'errors': [],
        'warnings': []
    }
    
    if journal_count == 0:
        validation['errors'].append(f"No records found for voucher {trans_id}")
    
    elif journal_count == 1:
        validation['warnings'].append("Only 1 record found. Journal should have at least 2 entries.")
        
        # Check if it's debit or credit
        journal = journals.first()
        if journal.debit > 0:
            validation['has_debit'] = True
            validation['warnings'].append("Only debit entry found. Missing credit entry.")
        else:
            validation['has_credit'] = True
            validation['warnings'].append("Only credit entry found. Missing debit entry.")
    
    elif journal_count == 2:
        # Calculate totals
        total_debit = sum(j.debit or 0 for j in journals)
        total_credit = sum(j.credit or 0 for j in journals)
        balance = total_debit - total_credit
        
        validation['is_balanced'] = balance == 0
        validation['total_debit'] = total_debit
        validation['total_credit'] = total_credit
        validation['balance'] = balance
        
        # Check if we have both debit and credit
        debit_count = sum(1 for j in journals if j.debit and j.debit > 0)
        credit_count = sum(1 for j in journals if j.credit and j.credit > 0)
        
        validation['has_debit'] = debit_count > 0
        validation['has_credit'] = credit_count > 0
        
        if not validation['is_balanced']:
            validation['errors'].append(f"Journal is not balanced. Difference: {balance}")
        
        if debit_count == 0:
            validation['warnings'].append("No debit entries found")
        if credit_count == 0:
            validation['warnings'].append("No credit entries found")
        
        if debit_count == 2:
            validation['warnings'].append("Both entries are debits (unusual)")
        if credit_count == 2:
            validation['warnings'].append("Both entries are credits (unusual)")
    
    else:
        validation['warnings'].append(f"Found {journal_count} records (more than typical 2-entry journal)")
    
    context = {
        'j': j,
        'journals': journals,
        'trans_id': trans_id,
    #    'rec_vou_no': rec_vou_no,
        'journal_count': journal_count,
        'validation': validation,
    }
    
    return render(request, 'journal_view.html', context)

def trans_update(request):

#    trans = Trans.objects.exclude(member_id__isnull=True).exclude(member_id=0)
    trans = Trans.objects.all()
#   ### Update Master
    for t in trans:
        if t.member_id and t.member_id != 0:
            if t.purpose == "Admission Fees":
               
                master = get_object_or_404(Master, pk=t.member_id)
                master.admit_fees = master.admit_fees + t.amount
            
                master.save()
                master = Master.objects.all()
            else:
                pass
            
            if t.purpose == "Savings":
                print(t.member_id)
                master = get_object_or_404(Master, pk=t.member_id)
                master.savings_tot = master.savings_tot + t.amount
            
                master.save()
                master = Master.objects.all()
            else:
                pass
            
            if t.purpose == "Savings Withdrawal":
                print(t.member_id)
                master = get_object_or_404(Master, pk=t.member_id)
                master.savings_tot = master.savings_tot + t.amount
            
                master.save()
                master = Master.objects.all()
            else:
                pass
            
            if t.purpose == "Shares":
                print(t.member_id)
                master = get_object_or_404(Master, pk=t.member_id)
                master.shares_tot = master.shares_tot + t.amount
            
                master.save()
                master = Master.objects.all()
            else:
                pass
            
            if t.purpose == "Shares Withdrawal":
                print(t.member_id)
                master = get_object_or_404(Master, pk=t.member_id)
                master.savings_tot = master.savings_tot + t.amount
            
                master.save()
                master = Master.objects.all()
            else:
                pass
            
            if t.purpose == "Loan Disbursement":
                print(t.member_id)
                master = get_object_or_404(Master, pk=t.member_id)
                master.savings_tot = master.savings_tot + t.amount
            
                master.save()
                master = Master.objects.all()
            else:
                pass
            
            if t.purpose == "Loan Repayment":
                print(t.member_id)
                master = get_object_or_404(Master, pk=t.member_id)
                master.savings_tot = master.savings_tot + t.amount
            
                master.save()
                master = Master.objects.all()
            else:
                pass
        else:
            pass      
         
#   ####  Create Statement
        Statement.objects.create(
            trans_id=t.id,
            date=t.date,
            trans_no=t.trans_no,
            rec_vou_no=t.rec_vou_no,
            member=t.member,
            amount=t.amount,
            pay_mode=t.pay_mode,
            trans_type=t.trans_type,
        
        ## Name 
            member_no=t.member_no,
            member_name=t.member_name,
            non_member_name=t.non_member_name,
            non_member_contact=t.non_member_contact,
        
        ## Bank Details
            bank=t.bank,
            bank_no=t.bank_no,
            bank_branch=t.bank_branch,
        
        ## Transfer Details
            momo_no=t.momo_no,
            momo_name=t.momo_name,
        
        ## Finance Details
    #        account=t.account,
            ledger_id=t.ledger_id,
            ledger_code=t.ledger_code,
            ledger_name=t.ledger_name,
        
        ## Other Details
            purpose=t.purpose,
            other_purpose=t.other_purpose,
            details=t.details,
        
        ## Loan Details
            loan_id=t.loan_id,
            loan_name=t.loan_name,
        
            trans_created_at=t.created_at,
            trans_updated_at=t.updated_at,
        )   
        
    #   ##  Update Ledger
        
        if t.ledger_code and t.ledger_code != 0:
            
           
            print(f"=== DEBUG: Processing Transaction {t.id} ===")
            print(f"Transaction Type: {t.trans_type}")
            print(f"Transaction Amount: {t.amount}")
            print(f"Ledger ID: {t.ledger_code}")
            
            try:
                
    #            led = get_object_or_404(Ledger, pk=t.ledger_code)
                
                led = get_object_or_404(Ledger, ledger_code=t.ledger_code)
                
                print(f"Found Ledger: {led.id} - {led.ledger_name}")
                print(f"Before update - Debit: {led.debit}, Credit: {led.credit}")
                
                
            
                if t.trans_type == "Payments":
                    led.debit = (led.debit or Decimal('0.00')) + t.amount
                    led.debit_cnt = (led.debit_cnt or 0) + 1
                elif t.trans_type == "Receipts":
                    led.credit = (led.credit or Decimal('0.00')) + t.amount
                    led.credit_cnt = (led.credit_cnt or 0) + 1
                    
                print(f"Updated Credit: +{t.amount} = {led.credit}")
                print(f"Updated Credit Count: {led.credit_cnt}")
                led.save()
            
            except Exception as e:
                print(f"✗ ERROR: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
                
            db_amount = 0.00
            cr_amount = 0.00
            if t.trans_type=="Payments":
                db_amount = t.amount
            if t.trans_type=="Receipts":
                cr_amount = t.amount
        
        Ledger_Statement.objects.create(
            
            trans_date=t.date,
            trans_id=t.id,
            ledger_code=t.ledger_code,
            ledger_name=t.ledger_name,
    
            debit=db_amount,
            credit=cr_amount,

            purpose=t.purpose,
            details=t.details,
    
            member_id=t.member_id,
            member_name=t.member_name,
            non_member_name=t.non_member_name,
            non_member_contact=t.non_member_contact,
    
            trans_created_at=t.created_at,
            trans_updated_at=t.updated_at, 
        )
            
    #   Update Ledger again for Cash, Bank and Transfer         
        ledger_code=''
        ledger_name=''
        if t.pay_mode == "Cash":
            cash = get_object_or_404(Ledger, ledger_code="1001")
            if t.trans_type == "Payments":
                cash.debit = (cash.debit or Decimal('0.00')) + t.amount
                cash.debit_cnt = (cash.debit_cnt or 0) + 1
            elif t.trans_type == "Receipts":
                cash.credit = (cash.credit or Decimal('0.00')) + t.amount
                cash.credit_cnt = (cash.credit_cnt or 0) + 1
            ledger_name = 'Cash'
            print(ledger_code)
            print(ledger_name)
            cash.save()
        
            
        if t.pay_mode == "Bank":
            bank = get_object_or_404(Ledger, ledger_code="1002")
            if t.trans_type == "Payments":
                bank.debit = (bank.debit or Decimal('0.00')) + t.amount
                bank.debit_cnt = (bank.debit_cnt or 0) + 1
            elif t.trans_type == "Receipts":
                bank.credit = (bank.credit or Decimal('0.00')) + t.amount
                bank.credit_cnt = (bank.credit_cnt or 0) + 1
            bank.save()
            ledger_name='Bank'
            
        if t.pay_mode == "Transfer":
            trns = get_object_or_404(Ledger, ledger_code="1003")
            if t.trans_type == "Payments":
                trns.debit = (trns.debit or Decimal('0.00')) + t.amount
                trns.debit_cnt = (trns.debit_cnt or 0) + 1
            elif t.trans_type == "Receipts":
                trns.credit = (trns.credit or Decimal('0.00')) + t.amount
                trns.credit_cnt = (trns.credit_cnt or 0) + 1
            trns.save()
            ledger_name='Transfer'
            
        print(ledger_code)
        print(ledger_name)
    #   ##  Create Ledger Statement  

        Ledger_Statement.objects.create(
            
            trans_date=t.date,
            trans_id=t.id,
            ledger_code=ledger_code,
            ledger_name=ledger_name,
    
            debit=db_amount,
            credit=cr_amount,

            purpose=t.purpose,
            details=t.details,
    
            member_id=t.member_id,
            member_name=t.member_name,
            non_member_name=t.non_member_name,
            non_member_contact=t.non_member_contact,
    
            trans_created_at=t.created_at,
            trans_updated_at=t.updated_at, 
        )
             
    return render(request, 'master_list_manage.html', {'master': master})

# ==================== SEARCH AND FILTER VIEWS ====================

def search_member(request):
    """AJAX view to search for members"""
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'GET':
        member_id = request.GET.get('member_id', '')
        
        try:
            member = Master.objects.get(id=int(member_id))
            data = {
                'exists': True,
                'name': f"{member.first_name} {member.last_name}".strip(),
                'id': member.id
            }
        except (Master.DoesNotExist, ValueError):
            data = {
                'exists': False,
                'name': '',
                'id': ''
            }
        
        return JsonResponse(data)
    
    return JsonResponse({'error': 'Invalid request'})

def trans_search(request):
    """Search transactions by various criteria"""
    query = request.GET.get('q', '')
    trans_type = request.GET.get('trans_type', '')
    pay_mode = request.GET.get('pay_mode', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    
    transactions = Trans.objects.all()
    
    if query:
        transactions = transactions.filter(
            Q(trans_no__icontains=query) |
            Q(member_name__icontains=query) |
            Q(non_member_name__icontains=query) |
            Q(purpose__icontains=query)
        )
    
    if trans_type:
        transactions = transactions.filter(trans_type=trans_type)
    
    if pay_mode:
        transactions = transactions.filter(pay_mode=pay_mode)
    
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            transactions = transactions.filter(date__gte=start_date)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            transactions = transactions.filter(date__lte=end_date)
        except ValueError:
            pass
    
    transactions = transactions.order_by('-date', '-created_at')
    
    return render(request, 'trans_search.html', {
        'transactions': transactions,
        'search_query': query,
        'selected_type': trans_type,
        'selected_mode': pay_mode,
        'start_date': start_date,
        'end_date': end_date,
    })


# ==================== DASHBOARD AND SUMMARY VIEWS ====================

def dashboard1(request):
    """Main dashboard with transaction summaries"""
    # Today's transactions
    today = datetime.now().date()
    today_transactions = Trans.objects.filter(date=today)
    
    # Monthly summary
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    monthly_transactions = Trans.objects.filter(
        date__year=current_year,
        date__month=current_month
    )
    
    # Summary calculations
    today_receipts = today_transactions.filter(trans_type='Receipts').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    today_payments = today_transactions.filter(trans_type='Payments').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    
    monthly_receipts = monthly_transactions.filter(trans_type='Receipts').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    monthly_payments = monthly_transactions.filter(trans_type='Payments').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    
    total_transactions = Trans.objects.count()
    total_members = Master.objects.count()
    
    # Recent transactions
    recent_transactions = Trans.objects.all().order_by('-created_at')[:10]
    
    return render(request, 'dashboard.html', {
        'today_receipts': today_receipts,
        'today_payments': today_payments,
        'monthly_receipts': monthly_receipts,
        'monthly_payments': monthly_payments,
        'total_transactions': total_transactions,
        'total_members': total_members,
        'recent_transactions': recent_transactions,
    })

# ==================== MASTER DATA VIEWS ====================

def master_list(request):
    """List all members"""
    members = Master.objects.all()
    
    # Search functionality
    query = request.GET.get('q', '')
    if query:
        members = members.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(other_names__icontains=query)
        )
    
    return render(request, 'master_list.html', {
        'members': members,
        'search_query': query,
    })

def master_detail(request, pk):
    """View member details and their transactions"""
    member = get_object_or_404(Master, pk=pk)
    transactions = Trans.objects.filter(member=member).order_by('-date')
    
    # Calculate member statistics
    total_transactions = transactions.count()
    total_receipts = transactions.filter(trans_type='Receipts').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    total_payments = transactions.filter(trans_type='Payments').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    
    return render(request, 'master_detail.html', {
        'member': member,
        'transactions': transactions,
        'total_transactions': total_transactions,
        'total_receipts': total_receipts,
        'total_payments': total_payments,
        }
    )


def render_to_pdf(template_src, context_dict):
    """Render HTML template to PDF"""
    html = render_to_string(template_src, context_dict)
    result = io.BytesIO()
    
    # Create PDF with landscape orientation
    pdf = pisa.pisaDocument(
        io.BytesIO(html.encode("UTF-8")), 
        result,
        encoding='UTF-8',
        link_callback=None
    )
    
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


def trans_view_pdf1(request, pk):
    """
    Generate detailed PDF for a single Trans record
    """
    # Get the transaction object
    transaction = get_object_or_404(Trans, pk=pk)
    
    # Create a file-like buffer to receive PDF data
    buffer = io.BytesIO()
    
    # Create the PDF document with SimpleDocTemplate for better formatting
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=50, leftMargin=50,
                            topMargin=50, bottomMargin=50)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Get sample style sheet
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#2c3e50'),
        fontName='Helvetica-Bold'
    )
    
    section_style = ParagraphStyle(
        'SectionStyle',
        parent=styles['Heading2'],
        fontSize=12,
        spaceAfter=12,
        spaceBefore=20,
        textColor=colors.HexColor('#2980b9'),
        fontName='Helvetica-Bold',
        leftIndent=10
    )
    
    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6
    )
    
    bold_style = ParagraphStyle(
        'BoldStyle',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica-Bold'
    )
    
    # HEADER - Title
    elements.append(Paragraph(f"TRANSACTION DETAILS REPORT", title_style))
    elements.append(Spacer(1, 10))
    
    # Header information table
    header_data = [
        [f"Transaction No: <b>{transaction.trans_no or 'N/A'}</b>", 
         f"Transaction ID: <b>{transaction.id}</b>"],
        [f"Transaction Type: <b>{transaction.trans_type}</b>", 
         f"Date: <b>{transaction.date.strftime('%d-%b-%Y')}</b>"],
    ]
    
    header_table = Table(header_data, colWidths=[doc.width/2.0]*2)
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ecf0f1')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.white),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 20))
    
    # SECTION 1: BASIC INFORMATION
    elements.append(Paragraph("1. BASIC INFORMATION", section_style))
    
    basic_data = [
        ['Field', 'Value'],
        ['Transaction Number', transaction.trans_no or 'N/A'],
        ['Transaction Type', transaction.trans_type],
        ['Purpose', transaction.purpose],
    ]
    
    # Add other purpose if exists and not empty
    if transaction.other_purpose and transaction.other_purpose.strip():
        basic_data.append(['Other Purpose', transaction.other_purpose])
    
    basic_data.extend([
        ['Payment Mode', transaction.pay_mode],
        ['Amount', f"GH₵ {transaction.amount:,.2f}"],
        ['Details', transaction.details or 'N/A'],
    ])
    
    basic_table = Table(basic_data, colWidths=[doc.width/3.0, doc.width*2/3.0])
    basic_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#34495e')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('TEXTCOLOR', (0, 1), (0, -1), colors.whitesmoke),
        ('TEXTCOLOR', (1, 1), (1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 4), (1, 4), 'RIGHT'),  # Align amount right
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 1), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(basic_table)
    elements.append(Spacer(1, 15))
    
    # SECTION 2: MEMBER/NON-MEMBER INFORMATION
    elements.append(Paragraph("2. PARTY INFORMATION", section_style))
    
    party_data = []
    if transaction.member:
        party_data = [
            ['Field', 'Value'],
            ['Member Name', transaction.member_name or 'N/A'],
            ['Member No', transaction.member_no or 'N/A'],
            ['Type', 'Member'],
        ]
        
        # Add member object details if available
        try:
            if hasattr(transaction.member, 'member_no'):
                party_data.append(['Member ID', transaction.member.member_no or 'N/A'])
            if hasattr(transaction.member, 'contact'):
                party_data.append(['Contact', transaction.member.contact or 'N/A'])
        except:
            pass
    else:
        party_data = [
            ['Field', 'Value'],
            ['Name', transaction.non_member_name or 'N/A'],
            ['Contact', transaction.non_member_contact or 'N/A'],
            ['Type', 'Non-Member'],
        ]
    
    party_table = Table(party_data, colWidths=[doc.width/3.0, doc.width*2/3.0])
    party_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#34495e')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('TEXTCOLOR', (0, 1), (0, -1), colors.whitesmoke),
        ('TEXTCOLOR', (1, 1), (1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(party_table)
    elements.append(Spacer(1, 15))
    
    # SECTION 3: PAYMENT DETAILS
    elements.append(Paragraph("3. PAYMENT DETAILS", section_style))
    
    payment_data = [
        ['Field', 'Value'],
        ['Payment Mode', transaction.pay_mode],
    ]
    
    # Add payment-specific details based on payment mode
    if transaction.pay_mode == 'Cheque':
        if transaction.bank:
            payment_data.append(['Bank', transaction.bank])
        if transaction.bank_no:
            payment_data.append(['Cheque No', transaction.bank_no])
        if transaction.bank_branch:
            payment_data.append(['Branch', transaction.bank_branch])
    
    elif transaction.pay_mode == 'Transfer':
        if transaction.bank:
            payment_data.append(['Bank', transaction.bank])
        if transaction.bank_no:
            payment_data.append(['Account No', transaction.bank_no])
        if transaction.bank_branch:
            payment_data.append(['Branch', transaction.bank_branch])
    
    elif transaction.pay_mode == 'Cash':
        payment_data.append(['Cash Payment', 'Yes'])
    
    # Add MoMo details if available
    if transaction.momo_no and transaction.momo_no.strip():
        payment_data.append(['MoMo Number', transaction.momo_no])
    if transaction.momo_name and transaction.momo_name.strip():
        payment_data.append(['MoMo Name', transaction.momo_name])
    
    payment_table = Table(payment_data, colWidths=[doc.width/3.0, doc.width*2/3.0])
    payment_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#34495e')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('TEXTCOLOR', (0, 1), (0, -1), colors.whitesmoke),
        ('TEXTCOLOR', (1, 1), (1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(payment_table)
    elements.append(Spacer(1, 15))
    
    # SECTION 4: FINANCIAL DETAILS
    elements.append(Paragraph("4. FINANCIAL DETAILS", section_style))
    
    financial_data = [
        ['Field', 'Value'],
        ['Amount', f"GH₵ {transaction.amount:,.2f}"],
    ]
    
    # Calculate receipts and payments
    receipts = transaction.receipts
    payments = transaction.payments
    
    financial_data.append(['Transaction Type', f"{transaction.trans_type}"])
    financial_data.append(['Receipts Amount', f"GH₵ {receipts:,.2f}" if receipts > 0 else 'GH₵ 0.00'])
    financial_data.append(['Payments Amount', f"GH₵ {payments:,.2f}" if payments > 0 else 'GH₵ 0.00'])
    
    # Add ledger/account information
    if transaction.account:
        financial_data.append(['Account', str(transaction.account)])
    if transaction.ledger_name:
        financial_data.append(['Ledger Name', transaction.ledger_name])
    if transaction.ledger_id:
        financial_data.append(['Ledger ID', transaction.ledger_id])
    
    financial_table = Table(financial_data, colWidths=[doc.width/3.0, doc.width*2/3.0])
    financial_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#34495e')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('TEXTCOLOR', (0, 1), (0, -1), colors.whitesmoke),
        ('TEXTCOLOR', (1, 1), (1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 1), (1, 3), 'RIGHT'),  # Align amount columns right
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 1), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(financial_table)
    elements.append(Spacer(1, 15))
    
    # SECTION 5: LOAN DETAILS (if applicable)
    if transaction.loan_id or transaction.loan_name:
        elements.append(Paragraph("5. LOAN DETAILS", section_style))
        
        loan_data = [
            ['Field', 'Value'],
        ]
        
        if transaction.loan_id:
            loan_data.append(['Loan ID', transaction.loan_id])
        if transaction.loan_name:
            loan_data.append(['Loan Name', transaction.loan_name])
        
        loan_table = Table(loan_data, colWidths=[doc.width/3.0, doc.width*2/3.0])
        loan_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#34495e')),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('TEXTCOLOR', (0, 1), (0, -1), colors.whitesmoke),
            ('TEXTCOLOR', (1, 1), (1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(loan_table)
        elements.append(Spacer(1, 15))
    
    # SECTION 6: SYSTEM INFORMATION
    elements.append(Paragraph("6. SYSTEM INFORMATION", section_style))
    
    sys_data = [
        ['Field', 'Value'],
        ['Created At', transaction.created_at.strftime('%d-%b-%Y %I:%M %p')],
        ['Updated At', transaction.updated_at.strftime('%d-%b-%Y %I:%M %p')],
        ['Report Generated', datetime.now().strftime('%d-%b-%Y %I:%M %p')],
    ]
    
    sys_table = Table(sys_data, colWidths=[doc.width/3.0, doc.width*2/3.0])
    sys_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#34495e')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('TEXTCOLOR', (0, 1), (0, -1), colors.whitesmoke),
        ('TEXTCOLOR', (1, 1), (1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(sys_table)
    
    # FOOTER NOTE
    elements.append(Spacer(1, 20))
    footer_note = Paragraph(
        f"<i>This is a system generated report for transaction {transaction.trans_no or transaction.id}. "
        f"For any discrepancies, please contact the administrator.</i>",
        ParagraphStyle(
            'FooterNote',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
    )
    elements.append(footer_note)
    
    # Build the PDF
    doc.build(elements)
    
    # FileResponse sets the Content-Disposition header
    buffer.seek(0)
    
    # Generate filename
    filename = f"Transaction_{transaction.trans_no or transaction.id}_{transaction.date.strftime('%Y%m%d')}.pdf"
    
    return FileResponse(buffer, as_attachment=True, filename=filename)


def trans_view_pdf(request, pk):
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

def section_title(p, x, y, text):
    """Draw section title with underline"""
    p.setFont("Helvetica-Bold", 12)
    p.drawString(x, y, text)
    p.line(x, y-2, x + 200, y-2)

def draw_table(p, x, y, data, col_widths, row_height=20):
    """Draw a simple table"""
    for row in data:
        current_x = x
        for i, cell in enumerate(row):
            if i % 2 == 0:  # Label column
                p.setFont("Helvetica-Bold", 10)
                p.drawString(current_x, y, cell)
            else:  # Value column
                p.setFont("Helvetica", 10)
                p.drawString(current_x, y, cell)
            current_x += col_widths[i]
        y -= row_height
    return len(data) * row_height


@login_required
def post_transaction(request, trans_id):
    """Post a single transaction to journal and ledger"""
    
    transaction = get_object_or_404(Trans, id=trans_id)
    
    if transaction.status == 'POSTED':
        messages.warning(request, "Transaction already posted!")
        return redirect('transaction_detail', trans_id=trans_id)
    
    # Process the transaction
    service = TransactionPostingService(transaction, request.user)
    result = service.process()
    
    if result['success']:
        messages.success(request, f"Transaction {transaction.trans_no} posted successfully!")
        messages.info(request, f"Journal Entry: {result['journal'].journal_number}")
    else:
        for error in result['errors']:
            messages.error(request, f"Error: {error}")
    
    return redirect('transaction_detail', trans_id=trans_id)


# RecPayApp/views.py
from django.db import models

@login_required
def batch_post_transactions(request):
    """Post multiple transactions at once"""
    
    if request.method == 'POST':
        selected_ids = request.POST.getlist('selected_ids[]')
        
        if not selected_ids:
            messages.error(request, "No transactions selected")
            return redirect('RecPayApp:batch_post_transactions')
        
        success_count = 0
        error_count = 0
        
        for trans_id in selected_ids:
            try:
                transaction = Trans.objects.get(id=trans_id, status='DRAFT')
                service = TransactionPostingService(transaction, request.user)
                result = service.process()
                
                if result['success']:
                    success_count += 1
                else:
                    error_count += 1
                    
            except Exception as e:
                error_count += 1
        
        messages.success(request, f"Posted {success_count} transaction(s)")
        if error_count:
            messages.warning(request, f"{error_count} transaction(s) failed")
        
        return redirect('RecPayApp:batch_post_transactions')
    
    # GET request - show selection page
    transactions = Trans.objects.filter(status='DRAFT').order_by('-date')
    
    context = {
        'transactions': transactions,
        'total_count': transactions.count(),
        'total_amount': transactions.aggregate(total=models.Sum('amount'))['total'] or 0,
    }
    return render(request, 'RecPayApp/batch_post_select.html', context)


def trans_detail(request, pk):
    """View transaction details"""
    transaction = get_object_or_404(Trans, pk=pk)
    context = {
        'transaction': transaction,
    }
    return render(request, 'RecPayApp/trans_detail.html', context)


## ====================================Trans, JournalLine, JournalEntry, General Ledger, Statement View ==============

from django.db.models import Q
from django.http import HttpResponse
from django.template.loader import get_template
from openpyxl import Workbook
from .models import Trans
from FinanceApp.models import JournalEntry, JournalLine, GeneralLedger
from services.models import StateTrans, StateUpdate

def trans_audit_report(request, slug):
    trans_list = Trans.objects.filter(status='POSTED').order_by('-date', '-id')

    # Filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    batch = request.GET.get('batch')
    voucher = request.GET.get('voucher')

    if start_date:
        trans_list = trans_list.filter(date__gte=start_date)
    if end_date:
        trans_list = trans_list.filter(date__lte=end_date)
    if batch:
        trans_list = trans_list.filter(batch_number=batch)
    if voucher:
        trans_list = trans_list.filter(rec_vou_no__icontains=voucher)

    # Build audit data
    audit_data = []
    for trans in trans_list:
        journal = trans.journal_entries.first()
        if not journal:
            continue

        # Get state records
        state_trans = StateTrans.objects.filter(rec_vou_no=trans.rec_vou_no).first()
        state_update = StateUpdate.objects.filter(rec_vou_no=trans.rec_vou_no).first()

        # For each journal line, fetch the related GeneralLedger balance
        for line in journal.lines.all():
            account = line.account
            ledger = GeneralLedger.objects.filter(account=account).first()
            audit_data.append({
                # Trans fields
                'trans_id': trans.id,
                'rec_vou_no': trans.rec_vou_no,
                'trans_date': trans.date,
                'trans_type': trans.trans_type,
                'trans_amount': trans.amount,
                'trans_ledger_code': trans.ledger_code,
                'trans_ledger_name': trans.ledger_name,
                'trans_status': trans.status,
                'trans_batch': trans.batch_number,
                # Journal Entry fields
                'journal_entry_no': journal.entry_number,
                'journal_date': journal.entry_date,
                'journal_description': journal.description,
                # Journal Line fields
                'line_account_code': account.accountno,
                'line_account_name': account.name,
                'line_debit': line.debit,
                'line_credit': line.credit,
                'line_description': line.line_description,
                # General Ledger
                'gl_opening_balance': ledger.opening_balance if ledger else None,
                'gl_current_balance': ledger.current_balance if ledger else None,
                # State tables (optional)
                'state_trans_created': state_trans.created_at if state_trans else None,
                'state_update_created': state_update.created_at if state_update else None,
            })

    context = {
        'audit_data': audit_data,
        'start_date': start_date,
        'end_date': end_date,
        'batch': batch,
        'voucher': voucher,
    }
    return render(request, 'RecPayApp/trans_audit_report.html', context)


def trans_audit_report_excel(request):
    # (copy filtering logic same as above)
    # Build audit_data as above, then write to Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Transaction Audit"
    headers = ['Trans ID', 'Voucher', 'Date', 'Type', 'Amount', 'Ledger Code', 'Ledger Name', 'Status', 'Batch',
               'Journal No', 'Journal Date', 'Journal Desc',
               'Account Code', 'Account Name', 'Debit', 'Credit', 'Line Desc',
               'GL Opening Balance', 'GL Current Balance',
               'StateTrans Created', 'StateUpdate Created']
    ws.append(headers)
    for d in audit_data:
        ws.append([
            d['trans_id'], d['rec_vou_no'], d['trans_date'].strftime('%Y-%m-%d'), d['trans_type'],
            float(d['trans_amount']), d['trans_ledger_code'], d['trans_ledger_name'], d['trans_status'], d['trans_batch'],
            d['journal_entry_no'], d['journal_date'].strftime('%Y-%m-%d'), d['journal_description'],
            d['line_account_code'], d['line_account_name'], float(d['line_debit']), float(d['line_credit']), d['line_description'],
            float(d['gl_opening_balance']) if d['gl_opening_balance'] else '', float(d['gl_current_balance']) if d['gl_current_balance'] else '',
            d['state_trans_created'].strftime('%Y-%m-%d %H:%M:%S') if d['state_trans_created'] else '',
            d['state_update_created'].strftime('%Y-%m-%d %H:%M:%S') if d['state_update_created'] else '',
        ])
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="transaction_audit.xlsx"'
    wb.save(response)
    return response


def trans_jour_bal_list(request):
#    trans_list = Trans.objects.filter(status='POSTED').order_by('-date', '-id')
    trans_list = Trans.objects.all().order_by('-date', '-id')
    return render(request, 'RecPayApp/trans_jour_bal_list.html', {'trans_list': trans_list,})


def trans_jour_bal_view1(request, pk):
    # Pick a transaction from Trans
    transaction = get_object_or_404(Trans, pk=pk)#  
    
   # Select the transaction record from the JournalEntry
    jour_ent = transaction.journal_entries.first()
   
   # Select the corresponding record from the Journal Line 
    jour_line = JournalLine.objects.filter(journal_id=jour_ent.id)
    
   # Select the corresponding account details from the Chart of Accounts 
    coa = get_object_or_404(ChartOfAccounts, accountno=transaction.ledger_code)
    
   # Select the balnace and other details from the General Ledger 
    led = get_object_or_404(GeneralLedger, account_id=jour_ent.id)
    
    print(jour_ent.id)
    
    
    context = {
        'transaction': transaction,
        'jour_ent': jour_ent,
        'jour_line': jour_line,
        'coa': coa,
        'led': led,
    }
    
    
    return render(request, 'RecPayApp/trans_jour_bal_view.html', context)

def trans_jour_bal_view(request, pk):
    # 1. Get a specific transaction (Trans table) by its primary key
    transaction = get_object_or_404(Trans, pk=pk)

    # 2. Get the related JournalEntry (one transaction creates one journal entry)
    #    The reverse relation is 'journal_entries' because JournalEntry has a
    #    ForeignKey 'source_trans' to Trans.
    jour_ent = transaction.journal_entries.first()   # returns a JournalEntry object or None

    # 3. Get all JournalLine records that belong to that JournalEntry.
    #    One journal entry can have multiple lines (at least two: debit and credit).
    jour_lines = JournalLine.objects.filter(journal=jour_ent)   # returns a QuerySet

    # 4. Get the ChartOfAccounts record using the 'ledger_code' stored in the Trans.
    #    This ledger_code is the account code of the *main* account for this transaction
    #    (e.g., "10101001" for Cash). It is the same as the account used in one of the journal lines,
    #    but we fetch it directly here for quick reference.
    coa = get_object_or_404(ChartOfAccounts, accountno=transaction.ledger_code)

    # 5. Get the GeneralLedger record that holds the current balance for that account.
    #    GeneralLedger has a OneToOne relation to ChartOfAccounts (field 'account').
    #    So we use the coa object to get its related ledger entry.
    led = get_object_or_404(GeneralLedger, account=coa)   # NOT jour_ent.id

    # Debug print (optional)
    print(jour_ent.id)

    context = {
        'transaction': transaction,
        'jour_ent': jour_ent,
        'jour_lines': jour_lines,          # note: plural (multiple lines)
        'coa': coa,
        'led': led,
    }

    return render(request, 'RecPayApp/trans_jour_bal_view.html', context)

# RecPayApp/views.py

@login_required
def church_trans_create(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    members = Master.objects.filter(is_deleted=False).order_by('last_name', 'first_name')
    form = BaseTransForm()

    if request.method == 'POST':
        form = BaseTransForm(request.POST)
        if form.is_valid():
            trans = form.save(commit=False)
            trans.module = 'church'
            trans.entity = entity
            trans.created_by = request.user
            trans.save()
            messages.success(request, "Church transaction saved.")
            return redirect('church_trans_create', slug=slug)

    context = {
        'entity': entity,
        'form': form,
        'members': members,
        'trans_type': 'Church',
    }
    return render(request, 'RecPayApp/church_trans_create.html', context)


@login_required
def school_trans_create(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    pupils = Pupil.objects.filter(is_active=True).order_by('last_name', 'first_name')
    parents = Parent.objects.filter(is_active=True).order_by('last_name', 'first_name')
    staff = Staff.objects.filter(is_active=True).order_by('last_name', 'first_name')
    form = BaseTransForm()

    if request.method == 'POST':
        form = BaseTransForm(request.POST)
        if form.is_valid():
            trans = form.save(commit=False)
            trans.module = 'school'
            trans.entity = entity
            trans.created_by = request.user
            trans.save()
            messages.success(request, "School transaction saved.")
            return redirect('school_trans_create', slug=slug)

    context = {
        'entity': entity,
        'form': form,
        'pupils': pupils,
        'parents': parents,
        'staff': staff,
        'trans_type': 'School',
    }
    return render(request, 'RecPayApp/school_trans_create.html', context)


@login_required

def finance_trans_create1(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    
    # Get the list of accounts from the entity's Chart of Accounts
    coa = entity.get_default_coa()
    accounts = AccountModel.objects.filter(coa_model=coa).exclude(role='root').order_by('code')
    
    # For finance, we don't need member/loan selection.
    # We'll just use a plain transaction form.
    
    if request.method == 'POST':
        # Process the form
        try:
            # Parse date
            date_str = request.POST.get('date', '').strip()
            # ... similar parsing as in trans_create
            # We'll reuse the same logic but without member/loan fields
            
            # Create Trans record with module='finance'
            trans = Trans.objects.create(
                date=date,
                trans_no=request.POST.get('trans_no', ''),
                trans_type=request.POST.get('trans_type', ''),
                amount=amount,
                pay_mode=request.POST.get('pay_mode', ''),
                details=request.POST.get('details', ''),
                ledger_code=request.POST.get('ledger_code', ''),
                ledger_name=request.POST.get('ledger_name', ''),
                module='finance',
                entity=entity,
                created_by=request.user,
                # other fields as needed
            )
            messages.success(request, "Finance transaction saved.")
            return redirect('finance_trans_create', slug=slug)
        except Exception as e:
            messages.error(request, f"Error: {e}")
    
    # GET request – show form
    context = {
        'entity': entity,
        'accounts': accounts,
        'today': timezone.now().date(),
    }
    return render(request, 'RecPayApp/finance_trans_create.html', context)

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from decimal import Decimal
from datetime import datetime

from RecPayApp.models import Trans


@login_required
def finance_trans_create(request, slug):
    from django_ledger.models import EntityModel, LedgerModel, JournalEntryModel, AccountModel, TransactionModel
    entity = get_object_or_404(EntityModel, slug=slug)

    coa = entity.get_default_coa()
    accounts = AccountModel.objects.filter(coa_model=coa).exclude(role='root').order_by('code')

    if request.method == 'POST':
        try:
            date_str = request.POST.get('date', '').strip()
            date = None
            for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d']:
                try:
                    date = datetime.strptime(date_str, fmt).date()
                    break
                except ValueError:
                    continue
            if not date:
                messages.error(request, "Invalid date format. Use DD/MM/YYYY.")
                return render(request, 'RecPayApp/finance_trans_create.html', {'entity': entity, 'accounts': accounts})

            amount_str = request.POST.get('amount', '0').strip().replace(',', '')
            try:
                amount = Decimal(amount_str)
            except:
                messages.error(request, "Invalid amount.")
                return render(request, 'RecPayApp/finance_trans_create.html', {'entity': entity, 'accounts': accounts})

            chart_account = request.POST.get('chart_account', '')
            ledger_code = ''
            ledger_name = ''
            if chart_account:
                parts = chart_account.split(',')
                if len(parts) >= 2:
                    ledger_code = parts[1].strip()
                    ledger_name = parts[2].strip() if len(parts) > 2 else ''

            trans_no = request.POST.get('trans_no', '').strip()
            trans_type = request.POST.get('trans_type', '')
            pay_mode = request.POST.get('pay_mode', '')
            details = request.POST.get('details', '').strip()

            # Create Trans record – without 'entity'
            trans = Trans.objects.create(
                entity=entity,
                date=date,
                trans_no=trans_no,
                trans_type=trans_type,
                amount=amount,
                pay_mode=pay_mode,
                details=details,
                ledger_code=ledger_code,
                ledger_name=ledger_name,
                module='finance',
                # created_by is likely a ForeignKey to User; if your model uses 'created_by' then it's fine
                created_by=request.user,
            )

            messages.success(request, "✅ Finance transaction saved successfully.")
            return redirect('RecPayApp:finance_trans_create', slug=entity.slug)

        except Exception as e:
            messages.error(request, f"❌ Error: {str(e)}")
 
    context = {
        'entity': entity,
        'accounts': accounts,
        'today': timezone.now().date(),
    }
    return render(request, 'RecPayApp/finance_trans_create.html', context)


@login_required
def trans_approval_list(request, slug=None):
    # If slug is provided, filter by entity (if you have entity FK on Trans)
    # Otherwise, show all transactions (or filter by user's default entity)
    if slug:
        entity = get_object_or_404(EntityModel, slug=slug)
        trans_list = Trans.objects.filter(entity=entity).order_by('-date', '-id')
    else:
        # Get user's default entity
        profile = request.user.djan_led_profile
        entity = profile.default_entity
        if entity:
            trans_list = Trans.objects.filter(entity=entity).order_by('-date', '-id')
        else:
            trans_list = Trans.objects.none()
            messages.warning(request, "No entity assigned.")
    
    context = {
        'trans_list': trans_list,
        'entity': entity,
    }
    return render(request, 'RecPayApp/trans_approval_list.html', context)


from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Trans
from .utils import post_trans_to_ledger

@login_required
def process_transactions(request):
    if request.method == 'POST':
        action = request.POST.get('action', 'post')
        selected_ids = request.POST.getlist('selected_ids')
        if not selected_ids:
            messages.warning(request, "No transactions selected.")
            return redirect('RecPayApp:trans_approval_list')

        if action == 'post':
            posted_count = 0
            for trans_id in selected_ids:
                trans = Trans.objects.get(id=trans_id)
                if trans.journal_status != 'POSTED':
                    # Option 1: Directly call post function
                    # post_trans_to_ledger(trans)
                    # trans.journal_status = 'POSTED'
                    # trans.save()
                    # Or set to APPROVED and let signal handle it
                    trans.journal_status = 'APPROVED'
                    trans.save()
                    posted_count += 1
            messages.success(request, f"{posted_count} transactions posted to ledger.")
        elif action == 'approve':
            count = Trans.objects.filter(id__in=selected_ids).update(journal_status='APPROVED')
            messages.success(request, f"{count} transactions approved.")
        elif action == 'delete':
            count = Trans.objects.filter(id__in=selected_ids).delete()
            messages.success(request, f"{count} transactions deleted.")

        return redirect('RecPayApp:trans_approval_list')


@login_required
def trans_approval_list(request, slug):
    from django_ledger.models import EntityModel, LedgerModel, JournalEntryModel, AccountModel, TransactionModel
    entity = get_object_or_404(EntityModel, slug=slug)

    # Get all transactions for this entity (you need to link Trans to Entity)
    # If Trans has an `entity` field, filter by it.
    # If not, we'll assume all transactions belong to the user's default entity.
    # For now, we'll filter by the user's default entity.
    try:
        profile = request.user.djan_led_profile
        default_entity = profile.default_entity
    except:
        default_entity = None

    if default_entity and default_entity.slug == slug:
        transactions = Trans.objects.filter(entity=entity).order_by('-date', '-id')
    else:
        # If not linked, we can show all but we should check permissions.
        transactions = Trans.objects.filter(module='finance').order_by('-date', '-id')  # adjust module as needed

    # Only show transactions that are not already posted (or show all with status)
    # We'll show all and let supervisor decide.

    context = {
        'entity': entity,
        'transactions': transactions,
    }
    return render(request, 'RecPayApp/trans_approval_list.html', context)

@login_required
def trans_post_selected(request, slug):
    from django_ledger.models import EntityModel, LedgerModel, JournalEntryModel, AccountModel, TransactionModel
    entity = get_object_or_404(EntityModel, slug=slug)

    if request.method == 'POST':
        selected_ids = request.POST.getlist('selected_ids')
        action = request.POST.get('action', '')

        if not selected_ids:
            messages.warning(request, "No transactions selected.")
            return redirect('trans_list', slug=slug)

        if action == 'post':
            posted_count = 0
            for trans_id in selected_ids:
                trans = get_object_or_404(Trans, id=trans_id, entity=entity)
                if trans.journal_status != 'POSTED':
                    from .utils import post_trans_to_ledger
                    result = post_trans_to_ledger(trans)
                    if result:
                        posted_count += 1
                    else:
                        messages.error(request, f"Failed to post transaction #{trans.trans_no}")
                else:
                    messages.info(request, f"Transaction #{trans.trans_no} already posted.")
            messages.success(request, f"{posted_count} transactions posted to the ledger.")
        else:
            messages.warning(request, "No valid action selected.")

    return redirect('RecPayApp:trans_approval_list', slug=slug)

@login_required
def trans_post_selected(request, slug):
    from django_ledger.models import EntityModel, LedgerModel, JournalEntryModel, AccountModel, TransactionModel
    entity = get_object_or_404(EntityModel, slug=slug)

    if request.method == 'POST':
        selected_ids = request.POST.getlist('selected_ids')
        action = request.POST.get('action', '')

        if not selected_ids:
            messages.warning(request, "No transactions selected.")
            return redirect('RecPayApp:trans_approval_list', slug=slug)

        if action == 'post':
            posted_count = 0
            for trans_id in selected_ids:
                trans = get_object_or_404(Trans, id=trans_id, entity=entity)
                if trans.journal_status != 'POSTED':
                    from .utils import post_trans_to_ledger
                    result = post_trans_to_ledger(trans)
                    if result:
                        posted_count += 1
                    else:
                        messages.error(
                            request, f"Failed to post transaction #{trans.trans_no}")
                else:
                    messages.info(
                        request, f"Transaction #{trans.trans_no} already posted.")
            messages.success(
                request, f"{posted_count} transactions posted to the ledger.")
        else:
            messages.warning(request, "No valid action selected.")

    return redirect('RecPayApp:trans_approval_list', slug=slug)
