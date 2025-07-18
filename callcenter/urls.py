from django.urls import path
from . import views

app_name = 'callcenter'

urlpatterns = [
    # Legacy URLs for backward compatibility
    path('', views.dashboard, name='dashboard'),
    path('orders/', views.order_list, name='orders'),
    
    # Agent Panel URLs
    path('agent/', views.agent_dashboard, name='agent_dashboard'),
    path('agent/orders/', views.agent_order_list, name='agent_order_list'),
    path('agent/orders/<int:order_id>/', views.agent_order_detail, name='agent_order_detail'),
    path('agent/orders/<int:order_id>/log-call/', views.agent_log_call, name='agent_log_call'),
    
    # Manager Panel URLs
    path('manager/', views.manager_dashboard, name='manager_dashboard'),
    path('manager/orders/', views.manager_order_list, name='manager_order_list'),
    path('manager/orders/<int:order_id>/assign/', views.manager_assign_order, name='manager_assign_order'),
    path('manager/reports/', views.manager_agent_reports, name='manager_agent_reports'),
    
    # API URLs for AJAX
    path('api/update-status/', views.update_agent_status, name='update_agent_status'),
    path('api/orders/<int:order_id>/details/', views.get_order_details, name='get_order_details'),
] 