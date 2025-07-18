# stock_keeper/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Sum, Q, F
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import (
    Warehouse, WarehouseInventory, InventoryMovement, 
    TrackingNumber, StockKeeperSession, StockAlert
)
from orders.models import Order
from sellers.models import Product
from datetime import datetime, timedelta
import json

def is_stock_keeper(user):
    """Check if user is a stock keeper."""
    return user.groups.filter(name='Stock Keepers').exists() or user.is_staff

def is_warehouse_manager(user):
    """Check if user is a warehouse manager."""
    return user.groups.filter(name='Warehouse Managers').exists() or user.is_superuser

@login_required
@user_passes_test(is_stock_keeper)
def dashboard(request):
    """Stock Keeper Dashboard with warehouse-specific data."""
    today = timezone.now().date()
    
    # Get user's assigned warehouse (for now, use first active warehouse)
    warehouse = Warehouse.objects.filter(is_active=True).first()
    if not warehouse:
        messages.error(request, 'No active warehouse found.')
        return redirect('stock_keeper:warehouse_list')
    
    # Get or create active session
    session, created = StockKeeperSession.objects.get_or_create(
        user=request.user,
        warehouse=warehouse,
        is_active=True,
        defaults={'shift_start': timezone.now()}
    )
    
    # Get today's statistics
    today_movements = InventoryMovement.objects.filter(
        processed_by=request.user,
        processed_at__date=today
    )
    
    pending_tasks = InventoryMovement.objects.filter(
        status='pending',
        to_warehouse=warehouse
    ).count()
    
    stock_alerts = StockAlert.objects.filter(
        warehouse=warehouse,
        is_resolved=False
    ).count()
    
    completed_today = today_movements.filter(status='completed').count()
    
    total_items = WarehouseInventory.objects.filter(
        warehouse=warehouse
    ).aggregate(total=Sum('quantity'))['total'] or 0
    
    # Get urgent alerts
    urgent_alerts = StockAlert.objects.filter(
        warehouse=warehouse,
        is_resolved=False,
        priority__in=['high', 'urgent']
    )[:5]
    
    # Get pending tasks
    pending_movements = InventoryMovement.objects.filter(
        status='pending',
        to_warehouse=warehouse
    )[:10]
    
    # Get recent activities
    recent_activities = InventoryMovement.objects.filter(
        processed_by=request.user
    ).order_by('-processed_at')[:10]
    
    context = {
        'warehouse': warehouse,
        'session': session,
        'pending_tasks': pending_tasks,
        'stock_alerts': stock_alerts,
        'completed_today': completed_today,
        'total_items': total_items,
        'urgent_alerts': urgent_alerts,
        'pending_movements': pending_movements,
        'recent_activities': recent_activities,
        'today': today,
    }
    
    return render(request, 'stock_keeper/dashboard.html', context)

@login_required
@user_passes_test(is_stock_keeper)
def warehouse_list(request):
    """List all warehouses."""
    warehouses = Warehouse.objects.filter(is_active=True)
    
    context = {
        'warehouses': warehouses,
    }
    
    return render(request, 'stock_keeper/warehouse_list.html', context)

@login_required
@user_passes_test(is_stock_keeper)
def warehouse_detail(request, warehouse_id):
    """Warehouse detail view with inventory."""
    warehouse = get_object_or_404(Warehouse, id=warehouse_id)
    
    # Get inventory for this warehouse
    inventory = WarehouseInventory.objects.filter(
        warehouse=warehouse
    ).select_related('product').order_by('-quantity')
    
    # Apply filters
    search = request.GET.get('search', '')
    if search:
        inventory = inventory.filter(
            Q(product__name_en__icontains=search) |
            Q(product__name_ar__icontains=search) |
            Q(location_code__icontains=search)
        )
    
    status_filter = request.GET.get('status', '')
    if status_filter:
        if status_filter == 'low_stock':
            inventory = inventory.filter(quantity__lte=F('min_stock_level'))
        elif status_filter == 'out_of_stock':
            inventory = inventory.filter(quantity=0)
        elif status_filter == 'overstocked':
            inventory = inventory.filter(quantity__gte=F('max_stock_level'))
    
    # Pagination
    paginator = Paginator(inventory, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'warehouse': warehouse,
        'inventory': page_obj,
        'search_query': search,
        'status_filter': status_filter,
    }
    
    return render(request, 'stock_keeper/warehouse_detail.html', context)

@login_required
@user_passes_test(is_stock_keeper)
def barcode_scanner(request):
    """Barcode scanning interface."""
    return render(request, 'stock_keeper/barcode_scanner.html')

