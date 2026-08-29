# urls.py
from django.urls import path
from . import views

from .views import run_interest_accrual

app_name =  'services'


urlpatterns = [
#    path('', views.service_home, name='service_home'),
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/list/', views.transaction_list, name='transaction_list_alt'),
 
    
    # 02/06/2026
   # path('loan/daily/update/', views.manual_loan_update, name='manual_loan_update'),
    path('services/loan_daily_update/', views.run_loan_daily_update, name='loan_daily_update'),
    
    # 05/06/2026
    path('interest-accrual/', views.sav_run_interest_accrual, name='sav_run_interest_accrual'),
    path('interest-accrual/results/', views.sav_interest_accrual_results, name='sav_interest_accrual_results'),
    
   # path('entitydaily_intersettransaction_post/', views.transactionpostingservice, name='transactionpostingservice'),
    path('interest-accrual/<slug:entity_slug>/', run_interest_accrual, name='run_interest_accrual'),
    
    path('entity-config/<slug:entity_slug>/', views.edit_entity_config, name='edit_entity_config'),
    path('daily-loan-interest/<slug:entity_slug>/', views.run_daily_loan_interest, name='daily_loan_interest'),
    #path('daily-loan-interest/<slug:entity_slug>/', views.run_daily_loan_interest, name='daily_loan_interest')
   
]
