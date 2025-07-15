from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Sum, Avg, F, Q
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.utils.translation import gettext_lazy as _
import uuid
import csv
import json
from datetime import datetime, timedelta
from .models import DeliveryCompany, Courier, DeliveryRecord, DeliveryStatusHistory, DeliveryRecordEnhanced
from orders.models import Order
from users.models import User
from .forms import StatusUpdateForm, CourierForm, DeliveryCompanyForm, AssignmentForm, DeliveryRecordSimpleForm, DeliveryRecordEnhancedForm

# Create your views here.

@login_required
def dashboard(request):
    """Enhanced Delivery dashboard with real data and metrics."""
    # Get statistics for active deliveries card
    today = timezone.now().date()
    
    # Get counts for each delivery status
    assigned_count = DeliveryRecord.objects.filter(status='assigned').count()
    picked_up_count = DeliveryRecord.objects.filter(status='picked_up').count()
    in_transit_count = DeliveryRecord.objects.filter(status='in_transit').count()
    out_for_delivery_count = DeliveryRecord.objects.filter(status='out_for_delivery').count()
    
    active_deliveries = assigned_count + picked_up_count + in_transit_count + out_for_delivery_count
    
    # Count orders that are packaged but don't have delivery records yet
    packaged_orders_ids = Order.objects.filter(
        status__in=['packaged', 'processing']
    ).values_list('id', flat=True)
    
    # Get IDs of orders that already have delivery records
    delivered_orders_ids = DeliveryRecord.objects.values_list('order_id', flat=True)
    
    # Count unassigned orders ready for delivery
    pending_assignment_count = Order.objects.filter(
        id__in=packaged_orders_ids
    ).exclude(
        id__in=delivered_orders_ids
    ).count()
    
    ready_for_pickup_count = 0  # This status doesn't exist in the basic model
    
    # Completed today
    completed_today = DeliveryRecord.objects.filter(
        status='delivered',
        delivered_at__date=today
    ).count()
    
    # Failed deliveries
    failed_deliveries = DeliveryRecord.objects.filter(status='failed').count()
    
    # Get active courier count
    active_couriers = Courier.objects.filter(status='active').count()
    available_couriers = Courier.objects.filter(status='active', available=True).count()
    busy_couriers = active_couriers - available_couriers if active_couriers > available_couriers else 0
    
    # Calculate average delivery time (for completed deliveries)
    avg_delivery_time = 0
    completed_deliveries = DeliveryRecord.objects.filter(
        status='delivered',
        assigned_at__isnull=False,
        delivered_at__isnull=False
    )
    
    if completed_deliveries.exists():
        total_hours = 0
        delivery_count = 0
        
        for delivery in completed_deliveries:
            if delivery.assigned_at and delivery.delivered_at:
                time_diff = delivery.delivered_at - delivery.assigned_at
                total_hours += time_diff.total_seconds() / 3600
                delivery_count += 1
        
        if delivery_count > 0:
            avg_delivery_time = round(total_hours / delivery_count, 1)
    
    # Get recent deliveries for the table
    recent_deliveries = DeliveryRecord.objects.select_related(
        'order'
    ).order_by('-assigned_at')[:10]
    
    context = {
        'active_deliveries': active_deliveries + pending_assignment_count,
        'assigned_count': assigned_count,
        'picked_up_count': picked_up_count,
        'in_transit_count': in_transit_count,
        'out_for_delivery_count': out_for_delivery_count,
        'pending_assignment_count': pending_assignment_count,
        'ready_for_pickup_count': ready_for_pickup_count,
        'completed_today': completed_today,
        'failed_deliveries': failed_deliveries,
        'active_couriers': active_couriers,
        'available_couriers': available_couriers,
        'busy_couriers': busy_couriers,
        'avg_delivery_time': avg_delivery_time,
        'recent_deliveries': recent_deliveries,
        'today': today,
    }
    
    return render(request, 'delivery/dashboard.html', context)

