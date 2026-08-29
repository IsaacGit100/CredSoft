from django.urls import path
from . import views

app_name = 'Images'

urlpatterns = [
    path("entity/<slug:slug>/MembersApp/<int:pk>/view-images/", views.view_member_images, name="view_member_images"),
    path("entity/<slug:slug>/MembersApp/member_images/", views.member_images, name="member_images"),
    path("entity/<slug:slug>/MembersApp/member_images/<int:pk>/", views.member_images, name="member_images"),
    # path('member/image/delete/<int:pk>/', views_image.delete_image, name='delete_image'),
]