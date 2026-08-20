from django.urls import path
from . import views

app_name = 'CustomReports'

urlpatterns = [
    path('custom/dashboard/', views.dashboard, name='dashboard'),
    path('custom/build/', views.custom_report_builder, name='custom_report_builder'),
    path('get-table-columns/', views.get_table_columns, name='get_table_columns'),
    path('generate-pdf/', views.generate_custom_pdf, name='generate_custom_pdf'),
    path('generate-excel/', views.generate_custom_excel, name='generate_custom_excel'),
    path('load-saved-report/<int:report_id>/', views.load_saved_report, name='load_saved_report'),
]