from django.urls import path
from . import views

app_name = 'warehouse_inventory'

urlpatterns = [
    # Warehouse Management
    path('warehouses/', views.warehouse_list, name='warehouse_list'),
    path('warehouses/create/', views.warehouse_create, name='warehouse_create'),
    path('warehouses/<int:warehouse_id>/edit/', views.warehouse_edit, name='warehouse_edit'),
    path('warehouses/<int:warehouse_id>/delete/', views.warehouse_delete, name='warehouse_delete'),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Warehouse inventory
    path('warehouse/<int:warehouse_id>/', views.warehouse_inventory, name='warehouse_inventory'),
    path('warehouse/<int:warehouse_id>/add/', views.add_to_inventory, name='add_to_inventory'),
    path('warehouse/<int:warehouse_id>/movement/', views.inventory_movement, name='inventory_movement'),
    path('warehouse/<int:warehouse_id>/movements/', views.warehouse_movements, name='warehouse_movements'),
    
    # Search and tracking
    path('search/', views.search_inventory, name='search'),
    path('barcode-scan/', views.barcode_scan, name='barcode_scan'),
    path('tracking/<str:tracking_number>/', views.tracking_details, name='tracking_details'),
    
    # API endpoints
    path('api/inventory/movements/product/<int:product_id>/', views.product_movements, name='product_movements'),
] 