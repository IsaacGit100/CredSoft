from django.utils import timezone

from MembersApp.models import Master

# Create your models here.
from django.db import models

# Create your models here.
# models.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum
from decimal import Decimal


from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from django.utils import timezone
from django.db.models.fields import DateField
from django.db.models import Sum
from UserAuth.models import User
from django_ledger.models import EntityModel

# Create your models here.
class Loan(models.Model):
    STATUS_CHOICES = [
        ('New Loan', 'New Loan'),
        ('Active', 'Active'),
        ('Owing', 'Owing'),
        ('Completed', 'Completed'),
        ('Expired', 'Expired'),
        ('Credit', 'Credit'),
    ]

    LOAN_CLASS = [
        ('Current', 'Current'),
        ('OLEM', 'OLEM'),
        ('Substandard', 'Substandard'),
        ('Doubtfull', 'Doubtfull'),
        ('Loss', 'Loss'),
    ]

    TRANSACTION_TYPES = [
        ('DISBURSEMENT', 'Loan Disbursement'),
        ('REPAYMENT', 'Loan Repayment'),
        ('INTEREST', 'Interest Accrual'),
        ('PENALTY', 'Penalty'),
    ]

    # Borrower information
    entity = models.ForeignKey(
        EntityModel, on_delete=models.CASCADE, related_name="loan_entity"
    )
    master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name='loans')
    master_avail_bal = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True, default=0.00
    )
    master_name = models.CharField(max_length=60, null=True, blank=True, default='')
    date_applied = models.DateField(default=timezone.now)
    principal = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    purpose = models.CharField(max_length=500, blank=True, default='')
    voucher_no = models.CharField(max_length=12, null=True, blank=True, default='')

    # Loan details
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))],
        default=4.0)

    loan_term = models.PositiveIntegerField(help_text="Loan term in months", default=12)
    moratorium = models.PositiveIntegerField(default=0, help_text="Moratorium period in months")
    disbursement_date = models.DateField(default=timezone.now)

    # Approval information
    date_approved = models.DateField(default=timezone.now)
    approved_by = models.CharField(max_length=200, blank=True)
    monthly_repayment = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    next_repayment_date = models.DateField(default=timezone.now)
    expiry_date = models.DateField(null=True, blank=True, default=None)

    # System fields
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    guarantor_data = models.JSONField(default=dict, blank=True, null=True)
    master_avail_bal = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, default=0.00)

    # Repayments
    loan_class = models.CharField(max_length=15, choices=LOAN_CLASS, default='Current')
    loan_class_calc = models.CharField(max_length=15, choices=LOAN_CLASS, default='')

    tot_int = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, default=0.00)
    tot_ded = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, default=0.00)
    months_remain = models.IntegerField(default=0)
    payment_status = models.CharField(max_length=10, null=True, blank=True, default='')
    #    new_payment_date = models.DateField(default=timezone.now)

    loan_balance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, default=0.00)
    due_days = models.IntegerField(blank=True, null=True, default=0)
    due_interest = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, null=True, blank=True)
    due_repayment = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, null=True, blank=True)
    due_tot_repayment = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, null=True, blank=True)
    due_date = models.DateField(null=True, blank=True, default=timezone.now)
    overdue_days = models.IntegerField(blank=True, null=True)

    loan_trans_amount =  models.DecimalField(max_digits=15, decimal_places=2, default=0.00, null=True, blank=True)
    loan_upd_indicator = models.BooleanField(default=False)

    # Loan tracking fields
    last_interest_calculation_date = models.DateField(null=True, blank=True)
    last_penalty_calculation_date = models.DateField(null=True, blank=True)

    # Overdue tracking
    repayment_overdue = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    interest_overdue = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    penalty_accrued = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    # Payment tracking
    last_payment_date = models.DateField(null=True, blank=True)
    last_interest_paid = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    last_repayment_paid = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    next_payment_due_date = models.DateField(null=True, blank=True)
    last_due_date = models.DateField(null=True, blank=True, default=None)
    loan_update_cnt = models.IntegerField(null=True, blank=True, default=0 )

    loan_credit_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    @property
    def effective_interest_rate(self):
        """Get effective interest rate (member rate or global default)"""
        if self.master.loan_int_rate and self.master.loan_int_rate > 0:
            return self.master.loan_int_rate
        else:
            from SysSetup.models import SystemSettings
            settings = SystemSettings.objects.first()
            return settings.default_interest_rate if settings else Decimal('3.00')

    @property
    def total_overdue(self):
        """Total overdue amount (repayment + interest)"""
        return (self.repayment_overdue or 0) + (self.interest_overdue or 0)

    @property
    def is_overdue(self):
        """Check if loan is overdue"""
        if self.next_payment_due_date and self.next_payment_due_date < timezone.now().date():
            return True
        return False

    @property
    def days_overdue(self):
        """Number of days overdue"""
        if self.is_overdue and self.next_payment_due_date:
            return (timezone.now().date() - self.next_payment_due_date).days
        return 0

    @property
    def calculate_monthly_interest(self):
        """Calculate monthly interest based on current balance"""
        monthly_rate = (self.interest_rate / 100) / 12
        return self.balance * monthly_rate

    @property
    def get_outstanding_guarantor_amount(self):
        """Get total outstanding guarantor amount"""
        total_guaranteed = self.guarantors.aggregate(
            total=models.Sum('guaranteed_amount')
        )['total'] or Decimal('0')

        total_redeemed = self.guarantors.aggregate(
            total=models.Sum('redeemed_amount')
        )['total'] or Decimal('0')

        return total_guaranteed - total_redeemed

    @property
    def int_calc(self):
        """Calculate monthly repayment using amortization formula"""
        balance = float(self.loan_balance)
        int_rate = float(self.effective_interest_rate)
        term = self.months_remain

        if int_rate > 0:
            int_calc = balance * int_rate / 100
        else:
            int_calc = balance / term

        return Decimal(int_calc).quantize(Decimal('0.01'))

    @property
    def ded_calc(self):
        monthly_repayment = float(self.month_repayment)
        int =  float(self.int_calc)

        # Calculate principal portion
        principal_deduction = monthly_repayment - int

        return Decimal(principal_deduction).quantize(Decimal('0.01'))

    @property
    def month_repayment(self):
        balance = float(self.loan_balance)
        term = int(self.loan_term) 

        rep = balance / term

        return Decimal(rep).quantize(Decimal('0.01'))  

    @property
    def calculate_monthly_repayment(self):
        """Calculate monthly repayment using amortization formula"""
        principal = float(self.principal)
        monthly_rate = float(self.effective_interest_rate) / 100 / 12
        term = self.loan_term

        if monthly_rate > 0:
            monthly_payment = principal * monthly_rate * (1 + monthly_rate) ** term / ((1 + monthly_rate) ** term - 1)
        else:
            monthly_payment = principal / term

        return Decimal(monthly_payment).quantize(Decimal('0.01'))

    @property
    def generate_repayment_schedule(self):
        """Generate repayment schedule"""
        schedule = []
        balance = float(self.principal)
        monthly_rate = float(self.interest_rate) / 100 / 12
        monthly_payment = float(self.monthly_repayment)
        current_date = self.disbursement_date

        # Add moratorium period if any
        for month in range(self.moratorium):
            interest = balance * monthly_rate
            schedule.append({
                'month': month + 1,
                'date': current_date,
                'balance': balance,
                'principal': 0,
                'interest': round(interest, 2),
                'total_payment': round(interest, 2),
                'type': 'Moratorium'
            })
            # Move to next month
            current_date = self._add_months(current_date, 1)

        # Add actual repayment schedule
        for month in range(1, self.loan_term + 1):
            interest = balance * monthly_rate
            principal_payment = monthly_payment - interest

            if principal_payment > balance:
                principal_payment = balance

            total_payment = principal_payment + interest
            balance -= principal_payment

            schedule.append({
                'month': self.moratorium + month,
                'date': current_date,
                'balance': round(max(0, balance), 2),
                'principal': round(principal_payment, 2),
                'interest': round(interest, 2),
                'total_payment': round(total_payment, 2),
                'type': 'Repayment'
            })

            current_date = self._add_months(current_date, 1)

            if balance <= 0:
                break

        return schedule

    @property
    def _add_months(self, source_date, months):
        """Add months to a date"""
        import datetime
        month = source_date.month - 1 + months
        year = source_date.year + month // 12
        month = month % 12 + 1
        day = min(source_date.day, [31,
            29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
            31,30,31,30,31,31,30,31,30,31][month-1])
        return datetime.date(year, month, day)

    def __str__(self):
        return f"Loan #{self.id} - {self.master.full_name} - ₵{self.principal}"

    from decimal import Decimal

    @property
    def guarantee_details(self):
        """Get formatted guarantor details"""
        if not self.guarantor_data or 'guarantors' not in self.guarantor_data:
            return "No guarantors"

        details = []
        for guarantor in self.guarantor_data.get('guarantors', []):
            details.append(f"{guarantor['name']}: GHS {guarantor['amount']}")

        return "; ".join(details)

    @property
    def total_guaranteed(self):
        """Calculate total guaranteed amount from guarantor_data"""
        if self.guarantor_data is None or self.guarantor_data == {}:
            return Decimal('0')

        if 'total_guaranteed' in self.guarantor_data:
            return Decimal(str(self.guarantor_data['total_guaranteed']))

        if 'guarantors' in self.guarantor_data:
            guarantors = self.guarantor_data['guarantors']
            if guarantors:
                total = Decimal('0')
                for guarantor in guarantors:
                    amount = guarantor.get('amount', 0)
                    if isinstance(amount, str):
                        try:
                            total += Decimal(amount)
                        except (ValueError, TypeError):
                            total += Decimal('0')
                    else:
                        total += Decimal(str(amount))
                return total

        return Decimal('0')

    @property
    def master_tot_guaranteed(self):
        """Access master's tot_guaranteed through the loan"""
        return self.master.tot_guaranteed

    @property
    def master_tot_guaranted(self):
        """Access master's tot_guaranted through the loan"""
        return self.master.tot_guaranted

    @property
    def master_available_balance(self):
        """Get master's available balance"""
        return self.master.available_balance

    @property
    def guarantor_count(self):
        """Count number of guarantors"""
        if self.guarantor_data is None or self.guarantor_data == {}:
            return 0

        if 'guarantor_count' in self.guarantor_data:
            return self.guarantor_data['guarantor_count']

        if 'guarantors' in self.guarantor_data:
            return len(self.guarantor_data['guarantors'])

        return 0

    @property
    def active_guarantors(self):
        """Get only active guarantors (not fully released)"""
        if not self.guarantor_data or 'guarantors' not in self.guarantor_data:
            return []

        active = []
        for g in self.guarantor_data['guarantors']:
            # Check if guarantor still has unreleased amount
            released = Decimal(str(g.get('released_amount', 0)))
            guaranteed = Decimal(str(g.get('amount', 0)))

            if released < guaranteed:
                active.append(g)

        return active

    @property
    def shortfall(self):
        """Calculate shortfall between principal and guaranteed amount"""
        return max(Decimal('0'), self.principal - self.master_avail_bal)

    @property
    def coverage_status(self):
        """Determine coverage status"""
        if self.total_guaranteed >= self.principal:
            return 'fully_covered'
        elif self.total_guaranteed > 0:
            return 'covered_with_guarantors'
        else:
            return 'not_covered'

    @property
    def coverage_text(self):
        """Get coverage text description"""
        status_map = {
            'fully_covered': 'Fully Covered',
            'covered_with_guarantors': 'Partially Covered', 
            'not_covered': 'Not Covered'
        }
        return status_map.get(self.coverage_status, 'Not Covered')

    @property
    def expired_date(self):
        """Simple and reliable expiry date calculation"""
        if not self.disbursement_date or not self.loan_term:
            return None
        # Using average month length (30.44 days) for better accuracy
        days_in_term = int(self.loan_term * 30.44)
        return self.disbursement_date + timedelta(days=days_in_term)

    @property
    def days_since_expiry(self):
        """Days since loan expired (positive = overdue, negative = not due yet)"""
        if not self.expired_date:
            return None
        today = timezone.now().date()
        return (today - self.expired_date).days

    @property
    def is_expired(self):
        """Check if loan has expired"""
        return self.days_since_expiry and self.days_since_expiry > 0

    @property
    def automatic_loan_class(self):
        """Automatic loan classification based on days overdue"""
        if not self.is_expired:
            return "Current"

        days_overdue = self.days_since_expiry

        if days_overdue <= 30:
            return "Current"
        elif days_overdue <= 60:
            return "OLEM"
        elif days_overdue <= 180:
            return "Substandard"
        elif days_overdue <= 365:
            return "Doubtful"
        else:
            return "Loss"

    @property
    def loan_number(self):
        """Alias for loan_id for backward compatibility"""
        return self.loan_id

    @property
    def total_paid(self):
        """Total amount paid on this loan"""
        from decimal import Decimal
        total = self.repayments.aggregate(
            total=models.Sum('amount_paid')
        )['total']
        return total or Decimal('0.00')

    @property
    def interest_accrued(self):
        """Total interest accrued on this loan"""
        from decimal import Decimal
        total = self.repayments.aggregate(
            total=models.Sum('interest_paid')
        )['total']
        return total or Decimal('0.00')

    @property
    def principal_paid(self):
        """Total principal paid on this loan"""
        from decimal import Decimal
        total = self.repayments.aggregate(
            total=models.Sum('principal_paid')
        )['total']
        return total or Decimal('0.00')

    @property
    def outstanding_balance(self):
        """Current outstanding balance (principal - principal_paid)"""
        return self.principal - self.principal_paid

    @property
    def is_overdue(self):
        """Check if loan is overdue"""
        from django.utils import timezone
        if self.next_payment_date and self.next_payment_date < timezone.now().date():
            return True
        return False

    @property
    def days_overdue(self):
        """Number of days loan is overdue"""
        from django.utils import timezone
        if self.is_overdue and self.next_payment_date:
            return (timezone.now().date() - self.next_payment_date).days
        return 0


