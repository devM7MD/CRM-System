from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Sum, Avg, Q
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from .models import (
    CallLog, AgentPerformance, AgentSession, CustomerInteraction,
    OrderStatusHistory, OrderAssignment, ManagerNote, TeamPerformance
)
from orders.models import Order
from users.models import User
from inventory.models import Stock
from datetime import datetime, timedelta
import json

def is_call_center_agent(user):
    """Check if user is a call center agent."""
    return user.has_role('Call Center Agent') or user.is_superuser

def is_call_center_manager(user):
    """Check if user is a call center manager."""
    return user.has_role('Call Center Manager') or user.is_superuser

def has_callcenter_role(user):
    return (
        user.is_superuser or
        user.has_role('Super Admin') or
        user.has_role('Admin') or
        user.has_role('Call Center Manager') or
        user.has_role('Call Center Agent')
    )

# Agent Panel Views

@login_required
def agent_dashboard(request):
    """Call center agent dashboard."""
    if not has_callcenter_role(request.user):
        messages.error(request, "ليس لديك صلاحية للدخول لهذه الصفحة.")
        return redirect('dashboard:index')
    today = timezone.now().date()
    
    # Get or create agent session
    session, created = AgentSession.objects.get_or_create(
        agent=request.user,
        defaults={'status': 'available'}
    )
    
    # Update session status if needed
    if request.POST.get('status'):
        session.status = request.POST.get('status')
        session.save()
    
    # Get today's performance
    performance, created = AgentPerformance.objects.get_or_create(
        agent=request.user, 
        date=today,
        defaults={
            'total_calls_made': 0,
            'successful_calls': 0,
            'orders_confirmed': 0,
            'orders_cancelled': 0,
            'orders_postponed': 0,
            'total_orders_handled': 0,
        }
    )
    
    # Get assigned orders
    assigned_orders = Order.objects.filter(
        assignments__agent=request.user,
        assignments__assignment_date__date=today
    ).distinct()
    
    # Get recent calls
    recent_calls = CallLog.objects.filter(
        agent=request.user,
        call_time__date=today
    ).order_by('-call_time')[:10]
    
    # Get pending orders that need follow-up
    pending_orders = Order.objects.filter(
        status__in=['pending', 'pending_confirmation'],
        assignments__agent=request.user
    ).distinct()[:5]
    
    # Calculate metrics
    total_calls_today = CallLog.objects.filter(
        agent=request.user,
        call_time__date=today
    ).count()
    
    confirmed_orders = CallLog.objects.filter(
        agent=request.user,
        call_time__date=today,
        status='completed'
    ).count()
    
    failed_calls = CallLog.objects.filter(
        agent=request.user,
        call_time__date=today,
        status__in=['no_answer', 'busy', 'wrong_number']
    ).count()
    
    # Calculate average call duration
    call_durations = CallLog.objects.filter(
        agent=request.user,
        call_time__date=today
    ).aggregate(avg_duration=Avg('duration'))['avg_duration'] or 0
    
    avg_duration_minutes = round(call_durations / 60, 1) if call_durations > 0 else 0
    
    # Alerts & Notifications
    # 1. High Priority: Orders pending >2 hours
    two_hours_ago = timezone.now() - timedelta(hours=2)
    high_priority_count = Order.objects.filter(
        status__in=['pending', 'pending_confirmation'],
        date__lt=two_hours_ago
    ).count()

    # 2. Agent Overload: Agent with most assigned orders (if >30)
    overload_agent = (
        User.objects.filter(user_roles__role__name='Call Center Agent')
        .annotate(order_count=Count('assigned_orders'))
        .order_by('-order_count')
        .first()
    )
    agent_overload = None
    if overload_agent and overload_agent.order_count > 30:
        agent_overload = {
            'name': overload_agent.get_full_name(),
            'order_count': overload_agent.order_count
        }

    # 3. Low Stock Alert: Product with lowest stock (<5 units)
    low_stock = (
        Stock.objects.filter(product__isnull=False)
        .annotate(total=Sum('product__inventoryrecord__quantity'))
        .filter(total__lt=5)
        .order_by('total')
        .first()
    )
    low_stock_alert = None
    if low_stock:
        low_stock_alert = {
            'product': low_stock.product.name_en,
            'units': low_stock.total or 0
        }

    context = {
        'session': session,
        'performance': performance,
        'assigned_orders': assigned_orders,
        'recent_calls': recent_calls,
        'pending_orders': pending_orders,
        'total_calls_today': total_calls_today,
        'confirmed_orders': confirmed_orders,
        'failed_calls': failed_calls,
        'avg_duration_minutes': avg_duration_minutes,
        'today': today,
        'high_priority_count': high_priority_count,
        'agent_overload': agent_overload,
        'low_stock_alert': low_stock_alert,
    }
    
    return render(request, 'callcenter/agent/dashboard.html', context)

