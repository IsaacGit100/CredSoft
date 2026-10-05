# urls.py
from django.urls import path
from . import views


app_name = 'Tech'

urlpatterns = [
    path("entity/management/", views.entity_management, name="entity_management"),
    path("entity/create/", views.create_entity, name="create_entity"),
    path("coa/management/", views.coa_management, name="coa_management"),
    path("entity/<slug:slug>/tech_dashboard/", views.tech_dashboard, name="tech_dashboard"),
    path("technical-dashboard/", views.tech_dashboard, name="tech_dashboard"),
    path("user-management/", views.user_management, name="user_management"),
    path("user-management/<int:user_id>/reset-password/", views.reset_user_password, name="reset_user_password"),
    path("entity/<slug:slug>/edit/", views.edit_entity, name="edit_entity"),
    

    path("readiness/", views.system_readiness, name="system_readiness"),
    path("dashboard/", views.tech_dashboard, name="tech_dashboard"),
    
    path("reset-entity/", views.reset_entity_select,  name="reset_entity_select"),
    path("reset-entity/<slug:slug>/", views.reset_entity_confirm, name="reset_entity_confirm"),
    
]
