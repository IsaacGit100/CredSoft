# MembersApp/models.py
from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

from decimal import Decimal
from django.db import models
from django.db.models.base import Coalesce
from SysSetup.models import SystemSettings
from django.utils import timezone

from django.db.models import F, Value, Count, Sum, Avg
from django.db.models.functions import Coalesce

# models.py
from django.db import models
from django.db.models import Sum, Avg, Count, Q, Value
from django.db.models.functions import Coalesce
from decimal import Decimal

from django_ledger.models import EntityModel

class MasterManager(models.Manager):
    def with_balance(self):
        return self.annotate(current_balance=(
            Coalesce('tot_deposits', Value(0)) -
            Coalesce('tot_deposit_withdrawal', Value(0)) +
            Coalesce('tot_interest_accrued', Value(0))             
        ))
        
 #   def with_sav_avail_bal(self):
 #       return self.annotate(sav_avail_bal=(Coalesce('tot_deposits', Value(0)) - Coalesce('tot_deposit_withdrawal', Value(0)) + Coalesce('tot_interest_accrued', Value(0))))
  
    def with_sav_avail_bal(self):
        return self.annotate(
            sav_avail_bal=(
                Coalesce('tot_deposits', Value(0, output_field=models.DecimalField())) -
                Coalesce('tot_deposit_withdrawal', Value(0, output_field=models.DecimalField())) +
                Coalesce('tot_interest_accrued', Value(0, output_field=models.DecimalField()))
            )
        )
    
    def with_positive_balance(self):
        return self.with_balance().filter(current_balance__gt=0)
    
    def with_negative_balance(self):
        return self.with_balance().filter(current_balance__lt=0)
    
    def with_zero_sav_bal(self):
        return self.with_balance().filter(current_balance=0)
    
    def get_balance_summary(self):  # Renamed to avoid confusion
        """Get balance summary statistics"""
        result = self.with_balance().aggregate(
            total_balance=Sum('current_balance'),
            average_balance=Avg('current_balance'),
            count_with_balance=Count('id', filter=Q(current_balance__gt=0)),
            count_zero_balance=Count('id', filter=Q(current_balance=0)),
            count_negative=Count('id', filter=Q(current_balance__lt=0))
        )
        return result
    
    def get_total_savings_balance(self):
        """Get total savings balance"""
        result = self.with_balance().aggregate(
            total=Sum('current_balance')
        )['total']
        return result or Decimal('0.00')


