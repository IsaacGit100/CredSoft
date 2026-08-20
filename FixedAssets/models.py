from django.db import models

# Create your models here.
# FixedAssets/models.py
from django.db import models
from decimal import Decimal
from django.utils import timezone
from django_ledger.models import EntityModel, AccountModel, JournalEntryModel
from django.contrib.auth.models import User

class AssetCategory(models.Model):
    """E.g., Buildings, Vehicles, Computers, Furniture"""
    name = models.CharField(max_length=100)
    entity = models.ForeignKey(EntityModel, on_delete=models.CASCADE, related_name='category_assets', null=True, blank=True)
    depreciation_method = models.CharField(max_length=20, choices=[('SL', 'Straight-Line'), ('RB', 'Reducing Balance'),], default='SL')
    useful_life_years = models.IntegerField(help_text="Useful life in years")
    salvage_value_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="As % of cost")
    # The GL accounts for this category
    depreciation_rate = models.DecimalField(max_digits=5, decimal_places=2, default=20.00,
        help_text="Annual depreciation rate (%) for reducing balance method. Not used for straight‑line."
    )
    
    asset_account = models.ForeignKey(
        AccountModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='asset_categories_asset',
        help_text="GL account for asset cost"
    )
    accumulated_depreciation_account = models.ForeignKey(
        AccountModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='asset_categories_acc_dep',
        help_text="GL account for accumulated depreciation"
    )
    depreciation_expense_account = models.ForeignKey(
        AccountModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='asset_categories_dep_exp',
        help_text="GL account for depreciation expense"
    )
    
       
    def __str__(self):
        return self.name 


from django.db import models
from django_ledger.models import EntityModel

class FixedAsset(models.Model):
    entity = models.ForeignKey(
        EntityModel,
        on_delete=models.CASCADE,
        related_name='fixed_assets',
        null=True,
        blank=True
    )
    category = models.ForeignKey(AssetCategory, on_delete=models.CASCADE)
    asset_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    purchase_date = models.DateField()
    cost = models.DecimalField(max_digits=15, decimal_places=2)
    salvage_value = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    override_depreciation_rate = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text="Optional override rate (e.g., 20%)"
    )
    is_active = models.BooleanField(default=True)
    acquisition_date = models.DateField()
    disposal_date = models.DateField(null=True, blank=True)
    depreciation_method = models.CharField(
        max_length=20,
        choices=[
            ("straight_line", "Straight Line"),
            ("declining_balance", "Declining Balance"),
        ],
        default="straight_line",
    )
    useful_life_years = models.PositiveIntegerField(default=5)
    categoryaccount = models.CharField(max_length=20, null=True, blank=True, default=None)
    
    book_value = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    last_depreciation_date = models.DateField(null=True, blank=True, default=None)
    
    accumulated_depreciation = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, default=Decimal('0.00'))
    book_value = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))

    
    # ... other fields you have

    def __str__(self):
        return f"{self.asset_id} - {self.name}"
    
        
    @property
    def total_depreciation(self):
        if self.pk is None:
            return Decimal('0.00')
        return self.depreciation_entries.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    
    

    # class FixedAsset(models.Model):
    #    category = models.ForeignKey(AssetCategory, on_delete=models.CASCADE)
    #    name = models.CharField(max_length=200)
    #    description = models.TextField(blank=True)
    #    purchase_date = models.DateField()
    #    cost = models.DecimalField(max_digits=15, decimal_places=2)
    #    salvage_value = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    # Depreciation rate (if overriding category)
    #    override_depreciation_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Optional override rate (e.g., 20%)")
    #    is_active = models.BooleanField(default=True)
    #    acquisition_date = models.DateField()
    #    disposal_date = models.DateField(null=True, blank=True)

    @property
    def net_book_value(self):
        return self.cost - self.accumulated_depreciation


class DepreciationEntry(models.Model):
    """Records depreciation posted for a period"""
    entity = models.ForeignKey(
        EntityModel,
        on_delete=models.CASCADE,
        related_name='depreciation',
        null=True,
        blank=True
    )
    asset = models.ForeignKey(FixedAsset, on_delete=models.CASCADE, related_name='depreciation_entries')
    period_start = models.DateField()
    period_end = models.DateField()
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True) 
     
    journal_entry = models.ForeignKey(
        JournalEntryModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="depreciation_entries",
    )
