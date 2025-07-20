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
import json

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
    
    # Get real packaging statistics
    total_packaging_records = PackagingRecord.objects.count()
    completed_today = PackagingRecord.objects.filter(
        status='completed',
        packaging_completed__date=today
    ).count()
    
    pending_packaging = PackagingRecord.objects.filter(status='pending').count()
    in_progress_packaging = PackagingRecord.objects.filter(status='in_progress').count()
    
    # Get packaging tasks
    pending_tasks = PackagingTask.objects.filter(status='pending').count()
    in_progress_tasks = PackagingTask.objects.filter(status='in_progress').count()
    completed_tasks_today = PackagingTask.objects.filter(
        status='completed',
        completed_at__date=today
    ).count()
    
    # Get material statistics
    low_stock_materials = PackagingMaterial.objects.filter(
        current_stock__lte=F('min_stock_level')
    ).count()
    
    total_materials_cost = PackagingMaterial.objects.aggregate(
        total_cost=Sum(F('current_stock') * F('cost_per_unit'))
    )['total_cost'] or 0
    
    # Get recent packaging activities
    recent_packaging = PackagingRecord.objects.select_related(
        'order', 'packager'
    ).order_by('-packaging_started')[:10]
    
    # Get recent tasks
    recent_tasks = PackagingTask.objects.select_related(
        'order', 'assigned_to'
    ).order_by('-created_at')[:10]
    
    # Get orders that need packaging (processing orders)
    recent_packaging_orders = Order.objects.filter(status='processing').select_related('customer').order_by('-date')[:10]
    
    # Get quality check statistics
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
    
    # Get average packaging time
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
    
    # Calculate total packaging queue
    total_packaging_queue = Order.objects.filter(status='processing').count()
    
    context = {
        'total_packaging_records': total_packaging_records,
        'completed_today': completed_today,
        'pending_packaging': pending_packaging,
        'in_progress_packaging': in_progress_packaging,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'completed_tasks_today': completed_tasks_today,
        'low_stock_materials': low_stock_materials,
        'total_materials_cost': total_materials_cost,
        'recent_packaging': recent_packaging,
        'recent_tasks': recent_tasks,
        'recent_packaging_orders': recent_packaging_orders,
        'quality_checks_today': quality_checks_today,
        'quality_pass_rate': round(quality_pass_rate, 1),
        'avg_packaging_time': round(avg_packaging_time, 1),
        'total_packaging_queue': total_packaging_queue,
        'today': today,
    }
    
    return render(request, 'packaging/dashboard.html', context)

