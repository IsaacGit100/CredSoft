from django.contrib import admin
from django.urls import path, include
from . import views
from django_ledger.models import EntityModel, LedgerModel, JournalEntryModel, AccountModel,  TransactionModel

app_name = 'ChurchApp'

urlpatterns = [
    path('entity/<slug:slug>/dashboard/', views.church_dashboard, name='church_dashboard'),
    path('entity/<slug:slug>/members/', views.member_list_manage, name='member_list_manage'),
    path('entity/<slug:slug>/members/create/', views.member_create, name='member_create'),
    path('entity/<slug:slug>/members/<int:pk>/edit/', views.member_edit, name='member_edit'),
    #path('entity/<slug:slug>/members/<int:pk>/delete/', views.member_delete, name='member_delete'),
    path('entity/<slug:slug>/members/<int:pk>/delete/', views.member_delete, name='member_delete'),
    path('entity/<slug:slug>/members/<int:pk>/restore/', views.member_restore, name='member_restore'),  
     path('<slug:slug>/members/<int:pk>/', views.member_detail, name='member_detail'),
    #
    path('entity/<slug:slug>/clergy/list/manage', views.clergy_list_manage, name='clergy_list_manage'),
    
    path('entity/<slug:slug>/clergy/modal/list/', views.clergy_list_modal, name='clergy_list_modal'),
    path('entity/<slug:slug>/clergy/modal/delete/', views.clergy_delete_modal, name='clergy_delete_modal'),
    path('entity/<slug:slug>/clergy/modal/edit/', views.clergy_edit_modal, name='clergy_edit_modal'),
    
    path('entity/<slug:slug>/clergy/create/', views.clergy_create, name='clergy_create'),
    path('entity/<slug:slug>/clergy/<int:pk>/edit/', views.clergy_edit, name='clergy_edit'),
    path('entity/<slug:slug>/clergy/<int:pk>/delete/', views.clergy_delete, name='clergy_delete'),
    path('entity/<slug:slug>/clergy/<int:pk>/', views.clergy_detail, name='clergy_detail'),
    #
    path('entity/<slug:slug>/church_home/', views.church_home, name='church_home'),
    path('entity/<slug:slug>/service/create/', views.service_create, name='service_create'),
    path('entity/<slug:slug>/service/list/', views.service_list_manage, name='service_list_manage'),
    path('entity/<slug:slug>/service/<int:pk>/post/', views.service_post_to_ledger, name='service_post_to_ledger'),
    # Add detail, edit, delete as needed
    
    
     
    path('entity/<slug:slug>/church/data/entry/home/', views.church_data_entry_home, name='church_data_entry_home'),
    
    path('<slug:slug>/roles/', views.role_management, name='role_management'),
    path('<slug:slug>/roles/create/', views.role_create, name='role_create'),
    path('<slug:slug>/roles/member/<int:pk>/edit/', views.member_roles_edit, name='member_roles_edit'),
    path('<slug:slug>/roles/member/<int:pk>/', views.member_roles_detail, name='member_roles_detail'),
    
    # ChurchApp/urls.py


    # Service CRUD
    path('<slug:slug>/services/', views.service_list_manage, name='service_list_manage'),
    path('<slug:slug>/services/add/', views.service_create, name='service_create'),
    path('<slug:slug>/services/<int:pk>/edit/', views.service_update, name='service_update'),
    path('<slug:slug>/services/<int:pk>/delete/', views.service_delete, name='service_delete'),
    path('<slug:slug>/services/<int:pk>/', views.service_detail, name='service_detail'),
]


   

