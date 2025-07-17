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

@login_required
@user_passes_test(is_delivery_user)
def dashboard(request):
    """Delivery dashboard with statistics and current tasks"""
    today = timezone.now().date()
    
    # Get user's courier profile if exists
    courier = None
    if hasattr(request.user, 'courier_profile'):
        courier = request.user.courier_profile
    
    # Get delivery statistics
    if courier:
        # Courier-specific statistics
        deliveries = DeliveryRecord.objects.filter(courier=courier)
        today_deliveries = deliveries.filter(assigned_at__date=today)
        
        stats = {
            'assigned': today_deliveries.filter(status='assigned').count(),
            'picked_up': today_deliveries.filter(status='picked_up').count(),
            'in_transit': today_deliveries.filter(status='in_transit').count(),
            'delivered': today_deliveries.filter(status='delivered').count(),
            'failed': today_deliveries.filter(status='failed').count(),
        }
        
        # Current task (next delivery)
        current_task = today_deliveries.filter(
            status__in=['assigned', 'accepted', 'picked_up']
        ).order_by('estimated_delivery_time').first()
        
        # Next deliveries
        next_deliveries = today_deliveries.filter(
            status__in=['assigned', 'accepted']
        ).order_by('estimated_delivery_time')[:7]
        
    else:
        # Admin/Manager statistics
        deliveries = DeliveryRecord.objects.all()
        today_deliveries = deliveries.filter(assigned_at__date=today)
        
        stats = {
            'assigned': today_deliveries.filter(status='assigned').count(),
            'picked_up': today_deliveries.filter(status='picked_up').count(),
            'in_transit': today_deliveries.filter(status='in_transit').count(),
            'delivered': today_deliveries.filter(status='delivered').count(),
            'failed': today_deliveries.filter(status='failed').count(),
        }
        
        current_task = None
        next_deliveries = []
    
    # Overall statistics
    total_deliveries = deliveries.count()
    successful_deliveries = deliveries.filter(status='delivered').count()
    success_rate = (successful_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0
    
    # Recent activity
    recent_activity = DeliveryStatusHistory.objects.select_related(
        'delivery', 'changed_by'
    ).order_by('-timestamp')[:10]
    
    context = {
        'stats': stats,
        'current_task': current_task,
        'next_deliveries': next_deliveries,
        'total_deliveries': total_deliveries,
        'successful_deliveries': successful_deliveries,
        'success_rate': round(success_rate, 1),
        'recent_activity': recent_activity,
        'courier': courier,
        'today': today,
    }
    
    return render(request, 'delivery/dashboard.html', context)

@login_required
@user_passes_test(is_delivery_user)
def order_list(request):
    """List of orders for delivery with filtering and search"""
    # Get user's courier profile if exists
    courier = None
    if hasattr(request.user, 'courier_profile'):
        courier = request.user.courier_profile
    
    # Base queryset
    if courier:
        deliveries = DeliveryRecord.objects.filter(courier=courier)
    else:
        deliveries = DeliveryRecord.objects.all()
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        deliveries = deliveries.filter(
            Q(tracking_number__icontains=search_query) |
            Q(order__order_number__icontains=search_query) |
            Q(order__customer_name__icontains=search_query) |
            Q(order__customer_phone__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        deliveries = deliveries.filter(status=status_filter)
    
    # Filter by date
    date_filter = request.GET.get('date', '')
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            deliveries = deliveries.filter(assigned_at__date=filter_date)
        except ValueError:
            pass
    
    # Filter by priority
    priority_filter = request.GET.get('priority', '')
    if priority_filter:
        deliveries = deliveries.filter(priority=priority_filter)
    
    # Order by
    order_by = request.GET.get('order_by', '-assigned_at')
    deliveries = deliveries.order_by(order_by)
    
    # Pagination
    paginator = Paginator(deliveries, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics for filters
    status_counts = DeliveryRecord.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'date_filter': date_filter,
        'priority_filter': priority_filter,
        'order_by': order_by,
        'status_counts': status_counts,
        'courier': courier,
    }
    
    return render(request, 'delivery/order_list.html', context)

@login_required
@user_passes_test(is_delivery_user)
def order_detail(request, delivery_id):
    """Detailed view of a delivery order"""
    delivery = get_object_or_404(DeliveryRecord, id=delivery_id)
    
    # Check if user has access to this delivery
    courier = None
    if hasattr(request.user, 'courier_profile'):
        courier = request.user.courier_profile
        # Only restrict access if user is a courier and doesn't own this delivery
        # Super admins and admins can view all deliveries
        if (courier and delivery.courier != courier and 
            not request.user.is_superuser and 
            not request.user.has_role('Super Admin') and 
            not request.user.has_role('Admin')):
            messages.error(request, "You don't have permission to view this delivery.")
            return redirect('delivery:order_list')
    
    # Get delivery history
    status_history = delivery.status_history.all().order_by('-timestamp')
    
    # Get delivery attempts
    attempts = delivery.attempts.all().order_by('-attempt_time')
    
    # Get delivery proofs
    proofs = delivery.proofs.all().order_by('-capture_time')
    
    context = {
        'delivery': delivery,
        'status_history': status_history,
        'attempts': attempts,
        'proofs': proofs,
        'courier': courier,
    }
    
    return render(request, 'delivery/order_detail.html', context)

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
    """Performance tracking and statistics"""
    courier = None
    if hasattr(request.user, 'courier_profile'):
        courier = request.user.courier_profile
    
    # Date range
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    if courier:
        # Courier-specific performance
        performance_data = DeliveryPerformance.objects.filter(
            courier=courier,
            date__range=[start_date, end_date]
        ).order_by('date')
        
        # Daily statistics
        daily_stats = []
        for i in range(30):
            date = end_date - timedelta(days=i)
            try:
                perf = performance_data.get(date=date)
                daily_stats.append({
                    'date': date,
                    'total': perf.total_deliveries if perf else 0,
                    'successful': perf.successful_deliveries if perf else 0,
                    'failed': perf.failed_deliveries if perf else 0,
                })
            except DeliveryPerformance.DoesNotExist:
                daily_stats.append({
                    'date': date,
                    'total': 0,
                    'successful': 0,
                    'failed': 0,
                })
        
        # Overall statistics
        total_deliveries = courier.total_deliveries
        successful_deliveries = courier.successful_deliveries
        failed_deliveries = courier.failed_deliveries
        success_rate = courier.get_success_rate()
        rating = courier.rating
        
    else:
        # Admin/Manager performance overview
        performance_data = DeliveryPerformance.objects.filter(
            date__range=[start_date, end_date]
        ).values('date').annotate(
            total=Sum('total_deliveries'),
            successful=Sum('successful_deliveries'),
            failed=Sum('failed_deliveries'),
        ).order_by('date')
        
        daily_stats = list(performance_data)
        
        # Overall statistics
        total_deliveries = DeliveryRecord.objects.count()
        successful_deliveries = DeliveryRecord.objects.filter(status='delivered').count()
        failed_deliveries = DeliveryRecord.objects.filter(status='failed').count()
        success_rate = (successful_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0
        rating = Courier.objects.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
    
    context = {
        'courier': courier,
        'daily_stats': daily_stats,
        'total_deliveries': total_deliveries,
        'successful_deliveries': successful_deliveries,
        'failed_deliveries': failed_deliveries,
        'success_rate': round(success_rate, 1),
        'rating': round(rating, 2),
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'delivery/performance.html', context)

@login_required
@user_passes_test(is_courier)
def settings(request):
    """Courier settings and profile"""
    courier = request.user.courier_profile
    
    if request.method == 'POST':
        # Update availability
        availability = request.POST.get('availability')
        if availability in dict(Courier.AVAILABILITY_CHOICES):
            courier.availability = availability
            courier.save()
            messages.success(request, 'Availability updated successfully!')
        
        # Update location if provided
        lat = request.POST.get('latitude')
        lng = request.POST.get('longitude')
        if lat and lng:
            try:
                courier.current_location_lat = Decimal(lat)
                courier.current_location_lng = Decimal(lng)
                courier.last_location_update = timezone.now()
                courier.save()
                
                # Create location record
                CourierLocation.objects.create(
                    courier=courier,
                    latitude=courier.current_location_lat,
                    longitude=courier.current_location_lng,
                    battery_level=request.POST.get('battery_level'),
                    connection_type=request.POST.get('connection_type', 'cellular')
                )
                
                messages.success(request, 'Location updated successfully!')
            except (ValueError, TypeError):
                messages.error(request, 'Invalid location data!')
    
    context = {
        'courier': courier,
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
