# LoginApp/urls.py
from django.urls import path
from . import views

app_name = 'LoginApp'

urlpatterns = [
    path('dashboard/', views.login_dashboard, name='login_dashboard'),
    path('member/', views.member_login_history, name='member_login_history'),
    path('member/<int:member_id>/', views.member_login_history, name='member_login_history_detail'),
    path('admin/', views.admin_login_history, name='admin_login_history'),
    path('member/login/', views.member_login, name='member_login'),
]