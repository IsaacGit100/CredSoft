from django.utils import timezone
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum
from decimal import Decimal
from django.core.validators import MinValueValidator
from datetime import timedelta
from django.db.models.fields import DateField


# Import Tables
from UserAuth.models import User
from django_ledger.models import EntityModel
from MembersApp.models import Master
from RecPayApp.models import Trans

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

    STATUS_NEW = "NEW"
    STATUS_ACTIVE = "ACTIVE"
    STATUS_COMPLETED = "COMPLETED"
    STATUS_WRITTEN_OFF = "WRITTEN_OFF"

    # Borrower information
    entity = models.ForeignKey(EntityModel, on_delete=models.CASCADE, related_name="loan_entity")
    member = models.ForeignKey(Master, on_delete=models.CASCADE, related_name="loans")
    loan_no = models.CharField(max_length=20, unique=True, blank=True)
    master_name = models.CharField(max_length=60, null=True, blank=True, default='')
    date_applied = models.DateField(default=timezone.now)
    principal = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    purpose = models.CharField(max_length=500, blank=True, default='')
    voucher_no = models.CharField(max_length=12, null=True, blank=True, default='')
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))

    # Loan details
    interest_rate = models.DecimalField(max_digits=6, decimal_places=4, validators=[MinValueValidator(Decimal('0.01'))], default=4.0)
    penalty_rate = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("2.00"), help_text="Monthly penalty rate (%) on overdue principal")
    term_months = models.PositiveIntegerField(help_text="Loan term in months", default=12)
    moratorium_months = models.PositiveIntegerField(default=0, help_text="Moratorium period in months")
    date_disbursed = models.DateField(default=timezone.now)

    # New Fields
    principal_paid = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))
    interest_accrued = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))
    interest_paid = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))
    penalty_paid = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))
    member_balance_at_application = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))
    disbursement_trans = models.OneToOneField("RecPayApp.Trans", on_delete=models.SET_NULL, null=True, blank=True, related_name="disbursed_loan")

    # Approval information
    date_approved = models.DateField(default=timezone.now)
    approved_by = models.CharField(max_length=200, blank=True)
    monthly_repayment = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    next_repayment_date = models.DateField(default=timezone.now)
    expiry_date = models.DateField(null=True, blank=True, default=None)
    maturity_date = models.DateField(null=True, blank=True, default=None)

    # System fields
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)
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
    last_accrual_date = models.DateField(null=True, blank=True, default=None)

    # Overdue tracking
    repayment_overdue = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    interest_overdue = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    penalty_accrued = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    # Payment tracking
    last_payment_date = models.DateField(null=True, blank=True)
    last_interest_paid = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    last_repayment_paid = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    next_payment_date = models.DateField(null=True, blank=True)
    last_due_date = models.DateField(null=True, blank=True, default=None)
    loan_update_cnt = models.IntegerField(null=True, blank=True, default=0 )

    loan_credit_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_applied", "-id"]

    def __str__(self):
        return f"{self.loan_no} — {self.member.full_name} — ₵{self.principal}"

    @property
    def shortfall(self):
        gap = self.principal - (self.member_balance_at_application or Decimal("0.00"))
        return max(gap, Decimal("0.00"))

    @property
    def total_guaranteed(self):
        total = self.guarantors.aggregate(s=models.Sum("amount"))["s"]
        return total or Decimal("0.00")

    @property
    def total_released(self):
        total = self.guarantors.aggregate(s=models.Sum("released_amount"))["s"]
        return total or Decimal("0.00")

    @property
    def total_called(self):
        total = self.guarantors.aggregate(s=models.Sum("called_amount"))["s"]
        return total or Decimal("0.00")

    @property
    def total_holding(self):
        total = sum(g.holding for g in self.guarantors.all())
        return Decimal(str(total)) if total else Decimal("0.00")

    @property
    def monthly_interest(self):
        return (self.balance * self.interest_rate / Decimal("100")).quantize(
            Decimal("0.01")
        )

    @property
    def monthly_principal(self):
        if not self.term_months:
            return Decimal("0.00")
        return (self.principal / Decimal(self.term_months)).quantize(Decimal("0.01"))

    @property
    def is_fully_repaid(self):
        return self.balance <= 0

    def save(self, *args, **kwargs):
        if not self.loan_no:
            last = Loan.objects.order_by("-id").first()
            next_id = (last.id + 1) if last else 1
            self.loan_no = f"LN-{next_id:05d}"
        super().save(*args, **kwargs)
        
    @property
    def outstanding_balance(self):
        return Decimal("0.00")
    

    @property
    def effective_interest_rate(self):
        """Monthly rate (%) — member override → entity config → 3.00 fallback."""
        from djan_led.models import EntityConfig

        # 1. Member-specific
        if self.member and getattr(self.member, "loan_int_rate", None):
            if self.member.loan_int_rate > 0:
                return Decimal(str(self.member.loan_int_rate))

        # 2. Entity config
        try:
            cfg = EntityConfig.objects.filter(entity=self.entity).first()
            if cfg and cfg.loan_interest_rate and cfg.loan_interest_rate > 0:
                return Decimal(str(cfg.loan_interest_rate))
        except Exception:
            pass

        # 3. Fallback
        return Decimal("3.00")

    @property
    def effective_penalty_rate(self):
        """Monthly penalty rate (%) — same fallback chain."""
        from djan_led.models import EntityConfig

        try:
            cfg = EntityConfig.objects.filter(entity=self.entity).first()
            if cfg and getattr(cfg, "penalty_rate", None) and cfg.penalty_rate > 0:
                return Decimal(str(cfg.penalty_rate))
        except Exception:
            pass

        return self.penalty_rate or Decimal("2.00")

    def classify(self, today=None):
        """Rule 7 — classify loan by days past expiry."""
        today = today or timezone.now().date()

        if not self.expiry_date or today <= self.expiry_date:
            return "Current"

        days = (today - self.expiry_date).days
        if days <= 30:
            return "Current"
        elif days <= 60:
            return "OLEM"
        elif days <= 180:
            return "Substandard"
        elif days <= 365:
            return "Doubtful"
        return "Loss"

    def refresh_status(self):
        """Rule 3 & 4 — update status from balance."""
        if self.balance < 0:
            self.status = "Credit"
        elif self.balance == 0:
            self.status = "Completed"
        else:
            self.status = "Active"

    ## ===============================================Guarantor Models ==============================
