# urls.py
from django.urls import path
from . import views
from . import views_PDF
from . import views_excel


app_name =  'LoanApp'


urlpatterns = [
    path("entity/<slug:slug>/loans/home", views.loans_home, name="loans_home"),
    path("entity/<slug:slug>/main/menu/", views.main_menu, name="main_menu"),
    path("entity/<slug:slug>/loan/success/<int:loan_id>/", views.loan_success, name="loan_success"),
    path("entity/<slug:slug>/create-loan/", views.create_loan, name="create_loan"),
    path("entity/<slug:slug>/loan/<int:loan_id>/generate-pdf/", views_PDF.generate_loan_PDF, name="generate_loan_PDF"),
    path("entity/<slug:slug>/loan/<int:loan_id>/", views.loan_detail, name="loan_detail"),
    
    path("entity/<slug:slug>/search-master/", views.search_master, name="search_master"),
    path("entity/<slug:slug>/loan-form/", views.loan_form, name="loan_form"),
    path("entity/<slug:slug>/loan-form/<int:master_id>/", views.loan_form, name="loan_form_with_master"),
    path("entity/<slug:slug>/loan-form-with-master/<int:master_id>/", views.loan_form_with_master, name="loan_form_with_master"),
    # Loan management
    path("entity/<slug:slug>/loan-list/", views.loan_list, name="loan_list"),
    path("entity/<slug:slug>/loans/master/<int:master_id>/", views.master_loans, name="master_loans"),
    path("entity/<slug:slug>/loans/statistics/", views.loan_statistics, name="loan_statistics"),
    path("entity/<slug:slug>/loans/financials", views.loan_list_financials, name="loan_list_financials"),
    path("entity/<slug:slug>/loans/pdf/", views_PDF.loan_list_financials_pdf, name="loan_list_financials_pdf"),
    path(
        "entity/<slug:slug>/loans/excel/",
        views_excel.loan_list_financials_excel,
        name="loan_list_financials_excel",
    ),
    # AJAX endpoints
    #    path('calculate-loan/', views.calculate_loan_ajax, name='calculate_loan'),
    #    path('get-member-balance/<int:member_id>/', views.get_member_balance, name='get_member_balance'),
    path(
        "entity/<slug:slug>/guarantor-search/",
        views.guarantor_search,
        name="guarantor_search",
    ),
    path(
        "entity/<slug:slug>/loan-guarantors/<int:loan_id>/",
        views.loan_guarantors,
        name="loan_guarantors",
    ),
    path(
        "entity/<slug:slug>/loan/<int:loan_id>/print/",
        views.loan_print_view,
        name="loan_print",
    ),
    path(
        "entity/<slug:slug>/loan_list_other/",
        views.loan_list_other,
        name="loan_list_other",
    ),
    path(
        "entity/<slug:slug>/voucher_daily_update/",
        views.voucher_daily_update,
        name="voucher_daily_update",
    ),
    path("entity/<slug:slug>/gua-list/", views.gua_list, name="gua_list"),
    path(
        "entity/<slug:slug>/gua-list-pdf/", views_PDF.gua_list_pdf, name="gua_list_pdf"
    ),
    path(
        "entity/<slug:slug>/gua-list-excel/",
        views_excel.gua_list_excel,
        name="gua_list_excel",
    ),
    path(
        "entity/<slug:slug>/loans/update/process/",
        views.loan_update,
        name="loan_update",
    ),
    path(
        "entity/<slug:slug>/LoanApp/loan_update_list/",
        views.loan_update_list,
        name="loan_update_list",
    ),
    path(
        "entity/<slug:slug>/loan_update_list/pdf/", views.loan_update_list_pdf, name="loan_update_list_pdf"
    ),
    path(
        "entity/<slug:slug>/loan_update_list/excel/",
        views_excel.loan_update_list_excel,
        name="loan_update_list_excel",
    ),
    path(
        "entity/<slug:slug>/loan/<int:loan_id>/repayments/",
        views.loan_repayment_list,
        name="loan_repayment_list",
    ),
]
