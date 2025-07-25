from django.urls import path
from . import views

app_name = 'packaging'

urlpatterns = [
    # Main views
    path('', views.dashboard, name='dashboard'),
    path('orders/', views.order_list, name='orders'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    
    # Packaging operations
    path('orders/<int:order_id>/start/', views.start_packaging, name='start_packaging'),
    path('orders/<int:order_id>/complete/', views.complete_packaging, name='complete_packaging'),
    
    # Reports and Management
    path('report/', views.packaging_report, name='packaging_report'),
    path('materials-management/', views.materials_management, name='materials_management'),
    
    # Materials and inventory
    path('materials/', views.materials_inventory, name='materials_inventory'),
    
    # Quality control
    path('quality-control/', views.quality_control, name='quality_control'),
    path('quality-check/<int:packaging_id>/', views.perform_quality_check, name='perform_quality_check'),
    
    # API endpoints
    path('api/materials/', views.api_get_materials, name='api_get_materials'),
    path('api/materials/<int:material_id>/update-stock/', views.api_update_material_stock, name='api_update_material_stock'),
] 