@login_required
def order_list(request):
    """List of orders for delivery with filtering and search capabilities."""
    # Get filter parameters
    status = request.GET.get('status', '')
    date_range = request.GET.get('date', '')
    courier_id = request.GET.get('courier', '')
    search = request.GET.get('search', '')
    export = request.GET.get('export', '')
    
    # Base queryset for delivery records
    deliveries = DeliveryRecord.objects.select_related(
        'order', 'order__customer', 'driver'
    ).all()
    
    # Apply status filter
    if status:
        deliveries = deliveries.filter(status=status)
    
    # Apply date filter
    today = timezone.now().date()
    if date_range == 'today':
        deliveries = deliveries.filter(
            assigned_at__date=today
        )
    elif date_range == 'last_7_days':
        seven_days_ago = today - timedelta(days=7)
        deliveries = deliveries.filter(assigned_at__date__gte=seven_days_ago)
    elif date_range == 'last_30_days':
        thirty_days_ago = today - timedelta(days=30)
        deliveries = deliveries.filter(assigned_at__date__gte=thirty_days_ago)
    
    # Apply driver filter
    if courier_id:
        deliveries = deliveries.filter(driver_id=courier_id)
    
    # Apply search filter
    if search:
        deliveries = deliveries.filter(
            Q(order__order_code__icontains=search) |
            Q(tracking_number__icontains=search) |
            Q(order__customer__full_name__icontains=search) if 'customer__full_name' in [f.name for f in Order._meta.get_fields()] else Q() |
            Q(order__customer_name__icontains=search)
        )
    
    # Export to CSV if requested
    if export == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="deliveries_{today.strftime("%Y-%m-%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Order ID', 'Tracking Number', 'Customer', 'Location', 'Status', 
            'Assigned Date', 'Picked Up Date', 'Delivered Date', 'Driver'
        ])
        
        for delivery in deliveries:
            customer_name = delivery.order.customer.full_name if delivery.order.customer else delivery.order.customer_name or "Unknown"
            location = delivery.order.customer.country if delivery.order.customer else ""
            assigned_date = delivery.assigned_at.strftime('%Y-%m-%d') if delivery.assigned_at else ""
            picked_up_date = delivery.picked_up_at.strftime('%Y-%m-%d') if delivery.picked_up_at else ""
            delivered_date = delivery.delivered_at.strftime('%Y-%m-%d') if delivery.delivered_at else ""
            driver_name = delivery.driver.get_full_name() if delivery.driver else ""
            
            writer.writerow([
                delivery.order.order_code,
                delivery.tracking_number,
                customer_name,
                location,
                delivery.get_status_display(),
                assigned_date,
                picked_up_date,
                delivered_date,
                driver_name
            ])
        
        return response
    
    # Get list of orders that are packaged but don't have delivery records yet
    packaged_orders_ids = Order.objects.filter(
        status__in=['packaged', 'processing']
    ).values_list('id', flat=True)
    
    # Get IDs of orders that already have delivery records
    delivered_orders_ids = DeliveryRecord.objects.values_list('order_id', flat=True)
    
    # Find packaged orders without delivery records
    unassigned_orders = Order.objects.filter(
        id__in=packaged_orders_ids
    ).exclude(
        id__in=delivered_orders_ids
    ).select_related('customer').order_by('-date')
    
    # Create pseudo-delivery records for unassigned orders to display in the same list
    unassigned_deliveries = []
    for order in unassigned_orders:
        unassigned_deliveries.append({
            'order': order,
            'tracking_number': None,
            'status': 'unassigned',
            'driver': None,
            'assigned_at': None,
            'delivered_at': None,
            'id': None,
            'is_unassigned': True
        })
    
    # Combine both sets of deliveries
    all_deliveries = list(deliveries)
    for unassigned in unassigned_deliveries:
        all_deliveries.append(unassigned)
    
    # Paginate the results
    paginator = Paginator(all_deliveries, 15)  # Show 15 deliveries per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Get lists for filter dropdowns
    couriers = Courier.objects.filter(status='active')
    
    context = {
        'page_obj': page_obj,
        'status_filter': status,
        'date_filter': date_range,
        'courier_filter': courier_id,
        'search_query': search,
        'couriers': couriers,
        'unassigned_count': len(unassigned_deliveries),
    }
    
    return render(request, 'delivery/order_list.html', context)

