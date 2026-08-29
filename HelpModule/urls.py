# help_module/urls.py
from django.urls import path
from . import views

app_name = 'Help_Module'

urlpatterns = [
    path('', views.help_dashboard, name='dashboard'),
    path('search/', views.help_search, name='search'),
    path('category/<slug:category_slug>/', views.help_category, name='category'),
    path('topic/<slug:topic_slug>/', views.help_topic, name='topic'),
    path('module/<str:module_name>/', views.module_help, name='module_help'),
    path('guide/<slug:guide_slug>/', views.user_guide_detail, name='user_guide'),
    path('feedback/<int:topic_id>/', views.help_feedback, name='feedback'),
    path('contextual/', views.help_contextual, name='contextual'),
]