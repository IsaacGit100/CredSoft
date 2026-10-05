# urls.py
from django.urls import path
from . import views
from . import views_PDF
from . import views_excel


app_name =  'LoanApp'


urlpatterns = [
    path("entity/<slug:slug>/loans/home", views.loans_home, name="loans_home"),
    
    path("entity/<slug:slug>/loan/application/", views.loan_application, name="loan_application"),
    path("entity/<slug:slug>/loans/list/", views.loan_list, name="loan_list"),
    path("entity/<slug:slug>/loans/<int:pk>/", views.loan_detail, name="loan_detail"),
    path("entity/<slug:slug>/loans/<int:pk>/edit/", views.loan_edit, name="loan_edit"),
    path("entity/<slug:slug>/loans/<int:pk>/delete/", views.loan_delete, name="loan_delete"),

    path("entity/<slug:slug>/loans/pdf/", views.loan_list_pdf, name="loan_list_pdf"),
    path("entity/<slug:slug>/loans/excel/", views.loan_list_excel, name="loan_list_excel"),
    path("entity/<slug:slug>/loans/<int:pk>/acceptance/", views.loan_acceptance_letter, name="loan_acceptance_letter"),
    
    path("entity/<slug:slug>/loan-repayment/",  views.loan_repayment_create, name="loan_repayment_create"),
    path("entity/<slug:slug>/loan-repayment/<int:pk>/", views.loan_repayment_view, name="loan_repayment_view"),
    path("entity/<slug:slug>/loan-repayment/<int:pk>/delete/",  views.loan_repayment_delete, name="loan_repayment_delete"),
    
    path("<slug:slug>/loan/<int:loan_id>/schedule.pdf", views.loan_schedule_pdf,   name="loan_schedule_pdf"),
    path("<slug:slug>/loan/<int:loan_id>/schedule/email/", views.loan_schedule_email, name="loan_schedule_email"),
    

    


    # A. Preview from application form
    path("<slug:slug>/loan/schedule/preview.pdf", views.loan_schedule_preview_pdf, name="loan_schedule_preview"),

    # B. Print/download from Loan List
    path("<slug:slug>/loan/<int:loan_id>/schedule.pdf", views.loan_schedule_pdf, name="loan_schedule_pdf"),
]


