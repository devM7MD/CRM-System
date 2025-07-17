from django.urls import path
from . import views

app_name = 'callcenter'

urlpatterns = [
    # Legacy URLs (for backward compatibility)
    path('', views.dashboard, name='dashboard'),
    path('orders/', views.order_list, name='order_list'),
    
    # Manager Panel URLs
    path('manager/', views.manager_dashboard, name='manager_dashboard'),
    path('manager/orders/', views.manager_order_list, name='manager_order_list'),
    path('manager/agents/', views.manager_agent_reports, name='manager_agent_reports'),
    path('manager/assign/<int:order_id>/', views.assign_order, name='assign_order'),
    path('manager/note/<int:order_id>/', views.create_manager_note, name='create_manager_note'),
    
    # Agent Panel URLs
    path('agent/', views.agent_dashboard, name='agent_dashboard'),
    path('agent/orders/', views.agent_order_list, name='agent_order_list'),
    path('agent/order/<int:order_id>/', views.agent_order_detail, name='agent_order_detail'),
    path('agent/order/<int:order_id>/status/', views.update_order_status, name='update_order_status'),
    path('agent/order/<int:order_id>/call/', views.log_call, name='log_call'),
    path('agent/note/<int:note_id>/read/', views.mark_note_read, name='mark_note_read'),
    path('agent/availability/', views.update_availability, name='update_availability'),
    
    # API URLs
    path('api/order/<int:order_id>/', views.get_order_details_api, name='get_order_details_api'),
    path('api/agent/<int:agent_id>/performance/', views.get_agent_performance_api, name='get_agent_performance_api'),
] 