@login_required
def agent_order_list(request):
    """Agent's assigned orders list."""
    if not has_callcenter_role(request.user):
        messages.error(request, "ليس لديك صلاحية للدخول لهذه الصفحة.")
        return redirect('dashboard:index')
    # Get filter parameters
    status = request.GET.get('status', '')
    priority = request.GET.get('priority', '')
    search = request.GET.get('search', '')
    
    # Base queryset - assigned orders
    orders = Order.objects.filter(assignments__agent=request.user).distinct()
    
    # Apply filters
    if status:
        orders = orders.filter(status=status)
    
    if priority:
        orders = orders.filter(assignments__priority_level=priority)
    
    if search:
        orders = orders.filter(
            Q(id__icontains=search) |
            Q(customer__first_name__icontains=search) |
            Q(customer__last_name__icontains=search) |
            Q(customer_phone__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'orders': page_obj,
        'status_filter': status,
        'priority_filter': priority,
        'search_query': search,
    }
    
    return render(request, 'callcenter/agent/order_list.html', context)

@login_required
def agent_order_detail(request, order_id):
    """Agent's order detail view."""
    if not has_callcenter_role(request.user):
        messages.error(request, "ليس لديك صلاحية للدخول لهذه الصفحة.")
        return redirect('dashboard:index')
    order = get_object_or_404(Order, id=order_id, assignments__agent=request.user)
    
    # Get call logs for this order
    call_logs = CallLog.objects.filter(order=order, agent=request.user).order_by('-call_time')
    
    # Get manager notes
    manager_notes = ManagerNote.objects.filter(order=order, agent=request.user).order_by('-created_at')
    
    # Get status history
    status_history = OrderStatusHistory.objects.filter(order=order).order_by('-change_timestamp')
    
    context = {
        'order': order,
        'call_logs': call_logs,
        'manager_notes': manager_notes,
        'status_history': status_history,
    }
    
    return render(request, 'callcenter/agent/order_detail.html', context)

@login_required
def agent_log_call(request, order_id):
    """Log a call for an order."""
    if not has_callcenter_role(request.user):
        messages.error(request, "ليس لديك صلاحية للدخول لهذه الصفحة.")
        return redirect('dashboard:index')
    
    order = get_object_or_404(Order, id=order_id, assignments__agent=request.user)
    
    if request.method == 'POST':
        duration = request.POST.get('duration', 0)
        status = request.POST.get('status', 'completed')
        notes = request.POST.get('notes', '')
        customer_satisfaction = request.POST.get('customer_satisfaction')
        
        call_log = CallLog.objects.create(
            order=order,
            agent=request.user,
            duration=duration,
            status=status,
            notes=notes,
            customer_satisfaction=customer_satisfaction if customer_satisfaction else None
        )
        
        messages.success(request, 'Call logged successfully.')
        return redirect('callcenter:agent_order_detail', order_id=order_id)
    
    return render(request, 'callcenter/agent/log_call.html', {'order': order})

@login_required
def agent_reports(request):
    """Agent's personal performance reports view."""
    if not has_callcenter_role(request.user):
        messages.error(request, "ليس لديك صلاحية للدخول لهذه الصفحة.")
        return redirect('dashboard:index')
    
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    
    # Get agent's performance for the week
    performance_data = AgentPerformance.objects.filter(
        agent=request.user,
        date__gte=week_ago,
        date__lte=today
    ).order_by('date')
    
    # Calculate weekly totals for charts
    weekly_calls = [0] * 7
    weekly_confirmed = [0] * 7
    weekly_duration = [0] * 7
    
    for i, day_data in enumerate(performance_data):
        day_index = (day_data.date - week_ago).days
        if 0 <= day_index < 7:
            weekly_calls[day_index] = day_data.total_calls_made
            weekly_confirmed[day_index] = day_data.orders_confirmed
            weekly_duration[day_index] = float(day_data.average_call_duration or 0)
    
    context = {
        'agent': request.user,
        'performance_data': performance_data,
        'weekly_calls': weekly_calls,
        'weekly_confirmed': weekly_confirmed,
        'weekly_duration': weekly_duration,
        'week_start': week_ago,
        'today': today,
    }
    return render(request, 'callcenter/agent/agent_reports.html', context)

# Manager Panel Views

@login_required
def manager_dashboard(request):
    """Call center manager dashboard with comprehensive analytics."""
    if not has_callcenter_role(request.user):
        messages.error(request, "ليس لديك صلاحية للدخول لهذه الصفحة.")
        return redirect('dashboard:index')
    
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    
    # Enhanced overall statistics
    total_orders = Order.objects.count()
    orders_today = Order.objects.filter(date__date=today).count()
    orders_confirmed = Order.objects.filter(status='confirmed').count()
    orders_cancelled = Order.objects.filter(status='cancelled').count()
    orders_pending = Order.objects.filter(status__in=['pending', 'pending_confirmation']).count()
    orders_processed = Order.objects.filter(date__date=today).count()
    
    # Calculate rates
    confirmation_rate = (orders_confirmed / total_orders * 100) if total_orders > 0 else 0
    cancellation_rate = (orders_cancelled / total_orders * 100) if total_orders > 0 else 0
    
    # Get active agents and their status
    active_agents = AgentSession.objects.filter(status='available').count()
    total_agents = User.objects.filter(user_roles__role__name__in=['Call Center Agent']).count()
    
    # Get today's performance metrics
    today_performance = AgentPerformance.objects.filter(date=today)
    total_calls_handled = today_performance.aggregate(total=Sum('total_calls_made'))['total'] or 0
    avg_satisfaction = float(today_performance.aggregate(avg=Avg('customer_satisfaction_avg'))['avg'] or 0)
    avg_response_time = float(today_performance.aggregate(avg=Avg('average_call_duration'))['avg'] or 0)
    
    # Get recent assignments
    recent_assignments = OrderAssignment.objects.select_related('order', 'agent').order_by('-assignment_date')[:10]
    
    # Get pending orders that need attention
    pending_orders = Order.objects.filter(
        status__in=['pending', 'pending_confirmation']
    ).order_by('date')[:10]
    
    # Get high priority unassigned orders
    high_priority_unassigned = Order.objects.filter(
        status__in=['pending', 'pending_confirmation'],
        assignments__isnull=True
    ).order_by('-date')[:5]
    
    # Get available agents for assignment
    available_agents = User.objects.filter(
        user_roles__role__name='Call Center Agent',
        agent_sessions__status='available'
    ).distinct()
    
    # Get team performance data
    team_performance, created = TeamPerformance.objects.get_or_create(
        team='Main Team',
        date=today,
        defaults={
            'total_agents': total_agents,
            'orders_handled': orders_today,
            'orders_confirmed': orders_confirmed,
            'orders_cancelled': orders_cancelled,
        }
    )
    
    # Calculate team metrics
    team_avg_confirmation_rate = (orders_confirmed / total_orders * 100) if total_orders > 0 else 0
    team_avg_response_time = avg_response_time
    team_avg_satisfaction = avg_satisfaction
    team_efficiency_score = ((float(confirmation_rate) + (100 - float(cancellation_rate)) + (float(avg_satisfaction) * 20)) / 3)
    
    # Get top performing agents
    top_agents = AgentPerformance.objects.filter(
        date=today
    ).select_related('agent').order_by('-orders_confirmed')[:5]
    
    # Generate weekly trend data for charts
    weekly_trends = []
    for i in range(5):  # Last 5 days
        date = today - timedelta(days=i)
        day_performance = AgentPerformance.objects.filter(date=date)
        
        # Calculate confirmation rate for this day
        day_orders = Order.objects.filter(date__date=date)
        day_confirmed = day_orders.filter(status='confirmed').count()
        day_confirmation_rate = (day_confirmed / day_orders.count() * 100) if day_orders.count() > 0 else 0
        
        # Calculate average response time for this day
        day_avg_response = day_performance.aggregate(avg=Avg('average_call_duration'))['avg'] or 0
        
        weekly_trends.append({
            'date': date,
            'confirmation_rate': round(day_confirmation_rate, 1),
            'response_time': round(float(day_avg_response), 1),
        })
    
    # Reverse to show oldest to newest
    weekly_trends.reverse()
    
    # Prepare team performance comparison data
    team_performance_data = []
    for agent in User.objects.filter(user_roles__role__name='Call Center Agent')[:5]:
        performance = AgentPerformance.objects.filter(agent=agent, date=today).first()
        if performance:
            team_performance_data.append({
                'id': agent.id,
                'name': agent.get_full_name(),
                'orders_handled': performance.total_orders_handled,
                'orders_confirmed': performance.orders_confirmed,
                'confirmation_rate': (performance.orders_confirmed / performance.total_orders_handled * 100) if performance.total_orders_handled > 0 else 0,
                'avg_response_time': float(performance.average_call_duration or 0),
                'satisfaction': float(performance.customer_satisfaction_avg or 0),
            })
    
    # Alerts & Notifications
    # 1. High Priority: Orders pending >2 hours
    two_hours_ago = timezone.now() - timedelta(hours=2)
    high_priority_count = Order.objects.filter(
        status__in=['pending', 'pending_confirmation'],
        date__lt=two_hours_ago
    ).count()

    # 2. Agent Overload: Agent with most assigned orders (if >30)
    overload_agent = (
        User.objects.filter(user_roles__role__name='Call Center Agent')
        .annotate(order_count=Count('assigned_orders'))
        .order_by('-order_count')
        .first()
    )
    agent_overload = None
    if overload_agent and overload_agent.order_count > 30:
        agent_overload = {
            'name': overload_agent.get_full_name(),
            'order_count': overload_agent.order_count
        }

    # 3. Low Stock Alert: Product with lowest stock (<5 units)
    low_stock = (
        Stock.objects.filter(product__isnull=False)
        .annotate(total=Sum('product__inventoryrecord__quantity'))
        .filter(total__lt=5)
        .order_by('total')
        .first()
    )
    low_stock_alert = None
    if low_stock:
        low_stock_alert = {
            'product': low_stock.product.name_en,
            'units': low_stock.total or 0
        }

    context = {
        'total_orders': total_orders,
        'orders_today': orders_today,
        'orders_confirmed': orders_confirmed,
        'orders_cancelled': orders_cancelled,
        'orders_pending': orders_pending,
        'orders_processed': orders_processed,
        'confirmation_rate': round(confirmation_rate, 1),
        'cancellation_rate': round(cancellation_rate, 1),
        'active_agents': active_agents,
        'total_calls_handled': total_calls_handled,
        'avg_satisfaction': round(avg_satisfaction, 1),
        'avg_response_time': round(avg_response_time, 1),
        'recent_assignments': recent_assignments,
        'pending_orders': pending_orders,
        'high_priority_unassigned': high_priority_unassigned,
        'available_agents': available_agents,
        'team_performance': team_performance,
        'team_performance_data': team_performance_data,
        'team_avg_confirmation_rate': round(team_avg_confirmation_rate, 1),
        'team_avg_response_time': round(team_avg_response_time, 1),
        'team_avg_satisfaction': round(team_avg_satisfaction, 1),
        'team_efficiency_score': round(team_efficiency_score, 1),
        'top_agents': top_agents,
        'weekly_trends': weekly_trends,
        'today': today,
        'week_start': week_ago,
        'week_end': today,
        'high_priority_count': high_priority_count,
        'agent_overload': agent_overload,
        'low_stock_alert': low_stock_alert,
    }
    
    return render(request, 'callcenter/manager/dashboard.html', context)

@login_required
def manager_order_list(request):
    """Manager's comprehensive order management view."""
    if not has_callcenter_role(request.user):
        messages.error(request, "ليس لديك صلاحية للدخول لهذه الصفحة.")
        return redirect('dashboard:index')
    
    # Get filter parameters
    status = request.GET.get('status', '')
    agent = request.GET.get('agent', '')
    priority = request.GET.get('priority', '')
    search = request.GET.get('search', '')
    date_filter = request.GET.get('date', 'today')
    
    # Base queryset - all orders
    orders = Order.objects.all()
    
    # Apply date filter
    today = timezone.now().date()
    if date_filter == 'today':
        orders = orders.filter(date__date=today)
    elif date_filter == 'yesterday':
        yesterday = today - timedelta(days=1)
        orders = orders.filter(date__date=yesterday)
    elif date_filter == 'week':
        week_ago = today - timedelta(days=7)
        orders = orders.filter(date__date__gte=week_ago)
    elif date_filter == 'month':
        month_ago = today - timedelta(days=30)
        orders = orders.filter(date__date__gte=month_ago)
    
    # Apply filters
    if status:
        orders = orders.filter(status=status)
    
    if agent:
        orders = orders.filter(assignments__agent_id=agent)
    
    if priority:
        orders = orders.filter(assignments__priority_level=priority)
    
    if search:
        orders = orders.filter(
            Q(id__icontains=search) |
            Q(customer__icontains=search) |
            Q(customer_phone__icontains=search) |
            Q(product__name_en__icontains=search) |
            Q(product__code__icontains=search)
        )
    
    # Get summary statistics
    total_orders = Order.objects.count()
    assigned_orders = Order.objects.filter(assignments__isnull=False).distinct().count()
    unassigned_orders = Order.objects.filter(assignments__isnull=True).count()
    confirmed_orders = Order.objects.filter(status='confirmed').count()
    pending_orders = Order.objects.filter(status__in=['pending', 'pending_confirmation']).count()
    
    # Get high priority unassigned orders
    high_priority_unassigned = Order.objects.filter(
        status__in=['pending', 'pending_confirmation'],
        assignments__isnull=True
    ).order_by('-date')[:5]
    
    # Get available agents
    available_agents = User.objects.filter(
        user_roles__role__name='Call Center Agent',
        agent_sessions__status='available'
    ).distinct()
    
    # Get all agents for filter dropdown
    all_agents = User.objects.filter(user_roles__role__name='Call Center Agent').distinct()
    
    # Pagination
    paginator = Paginator(orders, 25)  # Show 25 orders per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'orders': page_obj,
        'total_orders': total_orders,
        'assigned_orders': assigned_orders,
        'unassigned_orders': unassigned_orders,
        'confirmed_orders': confirmed_orders,
        'pending_orders': pending_orders,
        'high_priority_unassigned': high_priority_unassigned,
        'available_agents': available_agents,
        'agents': all_agents,
        'status_filter': status,
        'agent_filter': agent,
        'priority_filter': priority,
        'search_filter': search,
        'date_filter': date_filter,
    }
    
    return render(request, 'callcenter/manager/order_list.html', context)