class Master(models.Model):
    # Use your custom manager as the default
    objects = MasterManager()  # ← This is the key fix!

    # ========== CHOICES ==========
    MEM_STATUS_CHOICES = [
        ('Active', 'Active'),
        ('InActive', 'InActive'),
    ]

    TITLE_CHOICES = [
        ('Mr.', 'Mr.'),
        ('Mrs.', 'Mrs.'),
        ('Miss', 'Miss'),
        ('Rev', 'Rev'),
        ('Dr.', 'Dr.'),
        ('Prof', 'Prof'),
        ('Canon', 'Canon'),
    ]

    ENROLL_FEES_PAID = [
        ('Yes', 'Yes'),
        ('No', 'No'),
    ]

    MIN_SHARES_PURCHASED = [
        ('Yes', 'Yes'),
        ('No', 'No'),
    ]

    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]

    MARITAL_STATUS_CHOICES = [
        ('Single', 'Single'),
        ('Married', 'Married'),
        ('Widowed', 'Widowed'),
    ]

    ROLE = [
        ('Member', 'Member'),
        ('Chairman', 'Chairman'),
        ('Manager', 'Manager'),
        ('Finance', 'Finance'),
        ('Admin', 'Admin'),
        ('Loans Manager', 'Loans Manager'),
    ]

    LOGIN_STATUS = [
        ('SUCCESS', 'Successful'),
        ('FAILED', 'Failed'),
        ('LOCKED', 'Account Locked'),
        ('EXPIRED', 'Session Expired'),
    ]

    # ========== PERSONAL INFORMATION ==========
    
    entity = models.ForeignKey(EntityModel, on_delete=models.CASCADE, related_name="cu_members")
    old_member_id = models.IntegerField(blank=True, null=True)
    title = models.CharField(max_length=10, choices=TITLE_CHOICES, blank=True, default='Mr.')
    first_name = models.CharField(max_length=100, blank=True, default='')
    last_name = models.CharField(max_length=100, blank=True, default='')
    other_names = models.CharField(max_length=200, blank=True, default='')
    full_name = models.CharField(max_length=150, blank=True, null=True)

    date_of_birth = models.DateField(blank=True, null=True)
    date_enrolled = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, default='')
    marital_status = models.CharField(max_length=10, choices=MARITAL_STATUS_CHOICES, blank=True, default='Single')
    church_member = models.CharField(max_length=3, blank=True, default='Yes')
    mem_status = models.CharField(max_length=10, choices=MEM_STATUS_CHOICES, blank=True, null=True, default='Active')
    ghana_card_no = models.CharField(max_length=15, blank=True, null=True, default='')
    profession = models.CharField(max_length=120, blank=True, null=True, default='')
    role = models.CharField(max_length=20, choices=ROLE, default='Member', blank=True, null=True)

    # ========== CONTACT INFORMATION ==========
    postal_address = models.TextField(blank=True, default='')
    residential_address = models.TextField(blank=True, default='')
    city = models.CharField(max_length=100, blank=True, default='')
    near_landmark = models.CharField(max_length=150, blank=True, default='')
    street_name = models.CharField(max_length=200, blank=True, default='')
    gps = models.CharField(max_length=100, blank=True, default='')
    telephone1 = models.CharField(max_length=20, blank=True, default='')
    telephone2 = models.CharField(max_length=20, blank=True, default='')
    email_address = models.EmailField(blank=True, default='')

    enrollment_fees =  models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, default=0.00)
    enroll_fees_paid = models.CharField(max_length=4, blank=True, choices=ENROLL_FEES_PAID, default='No')
    min_shares_purchased = models.CharField(max_length=4, blank=True, choices=MIN_SHARES_PURCHASED, default='No')

    # ========== # Next of Kin Information ==========

    nok_name1 = models.CharField(max_length=100, default='', blank=True)
    nok_address1 = models.CharField(max_length=100, default='', blank=True)
    nok_telephone1 = models.CharField(max_length=12, default='', blank=True)
    nok_relation1 = models.CharField(max_length=30, default='', blank=True)
    nok_percent1 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0.00)
    nok_gps1 = models.CharField(max_length=20, default='', blank=True)
    nok_email1 = models.CharField(max_length=100, default='', blank=True)

    nok_name2 = models.CharField(max_length=100, default='', blank=True)
    nok_address2 = models.CharField(max_length=100, default='', blank=True)
    nok_telephone2 = models.CharField(max_length=12, default='', blank=True)
    nok_relation2 = models.CharField(max_length=30, default='', blank=True)
    nok_percent2 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0.00)
    nok_gps2 = models.CharField(max_length=20, default='', blank=True)
    nok_email2 = models.CharField(max_length=100, default='', blank=True)

    nok_name3 = models.CharField(max_length=100, default='', blank=True)
    nok_address3 = models.CharField(max_length=100, default='', blank=True)
    nok_telephone3 = models.CharField(max_length=12, default='', blank=True)
    nok_relation3 = models.CharField(max_length=30, default='', blank=True)
    nok_percent3 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0.00)
    nok_gps3 = models.CharField(max_length=20, default='', blank=True)
    nok_email3 = models.CharField(max_length=100, default='', blank=True)

    # ========== STATUS FIELDS (WORKING) ==========
    is_deleted = models.BooleanField(default=False)
    is_deleted_date = models.DateTimeField(null=True, blank=True, default=None)
    del_rec = models.CharField(max_length=5, blank=True, null=True, default='')
    is_deleted_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='del_members')
    last_deleted_date = models.DateTimeField(null=True, blank=True, default=None)

    delete_history = models.JSONField(default=list, blank=True)      # Track all deletions
    restore_history = models.JSONField(default=list, blank=True)     # Track all restorations
    delete_users = models.JSONField(default=list, blank=True)        # Track who deleted
    restore_users = models.JSONField(default=list, blank=True)       # Track who restored

    # =========== SAVINGS / DEPOSIT ===========================================#
    sav_defer_int_appl = models.BooleanField(default=False)
    sav_int_rate = models.DecimalField(max_digits=6, decimal_places=4, default=0.0000)
    sav_int_rate_date = models.DateTimeField(null=True, blank=True, default=None)
    sav_defer_int_appl_date = models.DateTimeField(null=True, blank=True, default=None)
    sav_int_rate_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sav_int_rate')
    sav_defer_int_appl_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='save_defer')
    sav_int_accrued = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, blank=True, null=True)
    last_sav_int_accrual_date = models.DateField(null=True, blank=True, default=None)
    last_sav_int_accrual_run = models.DateTimeField(null=True, blank=True, default=None)
    sav_min_bal =  models.DecimalField(max_digits=15, decimal_places=2, default=0.00, blank=True, null=True)
    sav_min_bal_days = models.IntegerField(null=True, blank=True, default=0)
    
    tot_mnth_sav_int_accrued = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, default=0.00)
    sav_int_accrued_days = models.IntegerField(null=True, blank=True, default=0)

    # ============ LOAN INFORMATION ===========================================#
    loan_int_rate = models.DecimalField(max_digits=6, decimal_places=4, default=0.0000)
    loan_int_rate_date = models.DateTimeField(null=True, blank=True, default=None)
    loan_int_rate_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='loan_int_rate')

    loan_last_disb_date = models.DateTimeField(null=True, blank=True, default=None)
    loan_last_disb_princ = models.DecimalField(max_digits=6, decimal_places=4, default=0.00, blank=True, null=True)
    loan_disb_tot_princ = models.DecimalField(max_digits=6, decimal_places=4, default=0.00, blank=True, null=True)
    loan_disb_cnt = models.IntegerField(null=True, blank=True, default=0)
    loan_last_id = models.IntegerField(null=True, blank=True, default=0)
    #
    loan_last_repayment = models.DecimalField(max_digits=6, decimal_places=4, default=0.00, blank=True, null=True)
    loan_last_repayment_date = models.DateTimeField(null=True, blank=True, default=None)
    loan_tot_repayment = models.DecimalField(max_digits=6, decimal_places=4, default=0.00, blank=True, null=True)
    loan_repayment_cnt = models.IntegerField(null=True, blank=True, default=0)
    loan_last_repayment_id = models.IntegerField(null=True, blank=True, default=0)

    # ========== FINANCIAL FIELDS ==========
    open_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0, blank=True, null=True)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0, blank=True, null=True)
    tot_deposits = models.DecimalField(max_digits=15, decimal_places=2, default=0, blank=True, null=True)
    tot_deposit_withdrawal = models.DecimalField(max_digits=15, decimal_places=2, default=0, blank=True, null=True)
    tot_shares = models.DecimalField(max_digits=15, decimal_places=2, default=0, blank=True, null=True)
    tot_shares_withdrawal = models.DecimalField(max_digits=15, decimal_places=2, default=0, blank=True, null=True)
    tot_interest_accrued = models.DecimalField(max_digits=15, decimal_places=2, default=0, blank=True, null=True)
    tot_dividend = models.DecimalField(max_digits=15, decimal_places=2, default=0, blank=True, null=True)
    tot_dividend_withdrawal = models.DecimalField(max_digits=15, decimal_places=2, default=0, blank=True, null=True)
    tot_sav_int_deferred = models.DecimalField(max_digits=15, decimal_places=2, default=0, blank=True, null=True)
    tot_sav_int = models.DecimalField(max_digits=15, decimal_places=2, default=0, blank=True, null=True)
    

    # ========== AUDIT FIELDS ==========
    del_date_time = models.DateTimeField(null=True, blank=True)
    del_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='deleted_members')
    del_username = models.CharField(max_length=20, null=True, blank=True, default='')
    del_by_name = models.CharField(max_length=150, null=True, blank=True, default='')

    # ========== TIMESTAMPS ==========
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    # ========== APPROVALS ==========
    approved_by_chairman = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='chairman_approved')
    approved_by_manager = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='manager_approved')

    # ========== IMAGE MANAGEMENT ====
    profile_image = models.ImageField(upload_to='member_photos/%Y/%m/%d/', blank=True, null=True, help_text="Upload member passport photo")
    signature = models.ImageField(upload_to='member_signatures/%Y/%m/%d/', blank=True, null=True, help_text="Upload member signature")
    id_card_front = models.ImageField(upload_to='member_ids/%Y/%m/%d/', blank=True, null=True, help_text="Upload ID card front")
    id_card_back = models.ImageField(upload_to='member_ids/%Y/%m/%d/', blank=True, null=True, help_text="Upload ID card back")

    # ========== LOGIN HISTORY CAPTURE ======================
    # MembersApp/models.py
    class Meta:
        ordering = ['last_name', 'first_name']

    def save(self, *args, **kwargs):
        # Generate full_name
        name_parts = [self.last_name, self.first_name, self.other_names]
        self.full_name = ' '.join(filter(None, name_parts)).strip()

        # Sync del_rec with is_deleted
        if self.is_deleted:
            self.del_rec = 'Yes'
        elif not self.del_rec:
            self.del_rec = 'No'

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

    # ========== PROPERTIES ==========
    @property
    def sav_effective_int_rate(self):
        """Get effective interest rate (member rate or global default)"""
        if self.master.sav_int_rate and self.master.sav_int_rate > 0:
            return self.master.sav_int_rate
        else:
            from SysSetup.models import SystemSettings
            settings = SystemSettings.objects.first()
            return settings.savings_interest_rate if settings else Decimal('3.00')

    @property
    def sav_avail_bal(self):       
        deposits = self.tot_deposits or Decimal('0.00')
        withdrawals = self.tot_deposit_withdrawal or Decimal('0.00')
        accrued_int = self.tot_interest_accrued or Decimal(0.00)
        return deposits - withdrawals + accrued_int

    @property
    def total_credits(self):
        return (self.tot_shares or 0) + (self.tot_deposits or 0) + \
               (self.tot_dividend or 0) + (self.tot_interest_accrued or 0) + (self.tot_guaranteed or 0)

    @property
    def total_debits(self):
        return (self.tot_shares_withdrawal or 0) + (self.tot_deposit_withdrawal or 0) + \
               (self.tot_dividend_withdrawal or 0) + (self.tot_loans or 0) + (self.tot_guaranted or 0)

    @property
    def available_balance(self):
        return self.total_credits - self.total_debits

    @property
    def is_active(self):
        return not self.is_deleted

    @property
    def tot_guaranteed(self):
        """Total amount this member has guaranteed for others"""
        from decimal import Decimal
        total = self.guarantor_set.aggregate(
            total=models.Sum('guaranteed_amount')
        )['total']
        return total or Decimal('0.00')

    @property
    def tot_guaranted(self):
        """Total guarantee amount on this member's own loans (when they are the borrower)"""
        from decimal import Decimal
        total = 0
        for loan in self.loans.all():
            total += loan.total_guaranteed
        return Decimal(str(total))

    @property
    def tot_redeemed(self):
        """Total amount that has been redeemed from this member's guarantees"""
        from decimal import Decimal
        total = self.guarantor_set.aggregate(
            total=models.Sum('redeemed_amount')
        )['total']
        return total or Decimal('0.00')

    @property
    def tot_outstanding_guarantee(self):
        """Total amount still outstanding on this member's guarantees"""
        return self.tot_guaranteed - self.tot_redeemed

    @property
    def net_guarantee_position(self):
        """Net guarantee position (what they guaranteed for others minus what others guaranteed for them)"""
        return self.tot_guaranteed - self.tot_guaranteed_as_borrower

    # ## Loan Balances

    @property
    def tot_loan_balance(self):
        """Total outstanding loan balance for this member"""
        from decimal import Decimal
        total = 0
        for loan in self.loans.all():
            total += loan.outstanding_balance
        return Decimal(str(total))

    @property
    def tot_loans(self):
        """Total principal of all loans for this member"""
        from decimal import Decimal
        total = self.loans.aggregate(
            total=models.Sum('principal')
        )['total']
        return total or Decimal('0.00')

    @property
    def tot_loan_paid(self):
        """Total amount paid on all loans by this member"""
        from decimal import Decimal
        total = 0
        for loan in self.loans.all():
            total += loan.total_paid
        return Decimal(str(total))

    @property
    def tot_interest_paid(self):
        """Total interest paid on all loans by this member"""
        from decimal import Decimal
        total = 0
        for loan in self.loans.all():
            total += loan.interest_accrued
        return Decimal(str(total))

    @property
    def active_loans_count(self):
        """Number of active loans for this member"""
        return self.loans.filter(status='Active').count()

    @property
    def completed_loans_count(self):
        """Number of completed loans for this member"""
        return self.loans.filter(status='Completed').count()

    @property
    def overdue_loans_count(self):
        """Number of overdue loans for this member"""
        count = 0
        for loan in self.loans.all():
            if loan.is_overdue:
                count += 1
        return count

    # MembersApp/models.py - Add to Master class

    @property
    def tot_loan_repayment_overdue(self):
        """Total repayment overdue across all loans"""
        from decimal import Decimal
        total = 0
        for loan in self.loans.all():
            total += loan.repayment_overdue or 0
        return Decimal(str(total))

    @property
    def tot_loan_interest_overdue(self):
        """Total interest overdue across all loans"""
        from decimal import Decimal
        total = 0
        for loan in self.loans.all():
            total += loan.interest_overdue or 0
        return Decimal(str(total))

    @property
    def tot_loan_penalty(self):
        """Total penalty accrued across all loans"""
        from decimal import Decimal
        total = 0
        for loan in self.loans.all():
            total += loan.penalty_accrued or 0
        return Decimal(str(total))

    @property
    def total_guaranteed_given(self):
        """Total amount this member has guaranteed for others"""
        from decimal import Decimal
        total = self.guarantor_set.aggregate(
            total=models.Sum('guaranteed_amount')
        )['total']
        return total or Decimal('0.00')

    @property
    def total_guaranteed_redeemed(self):
        """Total amount redeemed from this member's guarantees"""
        from decimal import Decimal
        total = self.guarantor_set.aggregate(
            total=models.Sum('redeemed_amount')
        )['total']
        return total or Decimal('0.00')

    @property
    def net_loan_position(self):
        """Net loan position (loan balance vs savings)"""
        return (self.tot_savings or 0) - self.tot_loan_balance

    @property
    def loan_health_status(self):
        """Overall loan health status for the member"""
        if self.overdue_loans_count > 0:
            return "Critical"
        elif self.tot_loan_balance > (self.tot_savings or 0) * 0.7:
            return "High Risk"
        elif self.tot_loan_balance > 0:
            return "Active"
        else:
            return "Clean"

    # ###### Savings Interest Calculation #####
    # MembersApp/models.py

    @property
    def global_savings_rate(self):

        try:
            settings = SystemSettings.objects.first()
            return settings.savings_interest_rate if settings else Decimal('0.00')
        except:
            return Decimal('0.00')

    @property
    def effective_savings_rate(self):

        if self.sav_int_rate and self.sav_int_rate > Decimal('0.00'):
            return self.sav_int_rate
        return self.global_savings_rate

    @property
    def monthly_interest(self):   
        return (self.daily_interest * Decimal('30')).quantize(Decimal('0.01'))

    @property
    def daily_interest(self):

        # Get the effective rate
        rate = self.effective_savings_rate
        balance = self.sav_avail_bal

        # Convert to Decimal properly
        try:
            rate = Decimal(str(rate))
            balance = Decimal(str(balance))
        except:
            return Decimal('0.00')

        # Check if rate and balance are valid
        if rate <= Decimal('0.00') or balance <= Decimal('0.00'):
            return Decimal('0.00')

        # Calculate daily interest
        # Daily interest = (Balance * Rate%) / 365 / 100
        try:
            daily_interest = (balance * rate / Decimal('100')) / Decimal('365')
            # Return with 4 decimal places
            return daily_interest.quantize(Decimal('0.0001'))
        except:
            return Decimal('0.00')  

    # ============= IMAGE MANAGEMENT =====================
    @property
    def profile_image_url(self):
        """Get profile image URL or default placeholder"""
        if self.profile_image:
            return self.profile_image.url
        return '/static/images/default-avatar.png'

    @property
    def has_images(self):
        """Check if member has any images"""
        return any([self.profile_image, self.signature, self.id_card_front, self.id_card_back])


class Sav_Int_Table(models.Model): 
    entity = models.ForeignKey(EntityModel, on_delete=models.CASCADE, related_name="sav_int")
    date = models.DateField(blank=True, null=True, default=None)
    master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name='savings_int')
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0, blank=True, null=True)
    sav_int_rate = models.DecimalField(max_digits=8, decimal_places=4, default=0.0000)
    no_of_days = models.IntegerField(null=True, blank=True, default=0)
    sav_int = models.DecimalField(max_digits=15, decimal_places=2, default=0, blank=True, null=True)
    last_updated_date = models.DateField(blank=True, null=True, default=None)
    update_type = models.CharField(max_length=40, null=True, blank=True) # from the system settings table(Monthly, Quaterly .........)
    next_update_date = models.DateField(blank=True, null=True, default=None) # from the system settings table, next date of update using update_type
    applied = models.BooleanField(default=False)
    applied_date = models.DateField(null=True, blank=True)  # optional, for audit