## ############# Guarantor Model ###################
class Guarantor(models.Model):
    entity = models.ForeignKey(
        EntityModel, on_delete=models.CASCADE, related_name="loan_gua"
    )
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='guarantors')
    master = models.ForeignKey(Master, on_delete=models.CASCADE)
    guarantor_name = models.CharField(max_length=150, null=True, blank=True, default='')
    guaranteed_amount = models.DecimalField(max_digits=15, decimal_places=2)
    guaranteed_date = models.DateField(default=timezone.now)
    redeemed_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, default=0.00)
    redeemed_status = models.CharField(max_length=15, null=True, blank=True, default='' )

    status = models.CharField(max_length=10, null=True, blank=True, default='')

    def __str__(self):
        return f"{self.master.name} guarantees ₵{self.guarantee_amount} for Loan #{self.loan.id}"

    @property
    def guaranteed_diff(self):
        return max(Decimal('0'), self.guaranteed_amount - self.guaranteed_redeemed)


# loans/models.py - Add this model

class LoanSchedule(models.Model):
    """Monthly loan repayment schedule"""
    entity = models.ForeignKey(
        EntityModel, on_delete=models.CASCADE, related_name="loan_sche"
    )
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='schedule')
    installment_no = models.IntegerField()
    due_date = models.DateField()
    principal_due = models.DecimalField(max_digits=15, decimal_places=2)
    interest_due = models.DecimalField(max_digits=15, decimal_places=2)
    total_due = models.DecimalField(max_digits=15, decimal_places=2)
    balance_after = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(max_length=20, default='PENDING')  # PENDING, PAID, OVERDUE

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['installment_no']

    def __str__(self):
        return f"Installment {self.installment_no} - Loan {self.loan.loan_id}"

