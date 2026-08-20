from django.contrib import admin
from django.contrib.auth.models import User
from django_ledger.models import EntityModel, JournalEntryModel, TransactionModel, AccountModel, ChartOfAccountModel, LedgerModel

# ============================================================
# 1. DJANGO-LEDGER MODELS (READ-ONLY IN ADMIN)
#    These are already registered by django-ledger.
#    We only register the ones that are NOT already registered.
# ============================================================

# JournalEntryModel and TransactionModel are NOT registered by default
@admin.register(JournalEntryModel)
class JournalEntryModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'ledger', 'date', 'description', 'posted')
    list_filter = ('posted', 'date')
    search_fields = ('description', 'id')
    readonly_fields = ('id', 'created', 'updated')
    
    def date(self, obj):
        # Use the correct field name (try timestamp or created)
        return getattr(obj, 'created', None)
    date.short_description = 'Date'


@admin.register(TransactionModel)
class TransactionModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'journal_entry', 'account', 'amount', 'tx_type')
    list_filter = ('tx_type',)
    search_fields = ('journal_entry__description', 'account__name')
    readonly_fields = ('id', 'created', 'updated')


# ============================================================
# 2. ENTITYMODEL - Custom admin to avoid reverse URL issues
# ============================================================

@admin.register(EntityModel)
class EntityModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'admin', 'is_active')
    list_filter = ('is_active', 'admin')
    search_fields = ('name', 'slug')
    # IMPORTANT: No list_display_links to avoid reverse URL errors
    list_display_links = None
    readonly_fields = ('uuid', 'created', 'updated', 'path', 'depth', 'numchild')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'admin', 'parent')
        }),
        ('Status', {
            'fields': ('is_active', 'hidden')
        }),
        ('System Fields (read-only)', {
            'fields': ('uuid', 'created', 'updated', 'path', 'depth', 'numchild')
        }),
    )


# ============================================================
# 3. LEDGER MODEL - Already registered by django-ledger
#    But we keep a clean view if needed
# ============================================================

@admin.register(LedgerModel)
class LedgerModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'entity')
    list_filter = ('entity',)
    search_fields = ('name', 'slug')
    readonly_fields = ('uuid', 'created', 'updated')


# ============================================================
# 4. CHART OF ACCOUNTS
# ============================================================

@admin.register(ChartOfAccountModel)
class ChartOfAccountModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'entity', 'is_active')
    list_filter = ('entity', 'is_active')
    search_fields = ('name',)


# ============================================================
# 5. ACCOUNT MODEL
# ============================================================

@admin.register(AccountModel)
class AccountModelAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'role', 'balance_type', 'coa_model')
    list_filter = ('role', 'balance_type', 'coa_model__entity')
    search_fields = ('code', 'name')
    readonly_fields = ('uuid', 'created', 'updated')


# ============================================================
# 6. USER PROFILE (from djan_led)
# ============================================================

from djan_led.models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'default_entity')
    list_filter = ('default_entity',)
    search_fields = ('user__username', 'user__email')
    filter_horizontal = ('allowed_entities',)
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Entity Assignment', {
            'fields': ('default_entity', 'allowed_entities')
        }),
    )


# ============================================================
# 7. Keep it clean - no extra registrations
# ============================================================

# Unregister any conflicting registrations (if any)
# Django will handle duplicates gracefully