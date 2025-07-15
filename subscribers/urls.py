from django.urls import path
from . import views

app_name = 'subscribers'

urlpatterns = [
    path('', views.subscribers_list, name='list'),
    path('add/', views.add_user, name='add_user'),
] 