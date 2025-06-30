from django.urls import path
from . import views

app_name = 'followup'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('orders/', views.order_list, name='orders'),
    path('create/', views.create_followup, name='create'),
    path('detail/<int:followup_id>/', views.followup_detail, name='detail'),
    path('feedback/', views.feedback_list, name='feedback'),
    path('feedback/record/<int:order_id>/', views.record_feedback, name='record_feedback'),
] 