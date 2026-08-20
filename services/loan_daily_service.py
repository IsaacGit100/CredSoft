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
