# urls.py
from django.urls import path
from . import views

app_name = 'AndyApp'


urlpatterns = [
    path('entity/<slug:slug>/andy/home/', views.andy_home, name='andy_home'),
    path('entity/<slug:slug>/andy/master/', views.master_list, name='master_list'),
    path('entity/<slug:slug>/andy/trans_update/', views.trans_update, name='trans_update'),
]
