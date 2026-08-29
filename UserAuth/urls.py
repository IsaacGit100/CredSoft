# UserAuth/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

from django.urls import path
from .views import CustomPasswordChangeView
from django.contrib.auth.views import PasswordChangeDoneView

app_name = 'userauth'

urlpatterns = [
    # Authentication
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
   
    
    # User Profile
    path('profile/', views.user_profile, name='user_profile'),
    path('change-password/', views.change_password, name='change_password'),
    
    # Password Reset - Custom Views
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('password-reset/done/', views.password_reset_done, name='password_reset_done'),
    path('reset-password/confirm/<int:user_id>/<str:token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('reset-password/complete/', views.password_reset_complete, name='password_reset_complete'),
    
    # User Management (Admin only)
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:pk>/', views.user_detail, name='user_detail'),
    path('users/<int:pk>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),
    path('users/<int:pk>/toggle-status/', views.user_toggle_status, name='user_toggle_status'),
    path('users/<int:pk>/reset-password/', views.user_reset_password, name='user_reset_password'),
    
    path('change-password/', CustomPasswordChangeView.as_view(), name='change_password'),
    path('password-changed/', PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='password_change_done'),
    
    path('change-password/', views.change_password, name='change_password'),
    
    path('logout/', views.custom_logout, name='logout'), 
    path('logout/view/', views.logout_view, name='logout'),
    path('logout/confirm/', views.logout_confirm, name='logout_confirm'),
    
]