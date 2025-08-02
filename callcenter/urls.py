from django.urls import path
from . import views

app_name = 'callcenter'

urlpatterns = [
    # Legacy URLs for backward compatibility
    path('', views.dashboard, name='dashboard'),
    path('orders/', views.order_list, name='orders'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    
    # Agent Panel URLs
    path('agent/', views.agent_dashboard, name='agent_dashboard'),
    path('agent/orders/', views.agent_order_list, name='agent_order_list'),
    path('agent/orders/<int:order_id>/', views.agent_order_detail, name='agent_order_detail'),
    path('agent/orders/<int:order_id>/log-call/', views.agent_log_call, name='agent_log_call'),
    path('agent/reports/', views.agent_reports, name='agent_reports'),
    
    # Manager Panel URLs
    path('manager/', views.manager_dashboard, name='manager_dashboard'),
    path('manager/orders/', views.manager_order_list, name='manager_order_list'),
    path('manager/orders/<int:order_id>/assign/', views.manager_assign_order, name='manager_assign_order'),
    path('manager/reports/', views.manager_agent_reports, name='manager_agent_reports'),
    
    # Enhanced Manager URLs
    path('manager/orders/<int:order_id>/', views.manager_order_detail, name='manager_order_detail'),
    path('manager/agents/<int:agent_id>/report/', views.agent_performance_report, name='agent_performance_report'),
    path('manager/orders/bulk-assign/', views.bulk_assign_orders, name='bulk_assign_orders'),
    path('manager/export/report/', views.export_performance_report, name='export_performance_report'),
    
    # API URLs for AJAX
    path('api/update-status/', views.update_agent_status, name='update_agent_status'),
    path('api/orders/<int:order_id>/details/', views.get_order_details, name='get_order_details'),
    path('api/orders/<int:order_id>/assign/', views.assign_order_api, name='assign_order_api'),
    path('api/agents/<int:agent_id>/performance/', views.get_agent_performance, name='get_agent_performance'),
    path('api/orders/export/', views.export_orders_api, name='export_orders_api'),
    
    # Settings and Configuration URLs
    path('manager/settings/', views.manager_settings, name='manager_settings'),
    path('manager/settings/save/', views.save_settings, name='save_settings'),
    path('manager/orders/bulk-assign/', views.bulk_assign_orders, name='bulk_assign_orders'),
] 