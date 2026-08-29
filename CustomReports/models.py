from django.db import models

# Create your models here.
from django.db import models
import json

class SavedReport(models.Model):
    """Save custom report configurations for reuse"""
    name = models.CharField(max_length=100, verbose_name="Report Name")
    table_name = models.CharField(max_length=50, verbose_name="Table Name")
    selected_fields = models.TextField(verbose_name="Selected Fields")  # Store as JSON
    filters = models.TextField(blank=True, null=True, verbose_name="Filters")
    created_by = models.CharField(max_length=100, blank=True, verbose_name="Created By")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")
    
    class Meta:
        verbose_name = "Saved Report"
        verbose_name_plural = "Saved Reports"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_selected_fields_list(self):
        """Return selected fields as Python list"""
        try:
            return json.loads(self.selected_fields)
        except:
            return []