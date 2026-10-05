from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import CreditUnionConfig

from django.contrib import admin
from .models import CreditUnionConfig


@admin.register(CreditUnionConfig)
class CreditUnionConfigAdmin(admin.ModelAdmin):
    list_display = (
        "entity",
        "savings_interest_rate",
        "savings_interest_application",
        "savings_calc_type",
        "loan_interest_rate",
        "max_loan_term",
    )
    list_filter = (
        "savings_interest_application",
        "savings_calc_type",
        "entity__config__entity_type",
    )
    search_fields = ("entity__name", "entity__slug")
    # autocomplete_fields = ("entity",)          # ← removed (see error 1)

    fieldsets = (
        ("Entity", {"fields": ("entity",)}),
        (
            "Loans",
            {
                "fields": (
                    "max_loan_term",
                    "min_loan_amount",
                    "moratorium_days",
                    "loan_interest_rate",
                    "loan_asset_account_code",
                    "loan_interest_income_code",
                ),
            },
        ),
        (
            "Savings",
            {
                "fields": (
                    "min_savings_balance",
                    "savings_frequency",
                    "savings_interest_rate",
                    "savings_interest_application",
                    "savings_calc_type",
                ),
            },
        ),
        (
            "Accrual tracking",
            {
                "fields": ("last_interest_accrual_date", "last_interest_accrual_run"),
                "classes": ("collapse",),
            },
        ),
        (
            "Chart of accounts",
            {
                "fields": (
                    "interest_expense_account_code",
                    "savings_interest_payable_account_code",
                ),
            },
        ),
        (
            "Membership",
            {
                "fields": ("membership_fee", "min_shares"),
            },
        ),
    )