@login_required
def assign_orders(request):
    """Assign orders to couriers."""
    if request.method == 'POST':
        # Process assignment form
        order_ids = request.POST.getlist('order_ids')
        courier_id = request.POST.get('courier_id')
        company_id = request.POST.get('company_id')
        priority = request.POST.get('priority', 'normal')
        
        if not order_ids or not courier_id or not company_id:
            messages.error(request, _('Please select orders, courier and company for assignment.'))
            return redirect('delivery:assign')
        
        # Get the courier and company
        courier = get_object_or_404(Courier, id=courier_id)
        company = get_object_or_404(DeliveryCompany, id=company_id)
        
        # Assign each order
        success_count = 0
        for order_id in order_ids:
            order = get_object_or_404(Order, id=order_id)
            
            # Check if delivery record already exists
            try:
                delivery_record = DeliveryRecord.objects.get(order=order)
                # Update existing record
                delivery_record.driver = courier
                delivery_record.delivery_company = company
                delivery_record.priority = priority
                if delivery_record.status == 'pending_assignment':
                    delivery_record.status = 'assigned'
                delivery_record.assigned_at = timezone.now()
                delivery_record.save()
            except DeliveryRecord.DoesNotExist:
                # Create new delivery record
                tracking_number = f"TRK-{uuid.uuid4().hex[:8].upper()}"
                delivery_record = DeliveryRecord.objects.create(
                    order=order,
                    tracking_number=tracking_number,
                    driver=courier,
                    delivery_company=company,
                    status='assigned',
                    priority=priority,
                    assigned_at=timezone.now(),
                    delivery_cost=0  # Default value to satisfy non-null constraint
                )
            
            # Create status history
            DeliveryStatusHistory.objects.create(
                order=order,
                status='assigned',
                updated_by=request.user,
                notes=f"Assigned to {courier.name} ({company.name})"
            )
            
            # Update order status to 'shipped' if it's not already in a later stage
            if order.status in ['packaged', 'processing']:
                order.status = 'shipped'
                order.save()
            
            success_count += 1
        
        messages.success(request, _(f'Successfully assigned {success_count} orders to {courier.name}.'))
        return redirect('delivery:orders')
    
    # For GET requests, show orders available for assignment
    # Include orders that are in 'packaged' status (ready for delivery)
    orders = Order.objects.filter(
        status__in=['packaged', 'processing']
    ).exclude(
        id__in=DeliveryRecord.objects.exclude(
            status__in=['failed', 'returned']
        ).values_list('order_id', flat=True)
    ).select_related('customer').order_by('-date')
    
    # Get active couriers and companies
    couriers = Courier.objects.filter(status='active', available=True)
    companies = DeliveryCompany.objects.filter(status='active')
    
    context = {
        'orders': orders,
        'couriers': couriers,
        'companies': companies,
    }
    
    return render(request, 'delivery/assign_orders.html', context)

@login_required
def courier_management(request):
    """Manage delivery companies and couriers."""
    companies = DeliveryCompany.objects.all().order_by('name')
    couriers = Courier.objects.select_related('company').all().order_by('name')
    
    context = {
        'companies': companies,
        'couriers': couriers,
    }
    
    return render(request, 'delivery/courier_management.html', context)

