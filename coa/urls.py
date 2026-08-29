from django.urls import path
from . import views


from django.contrib import admin
from django.urls import path, include
from . import views
from . import views_visibility

app_name = 'coa'

urlpatterns = [
    ##
    path('coa/home/', views.coa_home, name='coa_home'),
    path('back/home/', views.back_to_home, name='back_to_home'),
    
 #   path('api/next-accountno/', views.next_accountno_api, name='next_accountno'),
    path('chart-of-accounts/', views.coa_list, name='coa_list'),
    path('chart-of-accounts/reset', views.coa_reset, name='coa_reset'),
  
    path('chart-of-accounts/create/', views.coa_create, name='coa_create'),
    path('chart-of-accounts/<int:pk>/edit/', views.coa_edit, name='coa_edit'),
    path('chart-of-accounts/<int:pk>/detail/', views.coa_detail, name='coa_detail'),
    
   
    
    
    path('chart-of-accounts/<int:pk>/delete/', views.coa_delete, name='coa_delete'),
    path('chart-of-accounts/pdf/', views.coa_pdf, name='coa_pdf'),
    path('chart-of-accounts/excel/', views.coa_excel, name='coa_excel'),
    
#    path('chart-of-accounts/reset/', views.coa_reset, name='coa_reset'),
    path('main/menu/', views.main_menu, name='main_menu'),
    
    # ADD THIS - Initialize COA URL
    path('chart-of-accounts/init/', views.coa_init_standalone, name='coa_init_standalone'),    
    
    # Account Visibility Manager
    path('visibility/', views_visibility.account_visibility_manager, name='account_visibility_manager'),
    path('visibility/save/', views_visibility.save_account_visibility, name='save_account_visibility'),
    path('visibility/reset/', views_visibility.reset_account_visibility, name='reset_account_visibility'),
    path('api/visible-accounts/', views_visibility.get_visible_accounts_api, name='get_visible_accounts'),
    
    

    path('visibility/refresh/', views_visibility.refresh_account_visibility, name='refresh_account_visibility'),


    
    
    
]
