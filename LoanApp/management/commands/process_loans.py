# LoanApp/management/commands/process_loans.py
from django.core.management.base import BaseCommand
from LoanApp.services.loan_processing_service import LoanProcessingService
from datetime import datetime

class Command(BaseCommand):
    help = 'Process daily loan interest and penalties'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Calculate without posting to database',
        )
    
    def handle(self, *args, **options):
        self.stdout.write("=" * 70)
        self.stdout.write("DAILY LOAN PROCESSING")
        self.stdout.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.stdout.write("=" * 70)
        
        service = LoanProcessingService()
        
        if options['dry_run']:
            self.stdout.write("\n⚠️  DRY RUN MODE - No changes will be saved\n")
        
        results = service.run_daily_processing()
        
        # Display Interest Results
        self.stdout.write("\n📈 INTEREST PROCESSING")
        self.stdout.write("-" * 40)
        self.stdout.write(f"Loans processed: {len(results['interest']['processed'])}")
        self.stdout.write(f"Total interest accrued: ₵{results['interest']['total_interest']:,.2f}")
        
        if results['interest']['processed']:
            self.stdout.write("\nProcessed Loans:")
            for item in results['interest']['processed'][:10]:
                self.stdout.write(f"  {item['member']} (Loan #{item['loan_number']}): ₵{item['interest']:,.2f}")
        
        # Display Penalty Results
        self.stdout.write("\n💰 PENALTY PROCESSING")
        self.stdout.write("-" * 40)
        self.stdout.write(f"Overdue loans processed: {len(results['penalty']['processed'])}")
        self.stdout.write(f"Total penalties accrued: ₵{results['penalty']['total_penalty']:,.2f}")
        
        if results['penalty']['processed']:
            self.stdout.write("\nPenalty Details:")
            for item in results['penalty']['processed'][:10]:
                self.stdout.write(f"  {item['member']} (Loan #{item['loan_number']}): "
                                 f"₵{item['penalty']:,.2f} ({item['days_overdue']} days overdue)")
        
        if results['interest']['errors'] or results['penalty']['errors']:
            self.stdout.write("\n❌ ERRORS")
            self.stdout.write("-" * 40)
            for err in results['interest']['errors']:
                self.stdout.write(f"  {err['error']}")
            for err in results['penalty']['errors']:
                self.stdout.write(f"  {err['error']}")
        
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write(self.style.SUCCESS("✅ DAILY LOAN PROCESSING COMPLETE"))
        self.stdout.write("=" * 70)