from django.urls import path
from . import views

app_name = 'warehouse'

urlpatterns = [
    path('', views.warehouse_dashboard, name='dashboard'),
    path('list/', views.warehouse_list, name='warehouse_list'),
    path('add/', views.add_warehouse, name='add_warehouse'),
    path('<int:pk>/', views.warehouse_detail, name='warehouse_detail'),
    path('<int:pk>/edit/', views.edit_warehouse, name='edit_warehouse'),
    path('<int:pk>/delete/', views.delete_warehouse, name='delete_warehouse'),
] 