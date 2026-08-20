# MembersApp/urls.py
from django.urls import path
from . import views
from . import views_mem_reports
from . import views_image
from . import views_min_sav

app_name = 'MembersApp'

urlpatterns = [
    path("members/home/", views.members_home, name="members_home"),
    path("main/menu/", views.main_menu, name="main_menu"),
    path("entity/<slug:slug>/MembersApp/member_list_manage/", views.member_list_manage, name="member_list_manage"),
    path("members/exit/", views.back_to_home, name="back_to_home"),
    ## ======================== member_list_manage ================================================
    path(
        "entity/<slug:slug>/MembersApp/member_create/",
        views.member_create,
        name="member_create",
    ),
    path("entity/<slug:slug>/MembersApp/member_detail/<int:pk>/detail/", views.member_detail, name="member_detail"),
    path(
        "entity/<slug:slug>/MembersApp/member_view/<int:pk>/",
        views.member_view,
        name="member_view",
    ),
    path(
        "entity/<slug:slug>/MembersApp/member_edit/<int:pk>/edit/",
        views.member_edit,
        name="member_edit",
    ),
    path(
        "entity/<slug:slug>/MembersApp/member_delete/<int:pk>/delete/",
        views.member_delete,
        name="member_delete",
    ),
    path(
        "entity/<slug:slug>/MembersApp/member_pdf/<int:pk>/pdf/",
        views.member_pdf,
        name="member_pdf",
    ),
    path(
        "entity/<slug:slug>/MembersApp/member_excel/<int:pk>/excel/",
        views.member_excel,
        name="member_excel",
    ),
    path("entity/<slug:slug>/MembersApp/member_single_setting/<int:pk>/", views.member_single_setting, name="member_single_setting"),
    ## ===========================PDF Reports======================================================
    path(
        "entity/<slug:slug>/MembersApp/members_info_pdf/",
        views_mem_reports.members_info_pdf,
        name="members_info_pdf",
    ),
    path(
        "entity/<slug:slug>/MembersApp/members_contact_pdf/",
        views_mem_reports.members_contact_pdf,
        name="members_contact_pdf",
    ),
    path(
        "entity/<slug:slug>/MembersApp/next_of_kin_pdf/",
        views_mem_reports.next_of_kin_pdf,
        name="next_of_kin_pdf",
    ),
    path(
        "entity/<slug:slug>/MembersApp/financial_report_pdf/",
        views_mem_reports.financial_report_pdf,
        name="financial_report_pdf",
    ),
    ## ==========================Excel Reports=====================================================
    path(
        "entity/<slug:slug>/MembersApp/members_info_excel/",
        views_mem_reports.members_info_excel,
        name="members_info_excel",
    ),
    path(
        "entity/<slug:slug>/MembersApp/members_contact_excel/",
        views_mem_reports.members_contact_excel,
        name="members_contact_excel",
    ),
    path(
        "entity/<slug:slug>/MembersApp/next_of_kin_excel/",
        views_mem_reports.next_of_kin_excel,
        name="next_of_kin_excel",
    ),
    path(
        "entity/<slug:slug>/MembersApp/financial_report_excel/",
        views_mem_reports.financial_report_excel,
        name="financial_report_excel",
    ),
    ## ==========================Image Management=================================================
    path(
        "entity/<slug:slug>/MembersApp/<int:pk>/view-images/",
        views_image.view_member_images,
        name="view_member_images",
    ),
    path(
        "entity/<slug:slug>/MembersApp/member_images/",
        views_image.member_images,
        name="member_images",
    ),
    path(
        "entity/<slug:slug>/MembersApp/member_images/<int:pk>/",
        views_image.member_images,
        name="member_images",
    ),
    # path('member/image/delete/<int:pk>/', views_image.delete_image, name='delete_image'),
    ## =========================Savings Interest Calculations ===================================
    path(
        "entity/<slug:slug>/MembersApp/savings_dashboard/",
        views_min_sav.savings_dashboard,
        name="savings_dashboard",
    ),
    path(
        "entity/<slug:slug>/MembersApp/process_savings_interest/",
        views_min_sav.process_savings_interest,
        name="min_sav_process",
    ),
    path(
        "entity/<slug:slug>/MembersApp/sav_int_process_list/",
        views_min_sav.sav_int_process_list,
        name="sav_int_process_list",
    ),
    path(
        "entity/<slug:slug>/MembersApp/members_sav_int_list/",
        views.members_sav_int_list,
        name="members_sav_int_list",
    ),
    # Delete image
    path(
        "entity/<slug:slug>/member/<int:pk>/image/delete/<str:image_type>/",
        views_image.delete_member_image,
        name="delete_member_image",
    ),
    path("entity/<slug:slug>/report/modal/", views.report_modal, name="report_modal"),
    path("entity/<slug:slug>/updated/member/list/", views.updated_member_list, name="updated_member_list"),
]