# loans/models.py - Add this model

# LoanApp/models.py

class LoanRepayment(models.Model):
    """Individual loan repayment record"""
    entity = models.ForeignKey(
        EntityModel, on_delete=models.CASCADE, related_name="loan_rep"
    )
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='repayments')
    master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name='loan_repayments')
    trans = models.ForeignKey('RecPayApp.Trans', on_delete=models.SET_NULL, null=True, blank=True)  # link to transaction
    trans_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    trans_date = models.DateField(null=True, blank=True)
    old_loan_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    new_loan_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    gua_redeemed_details = models.JSONField(default=dict, blank=True)   # store list of redeemed guarantor details
    interest_paid = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    repayment_paid = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)  # principal paid
    payment_date = models.DateField(null=True, blank=True)
    notes = models.CharField(max_length=150, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-payment_date']

    def __str__(self):
        return f"Repayment for {self.loan.id}: ₵{self.trans_amount}"

# LoanApp/models.py - Add this model
class LoanTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('DISBURSEMENT', 'Loan Disbursement'),
        ('REPAYMENT', 'Loan Repayment'),
        ('INTEREST', 'Interest Accrual'),
        ('PENALTY', 'Penalty'),
    ]

    loan = models.ForeignKey(
        'Loan', 
        on_delete=models.CASCADE, 
        related_name='loan_transactions'  # ✅ Unique name
    )
    entity = models.ForeignKey(
        EntityModel, on_delete=models.CASCADE, related_name="loan_trans"
    )
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    transaction_date = models.DateField()
    reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.loan.loan_id}: ₵{self.amount}"

