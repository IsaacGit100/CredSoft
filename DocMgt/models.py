from django.db import models

# Create your models here.
# Docs/models.py

from django.db import models
from django.contrib.auth import get_user_model
from django_ledger.models import EntityModel
from django.utils import timezone

User = get_user_model()


class Document(models.Model):
    """Document model for file management."""

    # Relationships
    entity = models.ForeignKey(EntityModel, on_delete=models.CASCADE, related_name='documents')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_documents')

    # Core fields
    document_name = models.CharField(max_length=200, help_text="Display name for the document")
    file = models.FileField(upload_to='documents/%Y/%m/%d/')
    description = models.TextField(blank=True, help_text="Optional description")
    file_size = models.PositiveIntegerField(editable=False, default=0, help_text="File size in bytes")

    # Metadata
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['document_name']
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'

    def __str__(self):
        return self.document_name

    def save(self, *args, **kwargs):
        # Calculate file size if file is present
        if self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)