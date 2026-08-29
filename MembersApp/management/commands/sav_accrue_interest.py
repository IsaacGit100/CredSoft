# MembersApp/management/commands/accrue_interest.py
from django.core.management.base import BaseCommand
from MembersApp.services.sav_int_service import InterestAccrualService
from datetime import datetime

class Command(BaseCommand):
    help = 'Accrue daily interest for all members'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Calculate without posting to database',
        )
    
    def handle(self, *args, **options):
        self.stdout.write("=" * 70)
        self.stdout.write("DAILY INTEREST ACCRUAL & APPLICATION")
        self.stdout.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.stdout.write("=" * 70)
        
        service = InterestAccrualService()
        
        if options['dry_run']:
            self.stdout.write("\n⚠️  DRY RUN MODE - No changes will be saved\n")
        
        results = service.run_daily_accrual()
        
        # Display results
        self.stdout.write(f"\n📊 SUMMARY")
        self.stdout.write("-" * 40)
        self.stdout.write(f"Application Frequency: {results['application_frequency']}")
        self.stdout.write(f"Days since last accrual: {results['days_since_last']}")
        self.stdout.write(f"Should apply today: {'Yes' if results['should_apply'] else 'No'}")
        self.stdout.write(f"Members processed: {len(results['accrued'])}")
        self.stdout.write(f"Total interest accrued: ₵{results['total_accrued']:,.2f}")
        
        if results['should_apply']:
            self.stdout.write(f"\n💰 INTEREST APPLIED TODAY")
            self.stdout.write("-" * 40)
            self.stdout.write(f"Total interest applied to deposits: ₵{results['total_applied']:,.2f}")
            self.stdout.write(f"Members who received interest: {len(results['applied'])}")
            
            # Show next application date
            next_date = service.get_next_application_date()
            self.stdout.write(f"Next application date: {next_date.strftime('%Y-%m-%d')}")
        
        if results['failed']:
            self.stdout.write(f"\n❌ FAILED ({len(results['failed'])})")
            self.stdout.write("-" * 40)
            for item in results['failed'][:10]:
                self.stdout.write(f"  {item['member_name']}: {item['error']}")
        
        # Show sample of accrued interest
        self.stdout.write(f"\n📈 SAMPLE OF ACCRUED INTEREST")
        self.stdout.write("-" * 40)
        for item in results['accrued'][:10]:
            if item['interest'] > 0:
                self.stdout.write(f"  {item['member_name']}: ₵{item['interest']:,.2f} ({item['days']} days)")
        
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write(self.style.SUCCESS("✅ DAILY INTEREST ACCRUAL COMPLETE"))
        self.stdout.write("=" * 70)