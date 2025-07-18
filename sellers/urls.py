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
    
    # Order management URLs
    path('orders/', views.order_list, name='orders'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    
    # Sales related URLs
    path('sales/', views.sales, name='sales'),
    
    # Inventory URL
    path('inventory/', views.inventory, name='inventory'),
    
    # Sourcing request URLs
    path('sourcing-requests/', views.sourcing_request_list, name='sourcing_requests'),
    path('sourcing-requests/create/', views.sourcing_request_create, name='sourcing_request_create'),
    path('sourcing-requests/<int:request_id>/', views.sourcing_request_detail, name='sourcing_request_detail'),
] 