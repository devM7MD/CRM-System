from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from users.models import AuditLog, User
from finance.models import OrderPayment
from django.db.models import Sum, F, Count, Q
from orders.models import Order
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect

User = get_user_model()

@login_required
def index(request):
    # Debug URL reversal
    import sys
    from django.urls import reverse
    try:
        print("URL reversal test:", file=sys.stderr)
        print(f"delivery:order_list - {reverse("delivery:order_list")}", file=sys.stderr)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
    """Main dashboard view showing key metrics and recent activities."""
    # Redirect sellers to their dashboard
    if hasattr(request.user, 'role') and request.user.role and request.user.role.slug == 'seller':
        return redirect('sellers:dashboard')
    
    # Redirect super_admin to super_admin dashboard
    if hasattr(request.user, 'role') and request.user.role and request.user.role.slug == 'super_admin':
        return redirect('dashboard:super_admin')
    
    # Redirect delivery users to delivery panel
    if hasattr(request.user, 'role') and request.user.role and request.user.role.slug == 'delivery':
        return redirect('delivery:panel_dashboard')
    
    today = timezone.now().date()
    month_start = today.replace(day=1)
    
    # Get statistics
    stats = {
        'total_orders': Order.objects.count(),
        'active_subscribers': User.objects.filter(is_active=True, role__slug='seller').count(),
        'pending_deliveries': Order.objects.filter(status__in=['packaged', 'shipped']).count(),
        'monthly_revenue': Order.objects.filter(date__date__gte=month_start).aggregate(
            revenue=Sum('price_per_unit')
        )['revenue'] or 0,
    }
    
    # Get recent users (subscribers)
    users = User.objects.filter(
        is_active=True, role__slug='seller'
    ).order_by('-date_joined')[:5]
    
    # Get recent activities
    audit_logs = AuditLog.objects.select_related('user').order_by('-timestamp')[:10]
    
    # Format activities for display
    recent_activities = []
    for log in audit_logs:
        activity = {
            'message': format_activity_message(log),
            'timestamp': log.timestamp,
            'color': get_activity_color(log.action),
            'icon': get_activity_icon(log.action)
        }
        recent_activities.append(activity)
    
    # Check for recent cancelled orders and format as notifications - using distinct to avoid duplicates
    today = timezone.now().date()
    cancelled_orders = Order.objects.filter(
        status='cancelled',
        date__date__gte=today - timedelta(days=7)
    ).order_by('-date')[:10]  # Get more than we need initially
    
    notifications = []
    seen_order_codes = set()  # Track order codes we've already processed
    
    for order in cancelled_orders:
        # Only add if we haven't seen this order code yet
        if order.order_code not in seen_order_codes:
            notifications.append({
                'id': order.id,  # Use the order ID as the notification ID
                'message': f"Order #{order.order_code} has been cancelled.",
                'type': 'info'
            })
            seen_order_codes.add(order.order_code)
            # Limit to 5 notifications
            if len(notifications) >= 5:
                break
    
    context = {
        'stats': stats,
        'users': users,
        'recent_activities': recent_activities,
        'notifications': notifications
    }
    
    # Print debug information
    import sys
    print("Debug - URL Reversal:", file=sys.stderr)
    from django.urls import reverse
    try:
        print(f"delivery:order_list - {reverse('delivery:order_list')}", file=sys.stderr)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
    
    return render(request, 'dashboard/index.html', context)

@login_required
def super_admin(request):
    """Super Admin dashboard view showing key metrics and system status."""
    today = timezone.now().date()
    month_start = today.replace(day=1)
    current_year = today.year
    
    # Get counts for stats cards
    user_count = User.objects.filter(is_active=True).count()
    seller_count = User.objects.filter(is_active=True, role__slug='seller').count()
    order_count = Order.objects.count()
    
    # Get monthly revenue
    try:
        monthly_revenue = OrderPayment.objects.filter(
            payment_date__year=current_year,
            payment_date__month=today.month,
            payment_status='paid'
        ).aggregate(total=Sum('amount'))['total'] or 0
        monthly_revenue = round(monthly_revenue, 2)
    except:
        monthly_revenue = 0
    
    # Generate monthly sales data for the current year
    monthly_sales_data = []
    for month in range(1, 13):
        # Get total order value for this month
        month_sales = Order.objects.filter(
            date__year=current_year,
            date__month=month,
            status__in=['completed', 'delivered']
        ).aggregate(
            total=Sum(F('price_per_unit') * F('quantity'))
        )['total'] or 0
        
        monthly_sales_data.append(float(month_sales))
    
    # Generate monthly user growth data
    user_growth_data = []
    for month in range(1, 13):
        # Count users registered in this month
        new_users = User.objects.filter(
            date_joined__year=current_year,
            date_joined__month=month
        ).count()
        
        user_growth_data.append(new_users)
    
    # Get recent activities
    recent_activities = AuditLog.objects.select_related('user').order_by('-timestamp')[:10]
    
    context = {
        'user_count': user_count,
        'seller_count': seller_count,
        'order_count': order_count,
        'monthly_revenue': monthly_revenue,
        'monthly_sales_data': monthly_sales_data,
        'user_growth_data': user_growth_data,
        'recent_activities': recent_activities
    }
    
    return render(request, 'dashboard/super_admin.html', context)

