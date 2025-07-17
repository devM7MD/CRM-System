from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from orders.models import Order

# Create your views here.

@login_required
def dashboard(request):
    """Packaging dashboard with real data."""
    # Get today's date
    today = timezone.now().date()
    
    # Get orders that need packaging (processing orders)
    pending_packaging = Order.objects.filter(status='processing').count()
    completed_today = Order.objects.filter(
        status='shipped',
        date__date=today
    ).count()
    
    # Get total orders in packaging queue
    total_packaging_queue = Order.objects.filter(
        status__in=['processing', 'pending']
    ).count()
    
    # Get orders by status for packaging
    orders_by_status = Order.objects.values('status').annotate(count=Count('id')).order_by('status')
    
    # Get recent orders that need packaging
    recent_packaging_orders = Order.objects.filter(
        status='processing'
    ).order_by('-date')[:10]
    
    # Get orders from last 7 days
    last_week_orders = Order.objects.filter(
        date__date__gte=today - timedelta(days=7)
    ).count()
    
    # Get orders from last 30 days
    last_month_orders = Order.objects.filter(
        date__date__gte=today - timedelta(days=30)
    ).count()
    
    context = {
        'pending_packaging': pending_packaging,
        'completed_today': completed_today,
        'total_packaging_queue': total_packaging_queue,
        'orders_by_status': orders_by_status,
        'recent_packaging_orders': recent_packaging_orders,
        'last_week_orders': last_week_orders,
        'last_month_orders': last_month_orders,
    }
    
    return render(request, 'packaging/dashboard.html', context)

@login_required
def order_list(request):
    """List of orders for packaging with real data."""
    # Get all orders that need packaging
    packaging_orders = Order.objects.filter(
        status='processing'
    ).order_by('-date')
    
    # Get search query
    search = request.GET.get('search', '')
    if search:
        packaging_orders = packaging_orders.filter(
            Q(order_code__icontains=search) |
            Q(customer__first_name__icontains=search) |
            Q(customer__last_name__icontains=search) |
            Q(customer_phone__icontains=search)
        )
    
    # Get status filter
    status_filter = request.GET.get('status', '')
    if status_filter:
        packaging_orders = packaging_orders.filter(status=status_filter)
    
    context = {
        'packaging_orders': packaging_orders,
        'search_query': search,
        'status_filter': status_filter,
    }
    
    return render(request, 'packaging/order_list.html', context)
