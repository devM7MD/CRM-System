from django.urls import path
from . import views

app_name = 'delivery'

urlpatterns = [
    # Main delivery views
    path('', views.dashboard, name='dashboard'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<uuid:delivery_id>/update-status/', views.update_status, name='update_status'),
    path('orders/<uuid:delivery_id>/complete/', views.complete_delivery, name='complete_delivery'),
    path('orders/<uuid:delivery_id>/failed/', views.failed_delivery, name='failed_delivery'),
    
    # Performance and settings
    path('performance/', views.performance, name='performance'),
    path('settings/', views.settings, name='settings'),
    
    # API endpoints for mobile integration
    path('api/update-location/', views.update_location, name='api_update_location'),
    path('api/update-availability/', views.update_availability, name='api_update_availability'),
    path('api/courier/<int:courier_id>/orders/', views.get_assigned_orders, name='api_get_assigned_orders'),
    path('api/upload-proof/', views.upload_proof, name='api_upload_proof'),
] 