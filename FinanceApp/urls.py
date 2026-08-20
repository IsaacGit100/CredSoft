from django.urls import path
from . import views
from . import views_journal
from . import views_reports
from . import views_ledger
from . import views_excelPDF
from . import views_inc


app_name = 'FinanceApp'

urlpatterns = [
  
    path('entity/<slug:slug>/finance_reports/', views.finance_reports_home, name='finance_reports_home'),
    path('entity/<slug:slug>/monthly-income-statement/', views.monthly_income_statement, name='monthly_income_statement'),
    path('entity/<slug:slug>/finance-dashboard/', views.finance_dashboard, name='finance_dashboard'),

    
    
    path('finance/home/', views.finance_home, name='finance_home'),
    path('finance/main_menu/', views.main_menu, name='main_menu'),
    path('finance/fin/home/', views.finance_fin_home, name='finance_fin_home'),
    path('back/to/home/', views.back_to_home, name='back_to_home'),
    path('opening/balance/home/', views.opening_balance_home, name='opening_balance_home'),
    path('journal/home/', views.journal_home, name='journal_home'),
     
    # ============================================================
    # JOURNAL ENTRY URLs (Header Management)
    # ============================================================
    path('journal-entries/', views_journal.journal_entry_manage, name='journal_entry_manage'),
    path('journal-entries/create/', views_journal.journal_entry_create, name='journal_entry_create'),
    path('journal-entries/<int:pk>/', views_journal.journal_entry_detail, name='journal_entry_detail'),
    path('journal-entries/<int:pk>/edit/', views_journal.journal_entry_edit, name='journal_entry_edit'),
    path('journal-entries/<int:pk>/delete/', views_journal.journal_entry_delete, name='journal_entry_delete'),
    path('journal-entries/<int:pk>/post/', views_journal.journal_entry_post, name='journal_entry_post'),
    path('journal-entries/<int:pk>/void/', views_journal.journal_entry_void, name='journal_entry_void'),
    
    # ============================================================
    # JOURNAL LINE URLs (Detail Management - Nested under Journal)
    # ============================================================
    path('entity/<slug:slug>/journal-entries/<int:journal_pk>/lines/', views_journal.journal_line_manage, name='journal_line_manage'),
    path('entity/<slug:slug>/journal-entries/<int:journal_pk>/lines/create/', views_journal.journal_line_create, name='journal_line_create'),
    path('entity/<slug:slug>/journal-entries/<int:journal_pk>/lines/<int:line_pk>/edit/', views_journal.journal_line_edit, name='journal_line_edit'),
    path('entity/<slug:slug>/journal-entries/<int:journal_pk>/lines/<int:line_pk>/delete/', views_journal.journal_line_delete, name='journal_line_delete'),

    path('entity/<slug:slug>/report/transaction-journal/', views_ledger.trans_journ_report, name='trans_journ_report'),
    path('entity/<slug:slug>/report/transaction-journal/pdf/', views_ledger.trans_journ_report_pdf, name='trans_journ_report_pdf'),
    path('entity/<slug:slug>/report/transaction-journal/excel/', views_ledger.trans_journ_report_excel, name='trans_journ_report_excel'),
    
    
    ## =========================Income Statement =====================================================
    path('FinanceApp/views_inc/income_statement', views_inc.income_statement, name='income_statement'),
    path('FinanceApp/views_inc/inc_state_print/', views_inc.inc_state_print, name='inc_state_print'),
    path('FinanceApp/views_inc/inc_state_pdf/', views_inc.inc_state_pdf, name='inc_state_pdf'),
    path('FinanceApp/views_inc/inc_state_excel/', views_inc.inc_state_excel, name='inc_state_excel'),
    
  
    ## =========================Ledgers ================================================================
    path('FinanceApp/views_ledger/ledger_list', views_ledger.ledger_list, name='ledger_list'),
    path('FinanceApp/views_ledger/ledger_list_print', views_ledger.ledger_list_print, name='ledger_list_print'),
    path('FinanceApp/views_ledger/ledger_list_pdf', views_ledger.ledger_list_pdf, name='ledger_list_pdf'),
    path('FinanceApp/views_ledger/ledger_list_excel', views_ledger.ledger_list_excel, name='ledger_list_excel'),
    
    
    
  
  
    path('reports/profit-loss/', views_reports.profit_loss, name='profit_loss'),
    path('reports/profit-loss/print/', views_reports.profit_loss_print, name='profit_loss_print'),
    path('reports/profit-loss/pdf/', views_reports.profit_loss_pdf, name='profit_loss_pdf'),
    path('reports/profit-loss/excel/', views_reports.profit_loss_excel, name='profit_loss_excel'),
    
    # ============================================================
    # LEDGER LINE URLs (Detail Management - Nested under Ledger)
    # ============================================================
    
    path('ledger/', views_ledger.ledger_list, name='ledger_list'),
  #  path('ledger/<str:account_code>/', views_ledger.ledger_account_detail, name='ledger_account_detail'),
    path('ledger/account/<int:account_id>/', views_ledger.ledger_account_detail, name='ledger_account_detail'),
    path('ledger/balances/', views_ledger.ledger_balances, name='ledger_balances'),
    path('reports/ledger-balances/pdf/', views_excelPDF.ledger_balances_pdf, name='ledger_balances_pdf'),
    path('reports/ledger-balances/excel/', views_excelPDF.ledger_balances_excel, name='ledger_balances_excel'),
    
    
    
    path('ledger/statement/', views_ledger.ledger_statement, name='ledger_statement'),
    path('ledger/statement/pdf/', views_excelPDF.ledger_statement_pdf, name='ledger_statement_pdf'),
    path('ledger/statement/excel/', views_excelPDF.ledger_statement_excel, name='ledger_statement_excel'),
    
    path('FinanceApp/views_general_ledger_print/', views_reports.general_ledger_print, name='general_ledger_print'),
    path('FinanceApp/views_general_ledger_pdf/', views_reports.general_ledger_pdf, name='general_ledger_pdf'),
    path('FinanceApp/views_general_ledger_excel/', views_reports.general_ledger_excel, name='general_ledger_excel'),
    
    
    path('entity/<slug:slug>/views_account_ledger_print/', views_reports.account_ledger_print, name='account_ledger_print'),
    path('entity/<slug:slug>/views_account_ledger_pdf/', views_reports.account_ledger_pdf, name='account_ledger_pdf'),
    path('entity/<slug:slug>/views_account_ledger_excel/', views_reports.account_ledger_excel, name='account_ledger_excel'),
    
    path('entity/<slug:slug>/ledger/opening-balance/', views_ledger.ledger_opening_balance, name='ledger_opening_balance'),
    path('entity/<slug:slug>/ledger/account-autocomplete/', views_ledger.account_autocomplete, name='account_autocomplete'),
    
    path('entity/<slug:slug>/trial-balance/pdf/', views.trial_balance_pdf, name='trial_balance_pdf'),
    
    #path('reports/trial-balance/', views_excelPDF.trial_balance_report, name='trial_balance'),
    
    path('entity/<slug:slug>/trialbalance/', views.trial_balance,  name='trial_balance'), 
    path('entity/<slug:slug>/balancesheet/', views.balance_sheet,  name='balance_sheet'), 
    
    
    path('trial-balance/', views_excelPDF.trial_balance,  name='trial_balance'),          # HTML (printable) page
    path('FinanceApp/views_excelPDF/trial_balance_list/', views_excelPDF.trial_balance_list, name='trial_balance_list'),
    path('FinanceApp/views_excelPDF/trial_balance_pdf/', views_excelPDF.trial_balance_pdf, name='trial_balance_pdf'),
    path('FinanceApp/views_excelPDF/trial_balance_excel/', views_excelPDF.trial_balance_excel, {'format': 'excel'}, name='trial_balance_excel'),
    
    
    path('indicators/', views.indicators_dashboard, name='indicators_dashboard'),
    
    path('reports/balance-sheet/',views_reports.balance_sheet, name='balance_sheet'),
    path('reports/balance-sheet/print/', views.balance_sheet_print, name='balance_sheet_print'),
    path('reports/balance-sheet/pdf/', views.balance_sheet_pdf, name='balance_sheet_pdf'),
    path('reports/balance-sheet/excel/', views.balance_sheet_excel, name='balance_sheet_excel'),
    
    
    
    
    
    
    
    
    
  #  path('reports/trial-balance/', views_excelPDF.trial_balance_html, name='trial_balance'),      # HTML
  #  path('reports/trial-balance/pdf/', views_excelPDF.trial_balance_pdf, name='trial_balance_pdf'),  # PDF
    
    
    
    

    
    # Journal Entry URLs
 #   path('journals/', views_journal.journal_entry_list_manage, name='journal_entry_list_manage'),
 #   path('journals/create/', views_journal.journal_entry_create, name='journal_entry_create'),
 #   path('journals/<int:pk>/', views_journal.journal_entry_detail, name='journal_entry_detail'),
 #   path('journals/<int:pk>/edit/', views_journal.journal_entry_edit, name='journal_entry_edit'),
 #   path('journals/<int:pk>/delete/', views_journal.journal_entry_delete, name='journal_entry_delete'),
 #   path('journals/<int:pk>/post/', views_journal.journal_entry_post, name='journal_entry_post'),
 #   path('journals/<int:pk>/void/', views_journal.journal_entry_void, name='journal_entry_void'),
    
    # Journal Line URLs
  #  path('journals/<int:journal_pk>/line/add/', views_journal.journal_line_add, name='journal_line_add'),
  #  path('journal-line/<int:pk>/edit/', views_journal.journal_line_edit, name='journal_line_edit'),
  #  path('journal-line/<int:pk>/delete/', views_journal.journal_line_delete, name='journal_line_delete'),
    
  #  path('journal/trans/', views.trans_detail, name='trans_detail'),
]