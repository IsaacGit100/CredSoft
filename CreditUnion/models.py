from django.db import models
from django_ledger.models import EntityModel, AccountModel

class CreditUnionConfig(models.Model):
    SAV_INT_APPL = [
        ("DAILY", "Daily"),
        ("MONTHLY", "Monthly"),
        ("QUARTERLY", "Quarterly"),
        ("YEARLY", "Yearly"),
    ]

    entity = models.OneToOneField(
        EntityModel, on_delete=models.CASCADE, related_name="cu_config"
    )

    # --- loans ---
    max_loan_term = models.PositiveIntegerField(default=36)  # months
    min_loan_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    moratorium_days = models.PositiveIntegerField(default=0)
    loan_interest_rate = models.DecimalField(
        max_digits=8, decimal_places=4, default=0, help_text="Annual interest rate (%)"
    )
    loan_asset_account_code = models.CharField(max_length=20, default="1080")
    loan_interest_income_code = models.CharField(max_length=20, default="4010")

    # --- savings ---
    min_savings_balance = models.DecimalField(
        max_digits=15, decimal_places=2, default=0
    )
    savings_frequency = models.CharField(max_length=20, default="monthly")
    savings_interest_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0
    )
    savings_interest_application = models.CharField(
        max_length=10, choices=SAV_INT_APPL, default="MONTHLY"
    )
    savings_calc_type = models.CharField(
        max_length=30,
        choices=[
            ("Simple_Sav_Interest", "Simple"),
            ("Compound_Sav_Interest", "Compound"),
        ],
        default="Simple_Sav_Interest",
    )
    sav_int_appl = models.CharField(
        max_length=20, blank=True, null=True, choices=SAV_INT_APPL, default=""
    )  # legacy alias

    # --- accrual tracking ---
    last_interest_accrual_date = models.DateField(null=True, blank=True)
    last_interest_accrual_run = models.DateTimeField(null=True, blank=True)

    # --- chart of accounts ---
    interest_expense_account_code = models.CharField(max_length=20, default="5020")
    savings_interest_payable_account_code = models.CharField(
        max_length=20, default="2020"
    )

    # --- membership ---
    membership_fee = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    min_shares = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.entity.name} CU config"