@login_required
@user_passes_test(is_stock_keeper)
def scan_product(request):
    """Handle barcode/QR code scanning."""
    if request.method == 'POST':
        data = json.loads(request.body)
        scan_data = data.get('scan_data', '')
        
        # Try to find product by barcode or tracking number
        tracking = TrackingNumber.objects.filter(
            Q(barcode=scan_data) | Q(tracking_number=scan_data)
        ).first()
        
        if tracking:
            inventory = WarehouseInventory.objects.filter(
                product=tracking.product,
                warehouse=tracking.warehouse
            ).first()
            
            return JsonResponse({
                'success': True,
                'product': {
                    'id': tracking.product.id,
                    'name': tracking.product.name_en,
                    'code': tracking.product.code,
                    'quantity': inventory.quantity if inventory else 0,
                    'location': inventory.location_code if inventory else '',
                    'tracking_number': tracking.tracking_number,
                    'barcode': tracking.barcode,
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Product not found'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required
@user_passes_test(is_stock_keeper)
def receive_stock(request):
    """Stock receiving interface."""
    if request.method == 'POST':
        # Handle stock receiving
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 0))
        warehouse_id = request.POST.get('warehouse_id')
        location_code = request.POST.get('location_code', '')
        condition = request.POST.get('condition', 'good')
        notes = request.POST.get('notes', '')
        
        if product_id and quantity > 0 and warehouse_id:
            product = get_object_or_404(Product, id=product_id)
            warehouse = get_object_or_404(Warehouse, id=warehouse_id)
            
            # Create movement record
            movement = InventoryMovement.objects.create(
                movement_type='stock_in',
                product=product,
                quantity=quantity,
                to_warehouse=warehouse,
                to_location=location_code,
                created_by=request.user,
                processed_by=request.user,
                status='completed',
                condition=condition,
                notes=notes,
                reason='Stock receiving'
            )
            
            # Update inventory
            inventory, created = WarehouseInventory.objects.get_or_create(
                product=product,
                warehouse=warehouse,
                defaults={'quantity': 0}
            )
            inventory.quantity += quantity
            if location_code:
                inventory.location_code = location_code
            inventory.save()
            
            messages.success(request, f'Successfully received {quantity} units of {product.name_en}')
            return redirect('stock_keeper:receive_stock')
    
    # Get pending receiving tasks
    pending_receiving = InventoryMovement.objects.filter(
        movement_type='stock_in',
        status='pending'
    ).select_related('product', 'to_warehouse')
    
    context = {
        'pending_receiving': pending_receiving,
    }
    
    return render(request, 'stock_keeper/receive_stock.html', context)

@login_required
@user_passes_test(is_stock_keeper)
def ship_orders(request):
    """Order shipping interface."""
    if request.method == 'POST':
        # Handle order shipping
        order_id = request.POST.get('order_id')
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 0))
        warehouse_id = request.POST.get('warehouse_id')
        
        if order_id and product_id and quantity > 0 and warehouse_id:
            order = get_object_or_404(Order, id=order_id)
            product = get_object_or_404(Product, id=product_id)
            warehouse = get_object_or_404(Warehouse, id=warehouse_id)
            
            # Check if enough stock
            inventory = WarehouseInventory.objects.filter(
                product=product,
                warehouse=warehouse
            ).first()
            
            if inventory and inventory.quantity >= quantity:
                # Create movement record
                movement = InventoryMovement.objects.create(
                    movement_type='stock_out',
                    product=product,
                    quantity=quantity,
                    from_warehouse=warehouse,
                    created_by=request.user,
                    processed_by=request.user,
                    status='completed',
                    reference_number=order.order_code,
                    reference_type='Order',
                    reason='Order fulfillment'
                )
                
                # Update inventory
                inventory.quantity -= quantity
                inventory.save()
                
                # Update order status
                order.status = 'shipped'
                order.save()
                
                messages.success(request, f'Successfully shipped {quantity} units of {product.name_en} for order {order.order_code}')
            else:
                messages.error(request, 'Insufficient stock for shipping')
            
            return redirect('stock_keeper:ship_orders')
    
    # Get orders ready for shipping
    ready_orders = Order.objects.filter(
        status='processing'
    ).select_related('customer', 'product')
    
    context = {
        'ready_orders': ready_orders,
    }
    
    return render(request, 'stock_keeper/ship_orders.html', context)

@login_required
@user_passes_test(is_stock_keeper)
def transfer_stock(request):
    """Stock transfer interface."""
    if request.method == 'POST':
        # Handle stock transfer
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 0))
        from_warehouse_id = request.POST.get('from_warehouse_id')
        to_warehouse_id = request.POST.get('to_warehouse_id')
        from_location = request.POST.get('from_location', '')
        to_location = request.POST.get('to_location', '')
        notes = request.POST.get('notes', '')
        
        if product_id and quantity > 0 and from_warehouse_id and to_warehouse_id:
            product = get_object_or_404(Product, id=product_id)
            from_warehouse = get_object_or_404(Warehouse, id=from_warehouse_id)
            to_warehouse = get_object_or_404(Warehouse, id=to_warehouse_id)
            
            # Check if enough stock in source warehouse
            from_inventory = WarehouseInventory.objects.filter(
                product=product,
                warehouse=from_warehouse
            ).first()
            
            if from_inventory and from_inventory.quantity >= quantity:
                # Create movement record
                movement = InventoryMovement.objects.create(
                    movement_type='transfer',
                    product=product,
                    quantity=quantity,
                    from_warehouse=from_warehouse,
                    to_warehouse=to_warehouse,
                    from_location=from_location,
                    to_location=to_location,
                    created_by=request.user,
                    processed_by=request.user,
                    status='completed',
                    notes=notes,
                    reason='Inter-warehouse transfer'
                )
                
                # Update source inventory
                from_inventory.quantity -= quantity
                from_inventory.save()
                
                # Update destination inventory
                to_inventory, created = WarehouseInventory.objects.get_or_create(
                    product=product,
                    warehouse=to_warehouse,
                    defaults={'quantity': 0}
                )
                to_inventory.quantity += quantity
                if to_location:
                    to_inventory.location_code = to_location
                to_inventory.save()
                
                messages.success(request, f'Successfully transferred {quantity} units of {product.name_en} from {from_warehouse.name} to {to_warehouse.name}')
            else:
                messages.error(request, 'Insufficient stock for transfer')
            
            return redirect('stock_keeper:transfer_stock')
    
    # Get pending transfer requests
    pending_transfers = InventoryMovement.objects.filter(
        movement_type='transfer',
        status='pending'
    ).select_related('product', 'from_warehouse', 'to_warehouse')
    
    context = {
        'pending_transfers': pending_transfers,
    }
    
    return render(request, 'stock_keeper/transfer_stock.html', context)

