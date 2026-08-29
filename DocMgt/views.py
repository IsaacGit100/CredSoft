from django.shortcuts import render

# Create your views here.
# Docs/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import FileResponse
from django_ledger.models import EntityModel
from .models import Document
from .forms import DocumentForm


@staff_member_required
def document_list(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)
    documents = Document.objects.filter(entity=entity, is_active=True).order_by('document_name')

    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        documents = documents.filter(
            Q(document_name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(documents, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'entity': entity,
        'documents': page_obj,
        'search_query': search_query,
        'total_documents': documents.count(),
    }
    return render(request, 'DocMgt/document_list.html', context)


@staff_member_required
def document_upload(request, slug):
    entity = get_object_or_404(EntityModel, slug=slug)

    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.entity = entity
            document.uploaded_by = request.user
            document.save()
            messages.success(request, f"Document '{document.document_name}' uploaded successfully.")
            return redirect('DocMgt:document_list', slug=entity.slug)
    else:
        form = DocumentForm()

    context = {
        'entity': entity,
        'form': form,
        'title': 'Upload Document',
    }
    return render(request, 'DocMgt/document_form.html', context)


@staff_member_required
def document_edit(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    document = get_object_or_404(Document, pk=pk, entity=entity)

    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            form.save()
            messages.success(request, f"Document '{document.document_name}' updated successfully.")
            return redirect('DocMgt:document_list', slug=entity.slug)
    else:
        form = DocumentForm(instance=document)

    context = {
        'entity': entity,
        'form': form,
        'document': document,
        'title': f'Edit Document: {document.document_name}',
    }
    return render(request, 'DocMgt/document_form.html', context)


@staff_member_required
def document_delete(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    document = get_object_or_404(Document, pk=pk, entity=entity)

    if request.method == 'POST':
        document.is_active = False
        document.save()
        messages.success(request, f"Document '{document.document_name}' deleted successfully.")
        return redirect('DocMgt:document_list', slug=entity.slug)

    context = {
        'entity': entity,
        'document': document,
    }
    return render(request, 'DocMgt/document_confirm_delete.html', context)


@staff_member_required
def document_download(request, slug, pk):
    entity = get_object_or_404(EntityModel, slug=slug)
    document = get_object_or_404(Document, pk=pk, entity=entity)

    if document.file:
        # Optionally log download activity
        return FileResponse(document.file, as_attachment=True, filename=document.file.name.split('/')[-1])
    else:
        messages.error(request, "File not found.")
        return redirect('DocMgt:document_list', slug=entity.slug)