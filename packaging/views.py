# packaging/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Q, Sum, Avg, F
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from datetime import datetime, timedelta
from .models import PackagingRecord, PackagingMaterial, PackagingTask, PackagingQualityCheck
from orders.models import Order
from delivery.models import Courier
from django.contrib.auth import get_user_model
from django.http import HttpResponse
import json
import uuid
import csv
from io import StringIO, BytesIO
import xlsxwriter

User = get_user_model()

def has_packaging_role(user):
    return (
        user.is_superuser or
        user.has_role('Super Admin') or
        user.has_role('Packaging')
    )

@login_required
def dashboard(request):
    """Packaging dashboard with real data."""
    today = timezone.now().date()
    
    # Get real packaging statistics from orders
    total_packaging_records = PackagingRecord.objects.count()
    completed_today = PackagingRecord.objects.filter(
        status='completed',
        packaging_completed__date=today
    ).count()
    
    # Get pending packaging from orders with status 'pending' and 'processing'
    pending_packaging = Order.objects.filter(status__in=['pending', 'processing']).count()
    in_progress_packaging = PackagingRecord.objects.filter(status='in_progress').count()
    
    # Get packaging tasks with optimized queries
    pending_tasks = PackagingTask.objects.filter(status='pending').count()
    in_progress_tasks = PackagingTask.objects.filter(status='in_progress').count()
    completed_tasks_today = PackagingTask.objects.filter(
        status='completed',
        completed_at__date=today
    ).count()
    
    # Get detailed material statistics from real data
    materials = PackagingMaterial.objects.all()
    low_stock_materials = materials.filter(
        current_stock__lte=F('min_stock_level'),
        current_stock__gt=0
    )
    out_of_stock_materials = materials.filter(current_stock=0)
    
    # Calculate material costs and inventory value
    total_materials_cost = materials.aggregate(
        total_cost=Sum(F('current_stock') * F('cost_per_unit'))
    )['total_cost'] or 0
    
    # Get material usage statistics from real data
    material_usage = {}
    
    # Analyze material usage from packaging records
    for record in PackagingRecord.objects.filter(status='completed'):
        try:
            materials_used = record.materials_used
            if isinstance(materials_used, str):
                materials_used = json.loads(materials_used)
            
            if isinstance(materials_used, dict):
                for material_id, quantity in materials_used.items():
                    material_usage[material_id] = material_usage.get(material_id, 0) + int(quantity)
        except (json.JSONDecodeError, ValueError, TypeError, AttributeError):
            continue
    
    # Get most used materials
    most_used_materials = []
    for material_id, quantity in sorted(material_usage.items(), key=lambda x: x[1], reverse=True)[:5]:
        try:
            material = PackagingMaterial.objects.get(id=material_id)
            most_used_materials.append({
                'name': material.name,
                'quantity': quantity,
                'unit': material.unit,
                'current_stock': material.current_stock,
                'is_low_stock': material.is_low_stock
            })
        except PackagingMaterial.DoesNotExist:
            continue
    
    # Get material type distribution
    material_types = {}
    for material_type, name in PackagingMaterial.MATERIAL_TYPES:
        count = materials.filter(material_type=material_type).count()
        if count > 0:
            material_types[name] = count
    
    # Get recent packaging activities with optimized queries
    recent_packaging = PackagingRecord.objects.select_related(
        'order', 'packager'
    ).order_by('-packaging_started')[:10]
    
    # Get recent tasks with optimized queries
    recent_tasks = PackagingTask.objects.select_related(
        'order', 'assigned_to'
    ).order_by('-created_at')[:10]
    
    # Get recent orders that need packaging (pending and processing orders) with optimized queries
    recent_packaging_orders = Order.objects.filter(status__in=['pending', 'processing']).order_by('-date')[:10]
    
    # Get quality check statistics with real data
    quality_checks_today = PackagingQualityCheck.objects.filter(
        checked_at__date=today
    ).count()
    
    quality_pass_rate = 0
    if quality_checks_today > 0:
        passed_checks = PackagingQualityCheck.objects.filter(
            checked_at__date=today,
            result='pass'
        ).count()
        quality_pass_rate = (passed_checks / quality_checks_today) * 100
    
    # Get average packaging time from real data
    completed_packages = PackagingRecord.objects.filter(
        status='completed',
        packaging_completed__isnull=False
    )
    
    total_duration = 0
    package_count = 0
    
    for package in completed_packages:
        if package.packaging_duration:
            total_duration += package.packaging_duration
            package_count += 1
    
    avg_packaging_time = (total_duration / package_count) if package_count > 0 else 0
    
    # Calculate total packaging queue from real data (orders with status 'pending' and 'processing')
    total_packaging_queue = Order.objects.filter(status__in=['pending', 'processing']).count()
    
    # Calculate weekly packaging trends
    weekly_stats = []
    for i in range(7):
        date = today - timedelta(days=i)
        completed_count = PackagingRecord.objects.filter(
            status='completed',
            packaging_completed__date=date
        ).count()
        weekly_stats.append({
            'date': date,
            'completed': completed_count
        })
    weekly_stats.reverse()
    
    context = {
        'total_packaging_records': total_packaging_records,
        'completed_today': completed_today,
        'pending_packaging': pending_packaging,
        'in_progress_packaging': in_progress_packaging,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'completed_tasks_today': completed_tasks_today,
        
        # Enhanced material stats
        'low_stock_materials': low_stock_materials,
        'low_stock_count': low_stock_materials.count(),
        'out_of_stock_count': out_of_stock_materials.count(),
        'total_materials_cost': total_materials_cost,
        'most_used_materials': most_used_materials,
        'material_types': material_types,
        
        # Other stats
        'recent_packaging': recent_packaging,
        'recent_tasks': recent_tasks,
        'recent_packaging_orders': recent_packaging_orders,
        'quality_checks_today': quality_checks_today,
        'quality_pass_rate': round(quality_pass_rate, 1),
        'avg_packaging_time': round(avg_packaging_time, 1),
        'total_packaging_queue': total_packaging_queue,
        'weekly_stats': weekly_stats,
        'today': today,
    }
    
    return render(request, 'packaging/dashboard.html', context)

