# Supervisor/urls.py
from django.urls import path
from . import views
from . import views_dividend
from . import views_dashboard

app_name = 'Supervisor'

urlpatterns = [
    # Add your URL patterns here
    # Example:
    path("entity/<slug:slug>/super/home/", views.super_home, name="super_home"),
    path("entity/<slug:slug>/super/finance/home/", views.super_finance_home, name="super_finance_home"),
    path("entity/<slug:slug>/main/dashboard/", views.super_home, name="main_dashboard"),
    path("entity/<slug:slug>/super/batch_process/", views.batch_process, name="batch_process"),
    path("entity/<slug:slug>/member/images/", views.members_images, name="members_images"),
    path("entity/<slug:slug>/member/list/delete/",  views.member_list_delete, name="member_list_delete"),
    path("entity/<slug:slug>/member/list/restore/", views.member_list_restore, name="member_list_restore"),
    # path('member/delete/', views.member_delete, name='member_delete'),
    path("entity/<slug:slug>/member/<int:pk>/delete-confirm/", views.member_delete_confirm, name="member_delete_confirm"),
    path("entity/<slug:slug>/member/<int:pk>/delete-perform/", views.member_delete_perform, name="member_delete_perform"),
    path("entity/<slug:slug>/member/<int:pk>/restore/", views.member_restore, name="member_restore"),
    path("entity/<slug:slug>/member/<int:pk>/permanent-delete/", views.member_permanent_delete, name="member_permanent_delete"),
    path("entity/<slug:slug>/delete-history/", views.delete_history_list, name="delete_history_list"),
    
    path("entity/<slug:slug>/supervisor/dashboard/", views_dashboard.database_dashboard,name="database_dashboard"),
    path("entity/<slug:slug>/Supervisor/reports_index/", views.reports_index, name="reports_index"),
    path("entity/<slug:slug>/menu/member/delete/restore/", views.del_restore_menu, name="del_restore_menu"),
    path("entity/<slug:slug>/menu/login/view/restore/", views.del_restore_menu, name="login_manager_menu"),
    path("entity/<slug:slug>/menu/tech/", views.tech_menu, name="tech_menu"),
    path("entity/<slug:slug>/menu/batch/processing/menu/", views.batch_process_menu, name="batch_process_menu"),
    path("entity/<slug:slug>/run-interest-accrual/", views.run_interest_accrual, name="run_interest_accrual"),
    path("entity/<slug:slug>/super-home/", views.super_home, name="super_home"),
    
    path("entity/<slug:slug>/pending_transactions/", views.pending_transactions, name='pending_transactions'),
    path("entity/<slug:slug>/post-selected/", views.post_selected_transactions, name='post_selected_transactions'),
]
