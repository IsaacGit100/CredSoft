"""
Run monthly interest accrual for all active loans of an entity.

Usage:
    python manage.py run_loan_accrual --slug <entity-slug>            # dry run
    python manage.py run_loan_accrual --slug <entity-slug> --apply    # write
"""

from django.core.management.base import BaseCommand
from django.utils import timezone

from django_ledger.models import EntityModel
from LoanApp.models import Loan, LoanInterestAudit
from LoanApp.services.loan_accrual import add_one_month


class Command(BaseCommand):
    help = "Run monthly interest accrual for all active loans."

    def add_arguments(self, parser):
        parser.add_argument("--slug", required=True)
        parser.add_argument("--apply", action="store_true")
        parser.add_argument(
            "--date", required=False, help="Override today's date (YYYY-MM-DD)"
        )

    def handle(self, *args, **options):
        entity = EntityModel.objects.get(slug=options["slug"])
        apply = options["apply"]

        today = timezone.now().date()
        if options.get("date"):
            from datetime import datetime

            today = datetime.strptime(options["date"], "%Y-%m-%d").date()

        self.stdout.write(f"Entity: {entity.name}")
        self.stdout.write(f"Today:  {today}")

        loans = Loan.objects.filter(
            entity=entity,
            status__in=["Active", "Owing", "New Loan"],
        ).order_by("id")

        self.stdout.write(f"Active loans: {loans.count()}")

        previews = []
        for loan in loans:
            if not loan.next_repayment_date:
                continue
            if loan.next_repayment_date > today:
                continue
            if LoanInterestAudit.objects.filter(
                loan=loan, next_repayment_date=loan.next_repayment_date
            ).exists():
                continue

            rate = loan.effective_interest_rate
            interest = (loan.balance * rate / 100).quantize(
                __import__("decimal").Decimal("0.01")
            )
            previews.append((loan, rate, interest))
            self.stdout.write(
                f"  {loan.loan_no} | {loan.member.full_name[:25]:<25} | "
                f"bal ₵{loan.balance:>10,.2f} x  {rate}% = ₵{interest:>10,.2f} | "
                f"due {loan.next_repayment_date} → {add_one_month(loan.next_repayment_date)}"
            )

        self.stdout.write(f"\nWould accrue on {len(previews)} loan(s).")

        if not apply:
            self.stdout.write(
                self.style.WARNING("\nDry run. Re-run with --apply to write.")
            )
            return

        from LoanApp.services.loan_accrual import accrue_interest_for_entity

        results = accrue_interest_for_entity(entity, today)
        self.stdout.write(self.style.SUCCESS(f"\nAccrued on {len(results)} loan(s)."))
