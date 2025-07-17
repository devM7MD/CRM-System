from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.utils import timezone
from django.db.models import Count, Sum, Avg, Q, F
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from datetime import datetime, timedelta
import json

from .models import (
    CallCenterAgent, AgentSession, CallLog, CustomerInteraction,
    OrderAssignment, ManagerNote, OrderStatusHistory, AgentPerformance, TeamPerformance
)
from orders.models import Order
from users.models import User

def is_call_center_manager(user):
    """Check if user is a call center manager"""
    return user.is_authenticated and hasattr(user, 'primary_role') and user.primary_role and user.primary_role.name.lower() in ['call center manager', 'super admin', 'admin']

def is_call_center_agent(user):
    """Check if user is a call center agent"""
    return user.is_authenticated and hasattr(user, 'primary_role') and user.primary_role and user.primary_role.name.lower() in ['call center agent', 'call center manager', 'super admin', 'admin']

def is_super_admin(user):
    """Check if user is super admin"""
    return user.is_authenticated and hasattr(user, 'primary_role') and user.primary_role and user.primary_role.name.lower() in ['super admin', 'admin']

# ==================== MANAGER PANEL VIEWS ====================

@login_required
@user_passes_test(is_call_center_manager)
def manager_dashboard(request):
    """Call Center Manager Dashboard"""
    today = timezone.now().date()
    
    # Get all orders for today
    today_orders = Order.objects.filter(date__date=today)
    total_orders = today_orders.count()
    
    # Order status counts
    confirmed_orders = today_orders.filter(status='confirmed').count()
    cancelled_orders = today_orders.filter(status='cancelled').count()
    postponed_orders = today_orders.filter(status='postponed').count()
    pending_orders = today_orders.filter(status='pending').count()
    
    # Calculate rates
    confirmation_rate = (confirmed_orders / total_orders * 100) if total_orders > 0 else 0
    cancellation_rate = (cancelled_orders / total_orders * 100) if total_orders > 0 else 0
    
    # Agent statistics
    active_agents = CallCenterAgent.objects.filter(availability='available').count()
    total_agents = CallCenterAgent.objects.filter(status='active').count()
    
    # Call statistics
    today_calls = CallLog.objects.filter(call_time__date=today)
    total_calls = today_calls.count()
    avg_response_time = today_calls.aggregate(avg_duration=Avg('duration'))['avg_duration'] or 0
    avg_response_time_minutes = avg_response_time / 60 if avg_response_time > 0 else 0
    
    # Customer satisfaction
    satisfaction_avg = today_calls.filter(customer_satisfaction__isnull=False).aggregate(
        avg_satisfaction=Avg('customer_satisfaction')
    )['avg_satisfaction'] or 0
    
    # Recent activity
    recent_assignments = OrderAssignment.objects.filter(
        assignment_date__date=today
    ).select_related('order', 'assigned_agent').order_by('-assignment_date')[:10]
    
    # Priority orders
    priority_orders = OrderAssignment.objects.filter(
        is_active=True,
        priority__in=['high', 'urgent']
    ).select_related('order', 'assigned_agent').order_by('priority', '-assignment_date')[:5]
    
    # Team performance
    team_performance = TeamPerformance.objects.filter(date=today).first()
    
    context = {
        'total_orders': total_orders,
        'confirmed_orders': confirmed_orders,
        'cancelled_orders': cancelled_orders,
        'postponed_orders': postponed_orders,
        'pending_orders': pending_orders,
        'confirmation_rate': round(confirmation_rate, 1),
        'cancellation_rate': round(cancellation_rate, 1),
        'active_agents': active_agents,
        'total_agents': total_agents,
        'total_calls': total_calls,
        'avg_response_time_minutes': round(avg_response_time_minutes, 1),
        'satisfaction_avg': round(satisfaction_avg, 1),
        'recent_assignments': recent_assignments,
        'priority_orders': priority_orders,
        'team_performance': team_performance,
        'today': today,
    }
    
    return render(request, 'callcenter/manager/dashboard.html', context)

