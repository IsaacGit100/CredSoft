from django.urls import path
from . import views

app_name = "Report"

urlpatterns = [
    path("<slug:slug>/trial-balance/", views.trial_balance, name="trial_balance"),
    path("<slug:slug>/journal-list/", views.journal_list, name="journal_list"),
    path("<slug:slug>/income-statement/", views.income_statement, name="income_statement"),
    path("<slug:slug>/cash-flow/", views.cash_flow, name="cash_flow"),
    path("<slug:slug>/trans-records/", views.trans_records, name="trans_records"),
    path("<slug:slug>/journal-records/", views.journal_records, name="journal_records"),
    path("<slug:slug>/balance-sheet/", views.balance_sheet, name="balance_sheet"),
    path("<slug:slug>/finance-dashboard/", views.finance_dashboard, name="finance_dashboard"),
    
    path("entity/<slug:slug>/finance_reports/", views.finance_reports, name="finance_reports"),
    path("<slug:slug>/", views.report_index, name="index"),
    path("entity/<slug:slug>/account/<str:code>/", views.account_details, name="account_details"),
    
    path("<slug:slug>/trans-records<str:code>/", views.account_details, name="account_details"),
    
    
]
