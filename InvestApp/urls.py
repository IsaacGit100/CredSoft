from django.contrib import admin
from django.urls import path, include
from . import views
from django.urls import path
from . import views
from . import views_PDF
from . import views_excel
from .views import BankListView, BankCreateView, BankUpdateView, BankDeleteView
from django_ledger.models import EntityModel

app_name = 'InvestApp'

urlpatterns = [
    path('entity/<slug:slug>/invest/home/', views.invest_home, name='invest_home'),
    
    path('entity/<slug:slug>/investment/', views.investment_list, name='investment_list'),
    path('entity/<slug:slug>/investments/new/', views.investment_create, name='investment_create'),
    path('entity/<slug:slug>/investments/<int:pk>/edit/', views.investment_update, name='investment_update'),
    path('entity/<slug:slug>/investments/<int:pk>/delete/', views.investment_delete, name='investment_delete'),

    path('entity/<slug:slug>/banks/', views.bank_list, name='bank_list'),
    path('entity/<slug:slug>/banks/new/', views.bank_create, name='bank_create'),
    path('entity/<slug:slug>/banks/<int:pk>/edit/', views.bank_update, name='bank_update'),
    path('entity/<slug:slug>/banks/<int:pk>/delete/', views.bank_delete, name='bank_delete'),
    path('entity/<slug:slug>/calculate-interest/', views.calculate_interest, name='calculate_interest'),

    path('entity/<slug:slug>/banks/', BankListView, name='bank_list'),
    path('entity/<slug:slug>/banks/new/', BankCreateView, name='bank_create'),
    path('entity/<slug:slug>/banks/<int:pk>/edit/', BankUpdateView, name='bank_update'),
    path('entity/<slug:slug>/banks/<int:pk>/delete/', BankDeleteView, name='bank_delete'),

    path('entity/<slug:slug>/investments/export/pdf/', views_PDF.export_investments_pdf, name='investment_export_pdf'),
    path('entity/<slug:slug>/invest/export/excel/', views_excel.invest_export_excel, name='invest_export_excel'),
    path('entity/<slug:slug>/investments/export/print/', views.export_investments_print, name='investment_export_print'),
    path('entity/<slug:slug>/invest/update/list/', views.invest_update_list, name='invest_update_list'),
    
    path('entity/<slug:slug>/update-status/', views.investment_status_update, name='investment_status_update'),
    path('entity/<slug:slug>/update-status/<int:pk>/', views.investment_status_update, name='investment_status_update_pk'),

    path('entity/<slug:slug>/report/quarterly/', views.quarterly_investment_report, name='quarterly_report'),
    path('entity/<slug:slug>/report/quarterly/pdf/', views_PDF.quarterly_report_pdf, name='quarterly_report_pdf'),
    path('entity/<slug:slug>/report/quarterly/excel/', views_excel.quarterly_report_excel, name='quarterly_report_excel'),
    
]