@login_required
@user_passes_test(is_call_center_manager)
def manager_order_list(request):
    """Manager view of all orders with assignment capabilities"""
    # Get filter parameters
    status = request.GET.get('status', '')
    date_range = request.GET.get('date', 'today')
    agent_id = request.GET.get('agent', '')
    priority = request.GET.get('priority', '')
    search = request.GET.get('search', '')
    
    # Base queryset
    orders = Order.objects.all().select_related('seller')
    
    # Apply filters
    if status:
        orders = orders.filter(status=status)
    
    if date_range == 'today':
        orders = orders.filter(date__date=timezone.now().date())
    elif date_range == 'yesterday':
        orders = orders.filter(date__date=timezone.now().date() - timedelta(days=1))
    elif date_range == 'last_7_days':
        orders = orders.filter(date__date__gte=timezone.now().date() - timedelta(days=7))
    elif date_range == 'last_30_days':
        orders = orders.filter(date__date__gte=timezone.now().date() - timedelta(days=30))
    
    if priority:
        orders = orders.filter(call_center_assignments__priority=priority, call_center_assignments__is_active=True)
    
    if search:
        orders = orders.filter(
            Q(order_code__icontains=search) |
            Q(customer__full_name__icontains=search) |
            Q(customer_phone__icontains=search)
        )
    
    # Get available agents
    available_agents = CallCenterAgent.objects.filter(
        status='active',
        availability__in=['available', 'busy']
    ).select_related('user')
    
    # Pagination
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'orders': page_obj,
        'available_agents': available_agents,
        'status_filter': status,
        'date_filter': date_range,
        'priority_filter': priority,
        'search_query': search,
        'status_choices': Order.STATUS_CHOICES,
    }
    
    return render(request, 'callcenter/manager/order_list.html', context)

@login_required
@user_passes_test(is_call_center_manager)
def manager_agent_reports(request):
    """Manager view of agent performance reports"""
    # Get filter parameters
    date_range = request.GET.get('date', 'today')
    agent_id = request.GET.get('agent', '')
    team = request.GET.get('team', '')
    
    # Base queryset
    performances = AgentPerformance.objects.all().select_related('agent')
    
    # Apply date filter
    if date_range == 'today':
        performances = performances.filter(date=timezone.now().date())
    elif date_range == 'yesterday':
        performances = performances.filter(date=timezone.now().date() - timedelta(days=1))
    elif date_range == 'last_7_days':
        performances = performances.filter(date__gte=timezone.now().date() - timedelta(days=7))
    elif date_range == 'last_30_days':
        performances = performances.filter(date__gte=timezone.now().date() - timedelta(days=30))
    
    # Apply agent filter
    if agent_id:
        performances = performances.filter(agent_id=agent_id)
    
    # Apply team filter
    if team:
        performances = performances.filter(agent__call_center_profile__team=team)
    
    # Get teams for filter
    teams = CallCenterAgent.objects.values_list('team', flat=True).distinct().exclude(team='')
    
    # Get agents for filter
    agents = CallCenterAgent.objects.filter(status='active').select_related('user')
    
    # Pagination
    paginator = Paginator(performances, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'performances': page_obj,
        'agents': agents,
        'teams': teams,
        'date_filter': date_range,
        'agent_filter': agent_id,
        'team_filter': team,
    }
    
    return render(request, 'callcenter/manager/agent_reports.html', context)

@login_required
@user_passes_test(is_call_center_manager)
def assign_order(request, order_id):
    """Assign order to agent"""
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        agent_id = request.POST.get('agent_id')
        priority = request.POST.get('priority', 'medium')
        notes = request.POST.get('notes', '')
        expected_completion = request.POST.get('expected_completion')
        
        if agent_id:
            agent = get_object_or_404(User, id=agent_id)
            
            # Deactivate any existing assignments
            OrderAssignment.objects.filter(order=order, is_active=True).update(is_active=False)
            
            # Create new assignment
            assignment = OrderAssignment.objects.create(
                order=order,
                assigned_agent=agent,
                assigned_by=request.user,
                priority=priority,
                assignment_notes=notes,
                expected_completion=expected_completion if expected_completion else None
            )
            
            messages.success(request, f'Order {order.order_number} assigned to {agent.get_full_name()}')
            return redirect('callcenter:manager_order_list')
    
    return redirect('callcenter:manager_order_list')

@login_required
@user_passes_test(is_call_center_manager)
def create_manager_note(request, order_id):
    """Create a note for an agent"""
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        agent_id = request.POST.get('agent_id')
        note_text = request.POST.get('note_text')
        note_type = request.POST.get('note_type', 'instruction')
        is_urgent = request.POST.get('is_urgent') == 'on'
        
        if agent_id and note_text:
            agent = get_object_or_404(User, id=agent_id)
            
            ManagerNote.objects.create(
                order=order,
                manager=request.user,
                agent=agent,
                note_text=note_text,
                note_type=note_type,
                is_urgent=is_urgent
            )
            
            messages.success(request, 'Note created successfully')
            return redirect('callcenter:manager_order_list')
    
    return redirect('callcenter:manager_order_list')

# ==================== AGENT PANEL VIEWS ====================

