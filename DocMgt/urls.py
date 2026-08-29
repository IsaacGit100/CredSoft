from django.urls import path
from . import views

app_name = 'DocMgt'

urlpatterns = [
    path('<slug:slug>/documents/', views.document_list, name='document_list'),
    path('<slug:slug>/documents/upload/', views.document_upload, name='document_upload'),
    path('<slug:slug>/documents/<int:pk>/edit/', views.document_edit, name='document_edit'),
    path('<slug:slug>/documents/<int:pk>/delete/', views.document_delete, name='document_delete'),
    path('<slug:slug>/documents/<int:pk>/download/', views.document_download, name='document_download'),
]