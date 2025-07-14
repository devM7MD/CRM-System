from django.urls import path
from . import views

app_name = 'subscribers'

urlpatterns = [
    path('', views.subscribers_list, name='list'),
    path('dashboard/', views.subscribers_list, name='dashboard'),
    path('add/', views.add_user, name='add_user'),
    path('<int:pk>/', views.subscriber_detail, name='detail'),
    path('seller/<str:seller_id>/', views.subscriber_detail, name='seller_detail'),
    path('<int:pk>/delete/', views.delete_subscriber, name='delete'),
]