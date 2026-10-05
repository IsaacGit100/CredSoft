from django.urls import path
from . import views

app_name = "Consolidated"

urlpatterns = [
    # Selection
    path("", views.select_context, name="select_context"),
    path("set-context/", views.set_context_bulk, name="set_context_bulk"),
    path("select/<slug:slug>/", views.set_context, name="set_context"),
    # Landing
    path("reports/", views.reports_home, name="reports_home"),
    # Financial
    path("consolidated/dashboard/", views.consolidated_dashboard, name="consolidated_dashboard"),
    
    path("trial-balance/", views.consolidated_trial_balance, name="consolidated_trial_balance"),
    path("income-statement/", views.consolidated_income_statement, name="consolidated_income_statement"),
    path(
        "balance-sheet/",
        views.consolidated_balance_sheet,
        name="consolidated_balance_sheet",
    ),
    path("cash-flow/", views.consolidated_cash_flow, name="consolidated_cash_flow"),
    # Membership & Operations
    path("reports/members/", views.report_members, name="report_members"),
    path("reports/clergy/", views.report_clergy, name="report_clergy"),
    path("reports/services/", views.report_services, name="report_services"),
    path("reports/dues-tithe/", views.report_dues_tithe_summary, name="report_dues_tithe_summary"),
    # Clergy
    path("reports/assets/", views.report_assets, name="report_assets"),
    path("reports/clergy/", views.report_clergy, name="report_clergy"),
    path("reports/clergy/<int:pk>/", views.clergy_detail, name="clergy_detail"),
    path("reports/clergy/<int:pk>/pdf/", views.clergy_pdf, name="clergy_pdf"),
    path("reports/clergy/<int:pk>/excel/", views.clergy_excel, name="clergy_excel"),
    # Services
    path("reports/services/", views.report_services, name="report_services"),
    path("reports/services/<int:pk>/", views.service_detail, name="service_detail"),
    path("reports/services/<int:pk>/pdf/", views.service_pdf, name="service_pdf"),
    path("reports/services/<int:pk>/excel/", views.service_excel, name="service_excel"),
    #
    path("reports/assets/", views.report_assets, name="report_assets"),
    path("reports/assets/<int:pk>/", views.asset_detail, name="asset_detail"),
    path("reports/assets/<int:pk>/pdf/", views.asset_pdf, name="asset_pdf"),
    path("reports/assets/<int:pk>/excel/", views.asset_excel, name="asset_excel"),
    path("admin/ports/", views.super_admin_portal, name="super_admin_portal"),
    
    path("diocese/", views.diocese_reports_home, name="diocese_reports_home"),
    path("diocese/trial-balance/", views.diocese_trial_balance, name="diocese_trial_balance"),
    path("diocese/income-statement/", views.diocese_income_statement, name="diocese_income_statement"),
    path("diocese/balance-sheet/", views.diocese_balance_sheet, name="diocese_balance_sheet"),
    path("diocese/cash-flow/", views.diocese_cash_flow, name="diocese_cash_flow"),
]
