from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count, Avg, Sum, F
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from django.db import transaction
import json
import uuid
from datetime import datetime, timedelta
from decimal import Decimal

from .models import (
    DeliveryCompany, Courier, DeliveryRecord, DeliveryStatusHistory,
    DeliveryAttempt, CourierSession, CourierLocation, DeliveryProof,
    DeliveryRoute, DeliveryPerformance
)
from orders.models import Order
from users.models import User

User = get_user_model()

def is_delivery_user(user):
    """Check if user has delivery role or is super admin"""
    return (user.is_superuser or 
            user.has_role('Super Admin') or 
            user.has_role('Admin') or
            (hasattr(user, 'primary_role') and user.primary_role and 'delivery' in user.primary_role.name.lower()))

def is_courier(user):
    """Check if user is a courier"""
    return hasattr(user, 'courier_profile') and user.courier_profile is not None

def has_delivery_role(user):
    return (
        user.is_superuser or
        user.has_role('Super Admin') or
        user.has_role('Delivery')
    )

@login_required
def dashboard(request):
    """Delivery dashboard with real statistics and current tasks"""
    today = timezone.now().date()
    
    # Get date range from request
    start_date = request.GET.get('start_date', today)
    end_date = request.GET.get('end_date', today)
    
    try:
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        start_date = today
        end_date = today
    
    # Get user's courier profile if exists
    courier = None
    if hasattr(request.user, 'courier_profile'):
        courier = request.user.courier_profile
    
    # Get delivery statistics for the date range
    if courier:
        # Courier-specific statistics
        deliveries = DeliveryRecord.objects.filter(courier=courier)
        date_range_deliveries = deliveries.filter(assigned_at__date__range=[start_date, end_date])
        
        # Calculate real statistics
        total_deliveries = date_range_deliveries.count()
        successful_deliveries = date_range_deliveries.filter(status='delivered').count()
        failed_deliveries = date_range_deliveries.filter(status='failed').count()
        success_rate = (successful_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0
        
        # Get courier's average rating
        avg_rating = courier.rating or 0
        
        # Get courier's performance data
        performance_data = DeliveryPerformance.objects.filter(
            courier=courier,
            date__range=[start_date, end_date]
        ).aggregate(
            total_distance=Sum('total_distance'),
            total_time=Sum('total_time'),
            avg_delivery_time=Avg('average_delivery_time')
        )
        
        avg_delivery_time = performance_data['avg_delivery_time'] or 0
        total_distance = performance_data['total_distance'] or 0
        
        # Current task (next delivery)
        current_task = date_range_deliveries.filter(
            status__in=['assigned', 'accepted', 'picked_up']
        ).order_by('estimated_delivery_time').first()
        
        # Next deliveries
        next_deliveries = date_range_deliveries.filter(
            status__in=['assigned', 'accepted']
        ).order_by('estimated_delivery_time')[:7]
        
    else:
        # Admin/Manager statistics - all deliveries
        deliveries = DeliveryRecord.objects.all()
        date_range_deliveries = deliveries.filter(assigned_at__date__range=[start_date, end_date])
        
        # Calculate real statistics
        total_deliveries = date_range_deliveries.count()
        successful_deliveries = date_range_deliveries.filter(status='delivered').count()
        failed_deliveries = date_range_deliveries.filter(status='failed').count()
        success_rate = (successful_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0
        
        # Get average rating across all couriers
        avg_rating = Courier.objects.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
        
        # Get overall performance data
        performance_data = DeliveryPerformance.objects.filter(
            date__range=[start_date, end_date]
        ).aggregate(
            total_distance=Sum('total_distance'),
            total_time=Sum('total_time'),
            avg_delivery_time=Avg('average_delivery_time')
        )
        
        avg_delivery_time = performance_data['avg_delivery_time'] or 0
        total_distance = performance_data['total_distance'] or 0
        
        current_task = None
        next_deliveries = []
    
    # Calculate active deliveries (in progress)
    active_deliveries = date_range_deliveries.filter(
        status__in=['assigned', 'accepted', 'picked_up', 'in_transit', 'out_for_delivery']
    ).count()
    
    # Calculate completed today
    completed_today = date_range_deliveries.filter(status='delivered').count()
    
    # Get recent deliveries for the table
    recent_deliveries = DeliveryRecord.objects.select_related(
        'order', 'order__customer', 'courier'
    ).order_by('-assigned_at')[:10]
    
    # Get recent activity
    recent_activity = DeliveryStatusHistory.objects.select_related(
        'delivery', 'changed_by'
    ).order_by('-timestamp')[:10]
    
    # Get delivery companies count
    delivery_companies_count = DeliveryCompany.objects.filter(is_active=True).count()
    
    # Get active couriers count
    active_couriers_count = Courier.objects.filter(status='active').count()
    
    # Get courier's earnings (if courier)
    courier_earnings = 0
    if courier:
        # Calculate earnings based on successful deliveries and delivery cost
        successful_deliveries_for_earnings = date_range_deliveries.filter(status='delivered')
        courier_earnings = successful_deliveries_for_earnings.aggregate(
            total_earnings=Sum('delivery_cost')
        )['total_earnings'] or 0
    
    context = {
        'total_deliveries': total_deliveries,
        'successful_deliveries': successful_deliveries,
        'failed_deliveries': failed_deliveries,
        'success_rate': round(success_rate, 1),
        'avg_rating': round(avg_rating, 1),
        'avg_delivery_time': round(avg_delivery_time, 0),
        'total_distance': round(total_distance, 1),
        'courier_earnings': courier_earnings,
        'current_task': current_task,
        'next_deliveries': next_deliveries,
        'recent_activity': recent_activity,
        'courier': courier,
        'today': today,
        'start_date': start_date,
        'end_date': end_date,
        'active_deliveries': active_deliveries,
        'completed_today': completed_today,
        'recent_deliveries': recent_deliveries,
        'delivery_companies_count': delivery_companies_count,
        'active_couriers_count': active_couriers_count,
    }
    
    return render(request, 'delivery/dashboard.html', context)

@login_required
@user_passes_test(is_delivery_user)
def order_list(request):
    """Display list of delivery orders with real data"""
    # Get user's courier profile if exists
    courier = None
    if hasattr(request.user, 'courier_profile'):
        courier = request.user.courier_profile
    
    # Get filter parameters
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    date_filter = request.GET.get('date', '')
    order_by = request.GET.get('order_by', '-assigned_at')
    
    # Base queryset
    if courier:
        # Courier sees only their assigned deliveries
        deliveries = DeliveryRecord.objects.filter(courier=courier)
    else:
        # Admin/Manager sees all deliveries
        deliveries = DeliveryRecord.objects.all()
    
    # Apply filters
    if search_query:
        deliveries = deliveries.filter(
            Q(tracking_number__icontains=search_query) |
            Q(order__customer_name__icontains=search_query) |
            Q(order__customer_phone__icontains=search_query) |
            Q(order__order_number__icontains=search_query)
        )
    
    if status_filter:
        deliveries = deliveries.filter(status=status_filter)
    
    if priority_filter:
        deliveries = deliveries.filter(priority=priority_filter)
    
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            deliveries = deliveries.filter(assigned_at__date=filter_date)
        except ValueError:
            pass
    
    # Apply ordering
    deliveries = deliveries.order_by(order_by)
    
    # Pagination
    paginator = Paginator(deliveries, 20)  # 20 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get status counts for statistics
    status_counts = []
    if courier:
        courier_deliveries = DeliveryRecord.objects.filter(courier=courier)
    else:
        courier_deliveries = DeliveryRecord.objects.all()
    
    for status_choice in DeliveryRecord.STATUS_CHOICES:
        count = courier_deliveries.filter(status=status_choice[0]).count()
        if count > 0:
            status_counts.append((status_choice[1], count))
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'date_filter': date_filter,
        'order_by': order_by,
        'status_counts': status_counts,
        'courier': courier,
        'total_orders': paginator.count,
    }
    
    return render(request, 'delivery/order_list.html', context)

@login_required
@user_passes_test(is_delivery_user)
def order_detail(request, order_id):
    """Display detailed order information with real data"""
    try:
        # Get the delivery record
        delivery = DeliveryRecord.objects.select_related(
            'order', 'order__customer', 'courier', 'delivery_company'
        ).get(order_id=order_id)
    
        # Check if user has access to this delivery
        courier = None
        if hasattr(request.user, 'courier_profile'):
            courier = request.user.courier_profile
            if delivery.courier != courier:
                messages.error(request, "You don't have access to this delivery.")
                return redirect('delivery:order_list')
    
        # Get delivery status history
        status_history = DeliveryStatusHistory.objects.filter(
            delivery=delivery
        ).select_related('changed_by').order_by('-timestamp')
    
        # Get delivery attempts
        delivery_attempts = DeliveryAttempt.objects.filter(
            delivery=delivery
        ).order_by('-attempt_time')
    
        # Get delivery proofs
        delivery_proofs = DeliveryProof.objects.filter(
            delivery=delivery
        ).order_by('-capture_time')
        
        # Get courier location history for this delivery
        location_history = []
        if courier:
            location_history = CourierLocation.objects.filter(
                courier=courier,
                timestamp__gte=delivery.assigned_at
            ).order_by('-timestamp')[:10]
        
        # Calculate delivery statistics
        delivery_time = delivery.get_delivery_time()
        estimated_time = delivery.get_estimated_delivery_time()
        
        # Get related deliveries (same courier, same day)
        related_deliveries = []
        if courier:
            related_deliveries = DeliveryRecord.objects.filter(
                courier=courier,
                assigned_at__date=delivery.assigned_at.date()
            ).exclude(id=delivery.id).order_by('assigned_at')[:5]
    
        context = {
            'delivery': delivery,
            'order': delivery.order,
            'courier': courier,
            'status_history': status_history,
            'delivery_attempts': delivery_attempts,
            'delivery_proofs': delivery_proofs,
            'location_history': location_history,
            'related_deliveries': related_deliveries,
            'delivery_time': delivery_time,
            'estimated_time': estimated_time,
        }
    
        return render(request, 'delivery/order_detail.html', context)
        
    except DeliveryRecord.DoesNotExist:
        messages.error(request, "Delivery not found.")
        return redirect('delivery:order_list')

@login_required
@user_passes_test(is_courier)
def update_status(request, delivery_id):
    """Update delivery status (AJAX)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    delivery = get_object_or_404(DeliveryRecord, id=delivery_id)
    courier = request.user.courier_profile
    
    # Check if courier owns this delivery
    if delivery.courier != courier:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    new_status = request.POST.get('status')
    notes = request.POST.get('notes', '')
    
    if new_status not in dict(DeliveryRecord.STATUS_CHOICES):
        return JsonResponse({'error': 'Invalid status'}, status=400)
    
    try:
        with transaction.atomic():
            # Update delivery status
            old_status = delivery.status
            delivery.status = new_status
            
            # Update timestamps based on status
            now = timezone.now()
            if new_status == 'accepted' and not delivery.accepted_at:
                delivery.accepted_at = now
            elif new_status == 'picked_up' and not delivery.picked_up_at:
                delivery.picked_up_at = now
            elif new_status == 'out_for_delivery' and not delivery.out_for_delivery_at:
                delivery.out_for_delivery_at = now
            elif new_status == 'delivered' and not delivery.delivered_at:
                delivery.delivered_at = now
                delivery.actual_delivery_time = now
            elif new_status == 'failed' and not delivery.failed_at:
                delivery.failed_at = now
            
            delivery.save()
            
            # Create status history
            DeliveryStatusHistory.objects.create(
                delivery=delivery,
                status=new_status,
                changed_by=request.user,
                notes=notes
            )
            
            # Update courier statistics if delivered
            if new_status == 'delivered' and old_status != 'delivered':
                courier.total_deliveries += 1
                courier.successful_deliveries += 1
                courier.save()
            elif new_status == 'failed' and old_status != 'failed':
                courier.total_deliveries += 1
                courier.failed_deliveries += 1
                courier.save()
            
            return JsonResponse({
                'success': True,
                'status': new_status,
                'message': f'Status updated to {new_status}'
            })
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@user_passes_test(is_courier)
def complete_delivery(request, delivery_id):
    """Complete delivery with proof"""
    delivery = get_object_or_404(DeliveryRecord, id=delivery_id)
    courier = request.user.courier_profile
    
    # Check if courier owns this delivery
    if delivery.courier != courier:
        messages.error(request, "You don't have permission to complete this delivery.")
        return redirect('delivery:order_detail', delivery_id=delivery_id)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Update delivery status
                delivery.status = 'delivered'
                delivery.delivered_at = timezone.now()
                delivery.actual_delivery_time = timezone.now()
                
                # Get form data
                customer_signature = request.POST.get('customer_signature', '')
                delivery_notes = request.POST.get('delivery_notes', '')
                customer_rating = request.POST.get('customer_rating')
                customer_feedback = request.POST.get('customer_feedback', '')
                
                # Update delivery record
                if customer_signature:
                    delivery.customer_signature = customer_signature
                if delivery_notes:
                    delivery.delivery_notes = delivery_notes
                if customer_rating:
                    delivery.customer_rating = int(customer_rating)
                if customer_feedback:
                    delivery.customer_feedback = customer_feedback
                
                # Handle proof photo
                if 'proof_photo' in request.FILES:
                    delivery.delivery_proof_photo = request.FILES['proof_photo']
                
                delivery.save()
                
                # Create status history
                DeliveryStatusHistory.objects.create(
                    delivery=delivery,
                    status='delivered',
                    changed_by=request.user,
                    notes=delivery_notes
                )
                
                # Create delivery proof
                if customer_signature:
                    DeliveryProof.objects.create(
                        delivery=delivery,
                        courier=courier,
                        proof_type='signature',
                        proof_data=customer_signature
                    )
                
                if 'proof_photo' in request.FILES:
                    DeliveryProof.objects.create(
                        delivery=delivery,
                        courier=courier,
                        proof_type='photo',
                        proof_data='Photo uploaded'
                    )
                
                # Update courier statistics
                courier.total_deliveries += 1
                courier.successful_deliveries += 1
                courier.save()
                
                messages.success(request, 'Delivery completed successfully!')
                return redirect('delivery:dashboard')
                
        except Exception as e:
            messages.error(request, f'Error completing delivery: {str(e)}')
    
    context = {
        'delivery': delivery,
        'courier': courier,
    }
    
    return render(request, 'delivery/complete_delivery.html', context)

@login_required
@user_passes_test(is_courier)
def failed_delivery(request, delivery_id):
    """Report failed delivery"""
    delivery = get_object_or_404(DeliveryRecord, id=delivery_id)
    courier = request.user.courier_profile
    
    # Check if courier owns this delivery
    if delivery.courier != courier:
        messages.error(request, "You don't have permission to report this delivery.")
        return redirect('delivery:order_detail', delivery_id=delivery_id)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Get form data
                failure_reason = request.POST.get('failure_reason')
                customer_feedback = request.POST.get('customer_feedback', '')
                notes = request.POST.get('notes', '')
                next_attempt_date = request.POST.get('next_attempt_date')
                
                # Create delivery attempt
                attempt = DeliveryAttempt.objects.create(
                    delivery=delivery,
                    courier=courier,
                    attempt_number=delivery.attempts.count() + 1,
                    result='failed',
                    failure_reason=failure_reason,
                    customer_feedback=customer_feedback,
                    notes=notes,
                    next_attempt_date=next_attempt_date if next_attempt_date else None
                )
                
                # Handle proof photo if provided
                if 'proof_image' in request.FILES:
                    attempt.proof_image = request.FILES['proof_image']
                    attempt.save()
                
                # Update delivery status
                delivery.status = 'failed'
                delivery.failed_at = timezone.now()
                delivery.save()
                
                # Create status history
                DeliveryStatusHistory.objects.create(
                    delivery=delivery,
                    status='failed',
                    changed_by=request.user,
                    notes=f"Failed: {failure_reason}. {notes}"
                )
                
                # Update courier statistics
                courier.total_deliveries += 1
                courier.failed_deliveries += 1
                courier.save()
                
                messages.success(request, 'Failed delivery reported successfully!')
                return redirect('delivery:dashboard')
                
        except Exception as e:
            messages.error(request, f'Error reporting failed delivery: {str(e)}')
    
    context = {
        'delivery': delivery,
        'courier': courier,
    }
    
    return render(request, 'delivery/failed_delivery.html', context)

@login_required
@user_passes_test(is_delivery_user)
def performance(request):
    """Display courier performance with real data"""
    # Get user's courier profile
    courier = None
    if hasattr(request.user, 'courier_profile'):
        courier = request.user.courier_profile
    
    if not courier:
        messages.error(request, "Courier profile not found.")
        return redirect('delivery:dashboard')
    
    # Get date range (default to current week)
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    start_date = request.GET.get('start_date', start_of_week)
    end_date = request.GET.get('end_date', end_of_week)
    
    try:
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        start_date = start_of_week
        end_date = end_of_week
    
    # Get performance data for the date range
        performance_data = DeliveryPerformance.objects.filter(
            courier=courier,
            date__range=[start_date, end_date]
    ).aggregate(
        total_deliveries=Sum('total_deliveries'),
        successful_deliveries=Sum('successful_deliveries'),
        failed_deliveries=Sum('failed_deliveries'),
        total_distance=Sum('total_distance'),
        total_time=Sum('total_time'),
        avg_delivery_time=Avg('average_delivery_time'),
        avg_rating=Avg('customer_rating')
    )
    
    # Calculate success rate
    total_deliveries = performance_data['total_deliveries'] or 0
    successful_deliveries = performance_data['successful_deliveries'] or 0
    success_rate = (successful_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0
    
    # Get earnings for the period
    earnings_data = DeliveryRecord.objects.filter(
        courier=courier,
        status='delivered',
        delivered_at__date__range=[start_date, end_date]
    ).aggregate(
        total_earnings=Sum('delivery_cost')
    )
    total_earnings = earnings_data['total_earnings'] or 0
    
    # Get daily performance for chart
    daily_performance = DeliveryPerformance.objects.filter(
        courier=courier,
        date__range=[start_date, end_date]
    ).order_by('date').values('date', 'total_deliveries', 'successful_deliveries')
    
    # Get achievements based on performance
    achievements = []
    
    # Perfect Week achievement
    if success_rate >= 100 and total_deliveries > 0:
        achievements.append('Perfect Week')
    
    # Speed Demon achievement
    avg_delivery_time = performance_data['avg_delivery_time'] or 0
    if avg_delivery_time <= 15:  # 15 minutes or less
        achievements.append('Speed Demon')
    
    # 5-Star Pro achievement
    avg_rating = performance_data['avg_rating'] or 0
    if avg_rating >= 4.8:
        achievements.append('5-Star Pro')
    
    # Premium Courier achievement
    if total_deliveries >= 50:
        achievements.append('Premium Courier')
    
    # Accuracy Expert achievement
    if success_rate >= 95:
        achievements.append('Accuracy Expert')
    
    # Tech Savvy achievement (based on app usage)
    if courier.sessions.filter(login_time__date__range=[start_date, end_date]).count() >= 5:
        achievements.append('Tech Savvy')
    
    # Get improvement areas
    improvement_areas = []
    
    if success_rate < 95:
        improvement_areas.append({
            'title': 'Maintain 95%+ success rate',
            'description': f'Currently at {success_rate:.1f}% - almost there!',
            'type': 'success_rate'
        })
    
    if avg_delivery_time > 20:
        improvement_areas.append({
            'title': 'Reduce average delivery time by 2 minutes',
            'description': 'Optimize routes and improve efficiency',
            'type': 'delivery_time'
        })
    
    if total_deliveries < 30:
        improvement_areas.append({
            'title': 'Work on weekend availability',
            'description': 'Increase earnings by 20% with weekend shifts',
            'type': 'availability'
        })
    
    # Get earnings breakdown
    earnings_breakdown = {
        'base_rate': total_earnings * 0.8,  # 80% base rate
        'bonuses': total_earnings * 0.15,   # 15% bonuses
        'tips': total_earnings * 0.05,      # 5% tips
        'total': total_earnings
    }
    
    # Get comparison with previous period
    prev_start_date = start_date - timedelta(days=(end_date - start_date).days + 1)
    prev_end_date = start_date - timedelta(days=1)
    
    prev_performance = DeliveryPerformance.objects.filter(
        courier=courier,
        date__range=[prev_start_date, prev_end_date]
    ).aggregate(
        total_deliveries=Sum('total_deliveries'),
        successful_deliveries=Sum('successful_deliveries'),
        total_earnings=Sum('total_distance')  # Using distance as proxy for earnings
    )
    
    prev_total_deliveries = prev_performance['total_deliveries'] or 0
    prev_successful_deliveries = prev_performance['successful_deliveries'] or 0
    
    # Calculate percentage changes
    delivery_change = ((total_deliveries - prev_total_deliveries) / prev_total_deliveries * 100) if prev_total_deliveries > 0 else 0
    success_change = ((successful_deliveries - prev_successful_deliveries) / prev_successful_deliveries * 100) if prev_successful_deliveries > 0 else 0
    
    context = {
        'courier': courier,
        'start_date': start_date,
        'end_date': end_date,
        'total_deliveries': total_deliveries,
        'successful_deliveries': successful_deliveries,
        'failed_deliveries': performance_data['failed_deliveries'] or 0,
        'success_rate': round(success_rate, 1),
        'avg_delivery_time': round(avg_delivery_time, 0),
        'avg_rating': round(avg_rating, 1),
        'total_earnings': total_earnings,
        'total_distance': round(performance_data['total_distance'] or 0, 1),
        'achievements': achievements,
        'improvement_areas': improvement_areas,
        'earnings_breakdown': earnings_breakdown,
        'daily_performance': list(daily_performance),
        'delivery_change': round(delivery_change, 1),
        'success_change': round(success_change, 1),
    }
    
    return render(request, 'delivery/performance.html', context)

@login_required
@user_passes_test(is_delivery_user)
def settings(request):
    """Display and handle courier settings"""
        # Get user's courier profile
    courier = None
    if hasattr(request.user, 'courier_profile'):
        courier = request.user.courier_profile
    
    if not courier:
        messages.error(request, "Courier profile not found.")
        return redirect('delivery:dashboard')
    
    # Handle form submission
    if request.method == 'POST':
        # Update courier settings
        try:
            # Update vehicle information
            courier.vehicle_type = request.POST.get('vehicle_type', courier.vehicle_type)
            courier.vehicle_number = request.POST.get('vehicle_number', courier.vehicle_number)
            courier.license_number = request.POST.get('license_number', courier.license_number)
            courier.max_daily_deliveries = int(request.POST.get('max_daily_deliveries', courier.max_daily_deliveries))
            
            # Update availability status
            courier.availability = request.POST.get('availability', courier.availability)
            
            courier.save()
            messages.success(request, "Settings updated successfully!")
            
        except Exception as e:
            messages.error(request, f"Error updating settings: {str(e)}")
    
    # Get courier's current session
    current_session = CourierSession.objects.filter(
                    courier=courier,
        logout_time__isnull=True
    ).first()
    
    # Get courier's recent locations
    recent_locations = CourierLocation.objects.filter(
        courier=courier
    ).order_by('-timestamp')[:5]
    
    # Get courier's performance summary
    performance_summary = DeliveryPerformance.objects.filter(
        courier=courier
    ).aggregate(
        total_deliveries=Sum('total_deliveries'),
        successful_deliveries=Sum('successful_deliveries'),
        total_distance=Sum('total_distance'),
        avg_rating=Avg('customer_rating')
    )
    
    context = {
        'courier': courier,
        'user': request.user,
        'current_session': current_session,
        'recent_locations': recent_locations,
        'performance_summary': performance_summary,
        'vehicle_types': [
            ('sedan', 'Sedan'),
            ('suv', 'SUV'),
            ('van', 'Van'),
            ('motorcycle', 'Motorcycle'),
            ('bicycle', 'Bicycle'),
        ],
        'availability_choices': Courier.AVAILABILITY_CHOICES,
    }
    
    return render(request, 'delivery/settings.html', context)

# API Endpoints for mobile app integration

@csrf_exempt
@require_http_methods(["POST"])
def update_location(request):
    """Update courier location (API endpoint)"""
    try:
        data = json.loads(request.body)
        courier_id = data.get('courier_id')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        battery_level = data.get('battery_level')
        connection_type = data.get('connection_type', 'cellular')
        
        courier = get_object_or_404(Courier, id=courier_id)
        
        # Update courier location
        courier.current_location_lat = Decimal(latitude)
        courier.current_location_lng = Decimal(longitude)
        courier.last_location_update = timezone.now()
        courier.save()
        
        # Create location record
        CourierLocation.objects.create(
            courier=courier,
            latitude=latitude,
            longitude=longitude,
            battery_level=battery_level,
            connection_type=connection_type
        )
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def update_availability(request):
    """Update courier availability (API endpoint)"""
    try:
        data = json.loads(request.body)
        courier_id = data.get('courier_id')
        availability = data.get('availability')
        
        courier = get_object_or_404(Courier, id=courier_id)
        
        if availability in dict(Courier.AVAILABILITY_CHOICES):
            courier.availability = availability
            courier.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'error': 'Invalid availability status'}, status=400)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["GET"])
def get_assigned_orders(request, courier_id):
    """Get assigned orders for courier (API endpoint)"""
    try:
        courier = get_object_or_404(Courier, id=courier_id)
        today = timezone.now().date()
        
        deliveries = DeliveryRecord.objects.filter(
            courier=courier,
            assigned_at__date=today,
            status__in=['assigned', 'accepted', 'picked_up', 'out_for_delivery']
        ).select_related('order').order_by('estimated_delivery_time')
        
        orders_data = []
        for delivery in deliveries:
            orders_data.append({
                'id': str(delivery.id),
                'tracking_number': delivery.tracking_number,
                'order_number': delivery.order.order_number,
                'customer_name': delivery.order.customer_name,
                'customer_phone': delivery.order.customer_phone,
                'customer_address': delivery.order.customer_address,
                'status': delivery.status,
                'priority': delivery.priority,
                'delivery_cost': str(delivery.delivery_cost),
                'estimated_delivery_time': delivery.estimated_delivery_time.isoformat() if delivery.estimated_delivery_time else None,
                'assigned_at': delivery.assigned_at.isoformat(),
            })
        
        return JsonResponse({'orders': orders_data})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def upload_proof(request):
    """Upload delivery proof (API endpoint)"""
    try:
        delivery_id = request.POST.get('delivery_id')
        courier_id = request.POST.get('courier_id')
        proof_type = request.POST.get('proof_type')
        proof_data = request.POST.get('proof_data')
        
        delivery = get_object_or_404(DeliveryRecord, id=delivery_id)
        courier = get_object_or_404(Courier, id=courier_id)
        
        # Verify courier owns this delivery
        if delivery.courier != courier:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        # Create proof record
        DeliveryProof.objects.create(
            delivery=delivery,
            courier=courier,
            proof_type=proof_type,
            proof_data=proof_data
        )
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