@login_required
def manager_assign_order(request, order_id):
    """Assign order to agent."""
    if not has_callcenter_role(request.user):
        messages.error(request, "ليس لديك صلاحية للدخول لهذه الصفحة.")
        return redirect('dashboard:index')
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        agent_id = request.POST.get('agent')
        priority = request.POST.get('priority', 'medium')
        notes = request.POST.get('notes', '')
        
        if agent_id:
            agent = get_object_or_404(User, id=agent_id)
            
            # Create assignment
            OrderAssignment.objects.create(
                order=order,
                manager=request.user,
                agent=agent,
                priority_level=priority,
                manager_notes=notes,
            )
            
            messages.success(request, f'Order {order.id} assigned to {agent.get_full_name() or agent.username}')
        else:
            messages.error(request, 'Please select an agent.')
        
        return redirect('callcenter:manager_order_list')
    
    order = get_object_or_404(Order, id=order_id)
    agents = User.objects.filter(groups__name='Call Center Agents')
    
    return render(request, 'callcenter/manager/assign_order.html', {
        'order': order,
        'agents': agents
    })

@login_required
def manager_agent_reports(request):
    """Manager's comprehensive agent performance reports view."""
    if not has_callcenter_role(request.user):
        messages.error(request, "ليس لديك صلاحية للدخول لهذه الصفحة.")
        return redirect('dashboard:index')
    
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    
    # Get all call center agents
    agents = User.objects.filter(user_roles__role__name='Call Center Agent').distinct()
    
    # Get team performance data for the week
    team_performance = []
    total_orders_processed = 0
    total_confirmation_rate = 0
    total_response_time = 0
    total_satisfaction = 0
    agent_count = 0
    
    for agent in agents:
        # Get agent's performance for the week
        performance = AgentPerformance.objects.filter(
            agent=agent,
            date__gte=week_ago,
            date__lte=today
        ).aggregate(
            total_orders=Sum('total_orders_handled'),
            total_confirmed=Sum('orders_confirmed'),
            avg_response_time=Avg('average_call_duration'),
            avg_satisfaction=Avg('customer_satisfaction_avg')
        )
        
        if performance['total_orders'] and performance['total_orders'] > 0:
            confirmation_rate = (performance['total_confirmed'] / performance['total_orders'] * 100)
            team_performance.append({
                'id': agent.id,
                'name': agent.get_full_name(),
                'orders_handled': performance['total_orders'],
                'orders_confirmed': performance['total_confirmed'],
                'confirmation_rate': round(confirmation_rate, 1),
                'avg_response_time': round(performance['avg_response_time'] or 0, 1),
                'satisfaction': round(performance['avg_satisfaction'] or 0, 1),
            })
            
            total_orders_processed += performance['total_orders']
            total_confirmation_rate += confirmation_rate
            total_response_time += performance['avg_response_time'] or 0
            total_satisfaction += performance['avg_satisfaction'] or 0
            agent_count += 1
    
    # Sort by confirmation rate (top performers first)
    team_performance.sort(key=lambda x: x['confirmation_rate'], reverse=True)
    
    # Calculate team averages
    team_avg_confirmation_rate = total_confirmation_rate / agent_count if agent_count > 0 else 0
    team_avg_response_time = total_response_time / agent_count if agent_count > 0 else 0
    team_avg_satisfaction = total_satisfaction / agent_count if agent_count > 0 else 0
    team_efficiency_score = ((float(team_avg_confirmation_rate) + (100 - (float(total_orders_processed) * 0.1)) + (float(team_avg_satisfaction) * 20)) / 3)
    
    # Get individual agent performance for today
    today_performance = {}
    for agent in agents:
        perf = AgentPerformance.objects.filter(agent=agent, date=today).first()
        if perf:
            today_performance[agent.id] = {
                'orders_handled': perf.total_orders_handled,
                'orders_confirmed': perf.orders_confirmed,
                'confirmation_rate': (perf.orders_confirmed / perf.total_orders_handled * 100) if perf.total_orders_handled > 0 else 0,
                'avg_response_time': float(perf.average_call_duration or 0),
                'satisfaction': float(perf.customer_satisfaction_avg or 0),
            }
    
    context = {
        'agents': agents,
        'team_performance': team_performance,
        'today_performance': today_performance,
        'total_orders_processed': total_orders_processed,
        'team_avg_confirmation_rate': round(team_avg_confirmation_rate, 1),
        'team_avg_response_time': round(team_avg_response_time, 1),
        'team_avg_satisfaction': round(team_avg_satisfaction, 1),
        'team_efficiency_score': round(team_efficiency_score, 1),
        'week_start': week_ago,
        'week_end': today,
        'today': today,
    }
    
    return render(request, 'callcenter/manager/agent_reports.html', context)

