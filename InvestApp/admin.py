
# Register your models here.
from django.contrib import admin
from .models import Investment, Bank


@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = ['certificate_no', 'date', 'get_bank_company_display', 'amount', 'rate', 'interest_expected', 'interest_earned']
    list_filter = ['date', 'investment_type', 'rollover']
    search_fields = ['certificate_no', 'account_no', 'bank__name', 'other_company']


@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ['name', 'branch', 'sort_code', 'bic_code']
    search_fields = ['name', 'branch']
