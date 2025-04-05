from . import views
from django.urls import path

urlpatterns = [
    path('', views.index, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('contact/', views.contact, name='contact'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('resetpassword/', views.forgot_password, name='resetpassword'),
    # path('resetpassword/<uidb64>/<token>/', views.reset_password_confirm, name='password_reset_confirm'),
    # path('resetpassword/done/', views.reset_password_done, name='password_reset_done'),
    # path('resetpassword/confirm/', views.reset_password_confirm, name='password_reset_confirm'),
    # path('resetpassword/complete/', views.reset_password_complete, name='password_reset_complete'),
    
]