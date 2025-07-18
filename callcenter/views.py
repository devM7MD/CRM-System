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
from datetime import datetime, timedelta
import json

def is_call_center_agent(user):
    """Check if user is a call center agent."""
    return user.groups.filter(name='Call Center Agents').exists() or user.is_staff

def is_call_center_manager(user):
    """Check if user is a call center manager."""
    return user.groups.filter(name='Call Center Managers').exists() or user.is_superuser

# Agent Panel Views

@login_required
@user_passes_test(is_call_center_agent)
def agent_dashboard(request):
    """Call center agent dashboard."""
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
    }
    
    return render(request, 'callcenter/agent/dashboard.html', context)

@login_required
@user_passes_test(is_call_center_agent)
def agent_order_list(request):
    """Agent's assigned orders list."""
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
@user_passes_test(is_call_center_agent)
def agent_order_detail(request, order_id):
    """Agent's order detail view."""
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
@user_passes_test(is_call_center_agent)
def agent_log_call(request, order_id):
    """Log a call for an order."""
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id, assignments__agent=request.user)
        
        call_log = CallLog.objects.create(
            order=order,
            agent=request.user,
            status=request.POST.get('status'),
            duration=int(request.POST.get('duration', 0)),
            notes=request.POST.get('notes', ''),
            customer_satisfaction=request.POST.get('customer_satisfaction'),
            resolution_status=request.POST.get('resolution_status', 'pending'),
        )
        
        # Update order status if provided
        new_status = request.POST.get('new_status')
        if new_status and new_status != order.status:
            OrderStatusHistory.objects.create(
                order=order,
                agent=request.user,
                previous_status=order.status,
                new_status=new_status,
                status_change_reason=request.POST.get('status_reason', ''),
            )
            order.status = new_status
            order.save()
        
        messages.success(request, 'Call logged successfully.')
        return redirect('callcenter:agent_order_detail', order_id=order_id)
    
    order = get_object_or_404(Order, id=order_id, assignments__agent=request.user)
    return render(request, 'callcenter/agent/log_call.html', {'order': order})

# Manager Panel Views

@login_required
@user_passes_test(is_call_center_manager)
def manager_dashboard(request):
    """Call center manager dashboard."""
    today = timezone.now().date()
    
    # Get overall statistics
    total_orders = Order.objects.count()
    orders_today = Order.objects.filter(date__date=today).count()
    orders_confirmed = Order.objects.filter(status='confirmed').count()
    orders_cancelled = Order.objects.filter(status='cancelled').count()
    orders_pending = Order.objects.filter(status__in=['pending', 'pending_confirmation']).count()
    
    # Calculate rates
    confirmation_rate = (orders_confirmed / total_orders * 100) if total_orders > 0 else 0
    cancellation_rate = (orders_cancelled / total_orders * 100) if total_orders > 0 else 0
    
    # Get active agents
    active_agents = AgentSession.objects.filter(status='available').count()
    
    # Get today's performance
    today_performance = AgentPerformance.objects.filter(date=today)
    total_calls_handled = today_performance.aggregate(total=Sum('total_calls_made'))['total'] or 0
    avg_satisfaction = today_performance.aggregate(avg=Avg('customer_satisfaction_avg'))['avg'] or 0
    
    # Get recent assignments
    recent_assignments = OrderAssignment.objects.select_related('order', 'agent').order_by('-assignment_date')[:10]
    
    # Get pending orders that need attention
    pending_orders = Order.objects.filter(
        status__in=['pending', 'pending_confirmation']
    ).order_by('date')[:10]
    
    # Get team performance
    team_performance, created = TeamPerformance.objects.get_or_create(
        team='Main Team',
        date=today,
        defaults={
            'total_agents': User.objects.filter(groups__name='Call Center Agents').count(),
            'orders_handled': orders_today,
            'orders_confirmed': orders_confirmed,
            'orders_cancelled': orders_cancelled,
        }
    )
    
    context = {
        'total_orders': total_orders,
        'orders_today': orders_today,
        'orders_confirmed': orders_confirmed,
        'orders_cancelled': orders_cancelled,
        'orders_pending': orders_pending,
        'confirmation_rate': round(confirmation_rate, 1),
        'cancellation_rate': round(cancellation_rate, 1),
        'active_agents': active_agents,
        'total_calls_handled': total_calls_handled,
        'avg_satisfaction': round(avg_satisfaction, 1),
        'recent_assignments': recent_assignments,
        'pending_orders': pending_orders,
        'team_performance': team_performance,
        'today': today,
    }
    
    return render(request, 'callcenter/manager/dashboard.html', context)

