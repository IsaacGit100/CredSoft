from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import SavedReport

@admin.register(SavedReport)
class SavedReportAdmin(admin.ModelAdmin):
    list_display = ['name', 'table_name', 'created_by', 'created_at']
    list_filter = ['table_name', 'created_at']
    search_fields = ['name', 'created_by']