from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django_ledger.models import EntityModel

from django.db import models
from django.contrib.auth.models import User
from django_ledger.models import EntityModel

class UserProfile(models.Model):
    USER_ROLES = (
        ("user", "User"),
        ("super_admin", "Super Admin"),
        ("technical", "Technical"),
        ("pos", "pos"),
        ("school", "school"),
        ("CreditUnion", "CreditUnion"),
        ("Church", "Church"),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='djan_led_profile')
    default_entity = models.ForeignKey(EntityModel, on_delete=models.SET_NULL, null=True, blank=True, related_name='default_users')
    allowed_entities = models.ManyToManyField(EntityModel, blank=True, related_name='allowed_users')
    role = models.CharField(max_length=20, choices=USER_ROLES, default='user')
    account_preferences = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='djan_led_profile')
    default_entity = models.ForeignKey(EntityModel, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='default_users',
        help_text="The entity this user is assigned to by default."
    )
    allowed_entities = models.ManyToManyField(
        EntityModel,
        blank=True,
        related_name='allowed_users',
        help_text="All entities this user can access."
    )

    def __str__(self):
        return f"{self.user.username} → {self.default_entity.name if self.default_entity else 'No entity'}"

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

# Auto-create profile when a user is created
from django.db.models.signals import post_save

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)


# djan_led/models.py
class EntityConfig(models.Model):
    SAV_INT_APPL = (
        ('DAILY', 'DAILY'),
        ('MONTHLY', 'MONTHLY'),
        ('QUARTERLY', 'QUARTERLY'),
        ('YEAR', 'YEARLY')
    )
    ENTITY_TYPE_CHOICES = [
        ('church', 'Church'),
        ('school', 'School'),
        ('credit_union', 'Credit Union'),
        ('pos', 'POS'),
        ('hospital', 'Hospital'),
        ('hotel', 'Hotel'),
        ('business', 'Business'),
        ('ngo', 'NGO'),
        ('other', 'Other'),
    ]

    entity = models.OneToOneField(EntityModel, on_delete=models.CASCADE, related_name="config")
    entity_type = models.CharField(max_length=20, choices=ENTITY_TYPE_CHOICES, default='church',
        blank=True,
        help_text="Select the type of entity"
    )
    # Loan settings
    loan_interest_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.0
    )
    max_loan_term = models.PositiveIntegerField(default=36)  # months
    min_loan_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)
    moratorium_days = models.PositiveIntegerField(default=0)

    # Savings settings
    savings_interest_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.0
    )
    min_savings_balance = models.DecimalField(
        max_digits=15, decimal_places=2, default=0.0
    )
    savings_frequency = models.CharField(max_length=20, default="monthly")
    sav_int_appl = models.CharField(max_length=20, null=True, blank=True, choices=SAV_INT_APPL, default='' )
    # Membership
    membership_fee = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)
    min_shares = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)

    # Reporting preferences
    currency = models.CharField(max_length=3, default="GHS")
    fiscal_year_start = models.DateField(null=True, blank=True)

    # Tax rules
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    tax_method = models.CharField(max_length=20, null=True, blank=True, default="standard")

    # In EntityConfig
    savings_interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    savings_interest_application = models.CharField(
        max_length=10,
        choices=[
            ("DAILY", "Daily"),
            ("MONTHLY", "Monthly"),
            ("QUARTERLY", "Quarterly"),
            ("YEARLY", "Yearly"),
        ],
        default="MONTHLY",
    )
    savings_calc_type = models.CharField(
        max_length=30,
        choices=[("Simple_Sav_Interest", "Simple"), ("Compound_Sav_Interest", "Compound")],
        default="Simple_Sav_Interest",
    )
    last_interest_accrual_date = models.DateField(null=True, blank=True)
    last_interest_accrual_run = models.DateTimeField(null=True, blank=True)

    interest_expense_account_code = models.CharField(max_length=20, default="5020")
    savings_interest_payable_account_code = models.CharField(max_length=20, default="2020")
    
    loan_interest_rate = models.DecimalField(max_digits=8, decimal_places=4, default=0, help_text="Annual interest rate (%)")
    loan_asset_account_code = models.CharField(max_length=20, default='1080')
    loan_interest_income_code = models.CharField(max_length=20, default='4010')

## ======================== Journal Entries =======================================
class ManualJournalEntry(models.Model):
    entity = models.ForeignKey(
        EntityModel, on_delete=models.CASCADE, related_name="manual_journal_entries"
    )
    date = models.DateField()
    description = models.CharField(max_length=200)
    debit_account_code = models.CharField(max_length=20)
    credit_account_code = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    journal_status = models.CharField(
        max_length=10,
        choices=[("PENDING", "Pending"), ("POSTED", "Posted")],
        default="PENDING",
    )
    journal_entry_id = models.CharField(
        max_length=50, null=True, blank=True
    )  # UUID of posted entry

    def __str__(self):
        return f"{self.date} - {self.description} ({self.amount})"
