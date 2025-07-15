from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Avg, Count, Q
from django.contrib import messages
from django.http import JsonResponse
from .models import FollowupRecord, CustomerFeedback
from orders.models import Order
from django.core.paginator import Paginator
from datetime import timedelta
import json

# Create your views here.

@login_required
def dashboard(request):
    """Followup dashboard with real data."""
    today = timezone.now().date()
    
    # Count pending follow-ups
    pending_followups = FollowupRecord.objects.filter(
        status__in=['pending', 'in_progress']
    ).count()
    
    # Count completed today
    completed_today = FollowupRecord.objects.filter(
        status='completed',
        completed_at__date=today
    ).count()
    
    # Calculate average rating
    avg_rating = CustomerFeedback.objects.aggregate(
        avg=Avg('rating')
    )['avg'] or 0.0
    
    # Get recent follow-ups - ensure we include orders that need follow-up
    recent_followups = FollowupRecord.objects.select_related(
        'order', 'order__customer', 'agent'
    ).order_by('-scheduled_for')[:10]
    
    # If no follow-up records exist, show orders that need follow-up
    if not recent_followups:
        # Find orders that are delivered/completed and would need a follow-up
        delivered_completed_orders = Order.objects.filter(
            status__in=['delivered', 'completed']
        ).select_related('customer').order_by('-date')[:5]
        
        # Convert these orders to a format similar to followup records for the template
        recent_followups = []
        for order in delivered_completed_orders:
            recent_followups.append({
                'id': None,  # No followup ID yet
                'order': order,
                'status': 'needs_followup',
                'scheduled_for': None,
                'get_status_display': lambda: 'Needs Follow-up',
                'needs_followup': True
            })
    
    context = {
        'pending_followups': pending_followups,
        'completed_today': completed_today,
        'avg_rating': round(avg_rating, 1),
        'recent_followups': recent_followups
    }
    
    return render(request, 'followup/dashboard.html', context)

@login_required
def order_list(request):
    """List of orders for followup with filtering."""
    # Get filter parameters
    status = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')
    search = request.GET.get('search', '')
    
    # Base queryset - focus on orders that are delivered or completed and need followup
    # Get orders that are delivered or completed and don't have follow-ups yet
    delivered_completed_orders = Order.objects.filter(
        status__in=['delivered', 'completed']
    )
    
    # Get orders that already have followup records
    orders_with_followup = FollowupRecord.objects.all().values_list('order_id', flat=True)
    
    # Filter to include orders that need followup (either don't have one or have incomplete ones)
    followups = FollowupRecord.objects.select_related(
        'order', 'order__customer', 'agent'
    ).all()
    
    # Apply status filter
    if status:
        followups = followups.filter(status=status)
    
    # Apply date filter
    today = timezone.now().date()
    if date_filter == 'today':
        followups = followups.filter(scheduled_for__date=today)
    elif date_filter == 'tomorrow':
        tomorrow = today + timedelta(days=1)
        followups = followups.filter(scheduled_for__date=tomorrow)
    elif date_filter == 'this_week':
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        followups = followups.filter(scheduled_for__date__range=[start_of_week, end_of_week])
    
    # Apply search filter
    if search:
        followups = followups.filter(
            Q(order__order_code__icontains=search) |
            Q(order__customer_name__icontains=search) |
            Q(order__customer_phone__icontains=search) |
            Q(order__customer__full_name__icontains=search) if 'customer__full_name' in [f.name for f in Order._meta.get_fields()] else Q()
        )
    
    # Also get orders that need followup but don't have any yet
    orders_needing_followup = []
    if not status or status == 'pending':
        # Find orders that are delivered/completed and don't have any followup records
        orders_without_followup = delivered_completed_orders.exclude(
            id__in=orders_with_followup
        ).select_related('customer', 'seller')
        
        # Apply search filter to these orders too
        if search:
            orders_without_followup = orders_without_followup.filter(
                Q(order_code__icontains=search) |
                Q(customer_name__icontains=search) |
                Q(customer_phone__icontains=search) |
                Q(customer__full_name__icontains=search) if 'customer__full_name' in [f.name for f in Order._meta.get_fields()] else Q()
            )
        
        # Convert these orders to a format similar to followup records for the template
        for order in orders_without_followup:
            orders_needing_followup.append({
                'id': None,  # No followup ID yet
                'order': order,
                'status': 'needs_followup',
                'scheduled_for': None,
                'needs_followup': True
            })
    
    # Combine regular followups with orders needing followup
    combined_followups = list(followups)
    for item in orders_needing_followup:
        combined_followups.append(item)
    
    # Sort by scheduled date (if exists) or order date
    combined_followups.sort(key=lambda x: x.scheduled_for if hasattr(x, 'scheduled_for') and x.scheduled_for else 
                           x['order'].date if isinstance(x, dict) and 'order' in x else 
                           x.order.date, 
                           reverse=True)
    
    # Paginate the results
    paginator = Paginator(combined_followups, 15)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status,
        'date_filter': date_filter,
        'search_query': search,
        'orders_needing_followup_count': len(orders_needing_followup)
    }
    
    return render(request, 'followup/order_list.html', context)

