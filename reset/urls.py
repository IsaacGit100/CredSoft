from django.urls import path
from . import views

app_name = 'reset'

urlpatterns = [
    path('confirm/', views.confirm_reset, name='confirm'),
    path('perform/', views.perform_reset, name='perform'),
]