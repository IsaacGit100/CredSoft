# CoreApp/services/batch_service.py
from django.utils import timezone
from django.core.management import call_command
from io import StringIO
from datetime import timedelta
from decimal import Decimal
from ..models import BatchProcess, BatchProcessLog

class BatchProcessingService:
    """Service to handle all batch processes"""
    
    def __init__(self, user=None):
        self.user = user
        self.results = {}
    
    def get_or_create_process(self, process_type, process_name, frequency='DAILY'):
        """Get or create a batch process record"""
        process, created = BatchProcess.objects.get_or_create(
            process_type=process_type,
            defaults={
                'process_name': process_name,
                'frequency': frequency,
                'next_run_due': timezone.now()
            }
        )
        return process
    
    def update_next_run_date(self, process):
        """Calculate next run date based on frequency"""
        now = timezone.now()
        
        if process.frequency == 'DAILY':
            process.next_run_due = now + timedelta(days=1)
        elif process.frequency == 'WEEKLY':
            process.next_run_due = now + timedelta(days=7)
        elif process.frequency == 'MONTHLY':
            # Next month same day
            if now.month == 12:
                process.next_run_due = now.replace(year=now.year+1, month=1, day=1)
            else:
                process.next_run_due = now.replace(month=now.month+1, day=1)
        elif process.frequency == 'QUARTERLY':
            process.next_run_due = now + timedelta(days=90)
        elif process.frequency == 'YEARLY':
            process.next_run_due = now + timedelta(days=365)
        
        process.save()
        return process.next_run_due
    
    def run_savings_interest(self, process, log):
        """Run savings interest accrual"""
        try:
            out = StringIO()
            call_command('accrue_interest', stdout=out)
            output = out.getvalue()
            
            log.message = output[:500]  # Store first 500 chars
            log.records_processed = self._parse_interest_count(output)
            return True
        except Exception as e:
            log.error_details = str(e)
            return False
    
    def run_loan_interest(self, process, log):
        """Run loan interest calculation"""
        try:
            out = StringIO()
            call_command('process_loans', stdout=out)
            output = out.getvalue()
            
            log.message = output[:500]
            return True
        except Exception as e:
            log.error_details = str(e)
            return False
    
    def _parse_interest_count(self, output):
        """Parse number of members processed from output"""
        import re
        match = re.search(r'Members processed: (\d+)', output)
        return int(match.group(1)) if match else 0
    
    def run_process(self, process_type):
        """Run a specific batch process"""
        process = BatchProcess.objects.get(process_type=process_type)
        
        # Create log entry
        log = BatchProcessLog.objects.create(
            process=process,
            status='RUNNING',
            run_by=self.user
        )
        
        process.last_run = timezone.now()
        process.last_run_by = self.user
        process.last_run_status = 'RUNNING'
        process.total_runs += 1
        process.save()
        
        # Run the actual process
        success = False
        if process_type == 'SAVINGS_INTEREST':
            success = self.run_savings_interest(process, log)
        elif process_type == 'LOAN_INTEREST':
            success = self.run_loan_interest(process, log)
        elif process_type == 'LOAN_PENALTY':
            success = self.run_loan_interest(process, log)  # Combined in same command
        
        # Update log
        log.completed_at = timezone.now()
        if success:
            log.status = 'COMPLETED'
            process.last_run_status = 'COMPLETED'
            process.successful_runs += 1
        else:
            log.status = 'FAILED'
            process.last_run_status = 'FAILED'
            process.failed_runs += 1
        
        log.save()
        
        # Update process
        process.last_run_message = log.message[:200] if log.message else ''
        process.save()
        
        # Update next run date
        self.update_next_run_date(process)
        
        return {'success': success, 'log': log}
    
    def get_all_processes_status(self):
        """Get status of all batch processes"""
        processes = BatchProcess.objects.all()
        return [
            {
                'id': p.id,
                'name': p.process_name,
                'type': p.process_type,
                'last_run': p.last_run,
                'last_run_by': p.last_run_by.username if p.last_run_by else None,
                'last_run_status': p.last_run_status,
                'next_run_due': p.next_run_due,
                'is_due': p.is_due,
                'days_since_last': p.days_since_last_run,
                'total_runs': p.total_runs,
                'successful_runs': p.successful_runs,
                'failed_runs': p.failed_runs,
            }
            for p in processes
        ]