@login_required
@user_passes_test(is_call_center_agent)
def agent_dashboard(request):
    """Call Center Agent Dashboard"""
    today = timezone.now().date()
    
    # Get agent profile
    try:
        agent_profile = request.user.call_center_profile
    except CallCenterAgent.DoesNotExist:
        messages.error(request, 'Agent profile not found. Please contact your supervisor.')
        return redirect('dashboard')
    
    # Get today's performance
    performance = AgentPerformance.objects.filter(agent=request.user, date=today).first()
    
    # Get assigned orders
    assigned_orders = OrderAssignment.objects.filter(
        assigned_agent=request.user,
        is_active=True
    ).select_related('order').order_by('priority', '-assignment_date')
    
    # Get priority orders
    priority_orders = assigned_orders.filter(priority__in=['high', 'urgent'])[:5]
    
    # Get recent calls
    recent_calls = CallLog.objects.filter(
        agent=request.user,
        call_time__date=today
    ).select_related('order').order_by('-call_time')[:10]
    
    # Get unread notes
    unread_notes = ManagerNote.objects.filter(
        agent=request.user,
        is_read_by_agent=False
    ).select_related('order', 'manager').order_by('-created_at')[:5]
    
    # Calculate today's stats
    today_calls = CallLog.objects.filter(agent=request.user, call_time__date=today)
    total_calls = today_calls.count()
    successful_calls = today_calls.filter(status='completed').count()
    
    # Get orders by status
    confirmed_orders = assigned_orders.filter(order__status='confirmed').count()
    cancelled_orders = assigned_orders.filter(order__status='cancelled').count()
    postponed_orders = assigned_orders.filter(order__status='postponed').count()
    
    context = {
        'agent_profile': agent_profile,
        'performance': performance,
        'assigned_orders': assigned_orders,
        'priority_orders': priority_orders,
        'recent_calls': recent_calls,
        'unread_notes': unread_notes,
        'total_calls': total_calls,
        'successful_calls': successful_calls,
        'confirmed_orders': confirmed_orders,
        'cancelled_orders': cancelled_orders,
        'postponed_orders': postponed_orders,
        'today': today,
    }
    
    return render(request, 'callcenter/agent/dashboard.html', context)