@login_required
@user_passes_test(is_call_center_manager)
def manager_order_list(request):
    """Manager's order management view."""
    # Get filter parameters
    status = request.GET.get('status', '')
    agent = request.GET.get('agent', '')
    priority = request.GET.get('priority', '')
    search = request.GET.get('search', '')
    
    # Base queryset - all orders
    orders = Order.objects.all()
    
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
            Q(customer__first_name__icontains=search) |
            Q(customer__last_name__icontains=search) |
            Q(customer_phone__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(orders, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get agents for filter
    agents = User.objects.filter(groups__name='Call Center Agents')
    
    context = {
        'orders': page_obj,
        'agents': agents,
        'status_filter': status,
        'agent_filter': agent,
        'priority_filter': priority,
        'search_query': search,
    }
    
    return render(request, 'callcenter/manager/order_list.html', context)

@login_required
@user_passes_test(is_call_center_manager)
def manager_assign_order(request, order_id):
    """Assign order to agent."""
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
@user_passes_test(is_call_center_manager)
def manager_agent_reports(request):
    """Manager's agent performance reports."""
    # Get date range
    date_range = request.GET.get('date_range', 'today')
    today = timezone.now().date()
    
    if date_range == 'today':
        start_date = today
        end_date = today
    elif date_range == 'yesterday':
        start_date = today - timedelta(days=1)
        end_date = start_date
    elif date_range == 'last_7_days':
        start_date = today - timedelta(days=7)
        end_date = today
    elif date_range == 'last_30_days':
        start_date = today - timedelta(days=30)
        end_date = today
    else:
        start_date = today
        end_date = today
    
    # Get agent performance
    agent_performance = AgentPerformance.objects.filter(
        date__range=[start_date, end_date]
    ).select_related('agent').order_by('-date', '-total_calls_made')
    
    # Get team summary
    team_summary = agent_performance.aggregate(
        total_calls=Sum('total_calls_made'),
        total_confirmed=Sum('orders_confirmed'),
        total_cancelled=Sum('orders_cancelled'),
        avg_satisfaction=Avg('customer_satisfaction_avg'),
    )
    
    context = {
        'agent_performance': agent_performance,
        'team_summary': team_summary,
        'date_range': date_range,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'callcenter/manager/agent_reports.html', context)

# API Views for AJAX

@login_required
def update_agent_status(request):
    """Update agent status via AJAX."""
    if request.method == 'POST':
        status = request.POST.get('status')
        session, created = AgentSession.objects.get_or_create(
            agent=request.user,
            defaults={'status': status}
        )
        session.status = status
        session.save()
        
        return JsonResponse({'status': 'success', 'new_status': status})
    
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def get_order_details(request, order_id):
    """Get order details via AJAX."""
    order = get_object_or_404(Order, id=order_id)
    
    data = {
        'id': order.id,
        'customer_name': order.customer.get_full_name() if order.customer else 'No Customer',
        'customer_phone': order.customer_phone,
        'status': order.status,
        'total_amount': str(order.total_price),
        'created_at': order.date.strftime('%Y-%m-%d %H:%M'),
    }
    
    return JsonResponse(data)

# Legacy views for backward compatibility

@login_required
def dashboard(request):
    """Legacy dashboard - redirect to appropriate panel."""
    if is_call_center_manager(request.user):
        return redirect('callcenter:manager_dashboard')
    elif is_call_center_agent(request.user):
        return redirect('callcenter:agent_dashboard')
    else:
        return redirect('callcenter:agent_dashboard')  # Default fallback

@login_required
def order_list(request):
    """Legacy order list - redirect to appropriate panel."""
    if is_call_center_manager(request.user):
        return redirect('callcenter:manager_order_list')
    elif is_call_center_agent(request.user):
        return redirect('callcenter:agent_order_list')
    else:
        return redirect('callcenter:agent_order_list')  # Default fallback
