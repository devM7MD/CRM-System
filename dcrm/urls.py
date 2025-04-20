from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('users/', views.users, name='users'),
    path('roles/', views.roles, name='roles'),
    path('orders/', views.orders, name='orders'),
    path('delivery/', views.delivery, name='delivery'),
    path('sourcing/', views.sourcing, name='sourcing'),
    path('warehouses/', views.warehouses, name='warehouses'),
    path('inventory/', views.inventory, name='inventory'),
    path('finances/', views.finances, name='finances'),
    path('marketplace/', views.marketplace, name='marketplace'),
    path('affiliate/', views.affiliate, name='affiliate'),
    path('atlasdrop/', views.atlasdrop, name='atlasdrop'),
    path('settings/', views.settings, name='settings'),
    path('logout/', views.logout_view, name='logout'),
]