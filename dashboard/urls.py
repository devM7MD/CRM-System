from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('alerts/', views.alerts, name='alerts'),
    path('activities/', views.activities, name='activities'),
    path('tasks/', views.tasks, name='tasks'),
    path('reports/', views.reports, name='reports'),
    path('help/', views.help, name='help'),
    path('settings/', views.settings, name='settings'),
    path('system-status/', views.system_status, name='system_status'),
    path('activity/<int:activity_id>/', views.activity_detail, name='activity_detail'),
    path('audit-log/', views.audit_log, name='audit_log'),
] 