class Guarantor(models.Model):
    STATUS_ACTIVE = "ACTIVE"
    STATUS_PARTIAL = "PARTIAL"
    STATUS_RELEASED = "RELEASED"
    STATUS_CALLED = "CALLED"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_PARTIAL, "Partially Released"),
        (STATUS_RELEASED, "Released"),
        (STATUS_CALLED, "Called"),
    ]
    entity = models.ForeignKey(EntityModel, on_delete=models.CASCADE, related_name="loan_gua")
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name="guarantors")
    member = models.ForeignKey(Master, on_delete=models.CASCADE, related_name="guarantees_given")
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Amount this member has pledged.", default=0.00)

    released_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))
    called_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))
    date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("loan", "member")]
        ordering = ["date", "id"]

    def __str__(self):
        return f"{self.member.full_name} → ₵{self.amount} on {self.loan.loan_no}"

    @property
    def holding(self):
        """Amount still blocked from the guarantor's available_balance."""
        val = self.amount - self.released_amount - self.called_amount
        return max(val, Decimal("0.00"))

    # -------- Save: update Member totals on create --------
    def save(self, *args, **kwargs):
        is_new = self._state.adding

        if is_new:
            # Validate guarantor has enough available_balance
            # (using current avail_bal BEFORE this guarantee is applied)
            available = self.member.available_balance or Decimal("0.00")
            if available < self.amount:
                raise ValueError(
                    f"{self.member.full_name} only has ₵{available} available, "
                    f"cannot guarantee ₵{self.amount}."
                )

        super().save(*args, **kwargs)

        if is_new:
            # Guarantor's money is held
            self.member.tot_gua_given = (
                self.member.tot_gua_given or Decimal("0.00")
            ) + self.amount
            self.member.save(update_fields=["tot_gua_given"])

            # Borrower's borrowing power grows
            self.loan.member.tot_gua_received = (
                self.loan.member.tot_gua_received or Decimal("0.00")
            ) + self.amount
            self.loan.member.save(update_fields=["tot_gua_received"])

    # -------- Release: loan is repaid, money returns --------
    def release(self, amount_to_release):
        amount_to_release = min(Decimal(str(amount_to_release)), self.holding)
        if amount_to_release <= 0:
            return Decimal("0.00")

        self.released_amount += amount_to_release
        self._refresh_status()
        self.save(update_fields=["released_amount", "status"])

        # Guarantor's money is freed
        self.member.tot_gua_given = max(
            (self.member.tot_gua_given or Decimal("0.00")) - amount_to_release,
            Decimal("0.00"),
        )
        self.member.save(update_fields=["tot_gua_given"])

        # Borrower's guarantee coverage shrinks
        self.loan.member.tot_gua_received = max(
            (self.loan.member.tot_gua_received or Decimal("0.00")) - amount_to_release,
            Decimal("0.00"),
        )
        self.loan.member.save(update_fields=["tot_gua_received"])

        return amount_to_release

    # -------- Call: loan defaulted, money is consumed --------
    def call(self, amount_to_call):
        amount_to_call = min(Decimal(str(amount_to_call)), self.holding)
        if amount_to_call <= 0:
            return Decimal("0.00")

        self.called_amount += amount_to_call
        self._refresh_status()
        self.save(update_fields=["called_amount", "status"])

        # Guarantor's money is gone (not returned)
        self.member.tot_gua_given = max(
            (self.member.tot_gua_given or Decimal("0.00")) - amount_to_call,
            Decimal("0.00"),
        )
        self.member.save(update_fields=["tot_gua_given"])

        # Borrower's coverage is also gone
        self.loan.member.tot_gua_received = max(
            (self.loan.member.tot_gua_received or Decimal("0.00")) - amount_to_call,
            Decimal("0.00"),
        )
        self.loan.member.save(update_fields=["tot_gua_received"])

        return amount_to_call

    def _refresh_status(self):
        if self.holding <= 0:
            self.status = (
                self.STATUS_CALLED if self.called_amount > 0 else self.STATUS_RELEASED
            )
        elif self.released_amount > 0 or self.called_amount > 0:
            self.status = self.STATUS_PARTIAL
        else:
            self.status = self.STATUS_ACTIVE

    ## ==============================Loan Repayment Model ==================================
