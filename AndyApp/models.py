from django.db import models

# Create your models here.
from django.db import models

# Create your models here.
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.core.validators import EmailValidator

class MastBoss(models.Model):
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
    
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]
    
    MARITAL_STATUS_CHOICES = [
        ('Single', 'Single'),
        ('Married', 'Married'),
        ('Widowed', 'Widowed'),
    ]
    
    CHURCH_MEMBER_CHOICES = [
        ('Yes', 'Yes'),
        ('No', 'No'),
    ]
    
    ENROLL_FEES_PAID = [
        ('Yes', 'Yes'),
        ('No', 'No'),
    ]
    
    MIN_SHARES_PURCHASED = [
        ('Yes', 'Yes'),
        ('No', 'No'),
    ]
    ROLE = [
        ('Member', 'Member'),
        ('Chairman', 'Chairman'),
        ('Finance', 'Fiance'),
        ('Education', 'Education'),
        ('Admin', 'Admin'),
        ('Loans', 'Loans'),
    ]
    LOAN_STATUS_CHOICES = [
        ('No Loan', 'No Loan'),
        ('Overdue', 'Overdue'),
        ('Active', 'Active'),
    ]
    # Personal Information
    title = models.CharField(max_length=10, choices=TITLE_CHOICES, blank=True, default='Mr.')
    last_name = models.CharField(max_length=100,  blank=True, default='')
    other_names = models.CharField(max_length=200, blank=True, default='')
    first_name = models.CharField(max_length=100, blank=True, default='')
    full_name = models.CharField(max_length=150, blank=True, null=True, default='')
    date_of_birth = models.DateField(blank=True, null=True)
    date_enrolled = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, default='')
    marital_status = models.CharField(max_length=10, choices=MARITAL_STATUS_CHOICES, blank=True, default='Single')
    church_member = models.CharField(max_length=3, choices=CHURCH_MEMBER_CHOICES, blank=True, default='Yes')
    mem_status = models.CharField(max_length=10, choices=MEM_STATUS_CHOICES, blank=True, null=True, default='Active')
    loan_status = models.CharField(max_length=10, choices=LOAN_STATUS_CHOICES, blank=True, null=True, default='No Loan')
    
    # Contact Information
    postal_address = models.TextField(blank=True, default='')
    residential_address = models.TextField(blank=True, default='')
    city = models.CharField(max_length=100, blank=True, default='')
    near_landmark = models.CharField(max_length=150, blank=True, default='')
    street_name = models.CharField(max_length=200, blank=True, default='')
    gps = models.CharField(max_length=100, blank=True, default='')
    telephone1 = models.CharField(max_length=20, blank=True, default='')
    telephone2 = models.CharField(max_length=20, blank=True, default='')
    email_address = models.EmailField(validators=[EmailValidator()], blank=True, default='')
    profession = models.CharField(max_length=120, blank=True, null=True, default='')
    role = models.CharField(max_length=20, choices=ROLE, default='Member', blank=True, null=True)
    
    # Next of Kin Information
    nok_name = models.CharField(max_length=200, blank=True, default='')
    nok_address = models.TextField(blank=True, default='')
    nok_city = models.CharField(max_length=100, blank=True, default='')
    nok_gps = models.CharField(max_length=100, blank=True, default='')
    nok_telephone = models.CharField(max_length=20, blank=True, default='')
    nok_email = models.EmailField(blank=True, validators=[EmailValidator()], default='')
    nok_title = models.CharField(max_length=50, default='', blank=True)
    nok_relation = models.CharField(max_length=50, default='', blank=True)
    
    # Next Of Kin Information
    nok_name1 = models.CharField(max_length=100, default='', blank=True)
    nok_address1 = models.CharField(max_length=100, default='', blank=True)
    nok_telephone1 = models.CharField(max_length=12, default='', blank=True)
    nok_relation1 = models.CharField(max_length=30, default='', blank=True)
    
    nok_name2 = models.CharField(max_length=100, default='', blank=True)
    nok_address2 = models.CharField(max_length=100, default='', blank=True)
    nok_telephone2 = models.CharField(max_length=12, default='', blank=True)
    nok_relation2 = models.CharField(max_length=30, default='', blank=True)
    
    nok_name3 = models.CharField(max_length=100, default='', blank=True)
    nok_address3 = models.CharField(max_length=100, default='', blank=True)
    nok_telephone3 = models.CharField(max_length=12, default='', blank=True)
    nok_relation3 = models.CharField(max_length=30, default='', blank=True)
    
    del_rec = models.CharField(max_length=3, blank=True, null=True, default='')
    
    manager = models.CharField(max_length=100, default='', blank=True)
    approved_by = models.CharField(max_length=100, default='', blank=True)
    
    # Financial Information
    enroll_fees_paid = models.CharField(max_length=4, blank=True, choices=ENROLL_FEES_PAID, default='No')
    min_shares_purchased = models.CharField(max_length=4, blank=True, choices=MIN_SHARES_PURCHASED, default='No')
    shares = models.DecimalField(max_digits=15, decimal_places=2, default=0, blank=True, null=True)
    dividend = models.DecimalField(max_digits=15, decimal_places=2, default=0, blank=True, null=True )
    deposit = models.DecimalField(max_digits=15, decimal_places=2, default=0, blank=True, null=True)
    interest = models.DecimalField(max_digits=15, decimal_places=2, default=0, blank=True, null=True)
    withdrawal = models.DecimalField(max_digits=15, decimal_places=2, default=0, blank=True, null=True)
    avail_bal = models.DecimalField(max_digits=15, decimal_places=2, default=0, blank=True, null=True)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0, blank=True, null=True)
    open_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0, blank=True, null=True)
    
    # Loan Information
    loan_principal = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    loan_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    loan_repayment = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    loan_interest = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    loan_disbursed = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    loan_guarateed = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    loan_disbursed_date = models.DateField(auto_now=True, blank=True, null=True)
    
    
    # Dates
    date_record_created = models.DateField(auto_now=True, blank=True, null=True)
    date_deposit_updated = models.DateField(auto_now=True, blank=True, null=True)
    date_loan_updated = models.DateField(auto_now=True, blank=True, null=True)
    date_withdrawal_updated = models.DateField(auto_now=True, blank=True, null=True)
    date_payment_made = models.DateField(auto_now=True, blank=True, null=True)
    
    date_processed = models.DateField(auto_now=True, blank=True, null=True)
   
    approved_by_chairman = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='chairman_approved'
    )

    approved_by_manager = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='manager_approved'
    )

    def __str__(self):
        return f"{self.last_name} - {self.first_name} ({self.role})"
        return f"{self.title} {self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        # Automatically generate full_name whenever saving
        self.full_name = f"{self.last_name} {self.first_name}".strip()
        if self.other_names:
            self.full_name += f" {self.other_names}"
        super().save(*args, **kwargs)
        