# Enhanced Manager Views

@login_required
def manager_order_detail(request, order_id):
    """Manager's detailed order view."""
    if not has_callcenter_role(request.user):
        messages.error(request, "ليس لديك صلاحية للدخول لهذه الصفحة.")
        return redirect('dashboard:index')
    
    order = get_object_or_404(Order, id=order_id)
    assignments = order.assignments.all().select_related('agent')
    call_logs = CallLog.objects.filter(order=order).order_by('-call_time')
    
    context = {
        'order': order,
        'assignments': assignments,
        'call_logs': call_logs,
    }
    
    return render(request, 'callcenter/manager/order_detail.html', context)

@login_required
def agent_performance_report(request, agent_id):
    """Individual agent performance report."""
    if not has_callcenter_role(request.user):
        messages.error(request, "ليس لديك صلاحية للدخول لهذه الصفحة.")
        return redirect('dashboard:index')
    
    agent = get_object_or_404(User, id=agent_id)
    period = request.GET.get('period', 'daily')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Get performance data based on period
    if period == 'daily':
        performance_data = AgentPerformance.objects.filter(
            agent=agent,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')
    elif period == 'weekly':
        # Weekly aggregation logic
        performance_data = []
    else:  # monthly
        # Monthly aggregation logic
        performance_data = []
    
    context = {
        'agent': agent,
        'performance_data': performance_data,
        'period': period,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return JsonResponse(context)

@login_required
def bulk_assign_orders(request):
    """Bulk assign orders to agents."""
    if not has_callcenter_role(request.user):
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            assignments = data.get('assignments', [])
            
            success_count = 0
            for assignment_data in assignments:
                try:
                    order = Order.objects.get(id=assignment_data['order_id'])
                    agent = User.objects.get(id=assignment_data['agent_id'])
                    
                    # Create or update assignment
                    assignment, created = OrderAssignment.objects.get_or_create(
                        order=order,
                        defaults={
                            'agent': agent,
                            'priority_level': 'medium',
                            'manager_notes': f'Bulk assigned by {request.user.get_full_name()}',
                            'assignment_date': timezone.now()
                        }
                    )
                    
                    if not created:
                        assignment.agent = agent
                        assignment.save()
                    
                    success_count += 1
                except (Order.DoesNotExist, User.DoesNotExist):
                    continue
            
            return JsonResponse({
                'success': True,
                'message': f'Successfully assigned {success_count} orders',
                'assigned_count': success_count
            })
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

@login_required
def export_performance_report(request):
    """Export performance report."""
    if not has_callcenter_role(request.user):
        messages.error(request, "ليس لديك صلاحية للدخول لهذه الصفحة.")
        return redirect('dashboard:index')
    
    # Implementation for exporting performance report
    # This would generate a CSV or Excel file
    return JsonResponse({'success': True, 'message': 'Export functionality coming soon'})

# API Views

@login_required
def assign_order_api(request, order_id):
    """API endpoint for assigning orders."""
    if not has_callcenter_role(request.user):
        return JsonResponse({'success': False, 'error': 'Unauthorized'})
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order = Order.objects.get(id=order_id)
            agent = User.objects.get(id=data['agent_id'])
            
            # Create or update assignment
            assignment, created = OrderAssignment.objects.get_or_create(
                order=order,
                defaults={
                    'agent': agent,
                    'priority_level': data.get('priority_level', 'medium'),
                    'manager_notes': data.get('manager_notes', ''),
                    'assignment_date': timezone.now()
                }
            )
            
            if not created:
                assignment.agent = agent
                assignment.priority_level = data.get('priority_level', 'medium')
                assignment.manager_notes = data.get('manager_notes', '')
                assignment.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Order assigned successfully',
                'assignment_id': assignment.id
            })
            
        except (Order.DoesNotExist, User.DoesNotExist, KeyError) as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def get_agent_performance(request, agent_id):
    """API endpoint for getting agent performance data."""
    if not has_callcenter_role(request.user):
        return JsonResponse({'success': False, 'error': 'Unauthorized'})
    
    try:
        agent = User.objects.get(id=agent_id)
        period = request.GET.get('period', 'daily')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        # Get performance data
        performance = AgentPerformance.objects.filter(
            agent=agent,
            date__gte=start_date,
            date__lte=end_date
        ).aggregate(
            total_orders=Sum('total_orders_handled'),
            total_confirmed=Sum('orders_confirmed'),
            avg_response_time=Avg('average_call_duration'),
            avg_satisfaction=Avg('customer_satisfaction_avg')
        )
        
        if performance['total_orders'] and performance['total_orders'] > 0:
            confirmation_rate = (performance['total_confirmed'] / performance['total_orders'] * 100)
        else:
            confirmation_rate = 0
        
        return JsonResponse({
            'success': True,
            'agent_name': agent.get_full_name(),
            'period': period,
            'orders_handled': performance['total_orders'] or 0,
            'orders_confirmed': performance['total_confirmed'] or 0,
            'confirmation_rate': round(confirmation_rate, 1),
            'avg_response_time': round(performance['avg_response_time'] or 0, 1),
            'satisfaction': round(performance['avg_satisfaction'] or 0, 1),
        })
        
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Agent not found'})

