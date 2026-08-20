from django.core.management.base import BaseCommand
from services.daily_loan_service import DailyLoanService


class Command(BaseCommand):
    help = "Accrue monthly interest on loans"

    def add_arguments(self, parser):
        parser.add_argument("--entity", required=True, help="Entity slug")
        parser.add_argument(
            "--force",
            action="store_true",
            help="Accrue for all active loans regardless of next date",
        )

    def handle(self, *args, **options):
        service = DailyLoanService(options["entity"])
        results = service.run_daily_loan_interest(force=options["force"])
        self.stdout.write(f"Processed: {len(results['processed'])}")
        self.stdout.write(f"Errors: {len(results['errors'])}")
        self.stdout.write(self.style.SUCCESS("Done."))
