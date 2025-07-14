from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Sales list (another name for finance_list)
    path('sales/', views.finance_list, name='list'),
    
    # Main finance list
    path('', views.finance_list, name='finance_list'),
    
    # Payment management
    path('add-payment/', views.add_payment, name='add_payment'),
    
    # New URL patterns for Quick Actions
    path('create-invoice/', views.create_invoice, name='create_invoice'),
    path('financial-reports/', views.financial_reports, name='financial_reports'),
    path('settings/', views.finance_settings, name='finance_settings'),
    path('pending-payments/', views.pending_payments, name='pending_payments'),
    
    # API endpoints
    path('api/seller-orders/', views.get_seller_orders, name='get_seller_orders'),
    path('api/update-fees/<int:order_id>/', views.update_fees, name='update_fees'),
    path('api/invoice/<int:order_id>/', views.generate_invoice, name='generate_invoice'),
] 