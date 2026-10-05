from django.contrib import admin
from django.urls import path, include
from . import views
from django.urls import path
from . import views


app_name = 'OpenBals'

from django.urls import path
from . import views

app_name = 'OpenBals'

urlpatterns = [
    # ---------- Batch List & Create ----------
    path('entity/<slug:slug>/OpenBals/list/', views.open_bal_list, name='open_bal_list'),                 # List all batches
    path('entity/<slug:slug>/OpenBals/home/', views.open_bal_home, name='open_bal_home'),
    path('entity/<slug:slug>/openBals/create/', views.open_bal_create, name='open_bal_create'),
    path('entity/<slug:slug>/OpenBals/post-to-trans/', views.open_bal_post_all, name='open_bal_post_all'),
    
    path('entity/<slug:slug>/openBals/pdf/', views.open_bal_pdf, name='open_bal_pdf'),
    path('entity/<slug:slug>/OpenBals/excel/', views.open_bal_excel, name='open_bal_excel'),
    path('entity/<slug:slug>/opening-balance/post-all/', views.open_bal_post_all, name='open_bal_post_all'),
    
]