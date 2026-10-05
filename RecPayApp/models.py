# RecPayApp/models.py

from decimal import Decimal
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
from django_ledger.models import EntityModel

User = get_user_model()


class Trans(models.Model):
    """
    Universal transaction staging table.
    Every module creates a Trans record; the supervisor posts them to the journal.
    """

    MODULE_CHOICES = (
        ("church", "Church"),
        ("school", "School"),
        ("credit_union", "Credit Union"),
        ("pos", "POS"),
        ("fixed_assets", "Fixed Assets"),
        ("open_balance", "Opening Balance"),
        ("finance", "Finance"),
        ("other", "Other"),
    )

    SUB_MODULE_CHOICES = (
        ("dues_tithe", "Dues / Tithes"),
        ("service", "Church Service"),
        ("general_receipt", "General Receipt"),
        ("general_payment", "General Payment"),
        ("opening_balance", "Opening Balance"),
        ("fixed_asset", "Fixed Asset Acquisition"),
        ("depreciation", "Depreciation"),
        ("loan", "Loan"),
        ("other", "Other"),
    )

    TRANS_TYPE = (
        ("Receipts", "Receipts"),
        ("Payments", "Payments"),
        ("Journal", "Journal Entry"),
    )

    PAY_MODE = (
        ("Cash", "Cash"),
        ("Cheque", "Cheque"),
        ("Transfer", "Transfer"),
        ("Momo", "Mobile Money"),
        ("None", "Non-Cash"),
    )

    STATUS_CHOICES = (
        ("DRAFT", "Draft"),
        ("POSTED", "Posted"),
        ("VOID", "Void"),
    )

    JOURNAL_STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("POSTED", "Posted"),
        ("REJECTED", "Rejected"),
    )

    # Core identification
    entity = models.ForeignKey(
        EntityModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
    )
    module = models.CharField(max_length=20, choices=MODULE_CHOICES, default="church")
    sub_module = models.CharField(
        max_length=25,
        choices=SUB_MODULE_CHOICES,
        default="other",
        help_text="Which sub-module created this transaction.",
    )
    trans_type = models.CharField(max_length=10, choices=TRANS_TYPE)
    date = models.DateField()
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    pay_mode = models.CharField(max_length=10, choices=PAY_MODE, default="Cash")

    # Voucher fields
    rec_vou_no = models.CharField(max_length=50, null=True, blank=True, default="")
    trans_no = models.CharField(max_length=50, null=True, blank=True, default="")
    voucher_sequence = models.PositiveIntegerField(default=0)
    old_trans_id = models.IntegerField(default=0)

    # Party
    member = models.ForeignKey(
        "MembersApp.Master",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
    )
    member_no = models.IntegerField(null=True, blank=True, default=0)
    member_name = models.CharField(max_length=80, null=True, blank=True, default="")

    church_member = models.ForeignKey(
        "ChurchApp.Member",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
    )
    non_member_name = models.CharField(max_length=80, null=True, blank=True, default="")
    non_member_contact = models.CharField(
        max_length=50, null=True, blank=True, default=""
    )

    # Bank / Cheque
    bank_date = models.DateField(null=True, blank=True)
    bank = models.CharField(max_length=100, blank=True, default="")
    bank_no = models.CharField(max_length=50, blank=True, default="")
    bank_branch = models.CharField(max_length=100, blank=True, default="")
    cheque_date = models.DateField(null=True, blank=True)
    cheque_no = models.CharField(max_length=32, blank=True, default="")

    # Mobile Money
    momo_no = models.CharField(max_length=50, blank=True, default="")
    momo_name = models.CharField(max_length=100, blank=True, default="")

    # Ledger for Receipts/Payments
    ledger_id = models.CharField(max_length=70, blank=True, null=True, default="")
    ledger_code = models.CharField(max_length=32, blank=True, null=True, default="")
    ledger_name = models.CharField(max_length=100, blank=True, null=True, default="")

    # Ledger for Journal entries
    debit_account_code = models.CharField(max_length=32, blank=True, default="")
    debit_account_name = models.CharField(max_length=100, blank=True, default="")
    credit_account_code = models.CharField(max_length=32, blank=True, default="")
    credit_account_name = models.CharField(max_length=100, blank=True, default="")

    # Other details
    purpose = models.CharField(max_length=60, blank=True, null=True, default="")
    other_purpose = models.CharField(max_length=60, blank=True, null=True, default="")
    details = models.CharField(max_length=150, blank=True, null=True, default="")

    # Loan
    loan = models.ForeignKey(
        "LoanApp.Loan",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
    )
    loan_name = models.CharField(max_length=50, blank=True, null=True, default="")

    # Generic source link
    source_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    source_object_id = models.PositiveIntegerField(null=True, blank=True)
    source = GenericForeignKey("source_content_type", "source_object_id")

    # Status
    batch_number = models.CharField(max_length=64, blank=True, null=True, default="")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="DRAFT")
    journal_status = models.CharField(
        max_length=10,
        choices=JOURNAL_STATUS_CHOICES,
        default="PENDING",
    )
    journal_entry_id = models.CharField(
        max_length=50, blank=True, null=True, default=""
    )
    posted_at = models.DateTimeField(null=True, blank=True)

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="trans_created",
    )
    created_by_name = models.CharField(max_length=80, null=True, blank=True, default="")
    created_by_username = models.CharField(
        max_length=80, null=True, blank=True, default=""
    )

    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="trans_updated",
    )

    class Meta:
        ordering = ["-date", "-created_at"]
        indexes = [
            models.Index(fields=["rec_vou_no"]),
            models.Index(fields=["date"]),
            models.Index(fields=["trans_type"]),
            models.Index(fields=["journal_status"]),
            models.Index(fields=["module"]),
            models.Index(fields=["sub_module"]),
            models.Index(fields=["entity"]),
        ]

    def __str__(self):
        who = self.member_name or self.non_member_name or "-"
        return f"{self.rec_vou_no} - {who} - {self.amount}"

    @property
    def can_edit(self):
        return self.journal_status == "PENDING"

    @property
    def can_delete(self):
        return self.journal_status in ("PENDING", "REJECTED")

    def lock_reason(self):
        return {
            "APPROVED": "Approved - awaiting posting.",
            "POSTED": "Posted to the journal.",
            "REJECTED": "Rejected.",
        }.get(self.journal_status, "")

    @property
    def receipts(self):
        return self.amount if self.trans_type == "Receipts" else Decimal("0.00")

    @property
    def payments(self):
        return self.amount if self.trans_type == "Payments" else Decimal("0.00")

    _MODULE_CODE = {
        "dues_tithe": "DUE",
        "service": "SRV",
        "general_receipt": "GEN",
        "general_payment": "GEN",
        "opening_balance": "OB",
        "fixed_asset": "FAA",
        "depreciation": "DEP",
        "loan": "LON",
        "other": "JRN",
    }

    def _class_letter(self):
        if self.trans_type == "Receipts":
            return "R"
        if self.trans_type == "Payments":
            return "P"
        if self.sub_module == "depreciation":
            return "D"
        if self.sub_module == "fixed_asset":
            return "D"
        if self.sub_module == "opening_balance":
            return "D" if self.debit_account_code else "C"
        return "J"

    def _module_code(self):
        code = self._MODULE_CODE.get(self.sub_module, "JRN")
        if self.sub_module == "opening_balance":
            return "OBA" if self._class_letter() == "D" else "OBL"
        return code

    def _voucher_prefix(self):
        return f"{self._class_letter()}-{self._module_code()}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        if is_new:
            # First save: INSERT, MySQL assigns the PK
            super().save(*args, **kwargs)

            # Compute per-entity sequence
            if not self.voucher_sequence:
                self.voucher_sequence = (
                    Trans.objects.filter(entity_id=self.entity_id)
                    .exclude(pk=self.pk)
                    .count()
                    + 1
                )

            # Build the voucher number
            if not self.rec_vou_no:
                prefix = self._voucher_prefix()
                self.rec_vou_no = f"{prefix}-{self.voucher_sequence:06d}-{self.pk:08d}"
                self.trans_no = self.rec_vou_no

            # Fill in member name if not set
            if self.member and not self.member_name:
                self.member_name = self.member.full_name
                self.member_no = self.member.id
            elif self.church_member and not self.member_name:
                self.member_name = self.church_member.full_name
                self.member_no = 0

            if self.loan and not self.loan_name:
                self.loan_name = str(self.loan)

            # Remove force_insert so the second save is an UPDATE
            kwargs.pop("force_insert", None)
            kwargs.pop("force_update", None)

            # Second save: UPDATE the row with the computed fields
            super().save(*args, **kwargs)
            return

        # Regular update of an existing row
        if not self.trans_no:
            self.trans_no = self.rec_vou_no

        if self.member and not self.member_name:
            self.member_name = self.member.full_name
            self.member_no = self.member.id
        elif self.church_member and not self.member_name:
            self.member_name = self.church_member.full_name
            self.member_no = 0

        if self.loan and not self.loan_name:
            self.loan_name = str(self.loan)

        super().save(*args, **kwargs)
