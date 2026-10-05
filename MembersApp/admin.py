from django.contrib import admin

# Register your models here.
# MembersApp/admin.py
from django.contrib import admin
from .models import Master

@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'member_id', 'role', 'mem_status', 'date_enrolled']
    list_filter = ['role', 'mem_status', 'gender', 'church_member']
    search_fields = ['first_name', 'last_name', 'other_names', 'full_name', 'email_address', 'telephone1']
    readonly_fields = ['full_name', 'date_created', 'date_updated']

    fieldsets = (
        ('Personal Information', {
            'fields': ('title', 'first_name', 'last_name', 'other_names', 'full_name', 
                      'date_of_birth', 'gender', 'marital_status', 'church_member')
        }),
        ('Contact Information', {
            'fields': ('postal_address', 'residential_address', 'city', 'near_landmark',
                      'street_name', 'gps', 'telephone1', 'telephone2', 'email_address')
        }),
        ('Membership Details', {
            'fields': ('date_enrolled', 'role', 'mem_status', 'profession')
        }),
        ('Financial Information', {
            'fields': ('enroll_fees_paid', 'min_shares_purchased', 'open_balance',
                      'tot_deposits', 'tot_shares', 'tot_interest_accrued', 'tot_dividend')
        }),
        ('Audit Information', {
            'fields': ('is_deleted', 'del_date_time', 'del_user', 'date_created', 'date_updated'),
            'classes': ('collapse',)
        }),
    )

    def member_id(self, obj):
        return obj.id
    member_id.short_description = 'ID'
    member_id.admin_order_field = 'id'

from django.contrib import admin
from .models import SavingsDailyLog, SavIntApplication


@admin.register(SavingsDailyLog)
class SavingsDailyLogAdmin(admin.ModelAdmin):
    list_display = (
        "date",
        "master",
        "old_balance",
        "effective_rate",
        "daily_interest",
        "new_balance",
        "was_month_end",
    )
    list_filter = ("date", "was_month_end")
    search_fields = ("master__full_name", "master__member_no")
    date_hierarchy = "date"
    readonly_fields = [f.name for f in SavingsDailyLog._meta.fields]


@admin.register(SavIntApplication)
class SavIntApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "period_end",
        "master",
        "frequency",
        "amount",
        "days",
        "status",
        "applied_at",
    )
    list_filter = ("status", "frequency", "period_end")
    search_fields = ("master__full_name", "master__member_no")
    date_hierarchy = "period_end"
