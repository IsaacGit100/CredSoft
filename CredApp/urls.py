# MembersApp/urls.py
from django.urls import path
from . import views
# from . import views_reports_pdf
# from . import views_reports_excel
# from . import views_image
# from . import views_min_sav

app_name = "CredApp"

urlpatterns = [
    path("entity/<slug:slug>/members/home/", views.members_home, name="members_home"),
    path(
        "entity/<slug:slug>/members/list/manage/",
        views.member_list_manage,
        name="member_list_manage",
    ),
    path(
        "entity/<slug:slug>/CredApp/member_create/",
        views.member_create,
        name="member_create",
    ),
    path(
        "entity/<slug:slug>/CredApp/member_edit/<int:pk>/edit/",
        views.member_edit,
        name="member_edit",
    ),
    # path("entity/<slug:slug>/CredApp/member_detail/<int:pk>/", views.member_detail, name="member_detail"),
    path(
        "entity/<slug:slug>/CredApp/member_view/<int:pk>/",
        views.member_view,
        name="member_view",
    ),
    path(
        "entity/<slug:slug>/CredApp/member_delete/<int:pk>/delete/",
        views.member_delete,
        name="member_delete",
    ),
    path(
        "entity/<slug:slug>/CredApp/member_pdf/<int:pk>/pdf/",
        views.member_pdf,
        name="member_pdf",
    ),
    path(
        "entity/<slug:slug>/CredApp/member_excel/<int:pk>/excel/",
        views.member_excel,
        name="member_excel",
    ),
    path(
        "entity/<slug:slug>/CredApp/member_sett",
        views.member_sett,
        name="member_set",
    ),
    
]
