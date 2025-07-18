from django.urls import path
from . import views

app_name = 'subscribers'

urlpatterns = [
    path('', views.subscribers_list, name='list'),
    path('add/', views.add_user, name='add_user'),
    path('user/<int:user_id>/', views.view_details, name='view_details'),
    path('user/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('user/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('user/<int:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
    path('export/', views.export_users, name='export_users'),
] 