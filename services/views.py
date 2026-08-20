# In your view

# services/savings_interest.py
# from MembersApp.services.interest_service import InterestAccrualService


from django.shortcuts import render, redirect
from decimal import Decimal
from datetime import date, timedelta
from django.db import transaction


from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
# from services.loan_daily_service import update_loans_daily

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum, Q

from RecPayApp.models import Trans
from MembersApp.models import Master
from LoanApp.models import Loan
from MembersApp.models import Master, Sav_Int_Table
from SysSetup.models import SystemSettings
# from services.loan_daily_service import update_loans_daily
#from services.sav_int_service import InterestAccrualService


# from services.services_trans_posting import process_transaction


def post_transaction(request, trans_id):
    transaction = get_object_or_404(Trans, id=trans_id)
    result = process_transaction(transaction, request.user)
    
    if result['success']:
        messages.success(request, f"Transaction {transaction.rec_vou_no} posted!")
    else:
        for error in result['errors']:
            messages.error(request, error)
    
    return redirect('RecPayApp:transaction_list')

## ======================= Daily Loan Processing ===========================
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
# from services.loan_daily_service import update_loans_daily

@staff_member_required
def run_loan_daily_update(request):
    if request.method == 'POST':
        result = update_loans_daily()
        # Display results as messages
        if result['errors']:
            for err in result['errors']:
                messages.error(request, err)
        messages.success(request, f"Processed {result['processed']} loans. "
                         f"Interest added: {result['interest_added_count']}, "
                         f"Completed: {result['completed_count']}, "
                         f"Expired: {result['expired_count']}, "
                         f"Record Processed: {result['reccnt']}")
        # You could also redirect to the same page to show the form again
        return render(request, 'services/run_loan_update.html', {'result': result})
    return render(request, 'services/run_loan_update.html')

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@login_required
def transaction_list(request):
    """
    Display all transactions with filtering and pagination
    """
    
    # ============================================
    # Get all transactions, newest first
    # ============================================
    transactions = Trans.objects.select_related('member', 'loan').order_by('-date', '-id')
    
    # ============================================
    # Apply filters
    # ============================================
    
    # Filter by transaction type
    trans_type = request.GET.get('trans_type')
    if trans_type:
        transactions = transactions.filter(trans_type=trans_type)
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        transactions = transactions.filter(status=status)
    
    # Filter by date range
    from_date = request.GET.get('from_date')
    if from_date:
        transactions = transactions.filter(date__gte=from_date)
    
    to_date = request.GET.get('to_date')
    if to_date:
        transactions = transactions.filter(date__lte=to_date)
    
    # Filter by member
    member_id = request.GET.get('member_id')
    if member_id:
        transactions = transactions.filter(member_id=member_id)
    
    # Filter by voucher number
    voucher = request.GET.get('voucher')
    if voucher:
        transactions = transactions.filter(rec_vou_no__icontains=voucher)
    
    # ============================================
    # Calculate summary statistics
    # ============================================
    
    summary = {
        'total_count': transactions.count(),
        'total_amount': transactions.aggregate(total=Sum('amount'))['total'] or Decimal('0.00'),
        'receipts_count': transactions.filter(trans_type='Receipts').count(),
        'receipts_total': transactions.filter(trans_type='Receipts').aggregate(total=Sum('amount'))['total'] or Decimal('0.00'),
        'payments_count': transactions.filter(trans_type='Payments').count(),
        'payments_total': transactions.filter(trans_type='Payments').aggregate(total=Sum('amount'))['total'] or Decimal('0.00'),
        'draft_count': transactions.filter(status='DRAFT').count(),
        'draft_total': transactions.filter(status='DRAFT').aggregate(total=Sum('amount'))['total'] or Decimal('0.00'),
        'posted_count': transactions.filter(status='POSTED').count(),
        'posted_total': transactions.filter(status='POSTED').aggregate(total=Sum('amount'))['total'] or Decimal('0.00'),
    }
    
    # ============================================
    # Pagination (50 per page)
    # ============================================
    
    paginator = Paginator(transactions, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # ============================================
    # Get members for filter dropdown
    # ============================================
    
    members = Master.objects.filter(is_deleted=False).order_by('first_name', 'last_name')[:100]
    
    # ============================================
    # Context for template
    # ============================================
    
    context = {
        'transactions': page_obj,
        'summary': summary,
        'members': members,
        'filters': {
            'trans_type': trans_type,
            'status': status,
            'from_date': from_date,
            'to_date': to_date,
            'member_id': member_id,
            'voucher': voucher,
        },
        'total_count': transactions.count(),
    }
    
    return render(request, 'RecPayApp/transaction_list.html', context)


@staff_member_required
def manual_loan_update(request):
    if request.method == 'POST':
        result = update_loans_daily()
        return JsonResponse(result)
    return render(request, 'services/manual_loan_update.html')


# ================ Savings Interest Calculation ===========================


def decimal_to_str(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    return obj


def make_serializable(data):
    """Convert Decimal to string for JSON serialization in session."""
    if isinstance(data, dict):
        return {k: make_serializable(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [make_serializable(item) for item in data]
    elif isinstance(data, Decimal):
        return str(data)
    return data


def make_serializable(data):
    if isinstance(data, dict):
        return {k: make_serializable(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [make_serializable(item) for item in data]
    elif isinstance(data, Decimal):
        return str(data)
    return data


@staff_member_required
def sav_run_interest_accrual(request):
    service = InterestAccrualService()

    if request.method == 'POST':
        # Run the accrual
        result = service.run_daily_accrual()

        # Convert Decimal to string for session storage
        serializable_result = make_serializable(result)

        # Store results in session
        request.session['interest_result'] = {
            'accrued': serializable_result['accrued'][:100],
            'applied': serializable_result['applied'],
            'failed': serializable_result['failed'],
            'total_accrued': serializable_result['total_accrued'],
            'total_applied': serializable_result['total_applied'],
            'days_since_last': serializable_result['days_since_last'],
            'application_frequency': serializable_result['application_frequency'],
            'should_apply': serializable_result['should_apply'],
            'accrued_count': len(result['accrued']),
            'applied_count': len(result['applied']),
            'failed_count': len(result['failed']),
        }

        messages.success(
            request, f"Interest accrual completed. Total accrued: ₵{result['total_accrued']:.2f}")
        return redirect('services:sav_interest_accrual_results')

    # GET request – show confirmation page
    context = {
        'today': service.today,
        'last_run': service.settings.last_interest_accrual_run if service.settings else None,
        'calc_type': service.savings_calc_type,
        'frequency': service.application_frequency,
    }
    return render(request, 'services/sav_run_interest_accrual.html', context)


@staff_member_required
def sav_interest_accrual_results(request):
    result = request.session.get('interest_result')
    if not result:
        return redirect('Supervisor:run_interest_accrual')

    # Paginate the accrued list if needed
    paginator = Paginator(result['accrued'], 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'result': result,
        'accrued_page': page_obj,
    }
    return render(request, 'services/sav_interest_accrual_results.html', context)


from services.transaction_posting_service import process_transaction


def post_selected_transaction(request, slug):
    trans = get_object_or_404(Trans, id=...)
    result = process_transaction(trans, request.user, slug)
    if result["success"]:
        messages.success(request, "Transaction posted successfully.")
    else:
        messages.error(request, f"Error: {result['errors']}")
    return redirect(...)


# services/views.py
import json
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .interest_accrual_service import InterestAccrualService


# services/views.py
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods
from .interest_accrual_service import InterestAccrualService


@staff_member_required
@require_http_methods(["GET", "POST"])
def run_interest_accrual(request, entity_slug):
    try:
        force_apply = request.GET.get("force_apply", "false").lower() == "true"
        service = InterestAccrualService(entity_slug)
        results = service.run_daily_accrual(force_apply=force_apply)
        return JsonResponse(
            {
                "success": True,
                "force_apply": force_apply,
                "results": results,
            },
            json_dumps_params={"default": str},
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


# services/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django_ledger.models import EntityModel
from djan_led.models import EntityConfig
from .forms import EntityConfigForm

@login_required
@staff_member_required
def edit_entity_config(request, entity_slug):
    entity = get_object_or_404(EntityModel, slug=entity_slug)
    config, created = EntityConfig.objects.get_or_create(entity=entity)

    if request.method == "POST":
        form = EntityConfigForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(
                request, f"Configuration for {entity.name} updated successfully."
            )
            return redirect("services:edit_entity_config", entity_slug=entity_slug)
    else:
        form = EntityConfigForm(instance=config)

    context = {
        "form": form,
        "entity": entity,
        "config": config,
    }
    return render(request, "services/entity_config_form.html", context)


@staff_member_required
def run_daily_loan_interest(request, entity_slug):
    force = request.GET.get("force", "false").lower() == "true"
    service = DailyLoanService(entity_slug)
    results = service.run_daily_loan_interest(force=force)
    return JsonResponse(
        {"success": True, "results": results}, json_dumps_params={"default": str}
    )

# services/daily_loan_service.py
import logging
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.shortcuts import get_object_or_404
from MembersApp.models import Master
from LoanApp.models import Loan, LoanInterestAudit
from djan_led.models import EntityConfig
from django_ledger.models import EntityModel
from .journal_engine import JournalEngine

logger = logging.getLogger(__name__)


class DailyLoanService:
    def __init__(self, entity_slug, engine=None):
        self.entity = get_object_or_404(EntityModel, slug=entity_slug)
        self.config, _ = EntityConfig.objects.get_or_create(entity=self.entity)
        self.today = timezone.now().date()

        if engine is not None:
            self.engine = engine
        else:
            self.engine = JournalEngine(entity_slug)

    def get_loan_interest_rate(self, loan):
        """Return member-specific rate or fallback to entity config."""
        if (
            loan.master
            and loan.master.loan_interest_rate
            and loan.master.loan_interest_rate > 0
        ):
            return Decimal(loan.master.loan_interest_rate)
        return Decimal(self.config.loan_interest_rate or 0)

    def get_monthly_rate(self, annual_rate):
        """Convert annual rate (as percentage) to monthly decimal."""
        return (annual_rate / Decimal("100")) / Decimal("12")

    def get_loan_class(self, loan):
        """Determine loan classification based on days past expiry."""
        if not loan.expiry_date:
            return "Current"
        days_past = (self.today - loan.expiry_date).days
        if days_past <= 0:
            return "Current"
        elif days_past <= 30:
            return "Current"
        elif days_past <= 60:
            return "Olem"
        elif days_past <= 180:
            return "Substandard"
        elif days_past <= 365:
            return "Doubtful"
        else:
            return "Loss"

    def should_accrue_interest(self, loan):
        """Check if today is on or after the next repayment date."""
        if not loan.next_repayment_date:
            return False
        return self.today >= loan.next_repayment_date
    
    def apply_interest_accrual(self, loan):
        """Accrue monthly interest, update loan, and log audit."""
        annual_rate = self.get_loan_interest_rate(loan)
        if annual_rate <= 0:
            logger.warning(f"Loan {loan.id}: interest rate is zero, skipping.")
            return

        monthly_rate = self.get_monthly_rate(annual_rate)
        balance_before = loan.loan_balance

        # Accrue interest
        interest = (balance_before * monthly_rate).quantize(Decimal("0.01"))
        balance_after = balance_before + interest

        # Update loan
        loan.loan_balance = balance_after
        loan.due_interest = (loan.due_interest or 0) + interest

        # Update next repayment date (add 1 month)
        if loan.next_repayment_date:
            loan.next_repayment_date += relativedelta(months=1)
        else:
            # If no next date, set to today + 1 month (shouldn't happen)
            loan.next_repayment_date = self.today + relativedelta(months=1)

        # Update status based on balance
        if loan.loan_balance == 0:
            loan.status = "Completed"
        elif loan.loan_balance < 0:
            loan.status = "Credit"
            loan.loan_credit_balance = abs(loan.loan_balance)
            loan.loan_balance = 0
        else:
            loan.status = "Active"

        # Update loan class based on expiry
        loan.classification = self.get_loan_class(loan)

        loan.save()

        # Create audit record
        LoanInterestAudit.objects.create(
            date=self.today,
            master=loan.master,
            loan=loan,
            next_repayment_date=loan.next_repayment_date,
            balance_before=balance_before,
            interest_rate=annual_rate,
            months=1,
            interest_accrued=interest,
            balance_after=loan.loan_balance,
            expiry_date=loan.expiry_date,
            loan_class=loan.classification,
        )

        # Create journal entry
        self.create_interest_journal(loan, interest)

        logger.info(
            f"Loan {loan.id}: interest {interest} accrued, new balance {loan.loan_balance}"
        )

    @login_required
    def create_interest_journal(self, loan, interest):
        """Create journal entry for interest accrual (debit loan receivable, credit interest income)."""
        if interest <= 0:
            return
        try:
            # Get account codes from config or defaults
            loan_asset_code = getattr(self.config, "loan_asset_account_code", "1080")
            interest_income_code = getattr(
                self.config, "loan_interest_income_code", "4010"
            )

            description = (
                f"Loan interest accrual - {loan.master.full_name} - Loan {loan.id}"
            )

            # Journal: Debit Loan Asset, Credit Interest Income
            self.engine.record_transaction(
                amount=interest,
                debit_account_code=loan_asset_code,
                credit_account_code=interest_income_code,
                description=description,
                date=self.today,
            )
            logger.info(f"Journal created for loan interest: {interest}")
        except Exception as e:
            logger.error(f"Journal creation failed: {e}")

    @login_required
    def run_daily_loan_interest(self, force=False):
        """
        Run daily loan interest accrual.
        If force=True, process all active loans regardless of next_repayment_date.
        """
        print("=" * 60)
        print("DAILY LOAN INTEREST ACCRUAL")
        print(f"Date: {self.today}")
        print("=" * 60)

        results = {
            "processed": [],
            "skipped": [],
            "errors": [],
            "total_interest": Decimal("0.00"),
        }

        # Get all loans that are not fully repaid (status not Completed/Credit)
        loans = Loan.objects.exclude(status__in=["Completed", "Credit"])

        if force:
            loans = Loan.objects.filter(status__in=["Active", "New Loan"])

        with transaction.atomic():
            for loan in loans.select_for_update():
                try:
                    if not force and not self.should_accrue_interest(loan):
                        print(
                            f"Loan {loan.id}: next date {loan.next_repayment_date} not reached, skipping."
                        )
                        results["skipped"].append(loan.id)
                        continue

                    # Check if loan has balance > 0 (if balance <=0, it should have been completed)
                    if loan.loan_balance <= 0:
                        loan.status = "Completed"
                        loan.save()
                        print(f"Loan {loan.id}: balance <=0, marked Completed.")
                        results["skipped"].append(loan.id)
                        continue

                    self.apply_interest_accrual(loan)
                    results["processed"].append(
                        {
                            "loan_id": loan.id,
                            "member": loan.master.full_name,
                            "interest": loan.due_interest,
                            "new_balance": loan.loan_balance,
                        }
                    )
                    results["total_interest"] += loan.due_interest

                except Exception as e:
                    print(f"Error on loan {loan.id}: {e}")
                    import traceback

                    traceback.print_exc()
                    results["errors"].append({"loan_id": loan.id, "error": str(e)})

        print(f"Processed: {len(results['processed'])}")
        print(f"Skipped: {len(results['skipped'])}")
        print(f"Errors: {len(results['errors'])}")
        print(f"Total interest accrued: {results['total_interest']}")
        return results
