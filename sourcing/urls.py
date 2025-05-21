from django.urls import path
from . import views

app_name = 'sourcing'

urlpatterns = [
    path('', views.sourcing_dashboard, name='dashboard'),
    path('requests/', views.sourcing_request_list, name='requests'),
    path('requests/create/', views.sourcing_request_create, name='create_request'),
    path('requests/<int:request_id>/', views.sourcing_request_detail, name='request_detail'),
    path('suppliers/', views.suppliers_list, name='suppliers'),
] 