@login_required
@user_passes_test(has_packaging_role)
def order_list(request):
    """List of orders for packaging with real data."""
    # Get orders that need packaging (pending and processing orders)
    # Include related data to optimize queries
    orders = Order.objects.filter(status__in=['pending', 'processing']).prefetch_related('items', 'packaging')
    
    # Get search query
    search = request.GET.get('search', '')
    if search:
        orders = orders.filter(
            Q(order_code__icontains=search) |
            Q(customer__icontains=search) |
            Q(customer_phone__icontains=search)
        )
    
    # Get status filter
    status_filter = request.GET.get('status', '')
    if status_filter:
        if status_filter == 'packaged':
            orders = orders.filter(packaging__status='completed')
        elif status_filter == 'in_progress':
            orders = orders.filter(packaging__status='in_progress')
        elif status_filter == 'pending':
            # Use more efficient query with Q objects
            orders = orders.filter(Q(packaging__isnull=True) | Q(packaging__status='pending'))
    
    # Get priority filter
    priority_filter = request.GET.get('priority', '')
    if priority_filter:
        orders = orders.filter(packaging_tasks__priority=priority_filter)
    
    # Get date filter
    date_filter = request.GET.get('date_filter', '')
    if date_filter:
        if date_filter == 'today':
            orders = orders.filter(date__date=timezone.now().date())
        elif date_filter == 'week':
            week_ago = timezone.now() - timedelta(days=7)
            orders = orders.filter(date__gte=week_ago)
        elif date_filter == 'month':
            month_ago = timezone.now() - timedelta(days=30)
            orders = orders.filter(date__gte=month_ago)
    
    # Add order by to ensure consistent sorting
    orders = orders.order_by('-date')
    
    # Pagination
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get packaging statistics using real data
    # Use aggregation for more efficient queries
    total_orders = orders.count()
    packaged_orders = orders.filter(packaging__status='completed').count()
    in_progress_orders = orders.filter(packaging__status='in_progress').count()
    pending_orders = orders.filter(Q(packaging__isnull=True) | Q(packaging__status='pending')).count()
    
    # Calculate additional statistics
    avg_processing_time = 0
    completed_packages = PackagingRecord.objects.filter(status='completed')
    
    if completed_packages.exists():
        total_minutes = 0
        count = 0
        for pkg in completed_packages:
            if pkg.packaging_duration:
                total_minutes += pkg.packaging_duration
                count += 1
        
        if count > 0:
            avg_processing_time = total_minutes / count
    
    packaging_stats = {
        'total_orders': total_orders,
        'packaged_orders': packaged_orders,
        'in_progress_orders': in_progress_orders,
        'pending_orders': pending_orders,
        'avg_processing_time': round(avg_processing_time, 1),
        'today_completed': PackagingRecord.objects.filter(
            status='completed',
            packaging_completed__date=timezone.now().date()
        ).count(),
    }
    
    # Get real material data for packaging
    materials = PackagingMaterial.objects.filter(
        is_active=True, 
        current_stock__gt=0
    ).order_by('material_type', 'name')
    
    context = {
        'orders': page_obj,
        'search_query': search,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'date_filter': date_filter,
        'packaging_stats': packaging_stats,
        'materials': materials,
    }
    
    return render(request, 'packaging/order_list.html', context)

