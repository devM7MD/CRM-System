from django.urls import path
from . import views

app_name = 'bug_reports'

urlpatterns = [
    path('report/', views.report_bug, name='report_bug'),
    path('ajax-report/', views.ajax_report_bug, name='ajax_report_bug'),
    path('image/<int:image_id>/', views.serve_bug_image, name='serve_bug_image'),
] 