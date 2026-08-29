# urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'core'

urlpatterns = [
    # Authentication
#    path('', views.login_view, name='home'),  # Redirect to login
#    path('login/', views.login_view, name='login'),
#    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
    
    
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Profile
    path('profile/', views.profile, name='profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('password_reset/', views.profile, name='password_reset'),
]


