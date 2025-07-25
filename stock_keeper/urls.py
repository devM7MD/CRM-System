# stock_keeper/urls.py
from django.urls import path
from . import views

app_name = 'stock_keeper'

urlpatterns = [
    # Dashboard and main views
    path('', views.dashboard, name='dashboard'),
    path('warehouses/', views.warehouse_list, name='warehouse_list'),
    path('warehouses/<int:warehouse_id>/', views.warehouse_detail, name='warehouse_detail'),
    
    # Barcode scanning
    path('scanner/', views.barcode_scanner, name='barcode_scanner'),
    path('scan/', views.scan_product, name='scan_product'),
    
    # Stock operations
    path('receive/', views.receive_stock, name='receive_stock'),
    path('ship/', views.ship_orders, name='ship_orders'),
    path('transfer/', views.transfer_stock, name='transfer_stock'),
    
    # History and reports
    path('movements/', views.movement_history, name='movement_history'),
    path('alerts/', views.alerts, name='alerts'),
    path('alerts/<int:alert_id>/resolve/', views.resolve_alert, name='resolve_alert'),
    
    # API endpoints
    path('api/search-product/', views.api_search_product, name='api_search_product'),
    path('api/inventory/<int:product_id>/', views.api_get_inventory, name='api_get_inventory'),
] 