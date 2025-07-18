from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta
from orders.models import Order
from .models import FollowupRecord, CustomerFeedback

# Create your views here.

@login_required
def dashboard(request):
    """Followup dashboard with real data."""
    # Get today's date
    today = timezone.now().date()
    
    # Get follow-up records that need attention
    pending_followups = FollowupRecord.objects.filter(status='pending').count()
    in_progress_followups = FollowupRecord.objects.filter(status='in_progress').count()
    total_followup_needed = pending_followups + in_progress_followups
    
    # Get completed follow-ups today
    completed_today = FollowupRecord.objects.filter(
        status='completed',
        completed_at__date=today
    ).count()
    
    # Get average customer feedback rating
    avg_rating = CustomerFeedback.objects.aggregate(
        avg_rating=Avg('rating')
    )['avg_rating'] or 0.0
    
    # Get recent follow-up records
    recent_followups = FollowupRecord.objects.select_related(
        'order', 'agent'
    ).order_by('-created_at')[:10]
    
    # Get recent completed follow-ups for the report modal
    recent_completed = FollowupRecord.objects.filter(
        status='completed'
    ).select_related('order', 'agent').order_by('-completed_at')[:10]
    
    # Get recent feedback for the feedback modal
    recent_feedback = CustomerFeedback.objects.select_related('order').order_by('-created_at')[:10]
    
    # Get completed follow-ups this week
    completed_this_week = FollowupRecord.objects.filter(
        status='completed',
        completed_at__date__gte=today - timedelta(days=7)
    ).count()
    
    # Get orders that need follow-up (delivered orders without follow-up records)
    delivered_orders = Order.objects.filter(status='delivered').count()
    orders_with_followup = FollowupRecord.objects.filter(
        order__status='delivered'
    ).values('order').distinct().count()
    orders_needing_followup = delivered_orders - orders_with_followup
    
    # Get follow-up statistics by status
    followup_by_status = FollowupRecord.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    context = {
        'pending_followups': total_followup_needed,
        'completed_today': completed_today,
        'completed_this_week': completed_this_week,
        'avg_rating': round(avg_rating, 1),
        'recent_followups': recent_followups,
        'recent_completed': recent_completed,
        'recent_feedback': recent_feedback,
        'orders_needing_followup': orders_needing_followup,
        'followup_by_status': followup_by_status,
        'total_followup_records': FollowupRecord.objects.count(),
        'total_feedback': CustomerFeedback.objects.count(),
    }
    
    return render(request, 'followup/dashboard.html', context)

@login_required
def order_list(request):
    """List of orders for followup with real data."""
    # Get all follow-up records with related data
    followup_records = FollowupRecord.objects.select_related(
        'order', 'agent'
    ).order_by('-created_at')
    
    # Get search query
    search = request.GET.get('search', '')
    if search:
        followup_records = followup_records.filter(
            Q(order__order_code__icontains=search) |
            Q(order__customer_phone__icontains=search) |
            Q(agent__first_name__icontains=search) |
            Q(agent__last_name__icontains=search)
        )
    
    # Get status filter
    status_filter = request.GET.get('status', '')
    if status_filter:
        followup_records = followup_records.filter(status=status_filter)
    
    # Get date filter
    date_filter = request.GET.get('date_filter', '')
    if date_filter:
        today = timezone.now().date()
        if date_filter == 'today':
            followup_records = followup_records.filter(scheduled_for__date=today)
        elif date_filter == 'tomorrow':
            tomorrow = today + timedelta(days=1)
            followup_records = followup_records.filter(scheduled_for__date=tomorrow)
        elif date_filter == 'this_week':
            week_start = today - timedelta(days=today.weekday())
            week_end = week_start + timedelta(days=6)
            followup_records = followup_records.filter(
                scheduled_for__date__range=[week_start, week_end]
            )
        elif date_filter == 'next_week':
            week_start = today + timedelta(days=7-today.weekday())
            week_end = week_start + timedelta(days=6)
            followup_records = followup_records.filter(
                scheduled_for__date__range=[week_start, week_end]
            )
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(followup_records, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'followup_records': page_obj,
        'search_query': search,
        'status_filter': status_filter,
        'date_filter': date_filter,
        'total_records': followup_records.count(),
    }
    
    return render(request, 'followup/order_list.html', context)
