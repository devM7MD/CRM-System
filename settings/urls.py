from django.urls import path
from . import views

app_name = 'settings'

urlpatterns = [
    path('', views.settings_dashboard, name='dashboard'),
    path('countries/', views.countries_management, name='countries'),
    path('delivery-companies/', views.delivery_companies_management, name='delivery_companies'),
    path('users/', views.users_management, name='users'),
    path('fees/', views.fees_management, name='fees'),
] 