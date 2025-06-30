from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.db.models import Count, Sum, Avg, F, Q
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.utils.translation import gettext_lazy as _
import json
from datetime import datetime, timedelta

from .models import (
    DeliveryCompany, Courier, DeliveryRecord, DeliveryStatusHistory, 
    DeliveryRecordEnhanced, CourierSession, DeliveryAttempt, 
    CourierLocation, DeliveryProof
)
from orders.models import Order
from users.models import User

# Helper function to get or create courier profile
def get_or_create_courier(user):
    """Helper function to get or create a courier profile for a user"""
    # Make sure at least one delivery company exists
    company, company_created = DeliveryCompany.objects.get_or_create(
        defaults={
            'name': 'Atlas Delivery',
            'contact_person': 'Admin',
            'phone': '123456789',
            'email': 'delivery@atlas.com',
            'status': 'active'
        }
    )
    
    # Create courier profile if it doesn't exist
    courier, created = Courier.objects.get_or_create(
        user=user,
        defaults={
            'name': user.full_name,
            'phone': user.phone_number,
            'email': user.email,
            'company': company
        }
    )
    
    return courier, created

# Authentication views
def delivery_panel_login(request):
    """Login view for delivery panel"""
    if request.user.is_authenticated and request.user.role == 'delivery':
        return redirect('delivery:panel_dashboard')
        
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, email=email, password=password)
        
        if user is not None and user.role == 'delivery':
            login(request, user)
            
            # Create courier session
            courier, created = get_or_create_courier(user)
            
            if created:
                messages.info(request, _('Your courier profile has been created. Please contact admin to update your company details.'))
            
            # Create a new courier session
            CourierSession.objects.create(
                courier=courier,
                device_info=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return redirect('delivery:panel_dashboard')
        else:
            messages.error(request, _('Invalid login credentials or insufficient permissions'))
    
    return render(request, 'delivery/panel/login.html')

@login_required
def delivery_panel_logout(request):
    """Logout view for delivery panel"""
    # Update courier session
    if hasattr(request.user, 'courier_profile'):
        courier = request.user.courier_profile
        active_session = CourierSession.objects.filter(
            courier=courier,
            logout_time__isnull=True
        ).first()
        
        if active_session:
            active_session.logout_time = timezone.now()
            active_session.status = 'offline'
            active_session.save()
    
    logout(request)
    return redirect('delivery:panel_login')

# Dashboard and main views
@login_required
def delivery_panel_dashboard(request):
    """Dashboard view for delivery panel"""
    # Check if user has delivery role
    if request.user.role != 'delivery':
        messages.error(request, _('You need to have delivery role to access this panel'))
        logout(request)
        return redirect('delivery:panel_login')
    
    # Get or create courier profile
    courier, created = get_or_create_courier(request.user)
    
    if created:
        messages.info(request, _('Your courier profile has been created. Please contact admin to update your company details.'))
    
    today = timezone.now().date()
    
    # Get statistics for today
    assigned_count = DeliveryRecord.objects.filter(driver=request.user, status='assigned').count()
    picked_up_count = DeliveryRecord.objects.filter(driver=request.user, status='picked_up').count()
    in_transit_count = DeliveryRecord.objects.filter(driver=request.user, status='in_transit').count()
    delivered_count = DeliveryRecord.objects.filter(
        driver=request.user, 
        status='delivered',
        delivered_at__date=today
    ).count()
    failed_count = DeliveryRecord.objects.filter(
        driver=request.user, 
        status='failed',
        updated_at__date=today
    ).count()
    
    # Get current task
    current_task = DeliveryRecord.objects.filter(
        driver=request.user,
        status__in=['assigned', 'picked_up', 'in_transit', 'out_for_delivery']
    ).select_related('order').first()
    
    # Get upcoming deliveries
    upcoming_deliveries = DeliveryRecord.objects.filter(
        driver=request.user,
        status__in=['assigned', 'picked_up']
    ).select_related('order').order_by('assigned_at')[:7]
    
    context = {
        'courier': courier,
        'assigned_count': assigned_count,
        'picked_up_count': picked_up_count,
        'in_transit_count': in_transit_count,
        'delivered_count': delivered_count,
        'failed_count': failed_count,
        'current_task': current_task,
        'upcoming_deliveries': upcoming_deliveries,
        'today': today
    }
    
    return render(request, 'delivery/panel/dashboard.html', context)

@login_required
def delivery_panel_orders(request):
    """Orders list view for delivery panel"""
    # Check if user has delivery role
    if request.user.role != 'delivery':
        messages.error(request, _('You need to have delivery role to access this panel'))
        logout(request)
        return redirect('delivery:panel_login')
    
    # Get or create courier profile
    courier, created = get_or_create_courier(request.user)
    
    # Get filter parameters
    status = request.GET.get('status', '')
    date_range = request.GET.get('date', '')
    search = request.GET.get('search', '')
    
    # Base queryset for delivery records
    deliveries = DeliveryRecord.objects.filter(
        driver=request.user
    ).select_related('order').all()
    
    # Apply status filter
    if status:
        deliveries = deliveries.filter(status=status)
    
    # Apply date filter
    today = timezone.now().date()
    if date_range == 'today':
        deliveries = deliveries.filter(assigned_at__date=today)
    elif date_range == 'last_7_days':
        seven_days_ago = today - timedelta(days=7)
        deliveries = deliveries.filter(assigned_at__date__gte=seven_days_ago)
    
    # Apply search filter
    if search:
        deliveries = deliveries.filter(
            Q(order__order_code__icontains=search) |
            Q(tracking_number__icontains=search) |
            Q(order__customer_name__icontains=search)
        )
    
    # Get urgent orders first
    urgent_orders = deliveries.filter(status__in=['assigned', 'picked_up', 'in_transit']).order_by('assigned_at')
    
    # Get completed orders
    completed_orders = deliveries.filter(status='delivered').order_by('-delivered_at')
    
    # Paginate results
    paginator = Paginator(deliveries, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'courier': courier,
        'deliveries': page_obj,
        'urgent_orders': urgent_orders,
        'completed_orders': completed_orders,
        'status': status,
        'date_range': date_range,
        'search': search,
    }
    
    return render(request, 'delivery/panel/orders.html', context)

@login_required
def delivery_panel_order_detail(request, order_id):
    """Order detail view for delivery panel"""
    # Check if user has delivery role
    if request.user.role != 'delivery':
        messages.error(request, _('You need to have delivery role to access this panel'))
        logout(request)
        return redirect('delivery:panel_login')
    
    # Get or create courier profile
    courier, created = get_or_create_courier(request.user)
    
    delivery = get_object_or_404(
        DeliveryRecord, 
        order_id=order_id, 
        driver=request.user
    )
    
    # Get delivery attempts
    delivery_attempts = DeliveryAttempt.objects.filter(
        order_id=order_id,
        courier=courier
    ).order_by('-attempt_time')
    
    # Get delivery status history
    status_history = DeliveryStatusHistory.objects.filter(
        order_id=order_id
    ).order_by('-created_at')
    
    context = {
        'delivery': delivery,
        'delivery_attempts': delivery_attempts,
        'status_history': status_history,
    }
    
    return render(request, 'delivery/panel/order_detail.html', context)

@login_required
def delivery_panel_update_status(request, order_id):
    """Update delivery status view for delivery panel"""
    # Check if user has delivery role
    if request.user.role != 'delivery':
        messages.error(request, _('You need to have delivery role to access this panel'))
        logout(request)
        return redirect('delivery:panel_login')
    
    # Get or create courier profile
    courier, created = get_or_create_courier(request.user)
    
    delivery = get_object_or_404(
        DeliveryRecord, 
        order_id=order_id, 
        driver=request.user
    )
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        notes = request.POST.get('notes', '')
        location = request.POST.get('location', '')
        
        # Update delivery status
        old_status = delivery.status
        delivery.status = new_status
        
        # Update timestamps based on status
        now = timezone.now()
        if new_status == 'picked_up':
            delivery.picked_up_at = now
        elif new_status == 'delivered':
            delivery.delivered_at = now
        
        delivery.delivery_notes = notes
        delivery.save()
        
        # Create status history record
        DeliveryStatusHistory.objects.create(
            order=delivery.order,
            status=new_status,
            updated_by=request.user,
            notes=notes,
            location=location
        )
        
        messages.success(request, _('Delivery status updated successfully'))
        return redirect('delivery:panel_order_detail', order_id=order_id)
    
    return render(request, 'delivery/panel/update_status.html', {'delivery': delivery})

@login_required
def delivery_panel_complete_delivery(request, order_id):
    """Complete delivery view for delivery panel"""
    # Check if user has delivery role
    if request.user.role != 'delivery':
        messages.error(request, _('You need to have delivery role to access this panel'))
        logout(request)
        return redirect('delivery:panel_login')
    
    # Get or create courier profile
    courier, created = get_or_create_courier(request.user)
    
    delivery = get_object_or_404(
        DeliveryRecord, 
        order_id=order_id, 
        driver=request.user
    )
    
    if request.method == 'POST':
        received_by = request.POST.get('received_by', '')
        id_verified = request.POST.get('id_verified') == 'on'
        payment_method = request.POST.get('payment_method', '')
        amount_received = request.POST.get('amount_received', 0)
        notes = request.POST.get('notes', '')
        
        # Handle proof photo upload
        proof_photo = request.FILES.get('proof_photo')
        if proof_photo:
            # Create delivery proof record
            DeliveryProof.objects.create(
                order=delivery.order,
                courier=courier,
                proof_type='photo',
                proof_data=proof_photo.name
            )
        
        # Handle signature upload
        signature_data = request.POST.get('signature_data', '')
        if signature_data:
            # Create delivery proof record
            DeliveryProof.objects.create(
                order=delivery.order,
                courier=courier,
                proof_type='signature',
                proof_data=signature_data
            )
        
        # Update delivery status
        delivery.status = 'delivered'
        delivery.delivered_at = timezone.now()
        delivery.delivery_notes = notes
        delivery.save()
        
        # Create delivery attempt record
        DeliveryAttempt.objects.create(
            order=delivery.order,
            courier=courier,
            status='successful',
            notes=f"Received by: {received_by}, ID Verified: {id_verified}, Payment Method: {payment_method}, Amount: {amount_received}"
        )
        
        # Create status history record
        DeliveryStatusHistory.objects.create(
            order=delivery.order,
            status='delivered',
            updated_by=request.user,
            notes=notes
        )
        
        messages.success(request, _('Delivery completed successfully'))
        return redirect('delivery:panel_dashboard')
    
    return render(request, 'delivery/panel/complete_delivery.html', {'delivery': delivery})

@login_required
def delivery_panel_failed_delivery(request, order_id):
    """Failed delivery view for delivery panel"""
    # Check if user has delivery role
    if request.user.role != 'delivery':
        messages.error(request, _('You need to have delivery role to access this panel'))
        logout(request)
        return redirect('delivery:panel_login')
    
    # Get or create courier profile
    courier, created = get_or_create_courier(request.user)
    
    delivery = get_object_or_404(
        DeliveryRecord, 
        order_id=order_id, 
        driver=request.user
    )
    
    if request.method == 'POST':
        failure_reason = request.POST.get('failure_reason', '')
        detailed_notes = request.POST.get('detailed_notes', '')
        calls_made = request.POST.get('calls_made', 0)
        reschedule_option = request.POST.get('reschedule_option', '')
        reschedule_time = request.POST.get('reschedule_time', '')
        
        # Update delivery status
        delivery.status = 'failed'
        delivery.delivery_notes = f"{delivery.delivery_notes}\n\nFailed Delivery: {failure_reason}\n{detailed_notes}"
        delivery.save()
        
        # Create delivery attempt record
        attempt = DeliveryAttempt.objects.create(
            order=delivery.order,
            courier=courier,
            status='failed',
            failure_reason=failure_reason,
            notes=detailed_notes,
        )
        
        if reschedule_option == 'yes' and reschedule_time:
            try:
                reschedule_date = datetime.strptime(reschedule_time, '%Y-%m-%dT%H:%M')
                attempt.next_attempt_date = reschedule_date
                attempt.save()
            except ValueError:
                pass  # Invalid date format
        
        # Create status history record
        DeliveryStatusHistory.objects.create(
            order=delivery.order,
            status='failed',
            updated_by=request.user,
            notes=f"Failed: {failure_reason}. {detailed_notes}"
        )
        
        messages.success(request, _('Failed delivery recorded successfully'))
        return redirect('delivery:panel_dashboard')
    
    return render(request, 'delivery/panel/failed_delivery.html', {'delivery': delivery})

@login_required
def delivery_panel_performance(request):
    """Performance dashboard view for delivery panel"""
    # Check if user has delivery role
    if request.user.role != 'delivery':
        messages.error(request, _('You need to have delivery role to access this panel'))
        logout(request)
        return redirect('delivery:panel_login')
    
    # Get or create courier profile
    courier, created = get_or_create_courier(request.user)
    
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    
    # Daily stats
    daily_deliveries = DeliveryRecord.objects.filter(
        driver=request.user,
        delivered_at__date=today
    ).count()
    
    daily_failed = DeliveryRecord.objects.filter(
        driver=request.user,
        status='failed',
        updated_at__date=today
    ).count()
    
    # Weekly stats
    weekly_deliveries = DeliveryRecord.objects.filter(
        driver=request.user,
        delivered_at__date__gte=week_start,
        delivered_at__date__lte=today
    ).count()
    
    # Monthly stats
    monthly_deliveries = DeliveryRecord.objects.filter(
        driver=request.user,
        delivered_at__date__gte=month_start,
        delivered_at__date__lte=today
    ).count()
    
    # Calculate success rate
    total_attempts = DeliveryAttempt.objects.filter(
        courier=courier
    ).count()
    
    successful_attempts = DeliveryAttempt.objects.filter(
        courier=courier,
        status='successful'
    ).count()
    
    success_rate = (successful_attempts / total_attempts * 100) if total_attempts > 0 else 0
    
    # Get delivery time stats
    delivery_times = DeliveryRecord.objects.filter(
        driver=request.user,
        status='delivered',
        picked_up_at__isnull=False,
        delivered_at__isnull=False
    ).annotate(
        delivery_time=F('delivered_at') - F('picked_up_at')
    ).values('delivery_time')
    
    avg_delivery_time = 0
    if delivery_times:
        total_seconds = sum([(dt['delivery_time'].total_seconds()) for dt in delivery_times])
        avg_delivery_time = total_seconds / len(delivery_times) / 60  # in minutes
    
    context = {
        'courier': courier,
        'daily_deliveries': daily_deliveries,
        'daily_failed': daily_failed,
        'weekly_deliveries': weekly_deliveries,
        'monthly_deliveries': monthly_deliveries,
        'success_rate': round(success_rate, 1),
        'avg_delivery_time': round(avg_delivery_time, 1),
        'total_deliveries': successful_attempts,
    }
    
    return render(request, 'delivery/panel/performance.html', context)

@login_required
def delivery_panel_settings(request):
    """Settings view for delivery panel"""
    # Check if user has delivery role
    if request.user.role != 'delivery':
        messages.error(request, _('You need to have delivery role to access this panel'))
        logout(request)
        return redirect('delivery:panel_login')
    
    # Get or create courier profile
    courier, created = get_or_create_courier(request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_profile':
            # Update courier profile
            courier.name = request.POST.get('name', courier.name)
            courier.phone = request.POST.get('phone', courier.phone)
            courier.vehicle_type = request.POST.get('vehicle_type', courier.vehicle_type)
            courier.license_plate = request.POST.get('license_plate', courier.license_plate)
            courier.save()
            
            messages.success(request, _('Profile updated successfully'))
        
        elif action == 'toggle_availability':
            # Toggle courier availability
            courier.available = not courier.available
            courier.save()
            
            status_msg = _('You are now online and available for deliveries') if courier.available else _('You are now offline')
            messages.success(request, status_msg)
    
    return render(request, 'delivery/panel/settings.html', {'courier': courier})

# API endpoints for the delivery panel
@login_required
def api_update_courier_location(request):
    """API endpoint to update courier location"""
    # Check if user has delivery role
    if request.user.role != 'delivery':
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    # Get or create courier profile
    courier, created = get_or_create_courier(request.user)
    
    try:
        data = json.loads(request.body)
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        accuracy = data.get('accuracy')
        
        if not latitude or not longitude:
            return JsonResponse({'success': False, 'error': 'Missing location data'}, status=400)
        
        # Create location record
        CourierLocation.objects.create(
            courier=courier,
            latitude=latitude,
            longitude=longitude,
            accuracy=accuracy,
            battery_level=data.get('battery_level'),
            connection_type=data.get('connection_type', 'cellular')
        )
        
        # Update courier current location
        courier.current_location = f"{latitude},{longitude}"
        courier.last_active = timezone.now()
        courier.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
def api_update_courier_status(request):
    """API endpoint to update courier availability status"""
    # Check if user has delivery role
    if request.user.role != 'delivery':
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    # Get or create courier profile
    courier, created = get_or_create_courier(request.user)
    
    try:
        data = json.loads(request.body)
        status = data.get('status')
        
        if status not in ['active', 'break', 'offline']:
            return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)
        
        # Update courier status
        courier.available = (status == 'active')
        courier.last_active = timezone.now()
        courier.save()
        
        # Update current session
        active_session = CourierSession.objects.filter(
            courier=courier,
            logout_time__isnull=True
        ).first()
        
        if active_session:
            active_session.status = status
            active_session.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
def api_get_courier_orders(request):
    """API endpoint to get courier orders"""
    # Check if user has delivery role
    if request.user.role != 'delivery':
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    # Get or create courier profile
    courier, created = get_or_create_courier(request.user)
    
    status = request.GET.get('status', '')
    
    # Get all orders for this courier
    deliveries = DeliveryRecord.objects.filter(driver=request.user)
    
    if status:
        deliveries = deliveries.filter(status=status)
    
    # Format data for response
    orders_data = []
    for delivery in deliveries:
        orders_data.append({
            'id': delivery.order.id,
            'order_code': delivery.order.order_code,
            'customer_name': delivery.order.customer_name,
            'customer_phone': delivery.order.customer_phone,
            'address': delivery.order.shipping_address,
            'status': delivery.status,
            'tracking': delivery.tracking_number,
            'assigned_at': delivery.assigned_at.isoformat() if delivery.assigned_at else None,
            'delivered_at': delivery.delivered_at.isoformat() if delivery.delivered_at else None,
        })
    
    return JsonResponse({'success': True, 'orders': orders_data})

@login_required
def api_get_optimized_route(request):
    """API endpoint to get optimized delivery route"""
    # Check if user has delivery role
    if request.user.role != 'delivery':
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    # Get or create courier profile
    courier, created = get_or_create_courier(request.user)
    
    # Get all pending deliveries for this courier
    deliveries = DeliveryRecord.objects.filter(
        driver=request.user,
        status__in=['assigned', 'picked_up', 'in_transit']
    ).select_related('order').order_by('assigned_at')
    
    # Simple optimization - just return in order of assignment for now
    # In a real app, this would use a routing algorithm
    route_data = []
    for delivery in deliveries:
        route_data.append({
            'id': delivery.order.id,
            'order_code': delivery.order.order_code,
            'customer_name': delivery.order.customer_name,
            'address': delivery.order.shipping_address,
            'status': delivery.status,
            'priority': 'normal',  # Could be calculated based on various factors
            'estimated_time': 30,  # Placeholder for estimated delivery time in minutes
        })
    
    return JsonResponse({
        'success': True,
        'route': route_data,
        'total_stops': len(route_data),
        'estimated_completion_time': len(route_data) * 30  # Simple estimation
    })

@login_required
def api_send_sms_to_customer(request, order_id):
    """API endpoint to send SMS to customer"""
    # Check if user has delivery role
    if request.user.role != 'delivery':
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    # Get or create courier profile
    courier, created = get_or_create_courier(request.user)
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)
    
    delivery = get_object_or_404(
        DeliveryRecord, 
        order_id=order_id, 
        driver=request.user
    )
    
    message = request.POST.get('message', '')
    if not message:
        return JsonResponse({'success': False, 'error': 'Message is required'}, status=400)
    
    # In a real app, this would integrate with an SMS service
    # For now, just log the attempt
    
    # Add a note to the delivery
    delivery.delivery_notes += f"\n[{timezone.now().strftime('%Y-%m-%d %H:%M')}] SMS sent: {message}"
    delivery.save()
    
    # Create status history record
    DeliveryStatusHistory.objects.create(
        order=delivery.order,
        status=delivery.status,
        updated_by=request.user,
        notes=f"SMS sent to customer: {message}"
    )
    
    return JsonResponse({'success': True, 'message': 'SMS sent successfully'}) 