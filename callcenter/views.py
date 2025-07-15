from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Sum
from .models import CallLog, AgentPerformance
from datetime import datetime, timedelta

# Create your views here.

@login_required
def dashboard(request):
    """Call center dashboard."""
    # Get today's date
    today = timezone.now().date()
    
    # Get call statistics
    call_logs = CallLog.objects.filter(call_time__date=today)
    total_calls_today = call_logs.count()
    
    # Get confirmed orders
    confirmed_orders = call_logs.filter(status='completed').count()
    
    # Get failed calls
    failed_calls = call_logs.filter(status__in=['no_answer', 'busy', 'wrong_number']).count()
    
    # Get average call duration
    avg_duration = call_logs.aggregate(avg_duration=Sum('duration'))['avg_duration'] or 0
    if total_calls_today > 0:
        avg_duration = avg_duration / total_calls_today
    
    # Format duration as minutes:seconds
    minutes = int(avg_duration // 60)
    seconds = int(avg_duration % 60)
    avg_call_duration = f"{minutes}:{seconds:02d}"
    
    # Get recent calls
    recent_calls = call_logs.order_by('-call_time')[:10]
    
    # Check if performance record exists for today
    try:
        agent_performance = AgentPerformance.objects.get(agent=request.user, date=today)
    except AgentPerformance.DoesNotExist:
        agent_performance = None
    
    context = {
        'total_calls_today': total_calls_today,
        'confirmed_orders': confirmed_orders,
        'failed_calls': failed_calls,
        'avg_call_duration': avg_call_duration,
        'recent_calls': recent_calls,
        'agent_performance': agent_performance,
    }
    
    return render(request, 'callcenter/dashboard.html', context)

@login_required
def order_list(request):
    """List of orders for call center agents."""
    # Get filter parameters
    status = request.GET.get('status', '')
    date_range = request.GET.get('date', 'today')
    agent_id = request.GET.get('agent', '')
    search = request.GET.get('search', '')
    
    # Base queryset - in a real implementation, this would fetch orders
    # For now, we'll just prepare the context
    
    # Get all call logs for date filtering
    call_logs = CallLog.objects.all()
    
    # Apply date filter
    today = timezone.now().date()
    if date_range == 'today':
        call_logs = call_logs.filter(call_time__date=today)
    elif date_range == 'yesterday':
        call_logs = call_logs.filter(call_time__date=today - timedelta(days=1))
    elif date_range == 'last_7_days':
        call_logs = call_logs.filter(call_time__date__gte=today - timedelta(days=7))
    elif date_range == 'last_30_days':
        call_logs = call_logs.filter(call_time__date__gte=today - timedelta(days=30))
    
    # Apply status filter
    if status:
        call_logs = call_logs.filter(status=status)
    
    # Apply agent filter
    if agent_id:
        call_logs = call_logs.filter(agent_id=agent_id)
    
    # Apply search filter - in a real implementation, this would search by order details
    # This is just a placeholder
    
    context = {
        'call_logs': call_logs,
        'status_filter': status,
        'date_filter': date_range,
        'agent_filter': agent_id,
        'search_query': search,
    }
    
    return render(request, 'callcenter/order_list.html', context)
