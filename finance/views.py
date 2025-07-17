from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg, Q, F
from django.utils import timezone
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
    total_revenue = Payment.objects.filter(payment_status='completed').aggregate(total=Sum('amount'))['total'] or 0
    # No Expense model, so set expenses to 0 for now
    total_expenses = 0
    net_profit = total_revenue - total_expenses
    pending_payments = Payment.objects.filter(payment_status='pending').count()
    recent_payments = Payment.objects.order_by('-payment_date')[:5]
    context = {
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'net_profit': net_profit,
        'pending_payments': pending_payments,
        'recent_payments': recent_payments,
    }
    return render(request, 'finance/dashboard.html', context)

@login_required
def payment_list(request):
    """List of payments."""
    return render(request, 'finance/payment_list.html')

@login_required
def sales_report(request):
    """Sales reports and analytics with real data."""
    # Get date range from request or default to this month
    date_range = request.GET.get('date_range', 'this_month')
    
    # Calculate date filters
    today = timezone.now().date()
    if date_range == 'today':
        start_date = today
        end_date = today
    elif date_range == 'yesterday':
        start_date = today - timedelta(days=1)
        end_date = start_date
    elif date_range == 'this_week':
        start_date = today - timedelta(days=today.weekday())
        end_date = today
    elif date_range == 'last_week':
        start_date = today - timedelta(days=today.weekday() + 7)
        end_date = start_date + timedelta(days=6)
    elif date_range == 'this_month':
        start_date = today.replace(day=1)
        end_date = today
    elif date_range == 'last_month':
        last_month = today.replace(day=1) - timedelta(days=1)
        start_date = last_month.replace(day=1)
        end_date = today.replace(day=1) - timedelta(days=1)
    elif date_range == 'this_year':
        start_date = today.replace(month=1, day=1)
        end_date = today
    else:
        start_date = today.replace(day=1)
        end_date = today

    # Get real data from database
    orders_in_period = Order.objects.filter(
        date__date__gte=start_date,
        date__date__lte=end_date
    )
    
    # Calculate KPIs using actual database fields
    total_sales = orders_in_period.aggregate(
        total=Sum(F('quantity') * F('price_per_unit'))
    )['total'] or 0
    total_orders = orders_in_period.count()
    avg_order_value = orders_in_period.aggregate(
        avg=Avg(F('quantity') * F('price_per_unit'))
    )['avg'] or 0
    
    # Calculate previous period for comparison
    period_days = (end_date - start_date).days + 1
    prev_start_date = start_date - timedelta(days=period_days)
    prev_end_date = start_date - timedelta(days=1)
    
    prev_orders = Order.objects.filter(
        date__date__gte=prev_start_date,
        date__date__lte=prev_end_date
    )
    prev_total_sales = prev_orders.aggregate(
        total=Sum(F('quantity') * F('price_per_unit'))
    )['total'] or 0
    prev_total_orders = prev_orders.count()
    prev_avg_order_value = prev_orders.aggregate(
        avg=Avg(F('quantity') * F('price_per_unit'))
    )['avg'] or 0
    
    # Calculate percentage changes
    sales_change = ((total_sales - prev_total_sales) / prev_total_sales * 100) if prev_total_sales > 0 else 0
    orders_change = ((total_orders - prev_total_orders) / prev_total_orders * 100) if prev_total_orders > 0 else 0
    avg_order_change = ((avg_order_value - prev_avg_order_value) / prev_avg_order_value * 100) if prev_avg_order_value > 0 else 0
    
    # Get top selling products using the correct Product model
    top_products = Product.objects.annotate(
        total_sold=Sum('orders__quantity'),
        total_revenue=Sum(F('orders__quantity') * F('orders__price_per_unit'))
    ).filter(
        orders__date__date__gte=start_date,
        orders__date__date__lte=end_date
    ).order_by('-total_sold')[:5]
    
    # Get sales by category (using product name as category for now)
    sales_by_category = Product.objects.filter(
        orders__date__date__gte=start_date,
        orders__date__date__lte=end_date
    ).values('name').annotate(
        total_sales=Sum('orders__quantity')
    ).order_by('-total_sales')
    
    # Prepare chart data
    category_labels = [item['name'] for item in sales_by_category]
    category_data = [item['total_sales'] for item in sales_by_category]
    
    # Get monthly sales data for trend chart
    monthly_sales = []
    monthly_labels = []
    for i in range(6, -1, -1):
        month_start = today.replace(day=1) - timedelta(days=i*30)
        month_end = (month_start.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        month_sales = Order.objects.filter(
            date__date__gte=month_start,
            date__date__lte=month_end
        ).aggregate(
            total=Sum(F('quantity') * F('price_per_unit'))
        )['total'] or 0
        
        monthly_sales.append(float(month_sales))
        monthly_labels.append(month_start.strftime('%b'))
    
    # Get all products and sellers for filters
    all_products = Product.objects.all()
    all_sellers = Seller.objects.all()
    
    context = {
        'total_sales': total_sales,
        'total_orders': total_orders,
        'avg_order_value': avg_order_value,
        'sales_change': sales_change,
        'orders_change': orders_change,
        'avg_order_change': avg_order_change,
        'top_products': top_products,
        'sales_by_category': sales_by_category,
        'category_labels': json.dumps(category_labels),
        'category_data': json.dumps(category_data),
        'monthly_sales': json.dumps(monthly_sales),
        'monthly_labels': json.dumps(monthly_labels),
        'all_products': all_products,
        'all_sellers': all_sellers,
        'date_range': date_range,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'finance/sales_report.html', context)
