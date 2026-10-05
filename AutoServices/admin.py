from django.db import models
from django.contrib import admin, messages
from django.utils import timezone
from .models import ServiceRun, EntityResetLog, ServiceGate

@admin.register(ServiceRun)
class ServiceRunAdmin(admin.ModelAdmin):
    list_display = (
        "run_date",
        "service_name",
        "kind",
        "status",
        "written",
        "skipped",
        "errors",
    )
    list_filter = ("kind", "status", "service_name", "run_date")
    search_fields = ("service_name",)
    date_hierarchy = "run_date"
    readonly_fields = [f.name for f in ServiceRun._meta.fields]


@admin.register(ServiceGate)
class ServiceGateAdmin(admin.ModelAdmin):
    list_display = ("run_date", "action", "decided_by", "decided_at", "run_after")
    list_filter = ("action", "run_date")
    date_hierarchy = "run_date"


@admin.register(EntityResetLog)
class EntityResetLogAdmin(admin.ModelAdmin):
    list_display = ("reset_at", "entity_name", "reset_by")
    list_filter = ("reset_at",)
    search_fields = ("entity_name", "entity_slug")
    date_hierarchy = "reset_at"
    readonly_fields = [f.name for f in EntityResetLog._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
