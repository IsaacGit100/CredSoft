# Docs/forms.py

from django import forms
from .models import Document


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["document_name", "file", "description"]
        widgets = {
            "document_name": forms.TextInput(attrs={"class": "form-control"}),
            "file": forms.FileInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
        labels = {
            "document_name": "Document Name",
            "file": "Select File",
            "description": "Description (optional)",
        }

    def clean_file(self):
        file = self.cleaned_data.get("file")
        if file:
            # Optional: limit file size (e.g., 20MB)
            if file.size > 20 * 1024 * 1024:
                raise forms.ValidationError("File size must be under 20MB.")
        return file
