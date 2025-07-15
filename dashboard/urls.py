from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('super-admin/', views.super_admin, name='super_admin'),
    path('alerts/', views.alerts, name='alerts'),
    path('activities/', views.activities, name='activities'),
    path('tasks/', views.tasks, name='tasks'),
    path('reports/', views.reports, name='reports'),
    path('reports/generate/', views.generate_report, name='generate_report'),
    path('help/', views.help, name='help'),
    path('settings/', views.settings, name='settings'),
    path('system-status/', views.system_status, name='system_status'),
    path('activity/<int:activity_id>/', views.activity_detail, name='activity_detail'),
    path('dismiss-notification/<int:notification_id>/', views.dismiss_notification, name='dismiss_notification'),
    path('audit-log/', views.activities, name='audit_log'),
] 