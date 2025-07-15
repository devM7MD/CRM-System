from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('payments/', views.payment_list, name='payments'),
    path('sales/', views.sales_report, name='sales'),
] 