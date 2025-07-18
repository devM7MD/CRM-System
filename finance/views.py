from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg, Q, F
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import datetime, timedelta
import json
from .models import Payment
from orders.models import Order
from products.models import Product
from sellers.models import Seller

# Create your views here.

@login_required
def dashboard(request):
    """Finance dashboard with real data."""
    # Calculate financial metrics
    total_revenue = Payment.objects.filter(payment_status='completed').aggregate(total=Sum('amount'))['total'] or 0
    total_expenses = 0  # No Expense model, so set expenses to 0 for now
    net_profit = total_revenue - total_expenses
    pending_payments = Payment.objects.filter(payment_status='pending').count()
    
    # Recent payments
    recent_payments = Payment.objects.select_related('order', 'order__customer').order_by('-payment_date')[:5]
    
    # Payment method distribution
    payment_methods = Payment.objects.values('payment_method').annotate(count=Count('payment_method'))
    
    # Monthly revenue trend (last 6 months)
    monthly_revenue = []
    for i in range(6):
        month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
        month_end = month_start.replace(day=28) + timedelta(days=4)
        month_end = month_end.replace(day=1) - timedelta(days=1)
        
        revenue = Payment.objects.filter(
            payment_status='completed',
            payment_date__gte=month_start,
            payment_date__lte=month_end
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        monthly_revenue.append({
            'month': month_start.strftime('%B %Y'),
            'revenue': float(revenue)
        })
    
    context = {
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'net_profit': net_profit,
        'pending_payments': pending_payments,
        'recent_payments': recent_payments,
        'payment_methods': payment_methods,
        'monthly_revenue': monthly_revenue,
    }
    return render(request, 'finance/dashboard.html', context)

@login_required
def payment_list(request):
    """List of payments with filtering and pagination."""
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    payment_method_filter = request.GET.get('payment_method', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    search_query = request.GET.get('search', '')
    
    # Base queryset
    payments = Payment.objects.select_related('order', 'order__customer').order_by('-payment_date')
    
    # Apply filters
    if status_filter:
        payments = payments.filter(payment_status=status_filter)
    
    if payment_method_filter:
        payments = payments.filter(payment_method=payment_method_filter)
    
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            payments = payments.filter(payment_date__date__gte=date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            payments = payments.filter(payment_date__date__lte=date_to_obj)
        except ValueError:
            pass
    
    if search_query:
        payments = payments.filter(
            Q(order__order_code__icontains=search_query) |
            Q(order__customer__full_name__icontains=search_query) |
            Q(transaction_id__icontains=search_query) |
            Q(notes__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(payments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter options
    status_choices = Payment.PAYMENT_STATUS
    payment_method_choices = Payment.PAYMENT_METHODS
    
    context = {
        'page_obj': page_obj,
        'status_choices': status_choices,
        'payment_method_choices': payment_method_choices,
        'current_status': status_filter,
        'current_payment_method': payment_method_filter,
        'date_from': date_from,
        'date_to': date_to,
        'search_query': search_query,
    }
    
    return render(request, 'finance/payment_list.html', context)

@login_required
def sales_report(request):
    """Sales report with analytics."""
    # Get date range from request
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Base queryset
    payments = Payment.objects.filter(payment_status='completed')
    
    # Apply date filters
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            payments = payments.filter(payment_date__date__gte=date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            payments = payments.filter(payment_date__date__lte=date_to_obj)
        except ValueError:
            pass
    
    # Calculate metrics
    total_sales = payments.aggregate(total=Sum('amount'))['total'] or 0
    total_orders = payments.values('order').distinct().count()
    avg_order_value = total_sales / total_orders if total_orders > 0 else 0
    
    # Payment method breakdown
    payment_method_breakdown = payments.values('payment_method').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    # Daily sales trend (last 30 days)
    daily_sales = []
    for i in range(30):
        date = timezone.now().date() - timedelta(days=i)
        daily_total = payments.filter(payment_date__date=date).aggregate(total=Sum('amount'))['total'] or 0
        daily_sales.append({
            'date': date.strftime('%Y-%m-%d'),
            'total': float(daily_total)
        })
    
    daily_sales.reverse()  # Show oldest first
    
    context = {
        'total_sales': total_sales,
        'total_orders': total_orders,
        'avg_order_value': avg_order_value,
        'payment_method_breakdown': payment_method_breakdown,
        'daily_sales': daily_sales,
        'date_from': date_from,
        'date_to': date_to,
    }
    
    return render(request, 'finance/sales_report.html', context)
