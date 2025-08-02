from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('list/', views.user_list, name='list'),
    path('create/', views.user_create, name='create'),
    path('edit/<int:user_id>/', views.user_edit, name='edit'),
    path('detail/<int:user_id>/', views.user_detail, name='detail'),
    
    # Role Management URLs
    path('<int:user_id>/add-role/', views.add_user_role, name='add_role'),
    path('remove-role/<int:user_role_id>/', views.remove_user_role, name='remove_role'),
    path('toggle-primary-role/<int:user_role_id>/', views.toggle_primary_role, name='toggle_primary_role'),
    path('profile/', views.profile, name='profile'),
    path('password-change/', views.password_change, name='password_change'),
    
    # AJAX endpoints for profile management
    path('profile/update/', views.profile_update, name='profile_update'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('profile/notification-settings/', views.notification_settings, name='notification_settings'),
    path('profile/security-settings/', views.security_settings, name='security_settings'),
] 