@login_required
def export_orders_api(request):
    """API endpoint for exporting orders."""
    if not has_callcenter_role(request.user):
        return JsonResponse({'success': False, 'error': 'Unauthorized'})
    
    # Implementation for exporting orders
    # This would generate a CSV file
    return JsonResponse({'success': True, 'message': 'Export functionality coming soon'})

# Missing view functions

@login_required
def update_agent_status(request):
    """Update agent status via AJAX."""
    if not has_callcenter_role(request.user):
        return JsonResponse({'success': False, 'error': 'Unauthorized'})
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            status = data.get('status')
            
            session, created = AgentSession.objects.get_or_create(
                agent=request.user,
                defaults={'status': status}
            )
            
            if not created:
                session.status = status
                session.save()
            
            return JsonResponse({
                'success': True,
                'status': status,
                'message': 'Status updated successfully'
            })
            
        except (KeyError, json.JSONDecodeError) as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def get_order_details(request, order_id):
    """Get order details for AJAX requests."""
    if not has_callcenter_role(request.user):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        order = Order.objects.get(id=order_id)
        data = {
            'id': order.id,
            'customer': order.customer,
            'product': order.product.name_en if order.product else 'N/A',
            'status': order.get_status_display(),
            'date': order.date.strftime('%Y-%m-%d %H:%M'),
            'price': str(order.price_per_unit),
            'notes': order.notes or '',
        }
        return JsonResponse(data)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)