@login_required
@user_passes_test(is_stock_keeper)
def movement_history(request):
    """Movement history view."""
    movements = InventoryMovement.objects.select_related(
        'product', 'from_warehouse', 'to_warehouse', 'created_by', 'processed_by'
    ).order_by('-created_at')
    
    # Apply filters
    movement_type = request.GET.get('type', '')
    if movement_type:
        movements = movements.filter(movement_type=movement_type)
    
    warehouse_id = request.GET.get('warehouse', '')
    if warehouse_id:
        movements = movements.filter(
            Q(from_warehouse_id=warehouse_id) | Q(to_warehouse_id=warehouse_id)
        )
    
    date_from = request.GET.get('date_from', '')
    if date_from:
        movements = movements.filter(created_at__date__gte=date_from)
    
    date_to = request.GET.get('date_to', '')
    if date_to:
        movements = movements.filter(created_at__date__lte=date_to)
    
    # Pagination
    paginator = Paginator(movements, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    warehouses = Warehouse.objects.filter(is_active=True)
    
    context = {
        'movements': page_obj,
        'warehouses': warehouses,
        'movement_type_filter': movement_type,
        'warehouse_filter': warehouse_id,
        'date_from': date_from,
        'date_to': date_to,
    }
    
    return render(request, 'stock_keeper/movement_history.html', context)

@login_required
@user_passes_test(is_stock_keeper)
def alerts(request):
    """Stock alerts view."""
    alerts = StockAlert.objects.select_related(
        'product', 'warehouse', 'resolved_by'
    ).order_by('-created_at')
    
    # Apply filters
    alert_type = request.GET.get('type', '')
    if alert_type:
        alerts = alerts.filter(alert_type=alert_type)
    
    priority = request.GET.get('priority', '')
    if priority:
        alerts = alerts.filter(priority=priority)
    
    resolved = request.GET.get('resolved', '')
    if resolved == 'true':
        alerts = alerts.filter(is_resolved=True)
    elif resolved == 'false':
        alerts = alerts.filter(is_resolved=False)
    
    # Pagination
    paginator = Paginator(alerts, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'alerts': page_obj,
        'alert_type_filter': alert_type,
        'priority_filter': priority,
        'resolved_filter': resolved,
    }
    
    return render(request, 'stock_keeper/alerts.html', context)

@login_required
@user_passes_test(is_stock_keeper)
def resolve_alert(request, alert_id):
    """Resolve a stock alert."""
    alert = get_object_or_404(StockAlert, id=alert_id)
    alert.resolve(request.user)
    messages.success(request, f'Alert "{alert.alert_type}" has been resolved.')
    return redirect('stock_keeper:alerts')

# API Views for AJAX
@login_required
@csrf_exempt
def api_search_product(request):
    """API endpoint for product search."""
    if request.method == 'POST':
        data = json.loads(request.body)
        search_term = data.get('search', '')
        
        products = Product.objects.filter(
            Q(name_en__icontains=search_term) |
            Q(name_ar__icontains=search_term) |
            Q(code__icontains=search_term)
        )[:10]
        
        results = []
        for product in products:
            results.append({
                'id': product.id,
                'name': product.name_en,
                'code': product.code,
                'image': product.image.url if product.image else '',
            })
        
        return JsonResponse({'results': results})
    
    return JsonResponse({'error': 'Invalid request'})

@login_required
def api_get_inventory(request, product_id):
    """API endpoint to get inventory for a product."""
    product = get_object_or_404(Product, id=product_id)
    inventory = WarehouseInventory.objects.filter(
        product=product
    ).select_related('warehouse')
    
    results = []
    for inv in inventory:
        results.append({
            'warehouse_id': inv.warehouse.id,
            'warehouse_name': inv.warehouse.name,
            'quantity': inv.quantity,
            'location': inv.location_code,
            'is_low_stock': inv.is_low_stock,
        })
    
    return JsonResponse({'inventory': results})
