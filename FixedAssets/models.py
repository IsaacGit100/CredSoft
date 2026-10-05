# FixedAssets/models.py

from decimal import Decimal

from django.db import models
from django.contrib.auth.models import User
from django_ledger.models import EntityModel, AccountModel, JournalEntryModel


class AssetCategory(models.Model):
    """E.g., Buildings, Vehicles, Computers, Furniture"""

    DEPRECIATION_METHODS = [
        ("SL", "Straight-Line"),
        ("RB", "Reducing Balance"),
    ]

    name = models.CharField(max_length=100)
    entity = models.ForeignKey(
        EntityModel,
        on_delete=models.CASCADE,
        related_name="category_assets",
        null=True,
        blank=True,
    )
    depreciation_method = models.CharField(
        max_length=20, choices=DEPRECIATION_METHODS, default="SL"
    )
    useful_life_years = models.IntegerField(help_text="Useful life in years")
    salvage_value_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00, help_text="As % of cost"
    )
    depreciation_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=20.00,
        help_text="Annual depreciation rate (%) for reducing balance method.",
    )

    # GL accounts for this category
    asset_account = models.ForeignKey(
        AccountModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="asset_categories_asset",
        help_text="GL account for asset cost",
    )
    accumulated_depreciation_account = models.ForeignKey(
        AccountModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="asset_categories_acc_dep",
        help_text="GL account for accumulated depreciation",
    )
    depreciation_expense_account = models.ForeignKey(
        AccountModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="asset_categories_dep_exp",
        help_text="GL account for depreciation expense",
    )

    class Meta:
        unique_together = ["entity", "name"]
        ordering = ["name"]

    def __str__(self):
        return self.name


class FixedAsset(models.Model):
    """Fixed Asset Register entry."""
    PAYMENT_MODE_CHOICES = [
        ("CASH", "Cash"),
        ("BANK", "Bank Transfer"),
        ("CHEQUE", "Cheque"),
        ("MOMO", "Mobile Money"),
        ("CREDIT", "Credit / Payable"),
    ]
    
    DEPRECIATION_METHODS = [
        ("straight_line", "Straight Line"),
        ("declining_balance", "Declining Balance"),
    ]

    entity = models.ForeignKey(EntityModel, on_delete=models.CASCADE, related_name="fixed_assets")
    category = models.ForeignKey(AssetCategory, on_delete=models.PROTECT, related_name="assets")

    # Identification
    asset_id = models.CharField(max_length=50)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Acquisition
    acquisition_date = models.DateField()
    cost = models.DecimalField(max_digits=15, decimal_places=2)
    salvage_value = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))

    # Depreciation
    useful_life_years = models.PositiveIntegerField(default=5)
    depreciation_method = models.CharField(max_length=20, choices=DEPRECIATION_METHODS, default="straight_line")
    override_depreciation_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Optional override rate (e.g., 20%)")

    # Status / values
    accumulated_depreciation = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))
    book_value = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))
    last_depreciation_date = models.DateField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    disposal_date = models.DateField(null=True, blank=True)

    # Link to Trans (created when registered — supervisor queue)
    trans = models.ForeignKey("RecPayApp.Trans", on_delete=models.SET_NULL, null=True, blank=True, related_name="fixed_assets")
    last_dep_trans = models.ForeignKey(
        "RecPayApp.Trans",
        on_delete=models.SET_NULL, null=True, blank=True, related_name="depreciated_asset",
        help_text="The most recent depreciation Trans linked to this asset.",
    )

    payment_mode = models.CharField(max_length=10, choices=PAYMENT_MODE_CHOICES, blank=True, default="")
    bank_name = models.CharField(max_length=100, blank=True, default="")
    bank_branch = models.CharField(max_length=100, blank=True, default="")
    bank_account_no = models.CharField(max_length=50, blank=True, default="")
    cheque_no = models.CharField(max_length=50, blank=True, default="")

    seller_name = models.CharField(max_length=200, blank=True, default="")
    seller_contact = models.CharField(max_length=50, blank=True, default="")
    seller_address = models.TextField(blank=True, default="")

    # Audit
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["asset_id"]
        unique_together = [("entity", "asset_id")]

    def __str__(self):
        return f"{self.asset_id} - {self.name}"

    @property
    def net_book_value(self):
        """Convenience alias for book_value."""
        return self.book_value

    def save(self, *args, **kwargs):
        # Ensure book_value is always derived from cost - accumulated_depreciation
        self.book_value = (self.cost or Decimal("0.00")) - (
            self.accumulated_depreciation or Decimal("0.00")
        )
        super().save(*args, **kwargs)


class DepreciationEntry(models.Model):
    """Records depreciation posted for a period."""

    entity = models.ForeignKey(EntityModel, on_delete=models.CASCADE, related_name="depreciation", null=True, blank=True)
    asset = models.ForeignKey(FixedAsset, on_delete=models.CASCADE, related_name="depreciation_entries")
    trans = models.ForeignKey("RecPayApp.Trans", on_delete=models.SET_NULL, null=True, blank=True, related_name="depreciation_entries")
    period_start = models.DateField()
    period_end = models.DateField()
    amount = models.DecimalField(max_digits=15, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    journal_entry = models.ForeignKey(JournalEntryModel, on_delete=models.SET_NULL, null=True, blank=True, related_name="depreciation_entries")

    class Meta:
        ordering = ["-period_end"]

    def __str__(self):
        return f"{self.asset.asset_id} – {self.period_end} – ₵{self.amount}"
