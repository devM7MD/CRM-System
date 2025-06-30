from django.urls import path
from . import views

app_name = 'roles'

urlpatterns = [
    path('', views.role_list, name='role_list'),
    path('create/', views.create_role, name='create_role'),
    path('<slug:slug>/', views.role_detail, name='role_detail'),
    path('<slug:slug>/edit/', views.edit_role, name='edit_role'),
    path('<slug:slug>/delete/', views.delete_role, name='delete_role'),
] 