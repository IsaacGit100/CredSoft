from django.urls import path
from . import views
from . import views_rep

app_name = "CreditUnion"

urlpatterns = [
    
    path("entity/<slug:slug>/credit_union_dashboard/", views.credit_union_dashboard, name="credit_union_dashboard"),
    path("entity/<slug:slug>/config/", views.credit_union_config_edit, name="credit_union_config_edit"),
    path("entity/<slug:slug>/supervisor/home", views.supervisor_credit_union_home, name="supervisor_credit_union_home"),
    path("entity/<slug:slug>/run-pending-transactions/", views.run_pending_transactions, name="run_pending_transactions"),
    #path("entity/<slug:slug>/supervisor/menu/", views.supervisor_credit_union, name="supervisor_credit_union"),
    path("entity/<slug:slug>/CreditUnion/member_list_manage/", views.member_list_manage, name="member_list_manage"),
    
    ## ======================== member_list_manage ================================================
    
    path("entity/<slug:slug>/member_create/", views.member_create, name="member_create"),
    path("entity/<slug:slug>/member_image_detail/<int:pk>/", views.member_image_detail, name="member_image_detail"),
    path("entity/<slug:slug>/member_setting/<int:pk>/", views.member_single_setting, name="member_single_setting"),
    
    path("entity/<slug:slug>/member_view/<int:pk>/", views.member_view, name="member_view"),
    path("entity/<slug:slug>/member_edit/<int:pk>/edit/", views.member_edit, name="member_edit"),
    path("entity/<slug:slug>/member_pdf/<int:pk>/pdf/", views.member_pdf, name="member_pdf"),
    path("entity/<slug:slug>/member_excel/<int:pk>/excel/", views.member_excel, name="member_excel"),
    path("entity/<slug:slug>/member_image_views/<int:pk>/", views.view_member_images, name="view_member_images"),
    path("entity/<slug:slug>/member_images/<int:pk>/", views.member_images, name="member_images"),
    
    path("entity/<slug:slug>/member/<int:pk>/image/delete/<str:image_type>/", views.delete_member_image, name="delete_member_image"),
    ## ===========================PDF Reports======================================================
    path("entity/<slug:slug>/members_info_pdf/", views_rep.members_info_pdf, name="members_info_pdf"),
    path("entity/<slug:slug>/members_contact_pdf/", views_rep.members_contact_pdf, name="members_contact_pdf"),
    path("entity/<slug:slug>/next_of_kin_pdf/", views_rep.next_of_kin_pdf, name="next_of_kin_pdf"),
    path("entity/<slug:slug>/financial_report_pdf/", views_rep.financial_report_pdf, name="financial_report_pdf"),
    
    ## ==========================Excel Reports=====================================================
    path("entity/<slug:slug>/members_info_excel/", views_rep.members_info_excel, name="members_info_excel"),
    path("entity/<slug:slug>/members_contact_excel/", views_rep.members_contact_excel, name="members_contact_excel"),
    path("entity/<slug:slug>/next_of_kin_excel/", views_rep.next_of_kin_excel, name="next_of_kin_excel"),
    path("entity/<slug:slug>/financial_report_excel/", views_rep.financial_report_excel, name="financial_report_excel"),
    
    ## ================================================================================================================
    path("entity/<slug:slug>/deposit-withdrawal/", views.deposit_withdrawal_manage, name="deposit_withdrawal_manage"),
    path("entity/<slug:slug>/deposit-withdrawal/<int:pk>/edit/", views.deposit_withdrawal_edit, name="deposit_withdrawal_edit"),
    path("entity/<slug:slug>/deposit-withdrawal/<int:pk>/delete/", views.deposit_withdrawal_delete, name="deposit_withdrawal_delete"),
    path("entity/<slug:slug>/deposit-withdrawal/<int:pk>/view/", views.deposit_withdrawal_view, name="deposit_withdrawal_view"),
    
    ## ========================== Trans Create ====================================================
    path("entity/<slug:slug>/trans-create/",           views.trans_create, name="trans_create"),
    path("entity/<slug:slug>/trans/<int:pk>/",         views.trans_view,   name="trans_view"),
    path("entity/<slug:slug>/trans/<int:pk>/edit/",    views.trans_edit,   name="trans_edit"),
    path("entity/<slug:slug>/trans/<int:pk>/delete/",  views.trans_delete, name="trans_delete"),
    path("entity/<slug:slug>/trans/<int:pk>/pdf/",     views.trans_pdf,    name="trans_pdf"),
    path("entity/<slug:slug>/trans/<int:pk>/excel/",   views.trans_excel,  name="trans_excel"),
    
    ## ==========================Savings Calculations=================================================
    
    # path("entity/<slug:slug>/MembersApp/<int:pk>/view-images/", views_image.view_member_images, name="view_member_images"),
    # path("entity/<slug:slug>/MembersApp/member_images/", views_image.member_images, name="member_images"),
    # path("entity/<slug:slug>/MembersApp/member_images/<int:pk>/", views_image.member_images, name="member_images"),
    # path('member/image/delete/<int:pk>/', views_image.delete_image, name='delete_image'),
    ## =========================Savings Interest Calculations ===================================
    # path("entity/<slug:slug>/MembersApp/savings_dashboard/", views_min_sav.savings_dashboard, name="savings_dashboard"),
    # path("entity/<slug:slug>/MembersApp/process_savings_interest/", views_min_sav.process_savings_interest, name="min_sav_process"),
    # path("entity/<slug:slug>/MembersApp/sav_int_process_list/", views_min_sav.sav_int_process_list, name="sav_int_process_list"),
    # path("entity/<slug:slug>/MembersApp/members_sav_int_list/", views.members_sav_int_list, name="members_sav_int_list"),
    # Delete image
    # path("entity/<slug:slug>/member/<int:pk>/image/delete/<str:image_type>/", views_image.delete_member_image, name="delete_member_image"),
    # path("entity/<slug:slug>/report/modal/", views.report_modal, name="report_modal"),
    # path("entity/<slug:slug>/updated/member/list/", views.updated_member_list, name="updated_member_list"),
]