@login_required
@user_passes_test(has_packaging_role)
def start_packaging(request, order_id):
    """Start packaging for an order with real data."""
    # Get the order with related data for better performance
    order = get_object_or_404(Order, id=order_id)
    
    # Check if order is already being packaged
    if hasattr(order, 'packaging') and order.packaging.status in ['in_progress', 'completed']:
        messages.warning(request, f'Order {order.order_code} is already being packaged')
        return redirect('packaging:order_detail', order_id=order_id)
    
    # Get available packaging materials with real stock data
    materials = PackagingMaterial.objects.filter(
        is_active=True,
        current_stock__gt=0
    ).order_by('material_type', 'name')
    
    if request.method == 'POST':
        package_type = request.POST.get('package_type', 'box')
        estimated_weight = request.POST.get('estimated_weight')
        dimensions = request.POST.get('dimensions', '')
        notes = request.POST.get('notes', '')
        
        # Generate a unique tracking number
        tracking_number = f"TRK-{uuid.uuid4().hex[:12].upper()}"
        
        # Process materials used
        materials_used = {}
        for key, value in request.POST.items():
            if key.startswith('material_') and value and int(value) > 0:
                material_id = key.replace('material_', '')
                try:
                    # Verify material exists and has enough stock
                    material = PackagingMaterial.objects.get(id=material_id)
                    quantity = int(value)
                    
                    if material.current_stock >= quantity:
                        materials_used[material_id] = quantity
                        
                        # Update material stock
                        material.current_stock -= quantity
                        material.save()
                    else:
                        messages.warning(request, f'Not enough stock for {material.name}')
                except (PackagingMaterial.DoesNotExist, ValueError):
                    continue
        
        # Create packaging record with real data
        packaging_record = PackagingRecord.objects.create(
            order=order,
            packager=request.user,
            package_type=package_type,
            package_weight=estimated_weight if estimated_weight else None,
            dimensions=dimensions,
            packaging_notes=notes,
            tracking_number=tracking_number,
            status='in_progress',
            materials_used=materials_used
        )
        
        # Create packaging task with real data
        priority = 'normal'
        if hasattr(order, 'is_express') and order.is_express:
            priority = 'high'
        elif hasattr(order, 'is_priority') and order.is_priority:
            priority = 'urgent'
            
        PackagingTask.objects.create(
            order=order,
            assigned_to=request.user,
            status='in_progress',
            started_at=timezone.now(),
            priority=priority,
            estimated_duration=15  # Default 15 minutes
        )
        
        messages.success(request, f'Packaging started for order {order.order_code}')
        return redirect('packaging:order_detail', order_id=order_id)
    
    # Get order items for packaging
    order_items = order.items.all() if hasattr(order, 'items') else []
    
    # Recommend package type based on order items
    recommended_package_type = 'box'  # Default
    if order_items:
        total_items = sum(item.quantity for item in order_items if hasattr(item, 'quantity'))
        if total_items == 1:
            # For single items, check size
            item = order_items[0]
            if hasattr(item, 'product') and hasattr(item.product, 'size'):
                if item.product.size == 'small':
                    recommended_package_type = 'envelope'
                elif item.product.size == 'medium':
                    recommended_package_type = 'box'
                else:
                    recommended_package_type = 'custom'
    
    context = {
        'order': order,
        'order_items': order_items,
        'materials': materials,
        'recommended_package_type': recommended_package_type,
    }
    
    return render(request, 'packaging/start_packaging.html', context)

@login_required
@user_passes_test(has_packaging_role)
def complete_packaging(request, order_id):
    """Complete packaging for an order with real data."""
    # Get order with related data
    order = get_object_or_404(Order, id=order_id)
    packaging_record = get_object_or_404(PackagingRecord, order=order)
    
    if packaging_record.status == 'completed':
        messages.warning(request, f'Packaging for order {order.order_code} is already completed')
        return redirect('packaging:order_detail', order_id=order_id)
    
    if request.method == 'POST':
        actual_weight = request.POST.get('actual_weight')
        final_dimensions = request.POST.get('final_dimensions', '')
        materials_used_json = request.POST.get('materials_used', '{}')
        quality_check_passed = request.POST.get('quality_check_passed') == 'on'
        completion_notes = request.POST.get('completion_notes', '')
        
        # Process materials used
        try:
            materials_used = json.loads(materials_used_json)
            
            # Update material inventory based on usage
            for material_id, quantity in materials_used.items():
                try:
                    material = PackagingMaterial.objects.get(id=material_id)
                    # If the material was already used, don't double-count
                    if not packaging_record.materials_used or material_id not in packaging_record.materials_used:
                        if material.current_stock >= int(quantity):
                            material.current_stock -= int(quantity)
                            material.save()
                        else:
                            messages.warning(request, f'Not enough stock for {material.name}')
                except (PackagingMaterial.DoesNotExist, ValueError):
                    continue
        except json.JSONDecodeError:
            materials_used = {}
        
        # Update packaging record with real data
        packaging_record.package_weight = actual_weight if actual_weight else None
        packaging_record.dimensions = final_dimensions
        packaging_record.materials_used = materials_used
        packaging_record.quality_check_passed = quality_check_passed
        packaging_record.packaging_notes = completion_notes
        packaging_record.status = 'completed'
        packaging_record.packaging_completed = timezone.now()
        packaging_record.save()
        
        # Update packaging task with real data
        task = PackagingTask.objects.filter(order=order, assigned_to=request.user).first()
        if task:
            task.status = 'completed'
            task.completed_at = timezone.now()
            
            # Calculate actual duration
            if task.started_at:
                duration_minutes = int((timezone.now() - task.started_at).total_seconds() / 60)
                task.actual_duration = duration_minutes
                
            task.save()
        else:
            # Create a completed task if none exists
            PackagingTask.objects.create(
                order=order,
                assigned_to=request.user,
                status='completed',
                started_at=packaging_record.packaging_started,
                completed_at=timezone.now(),
                actual_duration=int((timezone.now() - packaging_record.packaging_started).total_seconds() / 60)
            )
        
        # Create quality check record with real data
        if quality_check_passed:
            PackagingQualityCheck.objects.create(
                packaging_record=packaging_record,
                checker=request.user,
                check_type='visual',
                result='pass',
                notes=f'Auto-check on completion: {completion_notes}'
            )
        
        # Update order status to ready for shipping
        order.status = 'ready_for_shipping'
        order.save()
        
        messages.success(request, f'Packaging completed for order {order.order_code}')
        return redirect('packaging:orders')
    
    # Get order items for display
    order_items = order.items.all() if hasattr(order, 'items') else []
    
    # Get available materials for packaging
    available_materials = PackagingMaterial.objects.filter(
        is_active=True,
        current_stock__gt=0
    ).order_by('material_type', 'name')
    
    # Parse existing materials used
    used_materials = {}
    material_details = []
    
    if packaging_record.materials_used:
        if isinstance(packaging_record.materials_used, str):
            try:
                used_materials = json.loads(packaging_record.materials_used)
            except json.JSONDecodeError:
                used_materials = {}
        else:
            used_materials = packaging_record.materials_used
            
        # Get material details
        for material_id, quantity in used_materials.items():
            try:
                material = PackagingMaterial.objects.get(id=material_id)
                material_details.append({
                    'id': material.id,
                    'name': material.name,
                    'quantity': quantity,
                    'unit': material.unit
                })
            except PackagingMaterial.DoesNotExist:
                continue
    
    context = {
        'order': order,
        'order_items': order_items,
        'packaging_record': packaging_record,
        'available_materials': available_materials,
        'material_details': material_details,
        'used_materials_json': json.dumps(used_materials)
    }
    
    return render(request, 'packaging/complete_packaging.html', context)

