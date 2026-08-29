from django.urls import path
from . import views

app_name = "Dividend"

urlpatterns = [
    path("entity/<slug:slug>/dashboard/", views.dividend_home, name="union_dashboard"),
    # Dividend
    path("entity/<slug:slug>/dividend-appropriation/", views.dividend_appropriation_preview, name="dividend_appropriation_preview"),
    path("entity/<slug:slug>/dividend-appropriation/execute/", views.dividend_appropriation_execute, name="dividend_appropriation_execute"),
    path("entity/<slug:slug>/dividend-appropriation/pdf/", views.dividend_appropriation_pdf, name="dividend_appropriation_pdf"),
    path("entity/<slug:slug>dividend-appropriation/excel/", views.dividend_appropriation_excel, name="dividend_appropriation_excel"),
    
   
]
