# loans/services/loan_repayment_service.py
from decimal import Decimal
from django.db import transaction as db_transaction
from django.utils import timezone
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from ..models import Loan, Guarantor, LoanRepayment, LoanSchedule

class LoanRepaymentService:
    """
    Handles loan repayment processing with guarantor redemption
    Following the structured programming pattern
    """
    
    def __init__(self, loan, amount, payment_date, user):
        self.loan = loan
        self.amount = Decimal(str(amount))
        self.payment_date = payment_date
        self.user = user
        self.results = {
            'success': False,
            'principal_paid': Decimal('0'),
            'interest_paid': Decimal('0'),
            'balance_remaining': Decimal('0'),
            'guarantors_released': [],
            'errors': []
        }
    
    def process(self):
        """Main processing routine - like PERFORM MAIN-PROCESS"""
        try:
            with db_transaction.atomic():
                # Step 1: Calculate interest and principal portions
                self.calculate_interest_and_principal()
                
                # Step 2: Update loan totals
                self.update_loan_totals()
                
                # Step 3: Create repayment record
                self.create_repayment_record()
                
                # Step 4: Update loan balance
                self.update_loan_balance()
                
                # Step 5: Generate next month's interest
                self.generate_next_month_interest()
                
                # Step 6: Process guarantor redemption
                self.process_guarantor_redeem()
                
                self.results['success'] = True
                return self.results
                
        except Exception as e:
            self.results['errors'].append(str(e))
            return self.results
    
    def calculate_interest_and_principal(self):
        """Calculate monthly interest and principal portions"""
        # Monthly interest rate (annual rate / 12 / 100)
        monthly_rate = (self.loan.interest_rate / 100) / 12
        
        # Calculate interest for this month
        self.month_interest = self.loan.balance * monthly_rate
        
        # Principal portion = total payment - interest
        self.principal_paid = self.amount - self.month_interest
        
        # Ensure we don't overpay
        if self.principal_paid > self.loan.balance:
            self.principal_paid = self.loan.balance
            self.amount = self.month_interest + self.principal_paid
        
        self.results['interest_paid'] = self.month_interest
        self.results['principal_paid'] = self.principal_paid
        
    def update_loan_totals(self):
        """Update loan totals - interest and repayment"""
        # 2. Loan: tot_interest = tot_interest + month_interest
        self.loan.total_interest_paid = (self.loan.total_interest_paid or 0) + self.month_interest
        
        # 3. Loan total_repayment = total_repayment + amount
        self.loan.total_repaid = (self.loan.total_repaid or 0) + self.amount
        
        self.loan.save()
    
    def create_repayment_record(self):
        """Create repayment history record"""
        repayment = LoanRepayment.objects.create(
            loan=self.loan,
            amount=self.amount,
            principal_paid=self.principal_paid,
            interest_paid=self.month_interest,
            payment_date=self.payment_date,
            balance_after=self.loan.balance - self.principal_paid,
            created_by=self.user
        )
        self.repayment = repayment
    
    def update_loan_balance(self):
        """4. Loan balance = Loan balance - principal_paid"""
        self.loan.balance -= self.principal_paid
        self.loan.last_payment_date = self.payment_date
        self.loan.save()
        
        # Check if loan is fully paid
        if self.loan.balance <= 0:
            self.loan.status = 'PAID'
            self.loan.closed_date = self.payment_date
            self.loan.save()
        
        self.results['balance_remaining'] = self.loan.balance
    
    def generate_next_month_interest(self):
        """5. New month_int is generated for the following month"""
        # Calculate next payment due date (1 month from last payment)
        if self.loan.next_payment_due:
            next_due = self.loan.next_payment_due
        else:
            next_due = self.payment_date
        
        self.loan.next_payment_due = next_due + relativedelta(months=1)
        
        # Calculate next month's interest (for display/preview)
        monthly_rate = (self.loan.interest_rate / 100) / 12
        self.next_month_interest = self.loan.balance * monthly_rate
        self.loan.next_month_interest_projected = self.next_month_interest
        
        self.loan.save()
    
    def process_guarantor_redeem(self):
        """
        Process guarantor redemption in sequence
        Like PERFORM UNTIL NO-MORE-GUARANTORS
        """
        remaining_payment = self.principal_paid
        
        # Get active guarantors ordered by guarantee date (oldest first)
        guarantors = self.loan.guarantors.filter(
            redeemed_amount__lt=models.F('guaranteed_amount')
        ).order_by('guaranteed_date', 'id')
        
        for guarantor in guarantors:
            if remaining_payment <= 0:
                break
            
            # Calculate available amount from this guarantor
            available = guarantor.guaranteed_amount - (guarantor.redeemed_amount or 0)
            
            if available <= 0:
                continue
            
            # How much to redeem from this guarantor
            redeem_amount = min(available, remaining_payment)
            
            # Update guarantor
            guarantor.redeemed_amount = (guarantor.redeemed_amount or 0) + redeem_amount
            remaining_payment -= redeem_amount
            
            # Check if fully redeemed
            if guarantor.redeemed_amount >= guarantor.guaranteed_amount:
                guarantor.redeemed_status = 'FULLY_REDEEMED'
            else:
                guarantor.redeemed_status = 'PARTIALLY_REDEEMED'
            
            guarantor.save()
            
            # Record this redemption
            self.results['guarantors_released'].append({
                'name': guarantor.master.name,
                'amount': float(redeem_amount),
                'remaining': float(guarantor.guaranteed_amount - guarantor.redeemed_amount)
            })
        
        # If still remaining payment after all guarantors, mark as shortfall
        if remaining_payment > 0:
            self.results['shortfall'] = float(remaining_payment)