@login_required
def courier_detail(request, courier_id):
    """View and edit courier details."""
    courier = get_object_or_404(Courier, id=courier_id)
    
    if request.method == 'POST':
        # Update courier information
        name = request.POST.get('name')
        company_id = request.POST.get('company_id')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        status = request.POST.get('status')
        
        if not name or not company_id:
            messages.error(request, _('Name and company are required fields.'))
            return redirect('delivery:courier_detail', courier_id=courier_id)
        
        # Update courier
        courier.name = name
        courier.company_id = company_id
        courier.phone = phone
        courier.email = email
        courier.status = status
        courier.save()
        
        messages.success(request, _(f'Courier {name} updated successfully.'))
        return redirect('delivery:courier_management')
    
    # For GET requests, show courier details
    companies = DeliveryCompany.objects.filter(status='active')
    
    # Get courier performance metrics
    total_deliveries = DeliveryRecord.objects.filter(driver=courier).count()
    successful_deliveries = DeliveryRecord.objects.filter(driver=courier, status='delivered').count()
    failed_deliveries = DeliveryRecord.objects.filter(driver=courier, status='failed').count()
    
    success_rate = (successful_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0
    
    # Get active deliveries
    active_deliveries = DeliveryRecord.objects.filter(
        driver=courier,
        status__in=['assigned', 'picked_up', 'in_transit', 'out_for_delivery']
    ).select_related('order', 'order__customer').order_by('-assigned_at')
    
    context = {
        'courier': courier,
        'companies': companies,
        'total_deliveries': total_deliveries,
        'successful_deliveries': successful_deliveries,
        'failed_deliveries': failed_deliveries,
        'success_rate': round(success_rate, 1),
        'active_deliveries': active_deliveries,
    }
    
    return render(request, 'delivery/courier_detail.html', context)

@login_required
def delivery_tracking(request, tracking_number=None):
    """Track delivery status and history."""
    if not tracking_number and 'tracking_number' in request.GET:
        tracking_number = request.GET.get('tracking_number')
    
    if not tracking_number:
        # Show tracking search form
        return render(request, 'delivery/tracking_search.html')
    
    # Get delivery details
    delivery = get_object_or_404(DeliveryRecord, tracking_number=tracking_number)
    
    # Get status history
    history = DeliveryStatusHistory.objects.filter(
        order=delivery.order
    ).select_related('updated_by').order_by('-created_at')
    
    context = {
        'delivery': delivery,
        'history': history,
    }
    
    return render(request, 'delivery/tracking_detail.html', context)

@login_required
def update_delivery_status(request, delivery_id):
    """Update delivery status."""
    delivery = get_object_or_404(DeliveryRecord, id=delivery_id)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        notes = request.POST.get('notes', '')
        location = request.POST.get('location', '')
        
        if not status:
            messages.error(request, _('Status is required.'))
            return redirect('delivery:orders')
        
        # Update the status
        updated = delivery.update_status(status, request.user, notes, location)
        
        if updated:
            messages.success(request, _(f'Delivery status updated to {delivery.get_status_display()}.'))
        else:
            messages.info(request, _('Status was already set to this value.'))
        
        # Redirect back to referring page or orders list
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        return redirect('delivery:orders')
    
    # For GET requests, show status update form
    context = {
        'delivery': delivery,
        'status_choices': DeliveryRecord.STATUS_CHOICES,
    }
    
    return render(request, 'delivery/update_status.html', context)

@login_required
def barcode_scan(request):
    """Barcode scanning interface for processing orders."""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        barcode_data = request.POST.get('barcode')
        action = request.POST.get('action')
        
        if not barcode_data:
            return JsonResponse({'success': False, 'error': 'Barcode data is required'})
        
        # Try to find the delivery by tracking number
        try:
            delivery = DeliveryRecord.objects.get(tracking_number=barcode_data)
            
            # Process action
            if action == 'update_status':
                new_status = request.POST.get('status')
                if new_status:
                    delivery.update_status(new_status, request.user, 'Updated via barcode scan')
            
            # Return delivery details
            return JsonResponse({
                'success': True,
                'delivery': {
                    'id': delivery.id,
                    'tracking_number': delivery.tracking_number,
                    'order_code': delivery.order.order_code,
                    'customer': delivery.order.customer.full_name if delivery.order.customer else 'Unknown',
                    'status': delivery.status,
                    'status_display': delivery.get_status_display(),
                }
            })
            
        except DeliveryRecord.DoesNotExist:
            # Try to find by order code
            try:
                order = Order.objects.get(order_code=barcode_data)
                
                # Check if delivery exists for this order
                try:
                    delivery = DeliveryRecord.objects.get(order=order)
                    
                    # Return delivery details
                    return JsonResponse({
                        'success': True,
                        'delivery': {
                            'id': delivery.id,
                            'tracking_number': delivery.tracking_number,
                            'order_code': order.order_code,
                            'customer': order.customer.full_name if order.customer else 'Unknown',
                            'status': delivery.status,
                            'status_display': delivery.get_status_display(),
                        }
                    })
                    
                except DeliveryRecord.DoesNotExist:
                    # No delivery record yet
                    return JsonResponse({
                        'success': True,
                        'order': {
                            'id': order.id,
                            'order_code': order.order_code,
                            'customer': order.customer.full_name if order.customer else 'Unknown',
                            'status': order.status,
                            'no_delivery': True
                        }
                    })
                    
            except Order.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'No matching delivery or order found'})
    
    # For GET requests, show the barcode scanning interface
    return render(request, 'delivery/barcode_scan.html')

