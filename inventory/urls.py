from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.inventory_dashboard, name='dashboard'),
    path('products/', views.inventory_products, name='products'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('products/<int:product_id>/deduct-stock/', views.deduct_stock, name='deduct_stock'),
    path('products/<int:product_id>/delete/', views.delete_product, name='delete_product'),
    path('warehouses/', views.warehouse_list, name='warehouses'),
    path('movements/', views.inventory_movements, name='movements'),
    path('export/movements/', views.export_movements, name='export_movements'),
] 