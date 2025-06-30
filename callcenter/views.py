from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Sum, Avg, F, Q
from .models import CallLog, AgentPerformance
from orders.models import Order
from datetime import datetime, timedelta
from django.contrib import messages
from users.models import User
import csv
from django.http import HttpResponse

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
    avg_duration = call_logs.aggregate(avg_duration=Avg('duration'))['avg_duration'] or 0
    
    # Format duration as minutes:seconds
    minutes = int(avg_duration // 60)
    seconds = int(avg_duration % 60)
    avg_call_duration = f"{minutes}:{seconds:02d}"
    
    # Get recent calls with related order details
    recent_calls = CallLog.objects.select_related('order', 'agent').order_by('-call_time')[:5]
    
    # Format recent calls for display
    formatted_recent_calls = []
    for call in recent_calls:
        status_class = 'bg-yellow-100 text-yellow-500'
        status_icon = '<svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>'
        
        if call.status != 'completed':
            status_class = 'bg-red-100 text-red-500'
            status_icon = '<svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>'
        
        customer_name = call.order.customer.get_full_name() if call.order.customer else call.order.customer_name or "Unknown Customer"
        
        formatted_recent_calls.append({
            'order_id': call.order.id,
            'order_code': call.order.order_code,
            'customer_name': customer_name,
            'status': call.status,
            'status_class': status_class,
            'status_icon': status_icon,
            'notes': call.notes[:50] + '...' if len(call.notes) > 50 else call.notes,
            'time': call.call_time.strftime('%H:%M %p'),
            'call_time': call.call_time
        })
    
    # Get today's agent performance or create summary data
    try:
        agent_performance = AgentPerformance.objects.get(agent=request.user, date=today)
        
        # Calculate performance metrics
        call_completion_rate = (agent_performance.successful_confirmations / agent_performance.calls_made * 100) if agent_performance.calls_made > 0 else 0
        
        # For task completion, get real metrics from calls made vs assigned calls
        assigned_calls = 25  # This would ideally come from a task assignment system
        task_completion = f"{agent_performance.calls_made}/{assigned_calls}"
        
        # Calculate average response time (in minutes) from call duration
        avg_response_time = f"{agent_performance.average_call_duration / 60:.1f} min" if agent_performance.average_call_duration > 0 else "0 min"
        
        # Customer satisfaction would ideally come from feedback records
        # For now, calculate a proxy based on successful confirmations
        customer_satisfaction = f"{4 + (agent_performance.successful_confirmations / agent_performance.calls_made) if agent_performance.calls_made > 0 else 0:.1f}/5"
        
    except AgentPerformance.DoesNotExist:
        # If no performance record exists, calculate from call logs
        agent_calls = call_logs.filter(agent=request.user)
        total_agent_calls = agent_calls.count()
        successful_calls = agent_calls.filter(status='completed').count()
        
        call_completion_rate = (successful_calls / total_agent_calls * 100) if total_agent_calls > 0 else 0
        task_completion = f"{total_agent_calls}/25"  # Assuming 25 daily call target
        
        avg_resp_time = agent_calls.aggregate(avg=Avg('duration'))['avg'] or 0
        avg_response_time = f"{avg_resp_time / 60:.1f} min"
        
        customer_satisfaction = f"{4 + (successful_calls / total_agent_calls) if total_agent_calls > 0 else 0:.1f}/5"
    
    # Get upcoming scheduled calls - orders that are pending or processing and need to be called
    # Make sure we don't include orders that have already been called today
    called_order_ids = call_logs.filter(call_time__date=today).values_list('order_id', flat=True)
    
    upcoming_calls = Order.objects.filter(
        status__in=['pending', 'processing']
    ).exclude(
        id__in=called_order_ids
    ).order_by('date')[:3]
    
    # Orders pending confirmation - pending orders that haven't been successfully called yet
    completed_call_order_ids = CallLog.objects.filter(status='completed').values_list('order_id', flat=True)
    
    # Ensure we retrieve at least some orders for display
    pending_confirmation = Order.objects.filter(
        status='pending'
    ).exclude(
        id__in=completed_call_order_ids
    ).order_by('-date')[:5]
    
    # If no pending orders found, include processing orders too
    if not pending_confirmation.exists():
        pending_confirmation = Order.objects.filter(
            status__in=['pending', 'processing']
        ).order_by('-date')[:5]
    
    context = {
        'total_calls_today': total_calls_today,
        'confirmed_orders': confirmed_orders,
        'failed_calls': failed_calls,
        'avg_call_duration': avg_call_duration,
        'recent_calls': formatted_recent_calls,
        
        # Performance metrics
        'call_completion_rate': f"{call_completion_rate:.0f}%",
        'task_completion': task_completion,
        'avg_response_time': avg_response_time,
        'customer_satisfaction': customer_satisfaction,
        
        # Upcoming calls and pending confirmations
        'upcoming_calls': upcoming_calls,
        'pending_confirmation': pending_confirmation,
        
        # Today's date for template comparison
        'today': today,
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
    export = request.GET.get('export', '')
    
    # Base queryset - get all orders
    # For call center, we primarily want to show pending and processing orders
    orders = Order.objects.select_related('customer', 'seller').filter(
        status__in=['pending', 'processing']
    )
    
    # Apply date filter
    today = timezone.now().date()
    if date_range == 'today':
        orders = orders.filter(date__date=today)
    elif date_range == 'yesterday':
        orders = orders.filter(date__date=today - timedelta(days=1))
    elif date_range == 'last_7_days':
        orders = orders.filter(date__date__gte=today - timedelta(days=7))
    elif date_range == 'last_30_days':
        orders = orders.filter(date__date__gte=today - timedelta(days=30))
    
    # Apply status filter if specified
    if status:
        orders = orders.filter(status=status)
    
    # Apply search filter - search by order code or customer name/phone
    if search:
        orders = orders.filter(
            Q(order_code__icontains=search) |
            Q(customer_name__icontains=search) |
            Q(customer_phone__icontains=search) |
            Q(customer__full_name__icontains=search) if 'customer__full_name' in [f.name for f in Order._meta.get_fields()] else Q()
        )
    
    # Get all related call logs
    order_ids = orders.values_list('id', flat=True)
    call_logs = CallLog.objects.filter(order_id__in=order_ids)
    
    # Create a dictionary of order IDs to their call statuses
    call_status_map = {}
    for call in call_logs:
        if call.order_id not in call_status_map:
            call_status_map[call.order_id] = {
                'status': call.status,
                'count': 1
            }
        elif call.status == 'completed':
            # Completed calls take precedence
            call_status_map[call.order_id] = {
                'status': 'completed',
                'count': 1
            }
        elif call.status == 'no_answer':
            # Increment no answer count
            if call_status_map[call.order_id]['status'] == 'no_answer':
                call_status_map[call.order_id]['count'] += 1
            else:
                call_status_map[call.order_id] = {
                    'status': 'no_answer',
                    'count': 1
                }
    
    # Export to CSV if requested
    if export == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="orders_{date_range}_{today.strftime("%Y-%m-%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Order ID', 'Customer', 'Phone', 'Date', 'Total Amount', 'Status', 'Call Status'])
        
        for order in orders:
            call_status = call_status_map.get(order.id, {'status': 'not_called', 'count': 0})
            
            # Format the call status for display
            display_status = "Not Called"
            if call_status['status'] == 'completed':
                display_status = "Successful"
            elif call_status['status'] == 'no_answer':
                display_status = f"No Answer ({call_status['count']})"
            elif call_status['status'] == 'busy':
                display_status = "Busy"
            elif call_status['status'] == 'wrong_number':
                display_status = "Wrong Number"
            
            customer_name = order.customer.get_full_name() if order.customer else order.customer_name or "Unknown Customer"
            customer_phone = order.customer.phone_number if order.customer else order.customer_phone or ""
            
            writer.writerow([
                order.order_code,
                customer_name,
                customer_phone,
                order.date.strftime('%Y-%m-%d'),
                f"${order.total_price}",
                order.get_status_display(),
                display_status
            ])
        
        return response
    
    # Get list of available agents for the filter dropdown
    agents = User.objects.filter(
        id__in=CallLog.objects.values_list('agent_id', flat=True).distinct()
    )
    
    # Count total pending orders
    pending_count = orders.filter(status='pending').count()
    
    # Prepare the orders with call status for the template
    orders_with_status = []
    for order in orders:
        call_status = call_status_map.get(order.id, {'status': 'not_called', 'count': 0})
        
        # Create initials for the customer
        customer_name = order.customer.get_full_name() if order.customer else order.customer_name or "Unknown"
        name_parts = customer_name.split()
        if len(name_parts) >= 2:
            initials = f"{name_parts[0][0]}{name_parts[-1][0]}".upper()
        else:
            initials = customer_name[0:2].upper() if customer_name else "UN"
        
        # Format the call status for display
        display_status = "Not Called"
        status_class = "bg-gray-100 text-gray-800"
        if call_status['status'] == 'completed':
            display_status = "Successful"
            status_class = "bg-green-100 text-green-800"
        elif call_status['status'] == 'no_answer':
            display_status = f"No Answer ({call_status['count']})"
            status_class = "bg-yellow-100 text-yellow-800"
        elif call_status['status'] == 'busy':
            display_status = "Busy"
            status_class = "bg-yellow-100 text-yellow-800"
        elif call_status['status'] == 'wrong_number':
            display_status = "Wrong Number"
            status_class = "bg-red-100 text-red-800"
        
        # Add order with status to the list
        orders_with_status.append({
            'order': order,
            'call_status': display_status,
            'status_class': status_class,
            'customer_initials': initials,
            'customer_name': customer_name,
            'customer_phone': order.customer.phone_number if order.customer else order.customer_phone or "",
        })
    
    context = {
        'orders': orders_with_status,
        'pending_count': pending_count,
        'agents': agents,
        'status_choices': Order.STATUS_CHOICES,
        'current_status': status,
        'current_date_range': date_range,
        'current_agent': agent_id,
        'search_query': search,
    }
    
    return render(request, 'callcenter/order_list.html', context)

@login_required
def call_customer(request, order_id):
    """Handle customer call for a specific order."""
    # Get the order
    order = get_object_or_404(Order, id=order_id)
    
    # If this is a POST request, process the call outcome
    if request.method == 'POST':
        status = request.POST.get('status', '')
        notes = request.POST.get('notes', '')
        duration = request.POST.get('duration', 0)
        
        # Create a new call log
        call_log = CallLog.objects.create(
            order=order,
            agent=request.user,
            status=status,
            notes=notes,
            duration=int(duration)
        )
        
        # Update agent performance for today
        today = timezone.now().date()
        agent_performance, created = AgentPerformance.objects.get_or_create(
            agent=request.user,
            date=today,
            defaults={'calls_made': 0, 'successful_confirmations': 0, 'average_call_duration': 0}
        )
        
        # Update the performance metrics
        agent_performance.calls_made += 1
        if status == 'completed':
            agent_performance.successful_confirmations += 1
            
        # Update average call duration
        if agent_performance.average_call_duration == 0:
            agent_performance.average_call_duration = int(duration)
        else:
            agent_performance.average_call_duration = (
                (agent_performance.average_call_duration * (agent_performance.calls_made - 1)) + int(duration)
            ) / agent_performance.calls_made
            
        agent_performance.save()
        
        # If call was successful, update order status as needed
        if status == 'completed':
            # Logic to update order status based on call purpose
            # This would depend on your business logic
            customer_name = order.customer.get_full_name() if order.customer else order.customer_name or "Customer"
            messages.success(request, f'Call to {customer_name} completed successfully.')
        else:
            customer_name = order.customer.get_full_name() if order.customer else order.customer_name or "Customer"
            messages.info(request, f'Call to {customer_name} marked as {status}.')
            
        # Redirect back to dashboard
        return redirect('callcenter:dashboard')
    
    # For GET requests, show the call form
    # Create a customer_data dictionary with fallbacks for missing customer information
    if order.customer:
        customer_data = {
            'full_name': order.customer.get_full_name(),
            'phone': order.customer.phone_number,
            'email': order.customer.email,
            'address': getattr(order.customer, 'address', ''),
            'city': getattr(order.customer, 'city', ''),
            'state': getattr(order.customer, 'state', ''),
            'postal_code': getattr(order.customer, 'postal_code', ''),
            'country': getattr(order.customer, 'country', '')
        }
    else:
        # Fallback to order customer fields
        customer_data = {
            'full_name': order.customer_name or "Unknown Customer",
            'phone': order.customer_phone or "",
            'email': order.customer_email or "",
            'address': order.shipping_address or "",
            'city': "",
            'state': "",
            'postal_code': "",
            'country': ""
        }
    
    context = {
        'order': order,
        'customer': order.customer,
        'customer_data': customer_data
    }
    
    return render(request, 'callcenter/call_customer.html', context)
