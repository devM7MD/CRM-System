from django.urls import path
from . import views

app_name = 'roles'

urlpatterns = [
    path('', views.role_list, name='role_list'),
    path('create/', views.role_create, name='role_create'),
    path('<int:role_id>/', views.role_detail, name='role_detail'),
    path('<int:role_id>/edit/', views.role_edit, name='role_edit'),
    path('<int:role_id>/delete/', views.role_delete, name='role_delete'),
    path('<int:role_id>/permissions/', views.update_role_permissions, name='update_permissions'),
    path('assign/<int:user_id>/', views.assign_user_role, name='assign_user_role'),
] 