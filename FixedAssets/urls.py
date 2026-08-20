from django.urls import path
from . import views


app_name = 'FixedAssets'

urlpatterns = [
    path("entity/<slug:slug>/home/", views.fixed_assets_home, name="fixed_assets_home"),
    path(
        "entity/<slug:slug>/assets/dashboard/",
        views.asset_dashboard,
        name="asset_dashboard",
    ),
    # ===============================Assets Manage ==============================================
    path(
        "entity/<slug:slug>/assets/", views.asset_list_manage, name="asset_list_manage"
    ),
    path("entity/<slug:slug>/assets/add/", views.asset_add, name="asset_add"),
    path(
        "entity/<slug:slug>/assets/<int:pk>/edit/",
        views.asset_edit,
        name="asset_edit",
    ),
    path(
        "entity/<slug:slug>/assets/<int:pk>/delete/",
        views.asset_delete,
        name="asset_delete",
    ),
    path(
        "entity/<slug:slug>/register/",
        views.fixed_asset_register,
        name="fixed_asset_register",
    ),
    # ==============================depreciation ===================================================
    # path('entity/<slug:slug>/depreciation/', views.fixed_asset_depreciation, name='fixed_asset_depreciation'),
    path(
        "entity/<slug:slug>/post-depreciation/",
        views.post_depreciation,
        name="post_depreciation",
    ),
    path("entity/<slug:slug>/depreciation_list_manage/", views.depreciation_list_manage, name="depreciation_list_manage"),
    path("entity/<slug:slug>/excel/", views.depreciation_export_excel, name="depreciation_export_excel"),
    path("entity/<slug:slug>/pdf/", views.depreciation_export_pdf, name="depreciation_export_pdf"),
    # ============================= Category =======================================================
    path("entity/<slug:slug>/category_list_manage", views.category_list_manage, name="category_list_manage"),
    path("entity/<slug:slug>/category_create/", views.category_create, name="category_create"),
    path("entity/<slug:slug>/category/<int:pk>/edit/", views.category_edit, name="category_edit"),
    path("entity/<slug:slug>/categories/<int:pk>/delete/", views.category_delete, name="category_delete"),
    path("entity/<slug:slug>/asset_list_manage", views.asset_list_manage, name="asset_list_manage"),
    path("entity/<slug:slug>/post-depreciation/", views.post_depreciation, name="post_depreciation"),
    path("entity/<slug:slug>/depreciation-schedule/", views.depreciation_schedule, name="depreciation_schedule"),
    
    #  path('assets/assets_list_manage/', views.assets_list_manage, name='assets_list_manage'),
    #   path('assets/add/', views.asset_create, name='asset_create'),
    #   path('assets/<int:pk>/edit/', views.asset_edit, name='asset_edit'),
    #   path('assets/<int:pk>/delete/', views.asset_delete, name='asset_delete'),
    path("entity/<slug:slug>/fixed-assets-registrar/", views.fixed_assets_register_list, name="fixed_assets_register_list"),
    path("entity/<slug:slug>/fixed-assets-registrar/pdf/", views.fixed_assets_register_PDF, name="fixed_assets_register_PDF"),
    path("entity/<slug:slug>/fixed-assets-registrar/excel/", views.fixed_assets_register_excel, name="fixed_assets_register_excel"),
]
