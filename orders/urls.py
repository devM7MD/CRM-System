from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.OrderListView.as_view(), name='list'),
    path('create/', views.OrderCreateView.as_view(), name='create'),
    path('<int:pk>/', views.OrderDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', views.OrderUpdateView.as_view(), name='update'),
    path('import/', views.import_orders, name='import'),
    path('<int:order_id>/invoice/', views.download_invoice, name='invoice'),
    path('<int:order_id>/process/', views.process_order, name='process'),
    path('<int:order_id>/cancel/', views.cancel_order, name='cancel'),
    path('<int:order_id>/print/', views.print_order, name='print'),
] 