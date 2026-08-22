from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'default_entity')
    list_filter = ('default_entity',)
    search_fields = ('user__username', 'user__email')
    filter_horizontal = ('allowed_entities',)

# djan_led/admin.py

from djan_led.models import EntityConfig
@admin.register(EntityConfig)
class EntityConfigAdmin(admin.ModelAdmin):
    list_display = [
        "entity",
        "entity_type",
        "savings_interest_rate",
        "loan_interest_rate",
    ]
    list_filter = ["entity_type"]
    search_fields = ["entity__name", "entity__slug"]
    fieldsets = (
        (None, {"fields": ("entity", "entity_type")}),
        (
            "Interest Settings",
            {
                "fields": (
                    "savings_interest_rate",
                    "savings_interest_application",
                    "loan_interest_rate",
                    "savings_calc_type",
                )
            },
        ),
        (
            "Account Codes",
            {
                "fields": (
                    "interest_expense_account_code",
                    "savings_interest_payable_account_code",
                    "loan_asset_account_code",
                    "loan_interest_income_code",
                )
            },
        ),
        (
            "Dates",
            {
                "fields": ("last_interest_accrual_date", "last_interest_accrual_run"),
                "classes": ("collapse",),
            },
        ),
    )
