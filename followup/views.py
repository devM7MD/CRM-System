from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from orders.models import Order

# Create your views here.

@login_required
def dashboard(request):
    """Followup dashboard with real data."""
    # Get today's date
    today = timezone.now().date()
    
    # Get orders that need followup (pending and processing orders)
    pending_orders = Order.objects.filter(status='pending').count()
    processing_orders = Order.objects.filter(status='processing').count()
    total_followup_needed = pending_orders + processing_orders
    
    # Get orders by status
    orders_by_status = Order.objects.values('status').annotate(count=Count('id')).order_by('status')
    
    # Get recent orders that need followup
    recent_followup_orders = Order.objects.filter(
        status__in=['pending', 'processing']
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
        'pending_orders': pending_orders,
        'processing_orders': processing_orders,
        'total_followup_needed': total_followup_needed,
        'orders_by_status': orders_by_status,
        'recent_followup_orders': recent_followup_orders,
        'last_week_orders': last_week_orders,
        'last_month_orders': last_month_orders,
    }
    
    return render(request, 'followup/dashboard.html', context)

@login_required
def order_list(request):
    """List of orders for followup with real data."""
    # Get all orders that need followup
    followup_orders = Order.objects.filter(
        status__in=['pending', 'processing']
    ).order_by('-date')
    
    # Get search query
    search = request.GET.get('search', '')
    if search:
        followup_orders = followup_orders.filter(
            Q(order_code__icontains=search) |
            Q(customer__first_name__icontains=search) |
            Q(customer__last_name__icontains=search) |
            Q(customer_phone__icontains=search)
        )
    
    # Get status filter
    status_filter = request.GET.get('status', '')
    if status_filter:
        followup_orders = followup_orders.filter(status=status_filter)
    
    context = {
        'followup_orders': followup_orders,
        'search_query': search,
        'status_filter': status_filter,
    }
    
    return render(request, 'followup/order_list.html', context)
