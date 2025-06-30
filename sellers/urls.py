from django.urls import path
from . import views

app_name = 'sellers'

urlpatterns = [
    # Dashboard URL
    path('', views.dashboard, name='dashboard'),
    
    # Product management URLs
    path('products/', views.product_list, name='products'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('products/<int:product_id>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:product_id>/delete/', views.product_delete, name='product_delete'),
    path('products/<int:product_id>/update-stock/', views.product_update_stock, name='product_update_stock'),
    
    # Order management URLs
    path('orders/', views.order_list, name='orders'),
    path('orders/create/', views.order_create, name='order_create'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/update/', views.order_update, name='order_update'),
    path('orders/<int:order_id>/cancel/', views.order_cancel, name='order_cancel'),
    
    # Delivery tracking URLs
    path('delivery/', views.delivery_tracking, name='delivery_tracking'),
    path('delivery/export/', views.export_deliveries, name='export_deliveries'),
    path('delivery/<int:delivery_id>/', views.delivery_detail, name='delivery_detail'),
    
    # Finances URLs
    path('finances/', views.finances, name='finances'),
    path('finances/transactions/', views.finance_transactions, name='finance_transactions'),
    path('finances/reports/', views.finance_reports, name='finance_reports'),
    path('finances/export-inventory/', views.export_inventory, name='export_inventory'),
    path('finances/export-transactions/', views.export_transactions, name='export_transactions'),
    
    # Sales Channels URLs
    path('sales-channels/', views.sales_channels, name='sales_channels'),
    path('sales-channels/create/', views.sales_channel_create, name='sales_channel_create'),
    path('sales-channels/<int:channel_id>/', views.sales_channel_detail, name='sales_channel_detail'),
    path('sales-channels/<int:channel_id>/edit/', views.sales_channel_edit, name='sales_channel_edit'),
    path('sales-channels/<int:channel_id>/delete/', views.sales_channel_delete, name='sales_channel_delete'),
    
    # Settings URL
    path('settings/', views.settings, name='settings'),
    path('settings/profile/', views.profile_settings, name='profile_settings'),
    path('settings/security/', views.security_settings, name='security_settings'),
    path('settings/notifications/', views.notification_settings, name='notification_settings'),
    
    # Sales related URLs
    path('sales/', views.sales, name='sales'),
    
    # Inventory URL
    path('inventory/', views.inventory, name='inventory'),
    
    # Sourcing request URLs
    path('sourcing-requests/', views.sourcing_requests, name='sourcing_requests'),
    path('sourcing-requests/create/', views.create_sourcing_request, name='create_sourcing_request'),
    path('sourcing-requests/<int:request_id>/', views.sourcing_request_detail, name='sourcing_request_detail'),
    path('sourcing-requests/<int:request_id>/edit/', views.sourcing_request_edit, name='sourcing_request_edit'),
    path('sourcing-requests/<int:request_id>/delete/', views.sourcing_request_delete, name='sourcing_request_delete'),
    path('sourcing-requests/<int:request_id>/comment/', views.sourcing_request_comment, name='sourcing_request_comment'),
] 