@login_required
def barcode_scan_api(request):
    """API endpoint for barcode scanning that returns JSON data."""
    if request.method == 'POST':
        barcode_data = request.POST.get('barcode')
        action = request.POST.get('action')
        
        if not barcode_data:
            return JsonResponse({'success': False, 'error': 'Barcode data is required'})
        
        # Try to find the delivery by tracking number
        try:
            delivery = DeliveryRecord.objects.get(tracking_number=barcode_data)
            
            # Process action
            if action == 'update_status':
                new_status = request.POST.get('status')
                if new_status:
                    delivery.update_status(new_status, request.user, 'Updated via barcode scan API')
            
            # Return delivery details
            return JsonResponse({
                'success': True,
                'delivery': {
                    'id': delivery.id,
                    'tracking_number': delivery.tracking_number,
                    'order_code': delivery.order.order_code,
                    'customer': delivery.order.customer.full_name if delivery.order.customer else 'Unknown',
                    'status': delivery.status,
                    'status_display': delivery.get_status_display(),
                }
            })
            
        except DeliveryRecord.DoesNotExist:
            # Try to find by order code
            try:
                order = Order.objects.get(order_code=barcode_data)
                
                # Check if delivery exists for this order
                try:
                    delivery = DeliveryRecord.objects.get(order=order)
                    
                    # Return delivery details
                    return JsonResponse({
                        'success': True,
                        'delivery': {
                            'id': delivery.id,
                            'tracking_number': delivery.tracking_number,
                            'order_code': order.order_code,
                            'customer': order.customer.full_name if order.customer else 'Unknown',
                            'status': delivery.status,
                            'status_display': delivery.get_status_display(),
                        }
                    })
                    
                except DeliveryRecord.DoesNotExist:
                    # No delivery record yet
                    return JsonResponse({
                        'success': True,
                        'order': {
                            'id': order.id,
                            'order_code': order.order_code,
                            'customer': order.customer.full_name if order.customer else 'Unknown',
                            'status': order.status,
                            'no_delivery': True
                        }
                    })
                    
            except Order.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'No matching delivery or order found'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def get_couriers_by_company(request, company_id):
    """Get couriers filtered by company for dynamic form population."""
    couriers = Courier.objects.filter(
        company_id=company_id, 
        status='active',
        available=True
    ).values('id', 'name')
    
    return JsonResponse({'couriers': list(couriers)})

@login_required
def add_courier(request):
    """Add a new courier."""
    if request.method == 'POST':
        # Explicitly use the CourierForm from delivery app
        from .forms import CourierForm
        form = CourierForm(request.POST)
        if form.is_valid():
            courier = form.save()
            messages.success(request, _(f'Courier {courier.name} added successfully.'))
            return redirect('delivery:couriers')
    else:
        # Explicitly use the CourierForm from delivery app
        from .forms import CourierForm
        form = CourierForm()
    
    # Get active delivery companies for the form
    companies = DeliveryCompany.objects.filter(status='active')
    
    context = {
        'form': form,
        'companies': companies,
    }
    
    return render(request, 'delivery/add_courier.html', context)

@login_required
def add_company(request):
    """Add a new delivery company."""
    if request.method == 'POST':
        # Explicitly use the DeliveryCompanyForm from delivery app
        from .forms import DeliveryCompanyForm
        form = DeliveryCompanyForm(request.POST)
        if form.is_valid():
            company = form.save()
            messages.success(request, _(f'Delivery company {company.name} added successfully.'))
            return redirect('delivery:couriers')
    else:
        # Explicitly use the DeliveryCompanyForm from delivery app
        from .forms import DeliveryCompanyForm
        form = DeliveryCompanyForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'delivery/add_company.html', context)

# Import all delivery panel views
from .panel_views import (
    delivery_panel_login,
    delivery_panel_logout,
    delivery_panel_dashboard,
    delivery_panel_orders,
    delivery_panel_order_detail,
    delivery_panel_update_status,
    delivery_panel_complete_delivery,
    delivery_panel_failed_delivery,
    delivery_panel_performance,
    delivery_panel_settings,
    api_update_courier_location,
    api_update_courier_status,
    api_get_courier_orders,
    api_get_optimized_route,
    api_send_sms_to_customer
)