class Mastandy(models.Model):
    # Use your custom manager as the default

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
    title = models.CharField(
        max_length=10, choices=TITLE_CHOICES, blank=True, default='Mr.')
    first_name = models.CharField(max_length=100, blank=True, default='')
    last_name = models.CharField(max_length=100, blank=True, default='')
    other_names = models.CharField(max_length=200, blank=True, default='')
    full_name = models.CharField(max_length=150, blank=True, null=True)

    date_of_birth = models.DateField(blank=True, null=True)
    date_enrolled = models.DateField(blank=True, null=True)
    gender = models.CharField(
        max_length=10, choices=GENDER_CHOICES, blank=True, default='')
    marital_status = models.CharField(
        max_length=10, choices=MARITAL_STATUS_CHOICES, blank=True, default='Single')
    church_member = models.CharField(max_length=3, blank=True, default='Yes')
    mem_status = models.CharField(
        max_length=10, choices=MEM_STATUS_CHOICES, blank=True, null=True, default='Active')
    ghana_card_no = models.CharField(
        max_length=15, blank=True, null=True, default='')
    profession = models.CharField(
        max_length=120, blank=True, null=True, default='')
    role = models.CharField(max_length=20, choices=ROLE,
                            default='Member', blank=True, null=True)

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

    enrollment_fees = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True, default=0.00)
    enroll_fees_paid = models.CharField(
        max_length=4, blank=True, choices=ENROLL_FEES_PAID, default='No')
    min_shares_purchased = models.CharField(
        max_length=4, blank=True, choices=MIN_SHARES_PURCHASED, default='No')

    # ========== # Next of Kin Information ==========

    nok_name1 = models.CharField(max_length=100, default='', blank=True)
    nok_address1 = models.CharField(max_length=100, default='', blank=True)
    nok_telephone1 = models.CharField(max_length=12, default='', blank=True)
    nok_relation1 = models.CharField(max_length=30, default='', blank=True)
    nok_percent1 = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, default=0.00)
    nok_gps1 = models.CharField(max_length=20, default='', blank=True)
    nok_email1 = models.CharField(max_length=100, default='', blank=True)

    nok_name2 = models.CharField(max_length=100, default='', blank=True)
    nok_address2 = models.CharField(max_length=100, default='', blank=True)
    nok_telephone2 = models.CharField(max_length=12, default='', blank=True)
    nok_relation2 = models.CharField(max_length=30, default='', blank=True)
    nok_percent2 = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, default=0.00)
    nok_gps2 = models.CharField(max_length=20, default='', blank=True)
    nok_email2 = models.CharField(max_length=100, default='', blank=True)

    nok_name3 = models.CharField(max_length=100, default='', blank=True)
    nok_address3 = models.CharField(max_length=100, default='', blank=True)
    nok_telephone3 = models.CharField(max_length=12, default='', blank=True)
    nok_relation3 = models.CharField(max_length=30, default='', blank=True)
    nok_percent3 = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, default=0.00)
    nok_gps3 = models.CharField(max_length=20, default='', blank=True)
    nok_email3 = models.CharField(max_length=100, default='', blank=True)

    # ========== STATUS FIELDS (WORKING) ==========
    is_deleted = models.BooleanField(default=False)
    is_deleted_date = models.DateTimeField(null=True, blank=True, default=None)
    del_rec = models.CharField(max_length=5, blank=True, null=True, default='')
    
    last_deleted_date = models.DateTimeField(
        null=True, blank=True, default=None)

    delete_history = models.JSONField(
        default=list, blank=True)      # Track all deletions
    restore_history = models.JSONField(
        default=list, blank=True)     # Track all restorations
    delete_users = models.JSONField(
        default=list, blank=True)        # Track who deleted
    restore_users = models.JSONField(
        default=list, blank=True)       # Track who restored

   # =========== SAVINGS / DEPOSIT ===========================================#
    sav_defer_int_appl = models.BooleanField(default=False)
    sav_int_rate = models.DecimalField(max_digits=6, decimal_places=4, default=0.0000)
    sav_int_rate_date = models.DateTimeField(null=True, blank=True, default=None)
    sav_defer_int_appl_date = models.DateTimeField(null=True, blank=True, default=None)
    
   
    sav_int_accrued = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, blank=True, null=True)
    last_sav_int_accrual_date = models.DateField(null=True, blank=True, default=None)
    last_sav_int_accrual_run = models.DateTimeField(null=True, blank=True, default=None)
    sav_min_bal = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, blank=True, null=True)
    sav_min_bal_days = models.IntegerField(null=True, blank=True, default=0)

    # ============ LOAN INFORMATION ===========================================#
    loan_int_rate = models.DecimalField(max_digits=6, decimal_places=4, default=0.0000)
    loan_int_rate_date = models.DateTimeField(null=True, blank=True, default=None)
   

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
    tot_deposits = models.DecimalField(max_digits=15, decimal_places=2, default=0, blank=True, null=True)
    tot_deposit_withdrawal = models.DecimalField(max_digits=15, decimal_places=2, default=0, blank=True, null=True)
    tot_shares = models.DecimalField(max_digits=15, decimal_places=2, default=0, blank=True, null=True)
    tot_shares_withdrawal = models.DecimalField(max_digits=15, decimal_places=2, default=0, blank=True, null=True)
    tot_interest_accrued = models.DecimalField(max_digits=15, decimal_places=2, default=0, blank=True, null=True)
    tot_dividend = models.DecimalField(max_digits=15, decimal_places=2, default=0, blank=True, null=True)
    tot_dividend_withdrawal = models.DecimalField(max_digits=15, decimal_places=2, default=0, blank=True, null=True)
    tot_sav_int_deferred = models.DecimalField(max_digits=15, decimal_places=2, default=0, blank=True, null=True)

    # ========== AUDIT FIELDS ==========
    del_date_time = models.DateTimeField(null=True, blank=True)
   
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
    signature = models.ImageField(upload_to='member_signatures/%Y/%m/%d/',
                                  blank=True, null=True, help_text="Upload member signature")
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
               (self.tot_dividend or 0) + \
            (self.tot_interest_accrued or 0) + (self.tot_guaranteed or 0)

    @property
    def total_debits(self):
        return (self.tot_shares_withdrawal or 0) + (self.tot_deposit_withdrawal or 0) + \
               (self.tot_dividend_withdrawal or 0) + \
            (self.tot_loans or 0) + (self.tot_guaranted or 0)

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
    
class StateAndy(models.Model):
    date = models.DateField(null=True, blank=True, default=None)
    rec_no = models.CharField(max_length=15, null=True, blank=True, default='')
    amount = models.DecimalField(max_digits=18, null=True, blank=True, decimal_places=2, default=0.00)
    trans_type = models.CharField(max_length=10, null=True, blank=True, default='')
    desc = models.CharField(max_length=20, null=True, blank=True, default='')
    balance = models.DecimalField(max_digits=18, null=True, blank=True, decimal_places=2, default=0.00)
    master_id = models.IntegerField(default=0)
    state_code = models.CharField(max_length=50, null=True, blank=True, default='')
