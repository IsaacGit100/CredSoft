# LoanApp/services/loan_processing_service.py
from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from LoanApp.models import Loan
from MembersApp.models import Master
from SysSetup.models import SystemSettings
from FinanceApp.models import JournalEntry, JournalLine
from coa.models import ChartOfAccounts

class LoanProcessingService:
    """Service to handle daily loan processing, interest calculation, and penalties"""
    
    def __init__(self):
        self.settings = SystemSettings.objects.first()
        self.today = timezone.now().date()
        self.penalty_rate = self.settings.late_payment_penalty if self.settings else Decimal('5.00')
    
    def calculate_next_due_date(self, disbursement_date, current_due_date=None):
        """
        Calculate next payment due date
        Due date is same day next month (or 30 days for February)
        """
        if current_due_date:
            # Calculate next due date from current due date
            next_date = current_due_date + relativedelta(months=1)
            
            # Handle February special case (use 30 days from previous due date)
            if next_date.month == 2 and next_date.day > 28:
                # Use 30 days from previous due date
                next_date = current_due_date + timedelta(days=30)
            
            return next_date
        else:
            # First due date: next month same day
            next_date = disbursement_date + relativedelta(months=1)
            
            # Handle February
            if next_date.month == 2 and next_date.day > 28:
                next_date = disbursement_date + timedelta(days=30)
            
            return next_date
    
    def calculate_monthly_interest(self, loan):
        """Calculate monthly interest on current balance"""
        rate = loan.effective_interest_rate
        balance = loan.loan_balance
        
        if rate <= 0 or balance <= 0:
            return Decimal('0.00')
        
        # Monthly interest = (Balance * Annual Rate%) / 12 / 100
        monthly_interest = (balance * rate / Decimal('100')) / Decimal('12')
        return monthly_interest.quantize(Decimal('0.01'))
    
    def calculate_penalty(self, overdue_amount, days_overdue):
        """Calculate penalty on overdue amount"""
        if overdue_amount <= 0 or days_overdue <= 0 or self.penalty_rate <= 0:
            return Decimal('0.00')
        
        # Penalty = Overdue Amount × Penalty Rate% × Days / 365
        penalty = (overdue_amount * self.penalty_rate / Decimal('100')) * Decimal(str(days_overdue)) / Decimal('365')
        return penalty.quantize(Decimal('0.01'))
    
    def process_due_loans(self):
        """Process all loans that are due today"""
        results = {
            'processed': [],
            'errors': [],
            'total_interest': Decimal('0.00'),
            'total_penalty': Decimal('0.00')
        }
        
        # Find loans that are due today (Active or Owing status)
        due_loans = Loan.objects.filter(
            next_payment_due_date=self.today,
            status__in=['Active', 'Owing']
        )
        
        with transaction.atomic():
            for loan in due_loans:
                try:
                    # Calculate monthly interest
                    interest = self.calculate_monthly_interest(loan)
                    
                    if interest > 0:
                        # Check if loan is already overdue
                        if loan.is_overdue:
                            # Add to overdue interest
                            loan.interest_overdue = (loan.interest_overdue or 0) + interest
                            loan.status = 'Owing'
                        else:
                            # This is the regular monthly interest
                            # For now, add to loan balance or track separately
                            # Based on your business logic
                            loan.loan_balance += interest
                        
                        results['total_interest'] += interest
                    
                    # Update next due date
                    loan.next_payment_due_date = self.calculate_next_due_date(
                        loan.disbursement_date, 
                        loan.next_payment_due_date
                    )
                    
                    # Update last calculation date
                    loan.last_interest_calculation_date = self.today
                    loan.save()
                    
                    results['processed'].append({
                        'loan_id': loan.id,
                        'loan_number': loan.loan_number,
                        'member': loan.master.full_name,
                        'interest': float(interest),
                        'next_due_date': loan.next_payment_due_date,
                        'status': loan.status
                    })
                    
                except Exception as e:
                    results['errors'].append({
                        'loan_id': loan.id,
                        'error': str(e)
                    })
        
        return results
    
    def process_overdue_loans(self):
        """Process all overdue loans and calculate penalties"""
        results = {
            'processed': [],
            'errors': [],
            'total_penalty': Decimal('0.00')
        }
        
        # Find all overdue loans
        overdue_loans = Loan.objects.filter(
            next_payment_due_date__lt=self.today,
            status__in=['Active', 'Owing']
        ).exclude(repayment_overdue=0, interest_overdue=0)
        
        with transaction.atomic():
            for loan in overdue_loans:
                try:
                    days = loan.days_overdue
                    total_overdue = loan.total_overdue
                    
                    if total_overdue > 0 and days > 0:
                        # Calculate penalty
                        penalty = self.calculate_penalty(total_overdue, days)
                        
                        if penalty > 0:
                            loan.penalty_accrued = (loan.penalty_accrued or 0) + penalty
                            results['total_penalty'] += penalty
                            
                            # Update status
                            loan.status = 'Owing'
                            loan.last_penalty_calculation_date = self.today
                            loan.save()
                            
                            results['processed'].append({
                                'loan_id': loan.id,
                                'loan_number': loan.loan_number,
                                'member': loan.master.full_name,
                                'overdue_amount': float(total_overdue),
                                'days_overdue': days,
                                'penalty': float(penalty),
                                'total_penalty_accrued': float(loan.penalty_accrued)
                            })
                    
                except Exception as e:
                    results['errors'].append({
                        'loan_id': loan.id,
                        'error': str(e)
                    })
        
        return results
    
    def post_interest_journal(self, loan, interest_amount, is_overdue=False):
        """Create journal entry for interest accrual"""
        if interest_amount <= 0:
            return None
        
        try:
            # Get accounts
            loan_account = ChartOfAccounts.objects.get(accountno='10103001')  # Loans Receivable
            interest_income_account = ChartOfAccounts.objects.get(accountno='40101002')  # Loan Interest Income
            
            from datetime import datetime
            date_str = datetime.now().strftime('%Y%m%d')
            from FinanceApp.models import JournalEntry
            last = JournalEntry.objects.filter(
                entry_number__startswith=f'LOAN-INT-{date_str}'
            ).count()
            journal_number = f'LOAN-INT-{date_str}-{last + 1:04d}'
            
            description = f"Loan interest for {loan.master.full_name} - Loan #{loan.loan_number}"
            if is_overdue:
                description += " (Overdue)"
            
            journal = JournalEntry.objects.create(
                entry_number=journal_number,
                entry_date=self.today,
                description=description,
                status='POSTED',
                posted=True,
                posted_at=timezone.now()
            )
            
            # Debit: Loans Receivable (or Interest Receivable)
            JournalLine.objects.create(
                journal=journal,
                account=loan_account,
                member=loan.master,
                debit=interest_amount,
                credit=0,
                line_description=f"Interest accrued on loan #{loan.loan_number}"
            )
            
            # Credit: Interest Income
            JournalLine.objects.create(
                journal=journal,
                account=interest_income_account,
                member=loan.master,
                debit=0,
                credit=interest_amount,
                line_description=f"Interest income from loan #{loan.loan_number}"
            )
            
            return journal
            
        except Exception as e:
            print(f"Error creating journal: {e}")
            return None
    
    def post_penalty_journal(self, loan, penalty_amount):
        """Create journal entry for penalty accrual"""
        if penalty_amount <= 0:
            return None
        
        try:
            penalty_income_account = ChartOfAccounts.objects.get(accountno='40101003')  # Penalty Income
            
            from datetime import datetime
            date_str = datetime.now().strftime('%Y%m%d')
            from FinanceApp.models import JournalEntry
            last = JournalEntry.objects.filter(
                entry_number__startswith=f'PEN-{date_str}'
            ).count()
            journal_number = f'PEN-{date_str}-{last + 1:04d}'
            
            journal = JournalEntry.objects.create(
                entry_number=journal_number,
                entry_date=self.today,
                description=f"Late payment penalty for {loan.master.full_name} - Loan #{loan.loan_number}",
                status='POSTED',
                posted=True,
                posted_at=timezone.now()
            )
            
            # Debit: Loans Receivable (Penalty Receivable)
            loan_account = ChartOfAccounts.objects.get(accountno='10103001')
            JournalLine.objects.create(
                journal=journal,
                account=loan_account,
                member=loan.master,
                debit=penalty_amount,
                credit=0,
                line_description=f"Penalty on overdue loan #{loan.loan_number}"
            )
            
            # Credit: Penalty Income
            JournalLine.objects.create(
                journal=journal,
                account=penalty_income_account,
                member=loan.master,
                debit=0,
                credit=penalty_amount,
                line_description=f"Penalty income from loan #{loan.loan_number}"
            )
            
            return journal
            
        except Exception as e:
            print(f"Error creating penalty journal: {e}")
            return None
    
    def run_daily_processing(self):
        """Complete daily loan processing - interest and penalties"""
        
        # Step 1: Process loans that are due today (add monthly interest)
        interest_results = self.process_due_loans()
        
        # Step 2: Process overdue loans (calculate penalties)
        penalty_results = self.process_overdue_loans()
        
        return {
            'interest': interest_results,
            'penalty': penalty_results,
            'processing_date': self.today
        }