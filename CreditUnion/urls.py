from django.urls import path
from . import views

app_name = "CreditUnion"

urlpatterns = [
    path("entity/<slug:slug>/dashboard/", views.union_dashboard, name="union_dashboard"),
    path('entity/<slug:slug>/run-pending-transactions/', views.run_pending_transactions, name='run_pending_transactions'),
    
    path("sav-int-audit/<slug:entity_slug>/", views.sav_int_audit, name="sav_int_audit"),
    # ... other paths
]
