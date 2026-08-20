# CoreApp/management/commands/init_batch_processes.py
from django.core.management.base import BaseCommand
from CoreApp.models import BatchProcess
from CoreApp.services.batch_service import BatchProcessingService

class Command(BaseCommand):
    help = 'Initialize batch processes in the database'
    
    def handle(self, *args, **options):
        self.stdout.write("=" * 50)
        self.stdout.write("Initializing Batch Processes")
        self.stdout.write("=" * 50)
        
        # Define all batch processes
        processes = [
            ('SAVINGS_INTEREST', 'Savings Interest Accrual', 'DAILY'),
            ('LOAN_INTEREST', 'Loan Interest Calculation', 'DAILY'),
            ('LOAN_PENALTY', 'Loan Penalty Calculation', 'DAILY'),
            ('DAILY_REPORT', 'Daily Report Generation', 'DAILY'),
            ('BACKUP', 'Database Backup', 'DAILY'),
            ('MONTHLY_REPORT', 'Monthly Report Generation', 'MONTHLY'),
            ('QUARTERLY_REPORT', 'Quarterly Report Generation', 'QUARTERLY'),
            ('YEAR_END', 'Year End Closing', 'YEARLY'),
        ]
        
        service = BatchProcessingService()
        created_count = 0
        existing_count = 0
        
        for process_type, name, frequency in processes:
            process, created = BatchProcess.objects.get_or_create(
                process_type=process_type,
                defaults={
                    'process_name': name,
                    'frequency': frequency,
                    'next_run_due': timezone.now()
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"✓ Created: {name}"))
            else:
                existing_count += 1
                self.stdout.write(f"○ Already exists: {name}")
        
        self.stdout.write("=" * 50)
        self.stdout.write(self.style.SUCCESS(f"Initialization complete!"))
        self.stdout.write(f"Created: {created_count} | Existing: {existing_count}")
        self.stdout.write("=" * 50)