@login_required
@user_passes_test(has_packaging_role)
def order_detail(request, order_id):
    """Detailed view of order packaging with real data."""
    # Get order with related data for better performance
    order = get_object_or_404(Order, id=order_id)
    
    # Get packaging record with optimized query
    packaging_record = PackagingRecord.objects.filter(order=order).select_related('packager').first()
    
    # Get packaging task with optimized query
    packaging_task = PackagingTask.objects.filter(order=order).select_related('assigned_to').first()
    
    # Get quality checks with optimized query
    quality_checks = PackagingQualityCheck.objects.filter(
        packaging_record=packaging_record
    ).select_related('checker').order_by('-checked_at') if packaging_record else []
    
    # Get order items for display
    order_items = order.items.all() if hasattr(order, 'items') else []
    
    # Parse materials used
    material_details = []
    if packaging_record and packaging_record.materials_used:
        materials_used = packaging_record.materials_used
        if isinstance(materials_used, str):
            try:
                materials_used = json.loads(materials_used)
            except json.JSONDecodeError:
                materials_used = {}
        
        # Get material details
        for material_id, quantity in materials_used.items():
            try:
                material = PackagingMaterial.objects.get(id=material_id)
                material_details.append({
                    'name': material.name,
                    'quantity': quantity,
                    'unit': material.unit,
                    'cost': float(material.cost_per_unit) * int(quantity)
                })
            except (PackagingMaterial.DoesNotExist, ValueError, TypeError):
                continue
    
    # Calculate packaging metrics
    packaging_metrics = {}
    if packaging_record:
        # Calculate time metrics
        if packaging_record.packaging_completed and packaging_record.packaging_started:
            duration = (packaging_record.packaging_completed - packaging_record.packaging_started).total_seconds() / 60
            packaging_metrics['duration'] = round(duration, 1)
            
            # Calculate efficiency based on expected time
            expected_time = 15  # Default 15 minutes
            if packaging_task and packaging_task.estimated_duration:
                expected_time = packaging_task.estimated_duration
                
            efficiency = (expected_time / duration) * 100 if duration > 0 else 0
            packaging_metrics['efficiency'] = min(round(efficiency, 1), 100)  # Cap at 100%
        
        # Calculate material cost
        total_cost = sum(item['cost'] for item in material_details)
        packaging_metrics['material_cost'] = round(total_cost, 2)
    
    context = {
        'order': order,
        'order_items': order_items,
        'packaging_record': packaging_record,
        'packaging_task': packaging_task,
        'quality_checks': quality_checks,
        'material_details': material_details,
        'packaging_metrics': packaging_metrics
    }
    
    return render(request, 'packaging/order_detail.html', context)

