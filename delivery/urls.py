from django.urls import path
from . import views

app_name = 'delivery'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('orders/', views.order_list, name='order_list'),
    path('assign/', views.assign_orders, name='assign_orders'),
    path('couriers/', views.courier_management, name='courier_management'),
    path('couriers/<int:courier_id>/', views.courier_detail, name='courier_detail'),
    path('tracking/', views.delivery_tracking, name='tracking'),
    path('tracking/<str:tracking_number>/', views.delivery_tracking, name='tracking_detail'),
    path('update-status/<int:delivery_id>/', views.update_delivery_status, name='update_status'),
    path('barcode-scan/', views.barcode_scan, name='barcode_scan'),
    path('api/barcode-scan/', views.barcode_scan_api, name='barcode_scan_api'),
    path('api/couriers-by-company/<int:company_id>/', views.get_couriers_by_company, name='couriers_by_company'),
    path('add-courier/', views.add_courier, name='add_courier'),
    path('add-company/', views.add_company, name='add_company'),
    
    path('panel/', views.delivery_panel_dashboard, name='panel_dashboard'),
    path('panel/login/', views.delivery_panel_login, name='panel_login'),
    path('panel/logout/', views.delivery_panel_logout, name='panel_logout'),
    path('panel/orders/', views.delivery_panel_orders, name='panel_orders'),
    path('panel/orders/<int:order_id>/', views.delivery_panel_order_detail, name='panel_order_detail'),
    path('panel/update-status/<int:order_id>/', views.delivery_panel_update_status, name='panel_update_status'),
    path('panel/complete-delivery/<int:order_id>/', views.delivery_panel_complete_delivery, name='panel_complete_delivery'),
    path('panel/failed-delivery/<int:order_id>/', views.delivery_panel_failed_delivery, name='panel_failed_delivery'),
    path('panel/performance/', views.delivery_panel_performance, name='panel_performance'),
    path('panel/settings/', views.delivery_panel_settings, name='panel_settings'),
    
    path('api/panel/update-location/', views.api_update_courier_location, name='api_update_location'),
    path('api/panel/courier-status/', views.api_update_courier_status, name='api_update_status'),
    path('api/panel/orders/', views.api_get_courier_orders, name='api_get_orders'),
    path('api/panel/route/', views.api_get_optimized_route, name='api_get_route'),
    path('api/panel/send-sms/<int:order_id>/', views.api_send_sms_to_customer, name='api_send_sms'),
] 