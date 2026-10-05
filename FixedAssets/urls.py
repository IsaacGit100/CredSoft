from django.contrib import admin
from django.urls import path, include
from . import views
from django_ledger.models import (EntityModel, LedgerModel, JournalEntryModel, AccountModel, TransactionModel,)

app_name = "FixedAssets"


urlpatterns = [
    # Fixed Assets
    path('entity/<slug:slug>/home/', views.fixed_asset_home, name='fixed_asset_home'),
    
    path('entity/<slug:slug>/fixed_asset/list', views.fixed_asset_list, name='fixed_asset_list'),
    path('entity/<slug:slug>/create/', views.fixed_asset_create, name='fixed_asset_create'),
    path('entity/<slug:slug>/<int:pk>/edit/', views.fixed_asset_update, name='fixed_asset_update'),
    path('entity/<slug:slug>/<int:pk>/delete/', views.fixed_asset_delete, name='fixed_asset_delete'),
    path('entity/<slug:slug>/<int:pk>/post-to-trans/', views.fixed_asset_post_to_trans, name='fixed_asset_post_to_trans'),
    path('entity/<slug:slug>/run-depreciation/', views.run_depreciation, name='run_depreciation'),

    # Asset Categories
    path('entity/<slug:slug>/asset-categories/', views.asset_category_list, name='asset_category_list'),
    path('entity/<slug:slug>/asset-categories/create/', views.asset_category_create, name='asset_category_create'),
    path('entity/<slug:slug>/asset-categories/<int:pk>/edit/', views.asset_category_update, name='asset_category_update'),
    path('entity/<slug:slug>/asset-categories/<int:pk>/delete/', views.asset_category_delete, name='asset_category_delete'),
    
    path('entity/<slug:slug>/<int:pk>/edit/', views.fixed_asset_update, name='fixed_asset_update'),
    path('entity/<slug:slug>/<int:pk>/delete/', views.fixed_asset_delete, name='fixed_asset_delete'),
    path('entity/<slug:slug>/<int:pk>/post-to-trans/', views.fixed_asset_post_to_trans, name='fixed_asset_post_to_trans'),
    
    path('entity/<slug:slug>/<int:pk>/edit/', views.fixed_asset_update, name='fixed_asset_update'),
    path('entity/<slug:slug>/<int:pk>/delete/', views.fixed_asset_delete, name='fixed_asset_delete'),
    path('entity/<slug:slug>/<int:pk>/post-to-trans/', views.fixed_asset_post_to_trans, name='fixed_asset_post_to_trans'),
    
    path('entity/<slug:slug>/asset/list/pdf/', views.fixed_asset_list_pdf, name='fixed_asset_list_pdf'),
    path('entity/<slug:slug>/asset/list/excel/', views.fixed_asset_list_excel, name='fixed_asset_list_excel'),
    
    path('entity/<slug:slug>/asset-categories/pdf/', views.asset_category_list_pdf, name='asset_category_list_pdf'),
    path('entity/<slug:slug>/asset-categories/excel/', views.asset_category_list_excel, name='asset_category_list_excel'),
]

