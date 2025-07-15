from django.urls import path
from . import views

app_name = 'packaging'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('orders/', views.order_list, name='orders'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/package/', views.package_order, name='package_order'),
] 