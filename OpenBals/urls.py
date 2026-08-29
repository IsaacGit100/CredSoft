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
    path('entity/<slug:slug>/open_bals_list/', views.opening_balance_list, name='opening_balance_list'),                 # List all batches
    path('entity/<slug:slug>/opening_balance/create/', views.opening_balance_create, name='opening_balance_create'), 
    path('entity/<slug:slug>/open/balance/home/', views.opening_balance_home, name='opening_balance_home'),  

    # ---------- Batch Detail & Edit ----------
        # View a specific batch
    path('entity/<slug:slug>/opening_balance_edit/<int:pk>/edit/', views.opening_balance_edit, name='opening_balance_edit'),   
    path('entity/<slug:slug>/open_bal_delete/<int:pk>/delete/', views.opening_balance_delete, name='opening_balance_delete'),  # Delete a draft batch

    # ---------- Workflow Actions ----------
    path('', views.opening_balance_list, name='list'),
#    path('add/', views.opening_balance_add, name='add'),
    path('entity/<slug:slug>/<int:pk>/edit/', views.opening_balance_edit, name='edit'),
    path('entity/<slug:slug>/<int:pk>/delete/', views.opening_balance_delete, name='delete'),

    path('entity/<slug:slug>/open/balance/approve/', views.opening_balance_approve, name='opening_balance_approve'), 
    path('entity/<slug:slug>/post/execute/', views.opening_balance_post_execute, name='opening_balance_post_execute'),
    path('entity/<slug:slug>/open/balance/post/page/', views.opening_balance_post_page, name='opening_balance_post_page'),
    
    path('entity/<slug:slug>/export/excel/', views.export_excel, name='export_excel'),
    path('entity/<slug:slug>/export/pdf/', views.export_pdf, name='export_pdf'),
    path('entity/<slug:slug>/update-date/', views.bulk_update_date, name='bulk_update_date'),
    
    path('entity/<slug:slug>/clear-default-date/', views.clear_default_date, name='clear_default_date'),
    
]