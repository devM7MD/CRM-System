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
    path('profile/', views.profile, name='profile'),
    path('password-change/', views.password_change, name='password_change'),
    
    # AJAX endpoints for profile management
    path('profile/update/', views.profile_update, name='profile_update'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('profile/notification-settings/', views.notification_settings, name='notification_settings'),
    path('profile/security-settings/', views.security_settings, name='security_settings'),
] 