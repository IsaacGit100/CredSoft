from django.contrib import admin
from django.urls import path, include
from . import views
from django_ledger.models import EntityModel, LedgerModel, JournalEntryModel, AccountModel,  TransactionModel

app_name = 'ChurchApp'

urlpatterns = [
    
    
    path('entity/<slug:slug>/supervisor/church/', views.supervisor_church, name='supervisor_church'),
    path('entity/<slug:slug>/church_home/', views.church_home, name='church_home'), 
    path('entity/<slug:slug>/dashboard/', views.church_dashboard, name='church_dashboard'),
    
    path('entity/<slug:slug>/church/data/entry/home/', views.church_data_entry_home, name='church_data_entry_home'),
#
    path('entity/<slug:slug>/members/', views.member_list_manage, name='member_list_manage'),
    path('entity/<slug:slug>/members/create/', views.member_create, name='member_create'),
    
    path('entity/<slug:slug>/members/detail/<int:pk>/', views.member_detail, name='member_detail'),
    path('entity/<slug:slug>/members/<int:pk>/edit/', views.member_edit, name='member_edit'),
    path('entity/<slug:slug>/members/<int:pk>/delete/', views.member_delete, name='member_delete'),
    path('entity/<slug:slug>/members/<int:pk>/restore/', views.member_restore, name='member_restore'),
    path('entity/<slug:slug>/members/<int:pk>/pdf/', views.member_pdf, name='member_pdf'),
    path('entity/<slug:slug>/members/<int:pk>/excel/', views.member_excel, name='member_excel'),
    
    #
    path('entity/<slug:slug>/clergy/list/manage', views.clergy_list_manage, name='clergy_list_manage'),
    path('entity/<slug:slug>/clergy/modal/list/', views.clergy_list_modal, name='clergy_list_modal'),
    path('entity/<slug:slug>/clergy/modal/delete/', views.clergy_delete_modal, name='clergy_delete_modal'),
    path('entity/<slug:slug>/clergy/modal/edit/', views.clergy_edit_modal, name='clergy_edit_modal'),
    #
    path('entity/<slug:slug>/clergy/create/', views.clergy_create, name='clergy_create'),
    path('entity/<slug:slug>/clergy/<int:pk>/edit/', views.clergy_edit, name='clergy_edit'),
    path('entity/<slug:slug>/clergy/<int:pk>/delete/', views.clergy_delete, name='clergy_delete'),
    path('entity/<slug:slug>/clergy/<int:pk>/', views.clergy_detail, name='clergy_detail'),
    #
    path('entity/<slug:slug>/service/home/', views.service_home, name='service_home'),
    path('entity/<slug:slug>/service/create/', views.service_create, name='service_create'),
    path('entity/<slug:slug>/service/list/', views.service_list_manage, name='service_list_manage'),
    path('entity/<slug:slug>/service/pdf/', views.service_pdf, name='service_pdf'),
    
    path('entity/<slug:slug>/service/<int:service_id>/delete/', views.service_delete, name='service_delete'),
   
    path('entity/<slug:slug>/service/excel/', views.service_excel, name='service_excel'),
    
    path('entity/<slug:slug>/service/<int:service_id>/edit/', views.service_activity_edit, name="service_activity_edit"),
    path('entity/<slug:slug>/service/<int:service_id>/view/', views.service_activity_view, name="service_activity_view"),
    path('entity/<slug:slug>/service/<int:service_id>/pdf/', views.service_activity_pdf, name="service_activity_pdf"),
    path('entity/<slug:slug>/service/<int:service_id>/excel/', views.service_activity_excel, name="service_activity_excel"), 
    path('entity/<slug:slug>/service/<int:service_id>/post-to-trans/', views.service_post_to_trans, name="service_post_to_trans"),
    path('entity/<slug:slug>/service/<int:service_id>/post-success/', views.service_post_success, name='service_post_success'),
    
    
    path('<slug:slug>/services/report/', views.service_list_report, name='service_list_report'),
    path('<slug:slug>/services/report/pdf/', views.service_list_report_pdf, name='service_list_report_pdf'),
    path('<slug:slug>/services/report/excel/', views.service_list_report_excel, name='service_list_report_excel'),
        

    path('entity/<slug:slug>/service/<int:service_id>/post/', views.service_post_to_ledger, name='service_post_to_ledger'),
    # Add detail, edit, delete as needed
      
    path('<slug:slug>/roles/', views.role_management, name='role_management'),
    path('<slug:slug>/roles/create/', views.role_create, name='role_create'),
    path("entity/<slug:slug>/role/<int:pk>/update/", views.role_update, name="role_update"),
    path('<slug:slug>/roles/member/<int:pk>/edit/', views.member_roles_edit, name='member_roles_edit'),
    path("entity/<slug:slug>/role/<int:pk>/delete/", views.role_delete, name="role_delete"),
    path('<slug:slug>/roles/member/<int:pk>/', views.member_roles_detail, name='member_roles_detail'),
    path('<slug:slug>/roles/list/', views.role_list, name='role_list'),
    
    # ChurchApp/urls.py


    # Service CRUD
    
    path('<slug:slug>/services/add/', views.service_create, name='service_create'),
    path('<slug:slug>/services/<int:pk>/edit/', views.service_update, name='service_update'),

    #path('<slug:slug>/services/<int:service_id>/detail/', views.service_detail, name='service_detail'),
    
    
    # Dues and Tithes 
    path('<slug:slug>/dues-tithe/', views.dues_tithe_list_manage, name='dues_tithe_list_manage'),
    path('<slug:slug>/dues-tithe/add/', views.dues_tithe_create, name='dues_tithe_create'),
    path('<slug:slug>/dues-tithe/<int:pk>/view/', views.dues_tithe_view, name='dues_tithe_view'),
    path('<slug:slug>/dues-tithe/<int:pk>/delete/', views.dues_tithe_delete, name='dues_tithe_delete'),
    path("<slug:slug>/dues-tithe/edit/<int:pk>/", views.dues_tithe_edit, name="dues_tithe_edit"),
    
    path('<slug:slug>/dues-tithe/<int:pk>/pdf/', views.dues_tithe_pdf, name='dues_tithe_pdf'),
    path('<slug:slug>/dues-tithe/<int:pk>/excel/', views.dues_tithe_excel, name='dues_tithe_excel'),

    # Dues/Tithe PDF + Excel (filtered list)
    path('<slug:slug>/dues-tithe/report/pdf/', views.dues_tithe_list_pdf, name='dues_tithe_list_pdf'),
    path('<slug:slug>/dues-tithe/report/excel/', views.dues_tithe_list_excel, name='dues_tithe_list_excel'),
     
    path('<slug:slug>/trans-create/', views.trans_create, name='trans_create'),
    path("<slug:slug>/trans-edit/<int:pk>/", views.trans_edit, name="trans_edit"),
    
    path('<slug:slug>/service/create/', views.service_activity_create, name='service_activity_create'),
    #path('<slug:slug>/service/edit/', views.service_activity_edit, name='service_activity_edit'),
    path('<slug:slug>/config/', views.church_config_edit, name='church_config_edit'),

    # Guild CRUD
    path('<slug:slug>/guilds/', views.guild_list_manage, name='guild_list_manage'),
    path('<slug:slug>/guilds/add/', views.guild_create, name='guild_create'),
    path('<slug:slug>/guilds/<int:pk>/edit/', views.guild_update, name='guild_update'),
    path('<slug:slug>/guilds/<int:pk>/delete/', views.guild_delete, name='guild_delete'),
    path('<slug:slug>/guilds/<int:pk>/', views.guild_detail, name='guild_detail'),
    
    
    path("<slug:slug>/member-images/", views.member_images, name="member_images"),
    path("<slug:slug>/member-images/<int:pk>/",  views.member_images,  name="member_images"),
    path("entity/<slug:slug>/members/<int:pk>/images/view/", views.member_images_view, name="member_images_view"),
    
    path("entity/<slug:slug>/contributions/", views.member_contributions_list, name="member_contributions_list"),
    path("entity/<slug:slug>/contributions/pdf/", views.member_contributions_pdf, name="member_contributions_pdf"),
    path("entity/<slug:slug>/contributions/excel/", views.member_contributions_excel, name="member_contributions_excel"),  
    
]