class LoanRepayment(models.Model):
    """Individual loan repayment record"""
    entity = models.ForeignKey(EntityModel, on_delete=models.CASCADE, related_name="loan_rep")

    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name="repayments")
    member = models.ForeignKey(Master, on_delete=models.CASCADE, related_name='loan_repayments')

    trans = models.ForeignKey('RecPayApp.Trans', on_delete=models.SET_NULL, null=True, blank=True)  # link to transaction
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    reference = models.CharField(max_length=50, blank=True, default="")
    date = models.DateField(null=True, blank=True)
    due_interest_at_payment = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))
    principal_paid = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    interest_paid = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    penalty_paid = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))
    balance_before = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))
    balance_after = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))

    pending_releases = models.JSONField(default=list, blank=True)
    
    posted = models.BooleanField(default=False, help_text="True once a supervisor has posted the linked Trans.")
    due_interest_at_payment = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Loan.due_interest snapshot at the moment of this repayment.",
    )

    notes = models.CharField(max_length=250, blank=True, default="")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self):
        return f"{self.loan.loan_no} — ₵{self.amount} on {self.date}"

## ====================================================Guarantor Release Model =======================
class GuarantorRelease(models.Model):
    """One row per release action — traceability."""

    entity = models.ForeignKey(EntityModel, on_delete=models.CASCADE, related_name="guarantor_releases")
    repayment = models.ForeignKey(LoanRepayment, on_delete=models.CASCADE, related_name="guarantor_releases")
    guarantor = models.ForeignKey(Guarantor, on_delete=models.CASCADE, related_name="release_history")

    amount_released = models.DecimalField(max_digits=15, decimal_places=2)
    holding_before = models.DecimalField(max_digits=15, decimal_places=2)
    holding_after = models.DecimalField(max_digits=15, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Release ₵{self.amount_released} → {self.guarantor.member.full_name}"

class LoanInterestAudit(models.Model):
    """One row per monthly interest accrual event."""

    date = models.DateField(default=timezone.now)
    entity = models.ForeignKey(EntityModel, on_delete=models.CASCADE, related_name="loan_interest_audits")
    master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name="loan_interest_audits")
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name="interest_audits")

    next_repayment_date = models.DateField()
    balance_before = models.DecimalField(max_digits=15, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=6, decimal_places=4)
    months = models.IntegerField(default=1)
    interest_accrued = models.DecimalField(max_digits=15, decimal_places=2)
    balance_after = models.DecimalField(max_digits=15, decimal_places=2)
    expiry_date = models.DateField(null=True, blank=True)
    loan_class = models.CharField(max_length=20, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-id"]
        unique_together = [("loan", "next_repayment_date")]

    def __str__(self):
        return f"{self.loan.loan_no} — ₵{self.interest_accrued} on {self.date}"


class DailyLoanTable(models.Model):
    date = models.DateField(default=timezone.now, db_index=True)
    entity = models.ForeignKey(EntityModel, on_delete=models.CASCADE, related_name="loan_interest_entity")
    master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name="loan_interest_master")
    loan = models.ForeignKey("LoanApp.Loan", on_delete=models.CASCADE, related_name="daily_loan_table")

    due_interest = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    due_repayment = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    interest_part = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    repayment_part = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    outstanding_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    new_loan_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    new_due_interest = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    new_due_repayment = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-id"]
        unique_together = ("loan", "date")  # idempotency guard
        indexes = [models.Index(fields=["loan", "-date"])]

    def __str__(self):
        return f"{self.loan_id} {self.date} bal={self.new_loan_balance}"


class LoanDailyTable(models.Model):
    """
    Daily processing audit for one loan.
    Written only when loan.next_repayment_date == run date.
    Idempotent: (loan, date) unique.
    """

    date = models.DateField(default=timezone.now, db_index=True)
    entity = models.ForeignKey(
        "django_ledger.EntityModel",
        on_delete=models.CASCADE,
        related_name="loan_daily_rows",
    )
    member = models.ForeignKey(
        "MembersApp.Master",
        on_delete=models.CASCADE,
        related_name="loan_daily_rows",
    )
    loan = models.ForeignKey(
        "LoanApp.Loan",
        on_delete=models.CASCADE,
        related_name="daily_rows",
    )

    # inputs
    due_interest = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    due_repayment = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    interest_part = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    repayment_part = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    # outputs
    outstanding_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    new_loan_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    new_due_interest = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    new_due_repayment = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-id"]
        unique_together = ("loan", "date")
        indexes = [models.Index(fields=["loan", "-date"])]

    def __str__(self):
        return f"{self.loan_id} {self.date} bal={self.new_loan_balance}"