class LoanDefaultInterest(models.Model):
    entity = models.ForeignKey(
        EntityModel, on_delete=models.CASCADE, related_name="loan_default"
    )
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='default_interests')
    master = models.ForeignKey('MembersApp.Master', on_delete=models.CASCADE)
    master_full_name = models.CharField(max_length=150)
    old_loan_balance = models.DecimalField(max_digits=15, decimal_places=2)
    new_loan_balance = models.DecimalField(max_digits=15, decimal_places=2)
    interest_added = models.DecimalField(max_digits=15, decimal_places=2)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    prev_repayment_date = models.DateField(null=True, blank=True, default=None)
    next_repayment_date = models.DateField(null=True, blank=True, default=None)
    overdue_days = models.IntegerField(null=True, blank=True, default=0)

    def __str__(self):
        return f"Loan {self.loan.id} - Interest {self.interest_added} on {self.created_at.date()}"


class LoanInterestAudit(models.Model):
    date = models.DateField(auto_now_add=True)
    master = models.ForeignKey("MembersApp.Master", on_delete=models.CASCADE)
    loan = models.ForeignKey("LoanApp.Loan", on_delete=models.CASCADE)
    next_repayment_date = models.DateField()
    balance_before = models.DecimalField(max_digits=15, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=8, decimal_places=4)
    months = models.IntegerField(default=1)
    interest_accrued = models.DecimalField(max_digits=15, decimal_places=2)
    balance_after = models.DecimalField(max_digits=15, decimal_places=2)
    expiry_date = models.DateField()
    loan_class = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
