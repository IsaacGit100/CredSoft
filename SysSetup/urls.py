from django.urls import path
from . import views
# import UserAuth

app_name = 'SysSetup'

urlpatterns = [
    # Authentication
    path('', views.dashboard, name='dashboard'),
    path('Company/Setup/', views.company_setup, name='company_setup'),
]