@login_required
def alerts(request):
    """View for system alerts."""
    today = timezone.now().date()
    
    # Get all cancelled orders from the last 30 days
    cancelled_orders = Order.objects.filter(
        status='cancelled',
        date__date__gte=today - timedelta(days=30)
    ).order_by('-date')
    
    notifications = []
    for order in cancelled_orders:
        notifications.append({
            'message': f"Order #{order.order_code} has been cancelled.",
            'type': 'info',
            'date': order.date
        })
    
    return render(request, 'dashboard/alerts.html', {
        'alerts': notifications
    })

@login_required
def settings(request):
    """System settings view."""
    if not hasattr(request.user, 'role') or not request.user.role or request.user.role.slug not in ['super_admin', 'admin']:
        # Redirect to a permission denied page
        return render(request, 'dashboard/permission_denied.html')
    
    return render(request, 'dashboard/settings.html')

@login_required
def system_status(request):
    """System status and health view."""
    if not hasattr(request.user, 'role') or not request.user.role or request.user.role.slug not in ['super_admin', 'admin']:
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
    # Placeholder until reports model is created
    reports = []
    
    return render(request, 'dashboard/reports.html', {
        'reports': reports
    })

@login_required
def generate_report(request):
    """Generate a new report based on the provided template type."""
    report_type = request.GET.get('type', '')
    if request.method == 'POST':
        report_type = request.POST.get('type', '')
        
    # Just redirect back to reports page with a success message for now
    # In a real implementation, this would generate and save a report
    from django.contrib import messages
    
    # Clear any previous report generation messages to avoid duplication
    storage = messages.get_messages(request)
    for message in list(storage):
        # Only remove messages about report generation
        if "report is being generated" in str(message):
            storage.used = True
    
    # Add the new message
    if report_type:
        message_text = f"Your {report_type} report is being generated. It will be available shortly."
    else:
        message_text = f"Your report is being generated. It will be available shortly."
    
    messages.success(request, message_text)
    
    return redirect('dashboard:reports')

@login_required
def help(request):
    """Help center view."""
    return render(request, 'dashboard/help.html')

@login_required
@require_POST
@csrf_protect
def dismiss_notification(request, notification_id):
    """Handle AJAX request to dismiss a notification."""
    # In a real implementation, we would update a NotificationModel to mark it as read
    # For now, we'll just return a success response since we're using temporary notifications
    
    # You can add proper notification handling here when a Notification model is implemented
    # Example:
    # notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    # notification.is_read = True
    # notification.save()
    
    return JsonResponse({'status': 'success'})

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

def format_activity_message(log):
    """Format an audit log entry into a readable message."""
    entity_type = log.entity_type.replace('_', ' ').title()
    
    if log.action == 'create':
        return f"{log.user.full_name} created a new {entity_type}"
    elif log.action == 'update':
        return f"{log.user.full_name} updated a {entity_type}"
    elif log.action == 'delete':
        return f"{log.user.full_name} deleted a {entity_type}"
    elif log.action == 'login':
        return f"{log.user.full_name} logged in"
    elif log.action == 'logout':
        return f"{log.user.full_name} logged out"
    elif log.action == 'status_change':
        return f"{entity_type} status changed to {log.description}"
    else:
        return log.description

def get_activity_color(action):
    """Get the appropriate color for an activity type."""
    color_map = {
        'create': 'green',
        'update': 'blue',
        'delete': 'red',
        'view': 'gray',
        'login': 'indigo',
        'logout': 'purple',
        'password_change': 'yellow',
        'permission_change': 'orange',
        'status_change': 'teal'
    }
    return color_map.get(action, 'gray')

def get_activity_icon(action):
    """Get the appropriate icon for an activity type."""
    icon_map = {
        'create': 'plus',
        'update': 'edit',
        'delete': 'trash',
        'view': 'eye',
        'login': 'sign-in-alt',
        'logout': 'sign-out-alt',
        'password_change': 'key',
        'permission_change': 'lock',
        'status_change': 'exchange-alt'
    }
    return icon_map.get(action, 'bell')
