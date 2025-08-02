from django.urls import path
from . import views

app_name = 'sourcing'

urlpatterns = [
    path('', views.sourcing_dashboard, name='dashboard'),
    path('requests/', views.sourcing_request_list, name='requests'),
    path('requests/create/', views.sourcing_request_create, name='create_request'),
    path('requests/<int:request_id>/', views.sourcing_request_detail, name='request_detail'),
    path('requests/<int:request_id>/approve/', views.approve_sourcing_request, name='approve_request'),
    path('requests/<int:request_id>/reject/', views.reject_sourcing_request, name='reject_request'),
    path('suppliers/', views.suppliers_list, name='suppliers'),
    path('suppliers/add/', views.add_supplier, name='add_supplier'),
    path('suppliers/<int:supplier_id>/view/', views.view_supplier, name='view_supplier'),
    path('suppliers/<int:supplier_id>/edit/', views.edit_supplier, name='edit_supplier'),
    path('suppliers/<int:supplier_id>/delete/', views.delete_supplier, name='delete_supplier'),
] 