@login_required
@user_passes_test(has_packaging_role)
def materials_inventory(request):
    """Manage packaging materials inventory."""
    materials = PackagingMaterial.objects.filter(is_active=True)
    
    # Apply filters
    material_type = request.GET.get('type', '')
    if material_type:
        materials = materials.filter(material_type=material_type)
    
    stock_status = request.GET.get('stock_status', '')
    if stock_status == 'low':
        materials = materials.filter(current_stock__lte=F('min_stock_level'), current_stock__gt=0)
    elif stock_status == 'out':
        materials = materials.filter(current_stock=0)
    
    # Pagination
    paginator = Paginator(materials, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get inventory statistics
    inventory_stats = {
        'total_materials': materials.count(),
        'low_stock_materials': materials.filter(current_stock__lte=F('min_stock_level'), current_stock__gt=0).count(),
        'out_of_stock_materials': materials.filter(current_stock=0).count(),
        'total_value': materials.aggregate(
            total_value=Sum(F('current_stock') * F('cost_per_unit'))
        )['total_value'] or 0,
    }
    
    # Get material type counts
    material_type_counts = {}
    for material_type, _ in PackagingMaterial.MATERIAL_TYPES:
        material_type_counts[material_type] = materials.filter(material_type=material_type).count()
    
    context = {
        'materials': page_obj,
        'material_type_filter': material_type,
        'stock_status_filter': stock_status,
        'inventory_stats': inventory_stats,
        'material_type_counts': material_type_counts,
    }
    
    return render(request, 'packaging/materials_inventory.html', context)

@login_required
@user_passes_test(has_packaging_role)
def quality_control(request):
    """Quality control interface."""
    # Get pending quality checks
    pending_checks = PackagingRecord.objects.filter(
        status='completed',
        quality_check_passed=False
    ).select_related('order', 'packager')
    
    # Get recent quality checks
    recent_checks = PackagingQualityCheck.objects.select_related(
        'packaging_record', 'checker'
    ).order_by('-checked_at')[:20]
    
    context = {
        'pending_checks': pending_checks,
        'recent_checks': recent_checks,
    }
    
    return render(request, 'packaging/quality_control.html', context)

@login_required
@user_passes_test(has_packaging_role)
def perform_quality_check(request, packaging_id):
    """Perform quality check on a package."""
    packaging_record = get_object_or_404(PackagingRecord, id=packaging_id)
    
    if request.method == 'POST':
        check_type = request.POST.get('check_type')
        result = request.POST.get('result')
        notes = request.POST.get('notes', '')
        
        # Create quality check record
        PackagingQualityCheck.objects.create(
            packaging_record=packaging_record,
            checker=request.user,
            check_type=check_type,
            result=result,
            notes=notes
        )
        
        # Update packaging record
        packaging_record.quality_check_passed = (result == 'pass')
        packaging_record.quality_check_by = request.user
        packaging_record.quality_check_date = timezone.now()
        packaging_record.save()
        
        messages.success(request, f'Quality check completed for package {packaging_record.barcode}')
        return redirect('packaging:quality_control')
    
    context = {
        'packaging_record': packaging_record,
    }
    
    return render(request, 'packaging/perform_quality_check.html', context)

@login_required
@user_passes_test(has_packaging_role)
def packaging_report(request):
    """Packaging performance report with detailed statistics."""
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Get date filter
    date_filter = request.GET.get('date_filter', 'today')
    if date_filter == 'week':
        start_date = week_ago
    elif date_filter == 'month':
        start_date = month_ago
    else:
        start_date = today
    
    # Get packaging statistics
    completed_packages = PackagingRecord.objects.filter(
        status='completed',
        packaging_completed__date__gte=start_date
    ).select_related('order', 'packager')
    
    total_completed = completed_packages.count()
    total_duration = 0
    package_count = 0
    
    # Calculate packaging metrics
    package_types = {}
    package_weights = []
    
    for package in completed_packages:
        if package.packaging_duration:
            total_duration += package.packaging_duration
            package_count += 1
        
        # Count package types
        package_type = package.get_package_type_display()
        package_types[package_type] = package_types.get(package_type, 0) + 1
        
        # Collect weights for analysis
        if package.package_weight:
            package_weights.append(float(package.package_weight))
    
    avg_duration = (total_duration / package_count) if package_count > 0 else 0
    
    # Calculate weight statistics
    avg_weight = sum(package_weights) / len(package_weights) if package_weights else 0
    max_weight = max(package_weights) if package_weights else 0
    min_weight = min(package_weights) if package_weights else 0
    
    # Get quality check statistics
    quality_checks = PackagingQualityCheck.objects.filter(
        checked_at__date__gte=start_date
    ).select_related('packaging_record', 'checker')
    
    total_checks = quality_checks.count()
    passed_checks = quality_checks.filter(result='pass').count()
    failed_checks = quality_checks.filter(result='fail').count()
    conditional_checks = quality_checks.filter(result='conditional').count()
    
    pass_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0
    
    # Get quality check types breakdown
    check_types = {}
    for check in quality_checks:
        check_type = check.get_check_type_display()
        check_types[check_type] = check_types.get(check_type, 0) + 1
    
    # Get packager performance with more metrics
    packager_stats = []
    packagers = PackagingRecord.objects.filter(
        status='completed',
        packaging_completed__date__gte=start_date
    ).values('packager').distinct()
    
    for packager_data in packagers:
        if packager_data['packager']:
            packager = User.objects.get(id=packager_data['packager'])
            packages = PackagingRecord.objects.filter(
                packager=packager,
                status='completed',
                packaging_completed__date__gte=start_date
            )
            
            packager_duration = 0
            packager_count = 0
            packager_weights = []
            
            for package in packages:
                if package.packaging_duration:
                    packager_duration += package.packaging_duration
                    packager_count += 1
                if package.package_weight:
                    packager_weights.append(float(package.package_weight))
            
            avg_packager_duration = (packager_duration / packager_count) if packager_count > 0 else 0
            
            # Get quality checks performed by this packager
            quality_pass_rate = 0
            packager_checks = PackagingQualityCheck.objects.filter(
                checker=packager,
                checked_at__date__gte=start_date
            )
            
            if packager_checks.count() > 0:
                passed = packager_checks.filter(result='pass').count()
                quality_pass_rate = (passed / packager_checks.count()) * 100
            
            packager_stats.append({
                'packager': packager,
                'packages_completed': packages.count(),
                'avg_duration': avg_packager_duration,
                'total_time': packager_duration,
                'quality_checks': packager_checks.count(),
                'quality_pass_rate': round(quality_pass_rate, 1),
                'avg_weight': sum(packager_weights) / len(packager_weights) if packager_weights else 0
            })
    
    # Sort packager stats by packages completed (descending)
    packager_stats.sort(key=lambda x: x['packages_completed'], reverse=True)
    
    # Get daily statistics for chart
    daily_stats = []
    for i in range(7):
        date = today - timedelta(days=i)
        daily_packages = PackagingRecord.objects.filter(
            status='completed',
            packaging_completed__date=date
        )
        
        daily_completed = daily_packages.count()
        
        # Calculate daily average duration
        daily_duration = 0
        daily_count = 0
        for package in daily_packages:
            if package.packaging_duration:
                daily_duration += package.packaging_duration
                daily_count += 1
        
        daily_avg_duration = (daily_duration / daily_count) if daily_count > 0 else 0
        
        daily_checks = PackagingQualityCheck.objects.filter(
            checked_at__date=date
        ).count()
        
        daily_stats.append({
            'date': date,
            'completed': daily_completed,
            'checks': daily_checks,
            'avg_duration': round(daily_avg_duration, 1)
        })
    
    daily_stats.reverse()
    
    # Get material usage statistics
    material_usage = {}
    for package in completed_packages:
        if package.materials_used:
            try:
                materials = package.materials_used
                if isinstance(materials, str):
                    materials = json.loads(materials)
                
                for material_id, quantity in materials.items():
                    material_usage[material_id] = material_usage.get(material_id, 0) + int(quantity)
            except (json.JSONDecodeError, ValueError, TypeError):
                pass
    
    # Get material details
    material_stats = []
    for material_id, quantity in material_usage.items():
        try:
            material = PackagingMaterial.objects.get(id=material_id)
            material_stats.append({
                'name': material.name,
                'quantity': quantity,
                'unit': material.unit,
                'cost': float(material.cost_per_unit) * quantity
            })
        except PackagingMaterial.DoesNotExist:
            pass
    
    # Sort material stats by quantity (descending)
    material_stats.sort(key=lambda x: x['quantity'], reverse=True)
    
    # Calculate total material cost
    total_material_cost = sum(item['cost'] for item in material_stats)
    
    context = {
        # Basic metrics
        'total_completed': total_completed,
        'avg_duration': round(avg_duration, 1),
        'total_checks': total_checks,
        'passed_checks': passed_checks,
        'failed_checks': failed_checks,
        'conditional_checks': conditional_checks,
        'pass_rate': round(pass_rate, 1),
        
        # Package metrics
        'package_types': package_types,
        'avg_weight': round(avg_weight, 2),
        'max_weight': round(max_weight, 2),
        'min_weight': round(min_weight, 2),
        
        # Quality check metrics
        'check_types': check_types,
        
        # Packager performance
        'packager_stats': packager_stats,
        
        # Daily statistics
        'daily_stats': daily_stats,
        
        # Material usage
        'material_stats': material_stats,
        'total_material_cost': round(total_material_cost, 2),
        
        # Date filters
        'date_filter': date_filter,
        'start_date': start_date,
        'today': today,
    }
    
    # Check if export is requested
    export_format = request.GET.get('format')
    if export_format:
        if export_format == 'csv':
            return export_report_csv(request, context)
        elif export_format == 'pdf':
            return export_report_pdf(request, context)
    
    return render(request, 'packaging/packaging_report.html', context)

# Export functions
def export_report_csv(request, context):
    """Export packaging report data as CSV."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="packaging_report_{timezone.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow(['Packaging Report', f'Generated on {timezone.now().strftime("%Y-%m-%d %H:%M")}'])
    writer.writerow([f'Period: {context["date_filter"].title()}'])
    writer.writerow([])
    
    # Write key metrics
    writer.writerow(['Key Metrics'])
    writer.writerow(['Total Completed', 'Avg Duration (min)', 'Total Checks', 'Pass Rate (%)'])
    writer.writerow([
        context['total_completed'],
        context['avg_duration'],
        context['total_checks'],
        context['pass_rate']
    ])
    writer.writerow([])
    
    # Write quality check results
    writer.writerow(['Quality Check Results'])
    writer.writerow(['Passed', 'Conditional', 'Failed'])
    writer.writerow([
        context['passed_checks'],
        context['conditional_checks'],
        context['failed_checks']
    ])
    writer.writerow([])
    
    # Write daily statistics
    writer.writerow(['Daily Activity'])
    writer.writerow(['Date', 'Packages Completed', 'Quality Checks', 'Avg Duration (min)'])
    for stat in context['daily_stats']:
        writer.writerow([
            stat['date'].strftime('%Y-%m-%d'),
            stat['completed'],
            stat['checks'],
            stat['avg_duration']
        ])
    writer.writerow([])
    
    # Write packager performance
    writer.writerow(['Packager Performance'])
    writer.writerow(['Packager', 'Packages Completed', 'Avg Duration (min)', 'Total Time (min)', 'Quality Checks', 'QC Pass Rate (%)'])
    for stat in context['packager_stats']:
        writer.writerow([
            stat['packager'].get_full_name(),
            stat['packages_completed'],
            stat['avg_duration'],
            stat['total_time'],
            stat['quality_checks'],
            stat['quality_pass_rate']
        ])
    writer.writerow([])
    
    # Write material usage
    writer.writerow(['Material Usage'])
    writer.writerow(['Material', 'Quantity', 'Unit', 'Cost ($)'])
    for material in context['material_stats']:
        writer.writerow([
            material['name'],
            material['quantity'],
            material['unit'],
            material['cost']
        ])
    
    return response

def export_report_pdf(request, context):
    """Export packaging report data as PDF."""
    # For simplicity, we'll redirect to CSV export for now
    # In a real implementation, you'd use a PDF library like ReportLab or WeasyPrint
    return export_report_csv(request, context)

@login_required
@user_passes_test(has_packaging_role)
def export_materials(request):
    """Export materials inventory as CSV."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="materials_inventory_{timezone.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow(['Materials Inventory Report', f'Generated on {timezone.now().strftime("%Y-%m-%d %H:%M")}'])
    writer.writerow([])
    
    # Write materials data
    writer.writerow(['Name', 'Type', 'Current Stock', 'Unit', 'Min Stock Level', 'Cost Per Unit', 'Total Value', 'Status'])
    
    materials = PackagingMaterial.objects.all().order_by('material_type', 'name')
    for material in materials:
        status = "Out of Stock" if material.current_stock == 0 else "Low Stock" if material.current_stock <= material.min_stock_level else "In Stock"
        total_value = material.current_stock * material.cost_per_unit
        
        writer.writerow([
            material.name,
            material.get_material_type_display(),
            material.current_stock,
            material.unit,
            material.min_stock_level,
            material.cost_per_unit,
            total_value,
            status
        ])
    
    return response

@login_required
@user_passes_test(has_packaging_role)
def export_packager_performance(request):
    """Export packager performance data as CSV."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="packager_performance_{timezone.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow(['Packager Performance Report', f'Generated on {timezone.now().strftime("%Y-%m-%d %H:%M")}'])
    writer.writerow([])
    
    # Get date range
    today = timezone.now().date()
    month_ago = today - timedelta(days=30)
    
    # Get packager data
    packagers = User.objects.filter(packaged_orders__isnull=False).distinct()
    
    # Write packager performance data
    writer.writerow(['Packager', 'Total Packages', 'This Month', 'Avg Duration (min)', 'Quality Checks Performed', 'QC Pass Rate'])
    
    for packager in packagers:
        # Get all packages by this packager
        all_packages = PackagingRecord.objects.filter(packager=packager, status='completed')
        month_packages = all_packages.filter(packaging_completed__date__gte=month_ago)
        
        # Calculate average duration
        durations = []
        for package in all_packages:
            if package.packaging_duration:
                durations.append(package.packaging_duration)
        
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        # Get quality checks
        quality_checks = PackagingQualityCheck.objects.filter(checker=packager)
        passed_checks = quality_checks.filter(result='pass').count()
        pass_rate = (passed_checks / quality_checks.count() * 100) if quality_checks.count() > 0 else 0
        
        writer.writerow([
            packager.get_full_name(),
            all_packages.count(),
            month_packages.count(),
            round(avg_duration, 1),
            quality_checks.count(),
            round(pass_rate, 1)
        ])
    
    return response

@login_required
@user_passes_test(has_packaging_role)
def export_quality_checks(request):
    """Export quality check data as CSV."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="quality_checks_{timezone.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow(['Quality Checks Report', f'Generated on {timezone.now().strftime("%Y-%m-%d %H:%M")}'])
    writer.writerow([])
    
    # Get quality checks
    checks = PackagingQualityCheck.objects.all().select_related('packaging_record', 'checker').order_by('-checked_at')
    
    # Write quality check data
    writer.writerow(['Date', 'Order', 'Package ID', 'Check Type', 'Result', 'Checker', 'Notes'])
    
    for check in checks:
        writer.writerow([
            check.checked_at.strftime('%Y-%m-%d %H:%M'),
            check.packaging_record.order.order_code if check.packaging_record.order else 'N/A',
            check.packaging_record.barcode,
            check.get_check_type_display(),
            check.get_result_display(),
            check.checker.get_full_name() if check.checker else 'N/A',
            check.notes
        ])
    
    return response

@login_required
@user_passes_test(has_packaging_role)
def materials_management(request):
    """Materials management page with detailed inventory control."""
    # Get materials with stock alerts
    low_stock_materials = PackagingMaterial.objects.filter(
        current_stock__lte=F('min_stock_level')
    ).order_by('current_stock')
    
    out_of_stock_materials = PackagingMaterial.objects.filter(
        current_stock=0
    )
    
    # Get material usage statistics
    material_usage = []
    for material in PackagingMaterial.objects.all():
        # Count how many times this material was used in packaging records
        usage_count = 0
        for record in PackagingRecord.objects.all():
            try:
                materials_used = json.loads(record.materials_used) if isinstance(record.materials_used, str) else record.materials_used
                if material.name in materials_used:
                    usage_count += 1
            except (json.JSONDecodeError, TypeError):
                continue
        
        material_usage.append({
            'material': material,
            'usage_count': usage_count,
            'total_cost': material.current_stock * material.cost_per_unit,
        })
    
    # Sort by usage count
    material_usage.sort(key=lambda x: x['usage_count'], reverse=True)
    
    # Get recent stock movements (if we had a stock movement model)
    # For now, we'll show recent material updates
    
    # Get supplier information
    suppliers = PackagingMaterial.objects.values('supplier').distinct()
    supplier_stats = []
    
    for supplier_data in suppliers:
        if supplier_data['supplier']:
            supplier_name = supplier_data['supplier']
            materials = PackagingMaterial.objects.filter(supplier=supplier_name)
            total_value = sum(m.current_stock * m.cost_per_unit for m in materials)
            total_items = sum(m.current_stock for m in materials)
            
            supplier_stats.append({
                'name': supplier_name,
                'materials_count': materials.count(),
                'total_value': total_value,
                'total_items': total_items,
            })
    
    context = {
        'low_stock_materials': low_stock_materials,
        'out_of_stock_materials': out_of_stock_materials,
        'material_usage': material_usage[:10],  # Top 10 most used
        'supplier_stats': supplier_stats,
        'total_materials': PackagingMaterial.objects.count(),
        'total_value': PackagingMaterial.objects.aggregate(
            total=Sum(F('current_stock') * F('cost_per_unit'))
        )['total'] or 0,
    }
    
    return render(request, 'packaging/materials_management.html', context)

# API endpoints for AJAX
@login_required
def api_get_materials(request):
    """API endpoint to get packaging materials."""
    materials = PackagingMaterial.objects.filter(is_active=True)
    materials_data = []
    
    for material in materials:
        materials_data.append({
            'id': material.id,
            'name': material.name,
            'type': material.material_type,
            'current_stock': material.current_stock,
            'unit': material.unit,
            'is_low_stock': material.is_low_stock,
        })
    
    return JsonResponse({'materials': materials_data})

@login_required
def api_update_material_stock(request, material_id):
    """API endpoint to update material stock."""
    if request.method == 'POST':
        material = get_object_or_404(PackagingMaterial, id=material_id)
        new_stock = request.POST.get('new_stock')
        
        if new_stock is not None:
            material.current_stock = int(new_stock)
            material.save()
            return JsonResponse({'success': True, 'new_stock': material.current_stock})
    
    return JsonResponse({'success': False}, status=400)

@login_required
@user_passes_test(has_packaging_role)
def add_material(request):
    """Add a new packaging material."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        name = request.POST.get('name')
        material_type = request.POST.get('material_type')
        description = request.POST.get('description', '')
        current_stock = int(request.POST.get('current_stock', 0))
        min_stock_level = int(request.POST.get('min_stock_level', 10))
        unit = request.POST.get('unit', 'pieces')
        cost_per_unit = float(request.POST.get('cost_per_unit', 0))
        supplier = request.POST.get('supplier', '')
        
        # Create new material
        material = PackagingMaterial.objects.create(
            name=name,
            material_type=material_type,
            description=description,
            current_stock=current_stock,
            min_stock_level=min_stock_level,
            unit=unit,
            cost_per_unit=cost_per_unit,
            supplier=supplier
        )
        
        return JsonResponse({
            'success': True,
            'material_id': material.id,
            'name': material.name
        })
    except ValueError:
        return JsonResponse({'success': False, 'error': 'Invalid input data'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
@user_passes_test(has_packaging_role)
def get_material(request, material_id):
    """Get material details."""
    try:
        material = PackagingMaterial.objects.get(id=material_id)
        
        return JsonResponse({
            'id': material.id,
            'name': material.name,
            'material_type': material.material_type,
            'description': material.description,
            'current_stock': material.current_stock,
            'min_stock_level': material.min_stock_level,
            'unit': material.unit,
            'cost_per_unit': float(material.cost_per_unit),
            'supplier': material.supplier,
            'is_active': material.is_active
        })
    except PackagingMaterial.DoesNotExist:
        return JsonResponse({'error': 'Material not found'}, status=404)

@login_required
@user_passes_test(has_packaging_role)
def edit_material(request, material_id):
    """Edit an existing packaging material."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        material = PackagingMaterial.objects.get(id=material_id)
        
        # Update fields
        material.name = request.POST.get('name', material.name)
        material.material_type = request.POST.get('material_type', material.material_type)
        material.description = request.POST.get('description', material.description)
        material.current_stock = int(request.POST.get('current_stock', material.current_stock))
        material.min_stock_level = int(request.POST.get('min_stock_level', material.min_stock_level))
        material.unit = request.POST.get('unit', material.unit)
        material.cost_per_unit = float(request.POST.get('cost_per_unit', material.cost_per_unit))
        material.supplier = request.POST.get('supplier', material.supplier)
        
        material.save()
        
        return JsonResponse({
            'success': True,
            'material_id': material.id,
            'name': material.name
        })
    except PackagingMaterial.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Material not found'}, status=404)
    except ValueError:
        return JsonResponse({'success': False, 'error': 'Invalid input data'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
@user_passes_test(has_packaging_role)
def add_material_stock(request, material_id):
    """Add stock to a material."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        material = PackagingMaterial.objects.get(id=material_id)
        quantity = int(request.POST.get('quantity', 0))
        notes = request.POST.get('notes', '')
        
        if quantity <= 0:
            return JsonResponse({'success': False, 'error': 'Quantity must be positive'}, status=400)
        
        # Update stock
        material.current_stock += quantity
        material.updated_at = timezone.now()
        material.save()
        
        # Could log the stock addition in a separate model if needed
        
        return JsonResponse({
            'success': True,
            'material_id': material.id,
            'current_stock': material.current_stock,
            'name': material.name
        })
    except PackagingMaterial.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Material not found'}, status=404)
    except ValueError:
        return JsonResponse({'success': False, 'error': 'Invalid quantity'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