@login_required
@user_passes_test(is_call_center_agent)
def agent_order_list(request):
    """Agent view of assigned orders"""
    # Get filter parameters
    status = request.GET.get('status', '')
    priority = request.GET.get('priority', '')
    search = request.GET.get('search', '')
    
    # Base queryset - only assigned orders
    assignments = OrderAssignment.objects.filter(
        assigned_agent=request.user,
        is_active=True
    ).select_related('order')
    
    # Apply filters
    if status:
        assignments = assignments.filter(order__status=status)
    
    if priority:
        assignments = assignments.filter(priority=priority)
    
    if search:
        assignments = assignments.filter(
            Q(order__order_number__icontains=search) |
            Q(order__customer_name__icontains=search) |
            Q(order__customer_phone__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(assignments, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'assignments': page_obj,
        'status_filter': status,
        'priority_filter': priority,
        'search_query': search,
        'status_choices': Order.STATUS_CHOICES,
    }
    
    return render(request, 'callcenter/agent/order_list.html', context)

@login_required
@user_passes_test(is_call_center_agent)
def agent_order_detail(request, order_id):
    """Agent view of order details"""
    order = get_object_or_404(Order, id=order_id)
    
    # Check if agent is assigned to this order
    assignment = OrderAssignment.objects.filter(
        order=order,
        assigned_agent=request.user,
        is_active=True
    ).first()
    
    if not assignment and not is_super_admin(request.user):
        messages.error(request, 'You are not assigned to this order.')
        return redirect('callcenter:agent_order_list')
    
    # Get call logs for this order
    call_logs = CallLog.objects.filter(order=order).order_by('-call_time')
    
    # Get customer interactions
    interactions = CustomerInteraction.objects.filter(order=order).order_by('-interaction_time')
    
    # Get status history
    status_history = OrderStatusHistory.objects.filter(order=order).order_by('-change_timestamp')
    
    # Get manager notes
    notes = ManagerNote.objects.filter(order=order).order_by('-created_at')
    
    context = {
        'order': order,
        'assignment': assignment,
        'call_logs': call_logs,
        'interactions': interactions,
        'status_history': status_history,
        'notes': notes,
    }
    
    return render(request, 'callcenter/agent/order_detail.html', context)

@login_required
@user_passes_test(is_call_center_agent)
def update_order_status(request, order_id):
    """Update order status"""
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')
        reason = request.POST.get('reason', '')
        
        if new_status and new_status != order.status:
            # Record status change
            OrderStatusHistory.objects.create(
                order=order,
                agent=request.user,
                previous_status=order.status,
                new_status=new_status,
                status_change_reason=reason
            )
            
            # Update order status
            order.status = new_status
            order.save()
            
            messages.success(request, f'Order status updated to {new_status}')
            return redirect('callcenter:agent_order_detail', order_id=order_id)
    
    return redirect('callcenter:agent_order_detail', order_id=order_id)

@login_required
@user_passes_test(is_call_center_agent)
def log_call(request, order_id):
    """Log a call for an order"""
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        duration = request.POST.get('duration', 0)
        status = request.POST.get('status')
        notes = request.POST.get('notes', '')
        satisfaction = request.POST.get('satisfaction')
        
        if status:
            call_log = CallLog.objects.create(
                order=order,
                agent=request.user,
                duration=int(duration) if duration else 0,
                status=status,
                notes=notes,
                customer_satisfaction=int(satisfaction) if satisfaction else None
            )
            
            messages.success(request, 'Call logged successfully')
            return redirect('callcenter:agent_order_detail', order_id=order_id)
    
    return redirect('callcenter:agent_order_detail', order_id=order_id)

@login_required
@user_passes_test(is_call_center_agent)
def mark_note_read(request, note_id):
    """Mark a manager note as read"""
    note = get_object_or_404(ManagerNote, id=note_id, agent=request.user)
    note.is_read_by_agent = True
    note.read_at = timezone.now()
    note.save()
    
    return JsonResponse({'status': 'success'})

@login_required
@user_passes_test(is_call_center_agent)
def update_availability(request):
    """Update agent availability status"""
    if request.method == 'POST':
        availability = request.POST.get('availability')
        
        try:
            agent_profile = request.user.call_center_profile
            agent_profile.availability = availability
            agent_profile.save()
            
            messages.success(request, f'Availability updated to {availability}')
        except CallCenterAgent.DoesNotExist:
            messages.error(request, 'Agent profile not found')
    
    return redirect('callcenter:agent_dashboard')

# ==================== API VIEWS ====================

@login_required
@user_passes_test(is_call_center_agent)
def get_order_details_api(request, order_id):
    """API endpoint to get order details"""
    order = get_object_or_404(Order, id=order_id)
    
    data = {
        'order_number': order.order_number,
        'customer_name': order.customer_name,
        'customer_phone': order.customer_phone,
        'customer_address': order.customer_address,
        'status': order.status,
        'total_price': order.total_price,
        'created_at': order.created_at.isoformat(),
        'expected_delivery': order.expected_delivery.isoformat() if order.expected_delivery else None,
    }
    
    return JsonResponse(data)

@login_required
@user_passes_test(is_call_center_manager)
def get_agent_performance_api(request, agent_id):
    """API endpoint to get agent performance"""
    agent = get_object_or_404(User, id=agent_id)
    date_range = request.GET.get('date', 'today')
    
    # Get performance data
    if date_range == 'today':
        performance = AgentPerformance.objects.filter(agent=agent, date=timezone.now().date()).first()
    elif date_range == 'last_7_days':
        performances = AgentPerformance.objects.filter(
            agent=agent,
            date__gte=timezone.now().date() - timedelta(days=7)
        )
        # Aggregate data
        performance = {
            'total_orders_handled': performances.aggregate(Sum('total_orders_handled'))['total_orders_handled__sum'] or 0,
            'orders_confirmed': performances.aggregate(Sum('orders_confirmed'))['orders_confirmed__sum'] or 0,
            'customer_satisfaction_avg': performances.aggregate(Avg('customer_satisfaction_avg'))['customer_satisfaction_avg__avg'] or 0,
        }
    else:
        performance = None
    
    return JsonResponse(performance or {})

# ==================== LEGACY VIEWS (for backward compatibility) ====================

@login_required
def dashboard(request):
    """Legacy dashboard - redirect to appropriate panel"""
    if is_call_center_manager(request.user):
        return redirect('callcenter:manager_dashboard')
    elif is_call_center_agent(request.user):
        return redirect('callcenter:agent_dashboard')
    else:
        messages.error(request, 'Access denied. You do not have call center permissions.')
        return redirect('dashboard')

@login_required
def order_list(request):
    """Legacy order list - redirect to appropriate panel"""
    if is_call_center_manager(request.user):
        return redirect('callcenter:manager_order_list')
    elif is_call_center_agent(request.user):
        return redirect('callcenter:agent_order_list')
    else:
        messages.error(request, 'Access denied. You do not have call center permissions.')
        return redirect('dashboard')