@login_required
def create_followup(request):
    """Create a new follow-up record."""
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        scheduled_for = request.POST.get('scheduled_for')
        
        if not order_id or not scheduled_for:
            messages.error(request, "Order and scheduled date are required.")
            return redirect('followup:orders')
        
        # Check if order exists
        order = get_object_or_404(Order, id=order_id)
        
        # Create followup record
        followup = FollowupRecord.objects.create(
            order=order,
            agent=request.user,
            scheduled_for=scheduled_for,
            status='pending'
        )
        
        messages.success(request, f"Follow-up scheduled for order {order.order_code}")
        return redirect('followup:detail', followup_id=followup.id)
    
    # For GET requests, show form with available orders
    # Get orders that don't have follow-ups yet or have completed follow-ups
    existing_followup_orders = FollowupRecord.objects.filter(
        status__in=['pending', 'in_progress']
    ).values_list('order_id', flat=True)
    
    orders = Order.objects.filter(
        status__in=['delivered', 'completed']
    ).exclude(
        id__in=existing_followup_orders
    ).select_related('customer').order_by('-date')[:50]
    
    context = {
        'orders': orders
    }
    
    return render(request, 'followup/create_followup.html', context)

@login_required
def followup_detail(request, followup_id):
    """View and update a specific follow-up."""
    followup = get_object_or_404(FollowupRecord, id=followup_id)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        feedback = request.POST.get('feedback')
        
        # Update followup record
        followup.status = status
        followup.feedback = feedback
        
        # If completed, set completed_at
        if status == 'completed' and followup.status != 'completed':
            followup.completed_at = timezone.now()
        
        followup.save()
        
        messages.success(request, f"Follow-up for order {followup.order.order_code} updated.")
        return redirect('followup:orders')
    
    # Check if there's customer feedback
    try:
        feedback = CustomerFeedback.objects.get(order=followup.order)
    except CustomerFeedback.DoesNotExist:
        feedback = None
    
    context = {
        'followup': followup,
        'feedback': feedback
    }
    
    return render(request, 'followup/followup_detail.html', context)

@login_required
def feedback_list(request):
    """List all customer feedback."""
    feedbacks = CustomerFeedback.objects.select_related(
        'order', 'order__customer'
    ).order_by('-created_at')
    
    # Calculate statistics
    avg_rating = CustomerFeedback.objects.aggregate(
        avg=Avg('rating')
    )['avg'] or 0.0
    
    positive_count = CustomerFeedback.objects.filter(rating__gte=4).count()
    neutral_count = CustomerFeedback.objects.filter(rating=3).count()
    negative_count = CustomerFeedback.objects.filter(rating__lte=2).count()
    
    # Paginate the results
    paginator = Paginator(feedbacks, 15)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'avg_rating': round(avg_rating, 1),
        'positive_count': positive_count,
        'neutral_count': neutral_count,
        'negative_count': negative_count
    }
    
    return render(request, 'followup/feedback_list.html', context)

@login_required
def record_feedback(request, order_id):
    """Record customer feedback for an order."""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comments = request.POST.get('comments', '')
        
        if not rating:
            messages.error(request, "Rating is required.")
            return redirect('followup:record_feedback', order_id=order_id)
        
        # Create or update feedback
        try:
            feedback = CustomerFeedback.objects.get(order=order)
            feedback.rating = rating
            feedback.comments = comments
            feedback.save()
            messages.success(request, f"Feedback updated for order {order.order_code}")
        except CustomerFeedback.DoesNotExist:
            CustomerFeedback.objects.create(
                order=order,
                rating=int(rating),
                comments=comments
            )
            messages.success(request, f"Feedback recorded for order {order.order_code}")
        
        # Mark related followup as completed if it exists
        try:
            followup = FollowupRecord.objects.get(order=order, status__in=['pending', 'in_progress'])
            followup.status = 'completed'
            followup.completed_at = timezone.now()
            followup.save()
        except FollowupRecord.DoesNotExist:
            pass
        
        return redirect('followup:feedback')
    
    context = {
        'order': order
    }
    
    return render(request, 'followup/record_feedback.html', context)