@login_required
def manager_settings(request):
    """Manager settings page."""
    if not has_callcenter_role(request.user):
        messages.error(request, "ليس لديك صلاحية للدخول لهذه الصفحة.")
        return redirect('dashboard:index')
    
    # Get current settings (you can store these in database or cache)
    settings = {
        'auto_assign': True,
        'load_balancing': True,
        'priority_queue': False,
        'max_orders': 25,
        'response_threshold': 5,
        'auto_logout': 30,
        'high_priority_alerts': True,
        'performance_reports': True,
        'system_updates': False,
    }
    
    return render(request, 'callcenter/manager/settings.html', {'settings': settings})

@login_required
def save_settings(request):
    """Save manager settings via AJAX."""
    if not has_callcenter_role(request.user):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Here you would save the settings to database or cache
            # For now, we'll just return success
            settings = {
                'auto_assign': data.get('auto_assign', True),
                'load_balancing': data.get('load_balancing', True),
                'priority_queue': data.get('priority_queue', False),
                'max_orders': int(data.get('max_orders', 25)),
                'response_threshold': int(data.get('response_threshold', 5)),
                'auto_logout': int(data.get('auto_logout', 30)),
                'high_priority_alerts': data.get('high_priority_alerts', True),
                'performance_reports': data.get('performance_reports', True),
                'system_updates': data.get('system_updates', False),
            }
            
            # You can save these settings to a model or cache here
            # For example: CallCenterSettings.objects.update_or_create(user=request.user, defaults=settings)
            
            return JsonResponse({'success': True, 'message': 'Settings saved successfully'})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

