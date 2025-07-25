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
    elif role_name == 'Admin':
        return render(request, 'dashboard/admin.html')
    elif role_name == 'Seller':
        return render(request, 'dashboard/seller.html')
    elif role_name == 'Call Center Manager':
        return render(request, 'dashboard/call_center_manager.html')
    elif role_name == 'Call Center Agent':
        return render(request, 'dashboard/call_center_agent.html')
    elif role_name == 'Stock Keeper':
        return render(request, 'dashboard/stock_keeper.html')
    elif role_name == 'Packaging':
        return render(request, 'dashboard/packaging.html')
    elif role_name == 'Delivery':
        return render(request, 'dashboard/delivery.html')
    elif role_name == 'Follow-up':
        return render(request, 'dashboard/follow_up.html')
    elif role_name == 'Accountant':
        return render(request, 'dashboard/accountant.html')
    else:
        return render(request, 'dashboard/default.html')

def get_recent_activities(user):
    """Get recent activities for the dashboard."""
    # This is a placeholder - replace with real activity data
    activities = [
        {
            'id': 1,
            'event': 'User Login',
            'user': user.get_full_name(),
            'timestamp': timezone.now() - timedelta(minutes=5),
            'status': 'success'
        },
        {
            'id': 2,
            'event': 'Order Created',
            'user': 'John Doe',
            'timestamp': timezone.now() - timedelta(hours=1),
            'status': 'success'
        },
        {
            'id': 3,
            'event': 'Payment Processed',
            'user': 'Jane Smith',
            'timestamp': timezone.now() - timedelta(hours=2),
            'status': 'success'
        }
    ]
    return activities

@login_required
def alerts(request):
    """System alerts view."""
    return render(request, 'dashboard/alerts.html')

@login_required
def activities(request):
    """System activities view."""
    return render(request, 'dashboard/activities.html')

@login_required
def tasks(request):
    """Tasks view."""
    return render(request, 'dashboard/tasks.html')

@login_required
def reports(request):
    """Reports view."""
    return render(request, 'dashboard/reports.html')

@login_required
def help(request):
    """Help view."""
    return render(request, 'dashboard/help.html')

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
    """System status view."""
    return render(request, 'dashboard/system_status.html')

@login_required
def activity_detail(request, activity_id):
    """Activity detail view."""
    # This is a placeholder - replace with real activity data
    activity = {
        'id': activity_id,
        'event': 'Sample Activity',
        'user': 'Sample User',
        'timestamp': timezone.now(),
        'status': 'success',
        'details': 'This is a sample activity detail.'
    }
    return render(request, 'dashboard/activity_detail.html', {'activity': activity})

@login_required
def audit_log(request):
    """Audit log view."""
    # Check if user has admin or super admin role
    primary_role = request.user.get_primary_role()
    role_name = primary_role.name if primary_role else ''
    
    if role_name not in ['Super Admin', 'Admin'] and not request.user.is_superuser:
        # Redirect to a permission denied page
        return render(request, 'dashboard/permission_denied.html')
    
    # Get audit logs from the database
    audit_logs = AuditLog.objects.select_related('user').order_by('-timestamp')[:100]
    
    return render(request, 'dashboard/audit_log.html', {'audit_logs': audit_logs})
