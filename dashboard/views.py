from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from users.models import AuditLog
from finance.models import Payment
from django.db.models import Sum
from products.models import Product
from orders.models import Order

User = get_user_model()

@login_required
def index(request):
    """Main dashboard view that changes based on user role."""
    primary_role = request.user.get_primary_role()
    role_name = primary_role.name if primary_role else 'user'

    if role_name == 'Super Admin' or request.user.is_superuser:
        total_sales = Payment.objects.filter(payment_status='completed').aggregate(total=Sum('amount'))['total'] or 0
        active_users_count = User.objects.filter(is_active=True).count()
        # TODO: Replace with real alerts count if alerts model exists
        alerts_count = 0
        recent_activities = get_recent_activities(request.user)
        return render(request, 'dashboard/super_admin.html', {
            'active_users_count': active_users_count,
            'alerts_count': alerts_count,
            'total_sales': f"AED {total_sales:,.0f}",
            'recent_activities': recent_activities
        })
    elif role_name == 'Seller':
        seller_instance = getattr(request.user, 'seller_profile', None)
        products = Product.objects.filter(seller=request.user).order_by('-created_at')[:5] if seller_instance else []
        all_orders = Order.objects.filter(seller=seller_instance).order_by('-date') if seller_instance else []
        order_stats = {
            'total': all_orders.count() if all_orders else 0,
            'pending': all_orders.filter(status='pending').count() if all_orders else 0,
            'delivered': all_orders.filter(status='delivered').count() if all_orders else 0,
            'cancelled': all_orders.filter(status='cancelled').count() if all_orders else 0,
        } if all_orders else {'total': 0, 'pending': 0, 'delivered': 0, 'cancelled': 0}
        recent_orders = all_orders[:5] if all_orders else []
        all_products = Product.objects.filter(seller=request.user) if seller_instance else []
        total_inventory = sum(product.total_quantity for product in all_products) if all_products else 0
        available_inventory = sum(product.available_quantity for product in all_products) if all_products else 0
        in_delivery_inventory = total_inventory - available_inventory if all_products else 0
        # Sourcing requests (if model exists)
        sourcing_requests_count = 0
        pending_requests = 0
        approved_requests = 0
        return render(request, 'sellers/dashboard.html', {
            'total_sales': f"AED {order_stats['delivered'] * 1000:,.0f}" if order_stats['delivered'] else 'AED 0',
            'orders_count': order_stats['total'],
            'completed_orders': order_stats['delivered'],
            'processing_orders': order_stats['pending'],
            'cancelled_orders': order_stats['cancelled'],
            'total_inventory': total_inventory,
            'available_inventory': available_inventory,
            'in_delivery_inventory': in_delivery_inventory,
            'sourcing_requests_count': sourcing_requests_count,
            'pending_requests': pending_requests,
            'approved_requests': approved_requests,
            'products': products,
            'recent_orders': recent_orders
        })
    else:
        today = timezone.now().date()
        recent_activities = get_recent_activities(request.user)
        unread_notifications = get_unread_notifications_count(request.user)
        active_tasks = get_active_tasks_count(request.user)
        return render(request, 'dashboard/default.html', {
            'user': request.user,
            'active_tasks': active_tasks,
            'recent_activities': recent_activities,
            'recent_activities_count': len(recent_activities),
            'unread_notifications': unread_notifications,
            'notifications': get_user_notifications(request.user)
        })

@login_required
def alerts(request):
    """View for system alerts."""
    notifications = get_user_notifications(request.user)
    
    return render(request, 'dashboard/alerts.html', {
        'alerts': notifications
    })

@login_required
def settings(request):
    """System settings view."""
    # Check if user has admin or super admin role
    primary_role = request.user.get_primary_role()
    role_name = primary_role.name if primary_role else ''
    
    if role_name not in ['Super Admin', 'Admin'] and not request.user.is_superuser:
        # Redirect to a permission denied page
        return render(request, 'dashboard/permission_denied.html')
    
    return render(request, 'dashboard/settings.html')

@login_required
def system_status(request):
    """System status and health view."""
    # Check if user has admin or super admin role
    primary_role = request.user.get_primary_role()
    role_name = primary_role.name if primary_role else ''
    
    if role_name not in ['Super Admin', 'Admin'] and not request.user.is_superuser:
        # Redirect to a permission denied page
        return render(request, 'dashboard/permission_denied.html')
    
    return render(request, 'dashboard/system_status.html', {
        'status': 'healthy',  # Placeholder
        'database_response': '12ms',  # Placeholder
        'api_response': '19ms',  # Placeholder
        'last_backup': '2023-12-15 03:00:00',  # Placeholder
    })

@login_required
def activity_detail(request, activity_id):
    """Detail view for a specific audit log activity."""
    activity = get_object_or_404(AuditLog, id=activity_id)
    
    return render(request, 'dashboard/activity_detail.html', {
        'activity': activity
    })

@login_required
def activities(request):
    """View all user activities."""
    activities = get_recent_activities(request.user, limit=50)
    
    return render(request, 'dashboard/activities.html', {
        'activities': activities
    })

@login_required
def tasks(request):
    """View user tasks."""
    # Placeholder until tasks model is created
    tasks = []
    
    return render(request, 'dashboard/tasks.html', {
        'tasks': tasks
    })

@login_required
def reports(request):
    """View user reports."""
    # TODO: Replace with real reports if available
    reports = []
    return render(request, 'dashboard/reports.html', {
        'reports': reports
    })

@login_required
def help(request):
    """Help center view."""
    return render(request, 'dashboard/help.html')

# Helper functions

def get_recent_activities(user, limit=10):
    """Get recent activities for a user with the is_today flag."""
    activities = AuditLog.objects.filter(user=user).order_by('-timestamp')[:limit]
    today = timezone.now().date()
    
    # Add is_today flag to each activity
    for activity in activities:
        activity.is_today = activity.timestamp.date() == today
    
    return activities

def get_unread_notifications_count(user):
    """Get unread notifications count for a user."""
    # Placeholder until notification model is created
    return 3

def get_user_notifications(user):
    """Get notifications for a user."""
    # Placeholder until notification model is created
    today = timezone.now()
    yesterday = today - timedelta(days=1)
    two_days_ago = today - timedelta(days=2)
    
    notifications = [
        {
            'id': 1,
            'message': 'Your password was changed successfully',
            'timestamp': today,
            'is_read': True,
            'link': '#'
        },
        {
            'id': 2,
            'message': 'New comment on your sourcing request',
            'timestamp': yesterday,
            'is_read': False,
            'link': '#'
        },
        {
            'id': 3,
            'message': 'Order #ORD-2023-001 has been shipped',
            'timestamp': two_days_ago,
            'is_read': False,
            'link': '#'
        }
    ]
    
    return notifications

def get_active_tasks_count(user):
    """Get active tasks count for a user."""
    # Placeholder until tasks model is created
    return 5
