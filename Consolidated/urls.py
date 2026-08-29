from django.urls import path
from . import views

app_name = 'Consolidated'

urlpatterns = [
    # path('dashboard/', views.consolidated_dashboard, name='dashboard'),
    path('dashboard/after_login_redirect/', views.after_login_redirect, name='after_login_redirect'),
    path('portal/', views.super_admin_portal, name='portal'),
    path('dashboard/', views.consolidated_dashboard, name='dashboard'),
    
    path('portal/', views.super_admin_portal, name='portal'),
    path('dashboard/', views.consolidated_dashboard, name='dashboard'),
    path('income-statement/', views.consolidated_income_statement, name='income_statement'),
    path('balance-sheet/', views.consolidated_balance_sheet, name='balance_sheet'),
    path('cash-flow/', views.consolidated_cash_flow, name='cash_flow'),
    path('trial-balance/', views.consolidated_trial_balance, name='trial_balance'),
    path('export-pdf/', views.consolidated_export_pdf, name='export_pdf'),
    path('export-excel/', views.consolidated_export_excel, name='export_excel'),
    
    
    
]