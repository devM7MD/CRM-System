from django.urls import path
from . import views

app_name = 'followup'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('orders/', views.order_list, name='orders'),
] 