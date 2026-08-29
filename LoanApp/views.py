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
from dateutil.relativedelta import relativedelta

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.rl_settings import underlineWidth


# ## Tables
from .models import Loan, Guarantor
from MembersApp.models import Master
from django_ledger.models import EntityModel

## ############################
def loans_home(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    return render(request, 'LoanApp/loans_home.html')

@login_required
def back_to_home(request, slug):
    """Return to main dashboard"""
    return redirect('/')  # This takes user back to dashboard

@login_required
def main_menu(request):
    return render(request, 'SysSetup/loans_home.html')

@login_required
def search_master(request, slug):
    """Search for a master - simple but effective"""
    entity = get_object_or_404(EntityModel, slug=slug)
    query = request.GET.get('q', '').strip()
    results = []
    selected_master = None
    
    # Check if a master was selected
    master_id = request.GET.get('master_id')
    if master_id:
        selected_master = get_object_or_404(Master, pk=master_id)
        return redirect('loan_form_with_master', master_id=selected_master.pk)
    
    # Perform search if query exists
    if query:
        from django.db.models import Q
        
        # FIRST: Try exact matches
        
        # Check if query is a number (ID)
        if query.isdigit():
            try:
                # Use pk instead of id
                exact_match = Master.objects.get(pk=int(query))
                return redirect('LoanApp:loan_form_with_master', slug=entity.slug, master_id=exact_match.pk)
            except Master.DoesNotExist:
                pass
        
        # Check exact telephone1
        try:
            exact_match = Master.objects.get(telephone1=query)
            return redirect('LoanApp:loan_form_with_master', slug=entity.slug, master_id=exact_match.pk)
        except (Master.DoesNotExist, ValueError):
            pass
        
        # Check exact telephone2
        try:
            exact_match = Master.objects.get(telephone2=query)
            return redirect('LoanApp:loan_form_with_master', slug=entity.slug, master_id=exact_match.pk)
        except (Master.DoesNotExist, ValueError):
            pass
        
        # Check exact email
        try:
            exact_match = Master.objects.get(email_address__iexact=query)
            return redirect('LoanApp:loan_form_with_master', slug=entity.slug, master_id=exact_match.pk)
        except Master.DoesNotExist:
            pass
        
        # Check exact full name
        try:
            exact_match = Master.objects.get(full_name__iexact=query)
            return redirect('LoanApp:loan_form_with_master', slug=entity.slug, master_id=exact_match.pk)
        except Master.DoesNotExist:
            pass
        
        # SECOND: Broad search
        words = query.split()
        
        if len(words) == 1:
            word = words[0]
            results = Master.objects.filter(
                Q(last_name__icontains=word) |
                Q(first_name__icontains=word) |
                Q(other_names__icontains=word) |
                Q(full_name__icontains=word) |
                Q(telephone1__icontains=word) |
                Q(telephone2__icontains=word) |
                Q(email_address__icontains=word)
            ).distinct()[:20]
        else:
            first_name = words[0]
            last_name = words[-1] if len(words) > 1 else words[0]
            
            results = Master.objects.filter(
                Q(first_name__icontains=first_name, last_name__icontains=last_name) |
                Q(first_name__icontains=last_name, last_name__icontains=first_name) |
                Q(full_name__icontains=query)
            ).distinct()[:20]
    
    context = {
        'query': query,
        'results': results,
        'today': date.today(),
    }
    
    return render(request, 'LoanApp/search_master.html', context)

@login_required
def loan_form(request, slug, master_id=None):
    entity = get_object_or_404(EntityModel, slug=slug)
    """Display loan form with optional pre-selected master"""
    
    # Get all masters for the dropdown
    masters = Master.objects.all()
    
    # If a master_id is provided, get that specific master
    selected_master = None
    if master_id:
        selected_master = get_object_or_404(Master, id=master_id)
    
    context = {
        'masters': masters,
        'selected_master': selected_master,
        'today': date.today(),
    }
    
    return render(request, 'LoanApp/loan_form.html', context)


@login_required
def loan_form_with_master(request, slug, master_id=None):
    entity = get_object_or_404(EntityModel, slug=slug)
    """Display loan form with optional pre-selected master"""
    
    # Get all masters for the dropdown
    masters = Master.objects.all()
    
    # If a master_id is provided, get that specific master
    selected_master = None
    if master_id:
        selected_master = get_object_or_404(Master, id=master_id)
    
    context = {
        'masters': masters,
        'selected_master': selected_master,
        'today': date.today(),
    }
    
    return render(request, 'LoanApp/loan_form.html', context)


@login_required

def create_loan_success(request, slug, loan_id):
    entity = get_object_or_404(EntityModel, slug=slug)
    """Handle loan creation form submission"""
    if request.method == 'POST':
        master_id = request.POST.get('master_id')
        master = get_object_or_404(Master, id=master_id)
        
        # Process the loan creation
        # ... your loan creation logic here
        
        return redirect('loan_success')

@login_required    
def create_loan(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    """Handle loan creation - save borrower's balance at application time"""
    if request.method == 'POST':
        tot_repayment = 0.00
        try:
            print("DEBUG: Processing loan application...")

            # Get form data
            master_id = request.POST.get('master_id')
            principal = request.POST.get('principal')
            purpose = request.POST.get('purpose', '')
            interest_rate = request.POST.get('interest_rate')
            loan_term = request.POST.get('loan_term')
            moratorium = request.POST.get('moratorium', '0')
            voucher_no = request.POST.get('voucher_no', '')

            # Date fields

            date_applied = parse_date(request.POST.get('date_applied'))
            disbursement_date = parse_date(request.POST.get('disbursement_date'))
            date_approved = parse_date(request.POST.get('date_approved'))
            next_repayment_date = parse_date(request.POST.get('next_repayment_date'))
            int_loan_term = int(round(float(loan_term)))
            expiry_date = disbursement_date + relativedelta(months=int_loan_term)

            # Monthly repayment (from hidden field)
            monthly_repayment = request.POST.get('monthly_repayment')
            if not monthly_repayment:
                monthly_repayment = calculate_monthly_repayment(
                    Decimal(principal),
                    Decimal(interest_rate),
                    int(loan_term)
                )

            monthly_interest = float(principal) * float(interest_rate) / 100

            tot_repayment = float(monthly_repayment) + float(monthly_interest)
            approved_by = request.POST.get('approved_by', '')

            print(master_id)

            # Validate required fields
            if not all([master_id, principal, interest_rate, loan_term, voucher_no]):
                messages.error(request, 'Please fill in all required fields.')
                return redirect('create_loan')

            # Get borrower and their current balance
            master = Master.objects.get(id=master_id)
            master_current_balance = master.available_balance
            master_name = master.full_name

            print(f"DEBUG: Borrower {master.last_name} has current balance: ₵{master_current_balance}")

            # Prepare guarantor data
            guarantor_data = {
                'guarantors': [],
                'total_guaranteed': 0,
                'guarantor_count': 0
            }

            # Process guarantors
            guarantor_ids = request.POST.getlist('guarantor_ids[]')
            guarantor_amounts = request.POST.getlist('guarantor_amounts[]')
            guarantor_dates = request.POST.getlist('guarantor_dates[]')

            for i, guarantor_id in enumerate(guarantor_ids):
                if guarantor_id and i < len(guarantor_amounts) and guarantor_amounts[i]:
                    try:
                        guarantor_master = Master.objects.get(id=guarantor_id)
                        guarantor_amount = Decimal(guarantor_amounts[i])

                        guarantor_info = {
                            'id': int(guarantor_id),
                            'name': guarantor_master.full_name,
                            'amount': str(guarantor_amount),
                            'date': guarantor_dates[i] or timezone.now().date().isoformat(),
                            'member_id': guarantor_master.id,
                            'available_balance': str(guarantor_master.available_balance)  # Store guarantor's balance too
                        }
                        guarantor_data['guarantors'].append(guarantor_info)
                        guarantor_data['total_guaranteed'] += float(guarantor_amount)
                        guarantor_data['guarantor_count'] += 1

                    except Master.DoesNotExist:
                        print(f"DEBUG: Guarantor with ID {guarantor_id} not found")

            # Create loan with borrower's balance at application time

            loan = Loan.objects.create(
                
                master=master,
                entity = entity,
        #        master_id=master_id,
                master_name=master_name,
                master_avail_bal=master_current_balance,
                
                principal=Decimal(principal),
                loan_balance=Decimal(principal),
                purpose=purpose,
                voucher_no=voucher_no,
                # NEW: Save the borrower's balance at application time
                interest_rate=Decimal(interest_rate),
                loan_term=int(loan_term),
                months_remain=int(loan_term),
                moratorium=int(moratorium),
                date_applied=date_applied or timezone.now().date(),
                disbursement_date=disbursement_date or timezone.now().date(),
                expiry_date=expiry_date or timezone.now().date,
                date_approved=date_approved or timezone.now().date(),
                approved_by=approved_by,
                monthly_repayment=Decimal(monthly_repayment),
                next_repayment_date=next_repayment_date or timezone.now().date() + timedelta(days=30),
                status='New Loan',
                payment_status='Active',
                guarantor_data=guarantor_data,
                
                due_date=next_repayment_date,
                due_days=30,
                due_interest=monthly_interest,
                due_repayment=Decimal(monthly_repayment), 
                due_tot_repayment = tot_repayment          
            )

            print(f"DEBUG: Loan created with ID: {loan.id}")
            print(f"DEBUG: Borrower balance at application saved: ₵{master_current_balance}")

            # Also create Guarantor model instances

            guarantor_ids = request.POST.getlist('guarantor_ids[]')
            guarantor_amounts = request.POST.getlist('guarantor_amounts[]')
            guarantor_dates = request.POST.getlist('guarantor_dates[]')

            for i, guarantor_id in enumerate(guarantor_ids):
                if guarantor_id and i < len(guarantor_amounts) and guarantor_amounts[i]:
                    try:
                        print(f"Processing guarantor {i}:")
                        print(f"  ID: {guarantor_id}")
                        print(f"  Amount string: '{guarantor_amounts[i]}'")
                        print(f"  Amount type: {type(guarantor_amounts[i])}")
                        print(f"  Guarantor Date: '{guarantor_dates[i]}'")

                        guarantor_master = Master.objects.get(id=guarantor_id)
                        guarantor_amount = Decimal(guarantor_amounts[i])
                        guarantor_name = guarantor_master.full_name
                        print(f"  Guarantor Name: '{guarantor_name}'")

                        # Get the date string and parse it
                        date_str = guarantor_dates[i] if i < len(guarantor_dates) else None

                        # Parse the date (this should be your parse_date function)
                        # Make sure parse_date can handle both DD/MM/YYYY and YYYY-MM-DD
                        parsed_date = parse_date(date_str) if date_str else timezone.now().date()

                        print(f"Parsed date: {parsed_date}")

                        #  Create Guarantor record
                        print("Inside Guarantor Write")

                        Guarantor.objects.create(
                            loan=loan,
                            guarantor_name=guarantor_name,
                            master=guarantor_master,
                            guaranteed_amount=guarantor_amount,  # Use the converted variable
                            guaranteed_date=parsed_date,  # Use the parsed date
                            status='ACTIVE',
                        )
                        print("Exiting Guarantor Write")

                    except Master.DoesNotExist:
                        messages.error(request, f"Guarantor with ID {guarantor_id} not found")
                    except Exception as e:
                        messages.error(request, f"Error creating guarantor: {str(e)}")

            messages.success(request, f'Loan application submitted successfully! Loan ID: #{loan.id}')
            return redirect("LoanApp:loan_success", slug=slug, loan_id=loan.id)
        #    return redirect("LoanApp:loan_success", slug, loan_id=loan.id)

        except Exception as e:
            print(f"DEBUG: Error: {str(e)}")
            messages.error(request, f'Error creating loan: {str(e)}')
            return redirect('LoanApp:create_loan', slug)

    # GET request - show the form
    masters = Master.objects.all()

    context = {
        'masters': masters,
        'today': timezone.now().date(),
    }
    return render(request, 'LoanApp/loan_form.html', context)


@login_required
def loan_detail(request, slug, loan_id):
    entity = get_object_or_404(EntityModel, slug=slug)
    loan = get_object_or_404(Loan, id=loan_id)
    
    context = {
        'loan': loan,
        'shortfall': loan.shortfall,  # This will now work!
        'total_guaranteed': loan.total_guaranteed,
        'guarantor_count': loan.guarantor_count,
        'coverage_status': loan.coverage_status,
        'coverage_text': loan.coverage_text,
    }
    return render(request, 'LoanApp/loan_detail.html', context)

@login_required
def voucher_daily_update(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    vous = Voucher.objects.filter(desc="Loan Repayment")
    
    for vou in vous:
        
        # Use Voucher details to read Loan and Master Tables
        try:
            loan = Loan.objects.get(id=vou.loan_id)
        # Proceed with using the 'loan' object
            print(f"Loan found: {loan.principal}")
        
        except Loan.DoesNotExist:
        # Handle the case where no loan is found
            print(f"No Loan with ID {loan_id} matches the query.")
            loan = None  # Or assign a default value, or return an error response
        
        
        master = get_object_or_404(Master, id=vou.master_id)
        
        interest = loan.int_calc()
        old_balance = loan.loan_balance
        old_months = loan.months_remain
        old_tot_int = loan.tot_int
        old_tot_ded = loan.tot_ded
        old_next_repayment_date = loan.next_repayment_date 
        loan_id = id
        
        
        
        
        if vou.amount >= loan.int_calc():
            
            amt = vou.amount
            ded = amt - interest
            loan.new_ded_calc = ded
            loan.new_int_calc = interest
            loan.tot_int = loan.tot_int + loan.new_int_calc
            loan.tot_ded = loan.tot_ded + loan.new_ded_calc
            loan.months_remain = loan.months_remain - 1
            loan.loan_balance = loan.loan_balance - ded
            loan.loan_payment_status = "Active"
                 
        elif vou.amount < loan.int_calc():
            amt = vou.amount
            ded = 0.00
            loan.new_ded_calc = ded
            loan.new_int_calc = interest
            loan.tot_int = loan.tot_int + interest
            loan.tot_ded = loan.tot_ded + Decimal(ded)
            loan.months_remain = loan.months_remain - 1
            loan.loan_balance = loan.loan_balance - Decimal(ded)
            loan.loan_payment_status = "Active"
            
            loan.save()
                 
        gua_list = Guarantor.objects.filter(loan_id=vou.loan_id)
        GuaCnt = gua_list.count()
        
        if GuaCnt > 0:
            gua_amt_left = ded
            
            for gua in gua_list:
                print(gua_list)
                if gua_amt_left <= 0:
                    break
                gua_amt_state_write = 0
    #            read next record.
                if gua.guarantee_amount >= gua_amt_left:
                    gua.redeemed_amount = gua.redeemed_amount + gua_amt_left
                    gua_amt_state_write = gua_amt_left
                    gua_amt_left = 0
                    
                else: 
                    gua.redeemed_amount = gua.redeemed_amount + gua.guarantee_amount
                    gua_amt_left = gua_amt_left - gua.guarantee_amount
                    gua_amt_state_write = gua_amt_left
                    
                gua.save()
                
                gua_state = Gua_Statement.objects.create(
                    entity = entity,
                    voucher_id = vou.id,
                    master_id=vou.master_id,
                    loan_id=vou.loan_id,
                    guarantor_id=gua.id,
                    guaranteed_amount=gua.guarantee_amount,
                    redeemed_amount=gua.redeemed_amount,
                    amount_left=gua_amt_state_write,
                )
                    
    #    Save all guarantor records(id, loan_id, master_id, gua_amt_left) to statement guarantor_data                    

        state = Loan_Statement.objects.create(
            loan_id = vou.loan_id,
            master_id = vou.master_id,
            balance = old_balance,
            months = old_months,
            rate = loan.interest_rate,
            interest = interest,
            ded =  ded,
            amount = vou.amount,
            new_balance = loan.loan_balance,
            new_months = loan.months_remain,
            old_tot_int = old_tot_int,
            old_tot_ded = old_tot_ded,
            tot_int = loan.tot_int,
            tot_ded = loan.tot_ded,
            next_repayment_date = old_next_repayment_date,
            new_repayment_date = old_next_repayment_date + + timedelta(30),
           # guarantor_data = all guarantor record
        )
            
            
    return render(request, 'loan_list_other.html')


@login_required
def guarantor_search(request, slug):
    pass

@login_required
def loan_guarantors(request, slug):
    pass
##   ####################################################################

@login_required
def loan_list_other(request, slug):
    loans = Loan.objects.all()
    return render(request, 'LoanApp/loan_list_other1.html', {'loans': loans})

@login_required
def loan_state_list(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    state = Loan_Statement.objects.all()
    return render(request, 'loan_statement_list.html', {'loans': loans})

@login_required
def loan_success(request, slug, loan_id):
    entity = get_object_or_404(EntityModel, slug=slug)
    """Loan success page"""
    loan = get_object_or_404(Loan, id=loan_id)
    guarantors = loan.guarantors.all()
    
    context = {
        'loan': loan,
        'guarantors': guarantors,
    }
    return render(request, 'loan_success.html', context)


@login_required
def master_loans(request, slug, master_id):
    entity = get_object_or_404(EntityModel, slug=slug)
    """List all loans for a specific master"""
    master = get_object_or_404(Master, id=master_id)
    loans = Loan.objects.filter(borrower=master)
    
    context = {
        'master': master,
        'loans': loans,
    }
    return render(request, 'master_loans.html', context)

# Utility function
@login_required
def calculate_monthly_repayment(principal, annual_rate, term, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    """Calculate monthly repayment using amortization formula"""
    if principal <= 0 or annual_rate <= 0 or term <= 0:
        return Decimal('0.00')
    
    monthly_rate = float(annual_rate) / 100 / 12
    monthly_payment = float(principal) * monthly_rate * (1 + monthly_rate) ** term / ((1 + monthly_rate) ** term - 1)
    return Decimal(monthly_payment).quantize(Decimal('0.01'))

## ##################################################################
@login_required
def home(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    return render(request, 'home.html')

@login_required
def dashboard(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    """Main dashboard view"""
    total_loans = Loan.objects.count()
    total_members = Master.objects.count()
    active_loans = Loan.objects.filter(status='disbursed').count()
    total_principal = Loan.objects.aggregate(Sum('principal'))['principal__sum'] or 0
    
    context = {
        'total_loans': total_loans,
        'total_members': total_members,
        'active_loans': active_loans,
        'total_principal': total_principal,
    }
    return render(request, 'dashboard.html', context)

# views.py - Update create_loan function

# views.py - Add this new view

# Utility function
@login_required
def calculate_monthly_repayment(principal, annual_rate, term, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    """Calculate monthly repayment using amortization formula"""
    if principal <= 0 or annual_rate <= 0 or term <= 0:
        return Decimal('0.00')
    
    monthly_rate = float(annual_rate) / 100 / 12
    monthly_payment = float(principal) * monthly_rate * (1 + monthly_rate) ** term / ((1 + monthly_rate) ** term - 1)
    return Decimal(monthly_payment).quantize(Decimal('0.01'))


#### ##############################################################

@login_required
def calculate_repayment(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    """Calculate monthly repayment - called via form submission"""
    if request.method == 'POST':
        principal = request.POST.get('principal', '0')
        interest_rate = request.POST.get('interest_rate', '3.0')
        loan_term = request.POST.get('loan_term', '12')
        
        try:
            principal_dec = Decimal(principal)
            interest_rate_dec = Decimal(interest_rate)
            loan_term_int = int(loan_term)
            
            # Monthly repayment calculation
            monthly_rate = float(interest_rate_dec) / 100 / 12
            if monthly_rate > 0:
                monthly_repayment = float(principal_dec) * monthly_rate * (1 + monthly_rate) ** loan_term_int / ((1 + monthly_rate) ** loan_term_int - 1)
            else:
                monthly_repayment = float(principal_dec) / loan_term_int
            
            monthly_repayment_dec = Decimal(monthly_repayment).quantize(Decimal('0.01'))
            
            messages.info(request, f'Calculated Monthly Repayment: ₵{monthly_repayment_dec}')
            
        except Exception as e:
            messages.error(request, f'Error in calculation: {str(e)}')
    
    return redirect('loan_application')

def loan_success(request, slug, loan_id):
    entity = get_object_or_404(EntityModel, slug=slug)
    """Loan success page"""
    try:
        loan = get_object_or_404(Loan, id=loan_id)
        guarantors = loan.guarantors.all()
        
        context = {
            'loan': loan,
            'guarantors': guarantors,
            'borrower_name': loan.master.full_name,
        }
        return render(request, 'LoanApp/loan_success.html', context)
        
    except Exception as e:
        messages.error(request, f'Error displaying loan: {str(e)}')
        return redirect('LoanApp:loan_list', slug)

# views.py
from django.db.models import Q

def loan_list(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    """List all loans - properties handle guarantor_data automatically"""
    loans = Loan.objects.select_related('master').all()
    
    # Handle search
    search_query = request.GET.get('search', '')
    if search_query:
        loans = loans.filter(
            Q(master_name__icontains=search_query) |
            Q(purpose__icontains=search_query)
        )
    
    loans = loans.order_by('-date_applied')
    
    #  NO NEED for manual processing - properties handle everything!
    # Just use the loans queryset directly
    
    context = {
        'loans': loans,  # Pass the queryset directly
        'search_query': search_query,
        'total_loans': loans.count(),
    }
    return render(request, 'LoanApp/loan_list.html', context)

def master_loans(request, slug, master_id):
    entity = get_object_or_404(EntityModel, slug=slug)
    """List all loans for a specific master"""
    master = get_object_or_404(Master, id=master_id)
    loans = Loan.objects.filter(master=master)
    
    context = {
        'master': master,
        'loans': loans,
    }
    return render(request, 'LoanApp/master_loans.html', context)


# loans/views.py
def loan_statistics(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    """Loan statistics dashboard"""
   
    
    # Get all loans
    loans = Loan.objects.select_related('master').all()
    
    # Basic statistics
    total_loans = loans.count()
    active_loans = loans.filter(status='ACTIVE').count()
    completed_loans = loans.filter(status='COMPLETED').count()
    
    # Portfolio amounts
    total_portfolio = loans.aggregate(total=Sum('principal'))['total'] or Decimal('0')
    total_disbursed = loans.filter(status='ACTIVE').aggregate(total=Sum('principal'))['total'] or Decimal('0')
    total_outstanding = loans.aggregate(total=Sum('loan_balance'))['total'] or Decimal('0')
    total_repaid = total_portfolio - total_outstanding
    
    # Collection rate
    collection_rate = (total_repaid / total_portfolio * 100) if total_portfolio > 0 else 0
    
    # Status distribution for chart
    status_distribution = []
    status_colors = {
        'ACTIVE': 'success',
        'PENDING': 'warning',
        'COMPLETED': 'info',
        'DEFAULTED': 'danger'
    }
    
    for status_code, status_name in Loan.STATUS_CHOICES:
        count = loans.filter(status=status_code).count()
        if count > 0:
            percentage = (count / total_loans * 100) if total_loans > 0 else 0
            status_distribution.append({
                'name': status_name,
                'count': count,
                'percentage': round(percentage, 1),
                'color': status_colors.get(status_code, 'secondary')
            })
    
    # Chart data
    status_chart_data = {
        'labels': [s['name'] for s in status_distribution],
        'data': [s['count'] for s in status_distribution],
        'colors': ['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b']
    }
    
    # Top products (loan products by count/amount)
    top_products = []
    # Add your product logic here
    
    products_chart_data = {
        'labels': [p['name'] for p in top_products],
        'data': [float(p['amount']) for p in top_products]
    }
    
    # Monthly trends (last 6 months)
    trends_months = []
    trends_disbursed = []
    trends_repaid = []
    
    for i in range(5, -1, -1):
        month_date = datetime.now() - timedelta(days=30*i)
        month_name = month_date.strftime('%b %Y')
        trends_months.append(month_name)
        
        # Get data for this month
        month_start = month_date.replace(day=1)
        if month_date.month == 12:
            month_end = month_date.replace(year=month_date.year+1, month=1, day=1)
        else:
            month_end = month_date.replace(month=month_date.month+1, day=1)
        
        disbursed = Loan.objects.filter(
            disbursement_date__gte=month_start,
            disbursement_date__lt=month_end
        ).aggregate(total=Sum('principal'))['total'] or Decimal('0')
        
        trends_disbursed.append(float(disbursed))
        trends_repaid.append(0)  # Add repayment calculation logic
    
    trends_chart_data = {
        'months': trends_months,
        'disbursed': trends_disbursed,
        'repaid': trends_repaid
    }
    
    # Recent loans
    recent_loans = loans.order_by('-disbursement_date')[:10]
    
    # Top guarantors (using your existing logic)
    top_guarantors = []
    # Add your guarantor query here
    
    # Performance metrics
    avg_loan_size = loans.aggregate(avg=Sum('principal'))['avg'] or Decimal('0')
    if total_loans > 0:
        avg_loan_size = avg_loan_size / total_loans
    
    avg_interest_rate = loans.aggregate(avg=Sum('interest_rate'))['avg'] or Decimal('0')
    if total_loans > 0:
        avg_interest_rate = avg_interest_rate / total_loans
    
    avg_loan_term = loans.aggregate(avg=Sum('loan_term'))['avg'] or Decimal('0')
    if total_loans > 0:
        avg_loan_term = avg_loan_term / total_loans
    
    defaulted = loans.filter(status='DEFAULTED').count()
    default_rate = (defaulted / total_loans * 100) if total_loans > 0 else 0
    
    context = {
        'total_loans': total_loans,
        'active_loans': active_loans,
        'completed_loans': completed_loans,
        'total_portfolio': total_portfolio,
        'total_disbursed': total_disbursed,
        'total_outstanding': total_outstanding,
        'total_repaid': total_repaid,
        'collection_rate': round(collection_rate, 1),
        'status_distribution': status_distribution,
        'status_chart_data': status_chart_data,
        'top_products': top_products,
        'products_chart_data': products_chart_data,
        'trends_chart_data': trends_chart_data,
        'recent_loans': recent_loans,
        'top_guarantors': top_guarantors,
        'avg_loan_size': avg_loan_size,
        'avg_interest_rate': avg_interest_rate,
        'avg_loan_term': avg_loan_term,
        'default_rate': round(default_rate, 1),
    }
    
    return render(request, 'LoanApp/loan_statistics.html', context)


# views.py - Add this new view
def loan_print_view(request, slug, loan_id):
    entity = get_object_or_404(EntityModel, slug=slug)
    """Printer-friendly loan details view"""
    loan = get_object_or_404(Loan, id=loan_id)
    master = loan.master
    
    # Calculate coverage information
    balance_at_app = loan.master.available_balance
#    balance_at_app = loan.master.available_balance
    total_guaranteed = loan.guarantor_data.get('total_guaranteed', 0) if loan.guarantor_data else 0
    guarantor_count = loan.guarantor_data.get('guarantor_count', 0) if loan.guarantor_data else 0
    
    # Determine coverage status
    if balance_at_app >= loan.principal:
        coverage_status = 'FULLY COVERED BY BORROWER BALANCE'
    elif balance_at_app + total_guaranteed >= loan.principal:
        coverage_status = 'COVERED WITH GUARANTORS'
    else:
        coverage_status = 'INSUFFICIENT COVERAGE'
    
    shortfall = max(0, loan.principal - balance_at_app)
    
    context = {
        'loan': loan,
        'total_guaranteed': total_guaranteed,
        'guarantor_count': guarantor_count,
        'coverage_status': coverage_status,
        'shortfall': shortfall,
        'balance_at_app': balance_at_app,
    }
    return render(request, 'LoanApp/loan_print_view.html', context)

# views.py - Update the generate_loan_PDF function
###   ########################################################

def gua_list(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug) 
    """Simple list view showing loans with guarantor info"""
    # Get all loans
#    loans = Loan.objects.select_related('master').all()
    loans = Loan.objects.all()
    # Simple search
    search = request.GET.get('search', '')
    if search:
        loans = loans.filter(
            Q(loan_id__icontains=search) |
            Q(master__name__icontains=search) |
            Q(master__member_id__icontains=search)
        )
    
    # Prepare data for template
    loan_data = []
    for loan in loans:
        loan_data.append({
            'loan_id': id,
            'master_id': loan.master_id,
            'master_name': loan.master_name,
            'master_avail_bal':loan.master_avail_bal,
            'loan_balance': loan.loan_balance,
            'int_rate': loan.interest_rate,
            'term': loan.loan_term,
            'shortfall': loan.shortfall,
            'guarantee_details': loan.guarantee_details,
            'guarantee_total': loan.total_guaranteed,
            'guarantor_count': loan.guarantor_count,
        })
    
    context = {
        'loans': loan_data,
        'search': search,
        'total_loans': len(loan_data),
    }
    return render(request, 'LoanApp/gua_list.html', context)


def release_guarantors(slug, loan, amount_paid):
    entity = get_object_or_404(EntityModel, slug=slug)
    """
    Simple logic to release guarantors based on payment
    Returns: List of releases made
    """
    releases = []
    remaining_amount = amount_paid
    
    # Get active guarantors
    if not loan.guarantor_data or 'guarantors' not in loan.guarantor_data:
        return releases
    
    # Sort guarantors by guarantee date (oldest first) or amount (smallest first)
    # We'll release oldest guarantees first
    guarantors = sorted(
        loan.guarantor_data['guarantors'],
        key=lambda x: x.get('date', '')
    )
    
    for guarantor in guarantors:
        if remaining_amount <= 0:
            break
        
        # Get guarantor amounts
        guaranteed = Decimal(str(guarantor.get('amount', 0)))
        released = Decimal(str(guarantor.get('released_amount', 0)))
        available = guaranteed - released
        
        if available > 0:
            # How much to release from this guarantor
            release_amount = min(available, remaining_amount)
            
            # Update guarantor's released amount
            if 'released_amount' in guarantor:
                guarantor['released_amount'] = str(Decimal(str(guarantor['released_amount'])) + release_amount)
            else:
                guarantor['released_amount'] = str(release_amount)
            
            # Add release record
            releases.append({
                'guarantor_id': guarantor['id'],
                'guarantor_name': guarantor['name'],
                'amount_released': str(release_amount),
                'remaining_guarantee': str(available - release_amount),
                'date': timezone.now().date().isoformat()
            })
            
            remaining_amount -= release_amount
    
    # Save updated guarantor data
    loan.guarantor_data['guarantors'] = guarantors
    loan.save()
    
    return releases

from datetime import datetime

def parse_date(date_str):
    """Convert DD/MM/YYYY to Python date object"""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str.strip(), '%d/%m/%Y').date()
    except ValueError:
        return None

def convert_date_format(date_str):
    """Convert DD/MM/YYYY to YYYY-MM-DD for Django"""
    if not date_str:
        return None
    try:
        # Parse DD/MM/YYYY
        date_obj = datetime.strptime(date_str, '%d/%m/%Y')
        # Return YYYY-MM-DD format
        return date_obj.strftime('%Y-%m-%d')
    except:
        return None


# loans/views.py - Add repayment views

from .services.loan_repayment_service import LoanRepaymentService

@login_required
def loan_repayment(request, slug, loan_id):
    entity = get_object_or_404(EntityModel, slug=slug)
    """Process loan repayment"""
    loan = get_object_or_404(Loan, id=loan_id)
    
    if request.method == 'POST':
        amount = Decimal(request.POST.get('amount', 0))
        payment_date = request.POST.get('payment_date', timezone.now().date())
        
        if amount <= 0:
            messages.error(request, "Please enter a valid amount")
            return redirect('loan_repayment', loan_id=loan_id)
        
        if amount > loan.balance + loan.next_month_interest_projected:
            messages.warning(request, f"Amount exceeds total due. Maximum: ₵{loan.balance + loan.next_month_interest_projected}")
        
        # Process the repayment
        service = LoanRepaymentService(loan, amount, payment_date, request.user)
        result = service.process()
        
        if result['success']:
            messages.success(request, 
                f"Repayment of ₵{amount} processed successfully!\n"
                f"Principal: ₵{result['principal_paid']:.2f}, "
                f"Interest: ₵{result['interest_paid']:.2f}")
            
            if result['guarantors_released']:
                messages.info(request, 
                    f"Released {len(result['guarantors_released'])} guarantor(s)")
            
            if result.get('shortfall', 0) > 0:
                messages.warning(request, 
                    f"Shortfall of ₵{result['shortfall']:.2f} - No more guarantors available")
        else:
            for error in result['errors']:
                messages.error(request, error)
        
        return redirect('loan_detail', entity.slug, loan_id=loan_id)
    
    # GET request - show repayment form
    context = {
        'loan': loan,
        'monthly_interest': loan.calculate_monthly_interest(),
        'total_due': loan.balance + loan.calculate_monthly_interest(),
        'guarantors': loan.guarantors.all(),
        'recent_repayments': loan.repayments.all()[:5],
    }
    return render(request, 'LoanApp/loan_repayment.html', context)


from datetime import datetime

@login_required
def loan_list_financials(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug) 
    """Display all loans with totals"""
    loans = Loan.objects.select_related('master').all()
    
    # Calculate totals
    context = {
        'loans': loans,
        'total_principal': sum(loan.principal for loan in loans),
        'total_interest': sum(loan.tot_int or 0 for loan in loans),
        'total_repayable': sum(loan.tot_ded or 0 for loan in loans),
        'total_balance': sum(loan.loan_balance or 0 for loan in loans),
        'total_due_interest': sum(loan.due_interest or 0 for loan in loans),
        'total_due_repayment': sum(loan.due_repayment or 0 for loan in loans),
        'total_monthly_repayment': sum(loan.monthly_repayment or 0 for loan in loans),
    }
    
    return render(request, 'LoanApp/loan_list_financials.html', context)


from django.shortcuts import render, get_object_or_404
from .models import Loan, LoanRepayment

def loan_repayment_list(request, slug, loan_id):
    entity = get_object_or_404(EntityModel, slug=slug)
    loan = get_object_or_404(Lan, id=loan_id)
    repayments = LoanRepayment.objects.filter(loan=loan).order_by('-payment_date')
    context = {
        'loan': loan,
        'repayments': repayments,
    }
    return render(request, 'LoanApp/loan_repayment_list.html', context)


def loan_update_list(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    loans = Loan.objects.all()
    return render(request, "LoanApp/loan_update_list.html", {"loans": loans})


def loan_update_list_pdf(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    loans = Loan.objects.all()
    return render(request, "LoanApp/loan_update_list_pdf.html", {"loans": loans})


def loan_update(process, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    settings = SystemSettings.objects.first()
    loans = Loan.objects.exclude(status="Completed")

    for loan in loans:
        master = loan.master
        
        # 1. Check if loan balance is already 0
        if loan.loan_balance <= 0:
            loan.status = "Completed"
            loan.loan_update_cnt = loan.loan_update_cnt + 1
            loan.save()
            continue  # Move to the next loan

        if loan.next_repayment_date <= date.today():
            loan.loan_update_cnt = loan.loan_update_cnt + 1
            loan.save()
            continue  # Move to the next loan

        elif loan.due_interest > 0:
            # Monthly Loan Interest has not been paid
            loan.loan_balance = loan.loan_balance + loan.due_interest
            if master and master.loan_int_rate > 0:
                int_rate = master.loan_int_rate
            else:
                int_rate = settings.loan_interest_rate if settings else 0
            #
            interest = (loan.loan_balance * int_rate) / 100

            # repayment = loan.principal / loan.loan_term
            next_date = loan.next_repayment_date + timedelta(days=30)
            days_over = date.today() - loan.next_repayment_date
            loan.due_tot_repayment = loan.due_interest + loan.due_repayment
            loan.next_repayment_date = next_date
            loan.due_days = days_over.days  # Ensures it saves as a clean integer
            loan.loan_upd_indicator = True

        # 4. Process the overdue repayment
        if loan.next_repayment_date <= date.today() and loan.loan_balance > 0:
            interest = (loan.loan_balance * int_rate) / 100
            repayment = loan.principal / loan.loan_term
            next_date = loan.next_repayment_date + timedelta(days=30)
            days_over = date.today() - loan.next_repayment_date

            loan.due_interest += interest
            loan.due_repayment += repayment
            loan.due_tot_repayment = loan.due_interest + loan.due_repayment
            loan.next_repayment_date = next_date
            loan.due_days = days_over.days  # Ensures it saves as a clean integer

        # 5. Check if the overall loan has expired
        if (
            loan.expiry_date is not None
            and loan.expiry_date < date.today()
            and loan.loan_balance > 0
        ):
            exp_days = date.today() - loan.expiry_date
            loan.status = "Expired"
            loan.overdue_days = exp_days.days

        loan.loan_update_cnt = loan.loan_update_cnt + 1
        print(loan.id)
        # Save modifications for the current loan
        loan.save()

    return HttpResponse("Completed")
