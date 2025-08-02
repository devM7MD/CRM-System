from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    # Main Accountant Dashboard
    path('', views.accountant_dashboard, name='accountant_dashboard'),
    path('dashboard/', views.accountant_dashboard, name='dashboard'),
    
    # Order Financial Management
    path('orders/', views.order_financial_management, name='order_management'),
    
    # Fee Management
    path('orders/<int:order_id>/fees/', views.fee_management, name='fee_management'),
    
    # Payment Processing
    path('payments/process/', views.payment_processing, name='payment_processing'),
    
    # AJAX endpoints for seller details and payment history
    path('seller/<int:seller_id>/details/', views.seller_details, name='seller_details'),
    path('seller/<int:seller_id>/payments/', views.seller_payments, name='seller_payments'),
    
    # Invoice Generation
    path('orders/<int:order_id>/invoice/', views.invoice_generation, name='invoice_generation'),
    
    # Financial Reports
    path('reports/', views.financial_reports, name='financial_reports'),
    path('reports/print/', views.financial_reports_print, name='financial_reports_print'),
    
    # Bank Reconciliation
    path('reconciliation/', views.bank_reconciliation, name='bank_reconciliation'),
    
    # Legacy URLs for backward compatibility
    path('payments/', views.payment_list, name='payments'),
    path('sales/', views.sales_report, name='sales'),
] 