@login_required
@user_passes_test(has_packaging_role)
def order_list(request):
    """List of orders for packaging with real data."""
    # Get orders that need packaging (processing orders)
    orders = Order.objects.filter(status='processing').select_related('customer')
    
    # Get search query
    search = request.GET.get('search', '')
    if search:
        orders = orders.filter(
            Q(order_code__icontains=search) |
            Q(customer__first_name__icontains=search) |
            Q(customer__last_name__icontains=search) |
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
            orders = orders.filter(packaging__isnull=True) | orders.filter(packaging__status='pending')
    
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
    
    # Pagination
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get packaging statistics
    packaging_stats = {
        'total_orders': orders.count(),
        'packaged_orders': orders.filter(packaging__status='completed').count(),
        'in_progress_orders': orders.filter(packaging__status='in_progress').count(),
        'pending_orders': orders.filter(packaging__isnull=True).count() + orders.filter(packaging__status='pending').count(),
    }
    
    context = {
        'orders': page_obj,
        'search_query': search,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'date_filter': date_filter,
        'packaging_stats': packaging_stats,
    }
    
    return render(request, 'packaging/order_list.html', context)

@login_required
@user_passes_test(has_packaging_role)
def start_packaging(request, order_id):
    """Start packaging for an order."""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        package_type = request.POST.get('package_type', 'box')
        estimated_weight = request.POST.get('estimated_weight')
        dimensions = request.POST.get('dimensions', '')
        notes = request.POST.get('notes', '')
        
        # Create packaging record
        packaging_record = PackagingRecord.objects.create(
            order=order,
            packager=request.user,
            package_type=package_type,
            package_weight=estimated_weight if estimated_weight else None,
            dimensions=dimensions,
            packaging_notes=notes,
            status='in_progress'
        )
        
        # Create packaging task
        PackagingTask.objects.create(
            order=order,
            assigned_to=request.user,
            status='in_progress',
            started_at=timezone.now()
        )
        
        messages.success(request, f'Packaging started for order {order.order_code}')
        return redirect('packaging:order_detail', order_id=order_id)
    
    # Get available materials
    materials = PackagingMaterial.objects.filter(is_active=True)
    
    context = {
        'order': order,
        'materials': materials,
    }
    
    return render(request, 'packaging/start_packaging.html', context)

@login_required
@user_passes_test(has_packaging_role)
def complete_packaging(request, order_id):
    """Complete packaging for an order."""
    order = get_object_or_404(Order, id=order_id)
    packaging_record = get_object_or_404(PackagingRecord, order=order)
    
    if request.method == 'POST':
        actual_weight = request.POST.get('actual_weight')
        final_dimensions = request.POST.get('final_dimensions', '')
        materials_used = request.POST.get('materials_used', '{}')
        quality_check_passed = request.POST.get('quality_check_passed') == 'on'
        completion_notes = request.POST.get('completion_notes', '')
        
        # Update packaging record
        packaging_record.package_weight = actual_weight if actual_weight else None
        packaging_record.dimensions = final_dimensions
        packaging_record.materials_used = materials_used
        packaging_record.quality_check_passed = quality_check_passed
        packaging_record.packaging_notes = completion_notes
        packaging_record.status = 'completed'
        packaging_record.packaging_completed = timezone.now()
        packaging_record.save()
        
        # Update packaging task
        task = PackagingTask.objects.filter(order=order, assigned_to=request.user).first()
        if task:
            task.status = 'completed'
            task.completed_at = timezone.now()
            task.save()
        
        # Update order status to ready for shipping
        order.status = 'ready_for_shipping'
        order.save()
        
        messages.success(request, f'Packaging completed for order {order.order_code}')
        return redirect('packaging:order_list')
    
    context = {
        'order': order,
        'packaging_record': packaging_record,
    }
    
    return render(request, 'packaging/complete_packaging.html', context)

@login_required
@user_passes_test(has_packaging_role)
def order_detail(request, order_id):
    """Detailed view of order packaging."""
    order = get_object_or_404(Order, id=order_id)
    packaging_record = PackagingRecord.objects.filter(order=order).first()
    packaging_task = PackagingTask.objects.filter(order=order).first()
    quality_checks = PackagingQualityCheck.objects.filter(packaging_record=packaging_record) if packaging_record else []
    
    context = {
        'order': order,
        'packaging_record': packaging_record,
        'packaging_task': packaging_task,
        'quality_checks': quality_checks,
    }
    
    return render(request, 'packaging/order_detail.html', context)

@login_required
@user_passes_test(has_packaging_role)
def materials_inventory(request):
    """Manage packaging materials inventory."""
    materials = PackagingMaterial.objects.all()
    
    # Apply filters
    material_type = request.GET.get('type', '')
    if material_type:
        materials = materials.filter(material_type=material_type)
    
    stock_status = request.GET.get('stock_status', '')
    if stock_status == 'low':
        materials = materials.filter(current_stock__lte=F('min_stock_level'))
    elif stock_status == 'out':
        materials = materials.filter(current_stock=0)
    
    # Pagination
    paginator = Paginator(materials, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get inventory statistics
    inventory_stats = {
        'total_materials': materials.count(),
        'low_stock_materials': materials.filter(current_stock__lte=F('min_stock_level')).count(),
        'out_of_stock_materials': materials.filter(current_stock=0).count(),
        'total_value': materials.aggregate(
            total_value=Sum(F('current_stock') * F('cost_per_unit'))
        )['total_value'] or 0,
    }
    
    context = {
        'materials': page_obj,
        'material_type_filter': material_type,
        'stock_status_filter': stock_status,
        'inventory_stats': inventory_stats,
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
    )
    
    total_completed = completed_packages.count()
    total_duration = 0
    package_count = 0
    
    for package in completed_packages:
        if package.packaging_duration:
            total_duration += package.packaging_duration
            package_count += 1
    
    avg_duration = (total_duration / package_count) if package_count > 0 else 0
    
    # Get quality check statistics
    quality_checks = PackagingQualityCheck.objects.filter(
        checked_at__date__gte=start_date
    )
    
    total_checks = quality_checks.count()
    passed_checks = quality_checks.filter(result='pass').count()
    failed_checks = quality_checks.filter(result='fail').count()
    conditional_checks = quality_checks.filter(result='conditional').count()
    
    pass_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0
    
    # Get packager performance
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
            for package in packages:
                if package.packaging_duration:
                    packager_duration += package.packaging_duration
                    packager_count += 1
            
            avg_packager_duration = (packager_duration / packager_count) if packager_count > 0 else 0
            
            packager_stats.append({
                'packager': packager,
                'packages_completed': packages.count(),
                'avg_duration': avg_packager_duration,
            })
    
    # Get daily statistics for chart
    daily_stats = []
    for i in range(7):
        date = today - timedelta(days=i)
        daily_completed = PackagingRecord.objects.filter(
            status='completed',
            packaging_completed__date=date
        ).count()
        
        daily_checks = PackagingQualityCheck.objects.filter(
            checked_at__date=date
        ).count()
        
        daily_stats.append({
            'date': date,
            'completed': daily_completed,
            'checks': daily_checks,
        })
    
    daily_stats.reverse()
    
    context = {
        'total_completed': total_completed,
        'avg_duration': round(avg_duration, 1),
        'total_checks': total_checks,
        'passed_checks': passed_checks,
        'failed_checks': failed_checks,
        'conditional_checks': conditional_checks,
        'pass_rate': round(pass_rate, 1),
        'packager_stats': packager_stats,
        'daily_stats': daily_stats,
        'date_filter': date_filter,
        'start_date': start_date,
        'today': today,
    }
    
    return render(request, 'packaging/packaging_report.html', context)

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