# Legacy views for backward compatibility

@login_required
def dashboard(request):
    """Legacy dashboard view - redirects to appropriate dashboard."""
    if has_callcenter_role(request.user):
        if request.user.has_role('Call Center Manager') or request.user.has_role('Admin'):
            return redirect('callcenter:manager_dashboard')
        elif request.user.has_role('Call Center Agent'):
            return redirect('callcenter:agent_dashboard')
    
    return redirect('dashboard:index')

@login_required
def order_list(request):
    """Legacy order list view - redirects to appropriate order list."""
    if has_callcenter_role(request.user):
        if request.user.has_role('Call Center Manager'):
            return redirect('callcenter:manager_order_list')
        elif request.user.has_role('Call Center Agent'):
            return redirect('callcenter:agent_order_list')
    
    return redirect('dashboard:index')

@login_required
def order_detail(request, order_id):
    """Order detail view for call center staff."""
    if not has_callcenter_role(request.user):
        messages.error(request, "ليس لديك صلاحية للدخول لهذه الصفحة.")
        return redirect('dashboard:index')
    
    try:
        # Get the order
        order = Order.objects.get(id=order_id)
        
        # Check if agent is assigned to this order (if user is an agent)
        if request.user.has_role('Call Center Agent') and not order.assignments.filter(agent=request.user).exists():
            messages.error(request, "You are not assigned to this order.")
            return redirect('callcenter:agent_order_list')
        
        # Get call logs for this order
        call_logs = CallLog.objects.filter(order=order).order_by('-call_time')
        
        # Get status history
        status_history = OrderStatusHistory.objects.filter(order=order).order_by('-change_timestamp')
        
        # Get manager notes if applicable
        if request.user.has_role('Call Center Agent'):
            manager_notes = ManagerNote.objects.filter(order=order, agent=request.user).order_by('-created_at')
        else:
            manager_notes = ManagerNote.objects.filter(order=order).order_by('-created_at')
        
        context = {
            'order': order,
            'call_logs': call_logs,
            'manager_notes': manager_notes,
            'status_history': status_history,
        }
        
        return render(request, 'callcenter/order_detail.html', context)
        
    except Order.DoesNotExist:
        messages.error(request, "Order not found.")
        if request.user.has_role('Call Center Manager'):
            return redirect('callcenter:manager_order_list')
        elif request.user.has_role('Call Center Agent'):
            return redirect('callcenter:agent_order_list')
        else:
            return redirect('dashboard:index')
