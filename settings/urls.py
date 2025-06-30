from django.urls import path
from . import views

app_name = 'settings'

urlpatterns = [
    # Dashboard
    path('', views.settings_dashboard, name='dashboard'),
    
    # Country Management
    path('countries/', views.country_list, name='country_list'),
    path('countries/add/', views.country_create, name='country_create'),
    path('countries/<int:pk>/edit/', views.country_edit, name='country_edit'),
    path('countries/<int:pk>/delete/', views.country_delete, name='country_delete'),
    
    # Delivery Company Management
    path('delivery-companies/', views.delivery_company_list, name='delivery_company_list'),
    path('delivery-companies/add/', views.delivery_company_create, name='delivery_company_create'),
    path('delivery-companies/<int:pk>/edit/', views.delivery_company_edit, name='delivery_company_edit'),
    path('delivery-companies/<int:pk>/delete/', views.delivery_company_delete, name='delivery_company_delete'),
    
    # Fees Management
    path('fees/', views.fees_management, name='fees_management'),
    
    # User Management (redirects to Users app)
    path('users/', views.user_management, name='user_management'),
] 