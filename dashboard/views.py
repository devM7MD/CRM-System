from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from users.models import AuditLog

User = get_user_model()

@login_required
def index(request):
    """Main dashboard view that changes based on user role."""
    if request.user.role == 'super_admin':
        return render(request, 'dashboard/super_admin.html', {
            'active_users_count': User.objects.filter(is_active=True).count(),
            'alerts_count': 5,  # Will be replaced with actual notifications count
            'total_sales': "AED 257,842",  # Placeholder until connected to finance app
            'recent_activities': get_recent_activities(request.user)
        })
    elif request.user.role == 'seller':
        # Redirect to seller dashboard
        return render(request, 'sellers/dashboard.html', {
            'total_sales': "AED 42,651",  # Placeholder until connected to finance app
            'orders_count': 152,  # Placeholder until connected to orders app
            'completed_orders': 87,  # Placeholder
            'processing_orders': 53,  # Placeholder
            'cancelled_orders': 12,  # Placeholder
            'total_inventory': 534,  # Placeholder until connected to inventory app
            'available_inventory': 478,  # Placeholder
            'in_delivery_inventory': 56,  # Placeholder
            'sourcing_requests_count': 18,  # Placeholder until connected to sourcing app
            'pending_requests': 5,  # Placeholder
            'approved_requests': 13,  # Placeholder
            'products': [],  # Will be replaced with actual products
            'recent_orders': []  # Will be replaced with actual orders
        })
    else:
        # Generic dashboard for other roles
        today = timezone.now().date()
        
        # Get recent activities for the user
        recent_activities = get_recent_activities(request.user)
        
        # Count unread notifications - placeholder until notification model is created
        unread_notifications = get_unread_notifications_count(request.user)
        
        # Get active tasks - placeholder until tasks model is created
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
    if request.user.role not in ['super_admin', 'admin']:
        # Redirect to a permission denied page
        return render(request, 'dashboard/permission_denied.html')
    
    return render(request, 'dashboard/settings.html')

@login_required
def system_status(request):
    """System status and health view."""
    if request.user.role not in ['super_admin', 'admin']:
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
