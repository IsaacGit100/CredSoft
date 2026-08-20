# RecPayApp/urls.py
from django.urls import path
from . import views
from . import views_pdf
from . import views_excel
from . import views_batch
# from . import views_services

app_name = 'RecPayApp'

urlpatterns = [
    # Main views
    path("entity/<slug:slug>/home/", views.recpay_home, name="recpay_home"),
    path("entity/<slug:slug>/trans_create/", views.trans_create, name="trans_create"),
    path("entity/<slug:slug>/trans_list_manage/", views.trans_list_manage, name="trans_list_manage"),
    path("entity/<slug:slug>/trans_list/", views.trans_list, name='trans_list'),
    path("entity/<slug:slug>/trans_audit_report/", views.trans_audit_report, name="trans_audit_report"),
    path("entity/<slug:slug>/trans_jour_bal_list/", views.trans_jour_bal_list, name='trans_jour_bal_list'),
    
    path("entity/<slug:slug>/trans_all_pdf/", views_pdf.trans_all_pdf, name='trans_all_pdf'), 
    path("entity/<slug:slug>/trans_all_excel/", views_excel.trans_all_excel, name="trans_all_excel"),
    
    path("entity/<slug:slug>/trans_view/<int:pk>/", views.trans_view, name='trans_view'),
    path("entity/<slug:slug>/trans_delete/<int:pk>/", views.trans_delete, name="trans_delete"),
    path("entity/<slug:slug>/trans_edit/<int:pk>/", views.trans_edit, name='trans_edit'),
    path("entity/<slug:slug>/trans_pdf/<int:pk>/", views_pdf.trans_pdf, name='trans_pdf'),
    path("entity/<slug:slug>/trans_excel/<int:pk>/", views_excel.trans_excel, name='trans_excel'),
    path("entity/<slug:slug>/trans_view_pending/<int:pk>/", views.trans_view_pending, name='trans_view_pending'),
    
    
    
    path("batch-post/", views.batch_post_transactions, name="batch_post_transactions"),
    path("post/transaction/", views.post_transaction, name="post_transaction"),
    #   path('journal-list-manage/', views.journal_list_manage, name='journal_list_manage'),
    # API endpoints
    path(
        "api/member-info/<int:member_id>/",
        views.api_member_info,
        name="api_member_info",
    ),
    path(
        "api/member-loans/<int:member_id>/",
        views.api_member_loans,
        name="api_member_loans",
    ),
    path("trans-all-delete/", views.trans_all_delete, name="trans_all_delete"),
    path(
        "entity/<slug:slug>/trans/list/manage/",
        views.trans_list_manage,
        name="trans_list_manage",
    ),
    #  'entity/<slug:slug>/journal-entries/'
    
    
#    path("trans/excel/all/", views_excel.trans_excel_all, name="trans_excel_all"),
    path(
        "RecPayApp/batch_posting_dashboard/",
        views_batch.batch_posting_dashboard,
        name="batch_posting_dashboard",
    ),
    path(
        "RecPayApp/batch_post_review/",
        views_batch.batch_posting_preview,
        name="batch_posting_preview",
    ),
    path(
        "RecPayApp/batch_posting_confirm/",
        views_batch.batch_posting_confirm,
        name="batch_posting_confirm",
    ),
    path("trans/detail/<int:pk>/", views.trans_detail, name="trans_detail"),
    #  path('transactions/', views_services.transaction_list, name='transaction_list'),
    #  path('transactions/list/', views_services.transaction_list, name='transaction_list_alt'),
    #  ADD THIS - Process all transactions
    #  path('transactions/process/', views_services.process_all_drafts, name='process_transactions'),
    #  ADD THIS - Process single transaction
    #  path('transactions/process/<int:trans_id>/', views_services.process_single_transaction_view, name='process_single_transaction'),
    #  path('transactions/process/<int:trans_id>/', views_services.process_single_transaction_view, name='process_single_transaction'),
    #  path('transactions/detail/<int:trans_id>/', views_services.transaction_detail, name='transaction_detail'),
    path("report/trans-audit/", views.trans_audit_report, name="trans_audit_report"),
    path(
        "report/trans-audit/excel/",
        views.trans_audit_report_excel,
        name="trans_audit_report_excel",
    ),
    path("trans/jour/bal/list/", views.trans_jour_bal_list, name="trans_jour_bal_list"),
    path(
        "trans/jour/bal/view/<int:pk>/",
        views.trans_jour_bal_view,
        name="trans_jour_bal_view",
    ),
    path(
        "church/<slug:slug>/trans/create/",
        views.church_trans_create,
        name="church_trans_create",
    ),
    path(
        "school/<slug:slug>/trans/create/",
        views.school_trans_create,
        name="school_trans_create",
    ),
    # Entity Trans
    path(
        "entity/<slug:slug>/trans/list/manage/",
        views.trans_list_manage,
        name="trans_list_manage",
    ),
    path(
        "finance/<slug:slug>/trans/create/",
        views.finance_trans_create,
        name="finance_trans_create",
    ),
    path(
        "entity/<slug:slug>/trans/list/",
        views.trans_approval_list,
        name="trans_approval_list",
    ),
    path(
        "entity/<slug:slug>/trans/post/",
        views.trans_post_selected,
        name="trans_post_selected",
    ),
]
