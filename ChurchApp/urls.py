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
    #
    path('<slug:slug>/clergy/', views.clergy_list_manage, name='clergy_list_manage'),
    path('<slug:slug>/clergy/add/', views.clergy_create, name='clergy_create'),
    path('<slug:slug>/clergy/<int:pk>/edit/', views.clergy_update, name='clergy_update'),
    path('<slug:slug>/clergy/<int:pk>/delete/', views.clergy_delete, name='clergy_delete'),
    path('<slug:slug>/clergy/<int:pk>/', views.clergy_detail, name='clergy_detail'),
    #
    path('entity/<slug:slug>/church_home/', views.church_home, name='church_home'),
    path('entity/<slug:slug>/service/create/', views.service_create, name='service_create'),
    path('entity/<slug:slug>/service/list/', views.service_list, name='service_list'),
    path('entity/<slug:slug>/service/<int:pk>/post/', views.service_post_to_ledger, name='service_post_to_ledger'),
    # Add detail, edit, delete as needed
    
    path('<slug:slug>/ushers/', views.usher_list_manage, name='usher_list_manage'),
    path('<slug:slug>/ushers/add/', views.usher_create, name='usher_create'),
    path('<slug:slug>/ushers/<int:pk>/edit/', views.usher_update, name='usher_update'),
    path('<slug:slug>/ushers/<int:pk>/delete/', views.usher_delete, name='usher_delete'),
    path('<slug:slug>/ushers/<int:pk>/', views.usher_detail, name='usher_detail'),
    
    path('<slug:slug>/guilds/', views.guild_list_manage, name='guild_list_manage'),
    path('<slug:slug>/guilds/add/', views.guild_create, name='guild_create'),
    path('<slug:slug>/guilds/<int:pk>/edit/', views.guild_update, name='guild_update'),
    path('<slug:slug>/guilds/<int:pk>/delete/', views.guild_delete, name='guild_delete'),
    path('<slug:slug>/guilds/<int:pk>/', views.guild_detail, name='guild_detail'),
    
    path('<slug:slug>/officiants/', views.officiant_list_manage, name='officiant_list_manage'),
    path('<slug:slug>/officiants/add/', views.officiant_create, name='officiant_create'),
    path('<slug:slug>/officiants/<int:pk>/edit/', views.officiant_update, name='officiant_update'),
    path('<slug:slug>/officiants/<int:pk>/delete/', views.officiant_delete, name='officiant_delete'),
    path('<slug:slug>/officiants/<int:pk>/', views.officiant_detail, name='officiant_detail'),
    
     path('<slug:slug>/services/', views.service_list, name='service_list'),
    path('<slug:slug>/services/add/', views.service_create, name='service_create'),
    path('<slug:slug>/services/<int:pk>/edit/', views.service_update, name='service_update'),
    path('<slug:slug>/services/<int:pk>/delete/', views.service_delete, name='service_delete'),
    path('<slug:slug>/services/<int:pk>/', views.service_detail, name='service_detail'),
    
    
]

   

