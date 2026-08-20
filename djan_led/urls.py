# urls.py
from django.urls import path
from . import views
from . import views_reports

app_name = 'djan_led'


urlpatterns = [
    path("redirect/", views.after_login_redirect, name="after_login_redirect"),
    path("entity/<slug:slug>/", views.entity_dashboard, name="entity_dashboard"),
    path("djan_led/home/", views.djan_led_home, name="djan_led_home"),
    path("entity/<slug:slug>/cred/home/", views.supervisor_cred_home, name='supervisor_cred_home'),
    
    
    path("entity/<slug:slug>/coa/home/", views.coa_home, name="coa_home"),
    path("entity/<slug:slug>/chart-of-accounts/", views.chart_of_accounts, name="chart_of_accounts"),
    path("entity/<slug:slug>/autofill-coa/", views.autofill_chart_of_accounts, name="autofill_chart_of_accounts"),
    path("entity/<slug:slug>/chart-of-accounts/pdf/", views.chart_of_accounts_pdf, name="chart_of_accounts_pdf"),
    path("entity/<slug:slug>/chart-of-accounts/excel/", views.chart_of_accounts_excel, name="chart_of_accounts_excel"),
    
    path("entity/<slug:slug>/journal-entries/", views.journal_entries, name="journal_entries"),
    path("entity/<slug:slug>/trial-balance/", views.trial_balance, name="trial_balance"),
    path("entity/<slug:slug>/income-statement/", views.income_statement, name="income_statement"),
    path("entity/<slug:slug>/balance_sheet/", views.balance_sheet, name="balance_sheet"),
    path("entity/<slug:slug>/cash-flow/", views.cash_flow, name="cash_flow"),
    
    path("entity/<slug:slug>/journal-entry/<uuid:pk>/", views.journal_entry_detail, name="journal_entry_detail"),
    path("create-parish/", views.create_parish, name="create_parish"),
    path("entity/<slug:slug>/record-offering/", views.record_offering, name="record_offering"),
    path("entity/<slug:slug>/add-account/", views.add_account, name="add_account"),
    path("entity/<slug:slug>/opening-balance/", views.opening_balance_form, name="opening_balance_form"),
    path("entity/<slug:slug>/opening-balance-pdf/", views.opening_balance_PDF, name="opening_balance_PDF"),
    path("entity/<slug:slug>/opening-balance-excel/", views.opening_balance_excel, name="opening_balance_excel"),
    path("entity/<slug:slug>/entity_dashboard/", views.entity_dashboard, name="entity_dashboard"),
    path(
        "entity/<slug:slug>/account-visibility/",
        views.account_visibility,
        name="account_visibility",
    ),
    path("entity/<slug:slug>/super/Trans/Home/", views.supervisor_trans_home, name="supervisor_trans_home"),
    # =========================== Finance Reports ====================================
    path("entity/<slug:slug>/trial-balance/pdf/", views_reports.trial_balance_pdf, name="trial_balance_pdf"),
    path(
        "entity/<slug:slug>/trial-balance/excel/",
        views_reports.trial_balance_excel,
        name="trial_balance_excel",
    ),
    path(
        "entity/<slug:slug>/income-statement/pdf/",
        views_reports.income_statement_pdf,
        name="income_statement_pdf",
    ),
    path(
        "entity/<slug:slug>/income-statement/excel/",
        views_reports.income_statement_excel,
        name="income_statement_excel",
    ),
    path(
        "entity/<slug:slug>/balance-sheet/pdf/",
        views_reports.balance_sheet_pdf,
        name="balance_sheet_pdf",
    ),
    path(
        "entity/<slug:slug>/balance-sheet/excel/",
        views_reports.balance_sheet_excel,
        name="balance_sheet_excel",
    ),
    path(
        "entity/<slug:slug>/journal-entries/pdf/",
        views_reports.journal_entries_pdf,
        name="journal_entries_pdf",
    ),
    path(
        "entity/<slug:slug>/journal-entries/excel/",
        views_reports.journal_entries_excel,
        name="journal_entries_excel",
    ),
    path(
        "entity/<slug:slug>/cash-flow/pdf/",
        views_reports.cash_flow_pdf,
        name="cash_flow_pdf",
    ),
    path(
        "entity/<slug:slug>/cash-flow/excel/",
        views_reports.cash_flow_excel,
        name="cash_flow_excel",
    ),
    path("entity/<slug:slug>/settings/", views.entity_settings, name="entity_settings"),
    path(
        "entity/<slug:slug>/account_preferences/",
        views.account_preferences,
        name="account_preferences",
    ),
    path("entity/<slug:slug>/manual-journal-entry/create/", views.manual_journal_entry_create, name="manual_journal_entry_create"),
    path("entity/<slug:slug>/manual-journal-entry/list/", views.manual_journal_entry_list, name="manual_journal_entry_list"),
    path("entity/<slug:slug>/manual-journal-entry/", views.manual_journal_entry, name="manual_journal_entry"),
    path("entity/<slug:slug>/pending-journal-entries/", views.pending_journal_entries, name="pending_journal_entries"),
    path("entity/<slug:slug>/autofill/<str:account_type>/", views.autofill_accounts, name="autofill_accounts"),
    path("entity/<slug:slug>/autofill/<str:account_type>/", views.autofill_accounts, name="autofill_accounts"),
    path("entity/<slug:slug>/coa/manage/", views.coa_list_manage, name="coa_list_manage"),
    path("entity/<slug:slug>/coa/manage/<uuid:account_uuid>/edit/", views.coa_acc_edit, name="coa_acc_edit"),
    path("entity/<slug:slug>/coa/manage/<uuid:account_uuid>/delete/", views.coa_acc_delete, name="coa_acc_delete"),
    
    
    
    path('coa/add_coa_to_entity/', views.add_coa_to_entity, name='add_coa_to_entity' ),
    #path('user/management/', views.user_management, name='user_management'),
    #path('entity/management/', views.entity_management, name='entity_management'),
    
    # View COA
    path('entity/<slug:slug>/chart-of-accounts/', views.chart_of_accounts, name='chart_of_accounts'),

    # Manage (Edit/Delete) COA
    path('entity/<slug:slug>/coa/manage/', views.coa_list_manage, name='coa_list_manage'),

    # PDF Export
    path('entity/<slug:slug>/chart-of-accounts/pdf/', views.chart_of_accounts_pdf, name='chart_of_accounts_pdf'),

    # Excel Export
    path('entity/<slug:slug>/chart-of-accounts/excel/', views.chart_of_accounts_excel, name='chart_of_accounts_excel'),

  #  path('entity/<slug:slug>/tech_dashboard/', views.tech_dashboard, name='tech_dashboard'),
    path('coa-management/set-default/<slug:slug>/', views.set_default_coa, name='set_default_coa'),
    
   
   # path('user-management/<int:user_id>/reset-password/', views.reset_user_password, name='reset_user_password'),
    
]
