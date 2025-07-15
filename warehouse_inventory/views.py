from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, F, Q
from django.http import JsonResponse
from django.utils.translation import gettext as _
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta
from .models import Warehouse, WarehouseInventory, InventoryMovement, TrackingNumber
from products.models import Product
from orders.models import Order

@login_required
def dashboard(request):
    """Main inventory dashboard showing overview of all warehouses."""
    warehouses = Warehouse.objects.filter(is_active=True)
    
    # Get inventory statistics
    total_inventory = WarehouseInventory.objects.aggregate(
        total=Sum('quantity')
    )['total'] or 0
    
    # Get recent movements
    recent_movements = InventoryMovement.objects.select_related(
        'warehouse', 'product', 'created_by'
    ).order_by('-created_at')[:10]
    
    # Get low stock items
    low_stock_items = WarehouseInventory.objects.select_related(
        'warehouse', 'product'
    ).filter(quantity__lt=F('product__min_stock_level'))
    
    # Get today's movements count
    today = timezone.now().date()
    today_movements = InventoryMovement.objects.filter(
        created_at__date=today
    ).count()
    
    context = {
        'warehouses': warehouses,
        'total_inventory': total_inventory,
        'recent_movements': recent_movements,
        'low_stock_items': low_stock_items,
        'today_movements': today_movements,
    }
    return render(request, 'warehouse_inventory/dashboard.html', context)

@login_required
def warehouse_inventory(request, warehouse_id):
    """Display inventory for a specific warehouse."""
    warehouse = get_object_or_404(Warehouse, id=warehouse_id)
    
    # Get search parameters
    search = request.GET.get('search', '')
    sort = request.GET.get('sort', 'name')
    
    # Base queryset
    inventory_items = WarehouseInventory.objects.select_related(
        'product', 'warehouse'
    ).filter(warehouse=warehouse)
    
    # Apply search filter
    if search:
        inventory_items = inventory_items.filter(
            Q(product__name_en__icontains=search) |
            Q(product__name_ar__icontains=search) |
            Q(product__code__icontains=search)
        )
    
    # Apply sorting
    if sort == 'name':
        inventory_items = inventory_items.order_by('product__name_en')
    elif sort == 'quantity':
        inventory_items = inventory_items.order_by('quantity')
    elif sort == 'updated':
        inventory_items = inventory_items.order_by('-last_movement_date')
    
    # Pagination
    paginator = Paginator(inventory_items, 20)
    page = request.GET.get('page')
    inventory_items = paginator.get_page(page)
    
    context = {
        'warehouse': warehouse,
        'inventory_items': inventory_items,
        'total_items': inventory_items.paginator.count,
        'total_quantity': sum(item.quantity for item in inventory_items),
    }
    return render(request, 'warehouse_inventory/warehouse_inventory.html', context)

@login_required
def add_to_inventory(request, warehouse_id):
    """Add products to warehouse inventory from orders."""
    warehouse = get_object_or_404(Warehouse, id=warehouse_id)
    
    if request.method == 'POST':
        order_ids = request.POST.getlist('order_ids')
        notes = request.POST.get('notes', '')
        
        if not order_ids:
            messages.error(request, _('Please select at least one order.'))
            return redirect('warehouse_inventory:add_to_inventory', warehouse_id=warehouse.id)
        
        try:
            orders = Order.objects.filter(id__in=order_ids)
            for order in orders:
                for item in order.items.all():
                    # Create or update inventory
                    inventory, created = WarehouseInventory.objects.get_or_create(
                        warehouse=warehouse,
                        product=item.product,
                        defaults={'quantity': 0}
                    )
                    
                    # Record movement
                    movement = InventoryMovement.objects.create(
                        warehouse=warehouse,
                        product=item.product,
                        movement_type='in',
                        quantity_change=item.quantity,
                        reason=_('Added from Order #{}').format(order.id),
                        notes=notes,
                        created_by=request.user
                    )
                    
                    # Update inventory quantity
                    inventory.quantity += item.quantity
                    inventory.last_movement_date = movement.created_at
                    inventory.save()
            
            messages.success(request, _('Products added to inventory successfully.'))
            return redirect('warehouse_inventory:warehouse_inventory', warehouse_id=warehouse.id)
            
        except Exception as e:
            messages.error(request, _('Error adding products to inventory: {}').format(str(e)))
            return redirect('warehouse_inventory:add_to_inventory', warehouse_id=warehouse.id)
    
    # Get available orders
    orders = Order.objects.select_related('seller').prefetch_related('items__product')
    
    # Apply filters
    seller_id = request.GET.get('seller')
    if seller_id:
        orders = orders.filter(seller_id=seller_id)
    
    date_range = request.GET.get('date_range')
    if date_range:
        today = timezone.now().date()
        if date_range == 'today':
            orders = orders.filter(date__date=today)
        elif date_range == 'yesterday':
            orders = orders.filter(date__date=today - timedelta(days=1))
        elif date_range == 'last_7_days':
            orders = orders.filter(date__date__gte=today - timedelta(days=7))
        elif date_range == 'last_30_days':
            orders = orders.filter(date__date__gte=today - timedelta(days=30))
    
    status = request.GET.get('status')
    if status and status != 'all':
        orders = orders.filter(status=status)
    
    context = {
        'warehouse': warehouse,
        'orders': orders,
        'sellers': orders.values('seller', 'seller__name').distinct(),
    }
    return render(request, 'warehouse_inventory/add_to_inventory.html', context)

@login_required
def inventory_movement(request, warehouse_id):
    """Record inventory movement (in/out/transfer)."""
    warehouse = get_object_or_404(Warehouse, id=warehouse_id)
    
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        movement_type = request.POST.get('movement_type')
        quantity = request.POST.get('quantity')
        destination_warehouse_id = request.POST.get('destination_warehouse')
        reason = request.POST.get('reason', '')
        notes = request.POST.get('notes', '')
        
        try:
            product = Product.objects.get(id=product_id)
            quantity = int(quantity)
            
            if quantity < 1:
                raise ValueError(_('Quantity must be greater than zero.'))
            
            # Get or create inventory record
            inventory = WarehouseInventory.objects.get_or_create(
                warehouse=warehouse,
                product=product,
                defaults={'quantity': 0}
            )[0]
            
            if movement_type in ['out', 'transfer'] and inventory.quantity < quantity:
                raise ValueError(_('Insufficient stock for this movement.'))
            
            # Handle transfer movement
            if movement_type == 'transfer':
                if not destination_warehouse_id:
                    raise ValueError(_('Destination warehouse is required for transfer.'))
                
                destination_warehouse = Warehouse.objects.get(id=destination_warehouse_id)
                
                # Create movement for source warehouse
                InventoryMovement.objects.create(
                    warehouse=warehouse,
                    product=product,
                    movement_type='out',
                    quantity_change=-quantity,
                    reason=_('Transfer to {}').format(destination_warehouse.name),
                    notes=notes,
                    created_by=request.user
                )
                
                # Create movement for destination warehouse
                InventoryMovement.objects.create(
                    warehouse=destination_warehouse,
                    product=product,
                    movement_type='in',
                    quantity_change=quantity,
                    reason=_('Transfer from {}').format(warehouse.name),
                    notes=notes,
                    created_by=request.user
                )
                
                # Update source inventory
                inventory.quantity -= quantity
                inventory.save()
                
                # Update destination inventory
                dest_inventory = WarehouseInventory.objects.get_or_create(
                    warehouse=destination_warehouse,
                    product=product,
                    defaults={'quantity': 0}
                )[0]
                dest_inventory.quantity += quantity
                dest_inventory.save()
                
            else:
                # Create movement record
                quantity_change = quantity if movement_type == 'in' else -quantity
                movement = InventoryMovement.objects.create(
                    warehouse=warehouse,
                    product=product,
                    movement_type=movement_type,
                    quantity_change=quantity_change,
                    reason=reason,
                    notes=notes,
                    created_by=request.user
                )
                
                # Update inventory quantity
                inventory.quantity += quantity_change
                inventory.last_movement_date = movement.created_at
                inventory.save()
            
            messages.success(request, _('Inventory movement recorded successfully.'))
            return redirect('warehouse_inventory:warehouse_inventory', warehouse_id=warehouse.id)
            
        except (Product.DoesNotExist, Warehouse.DoesNotExist):
            messages.error(request, _('Invalid product or warehouse selected.'))
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, _('Error recording movement: {}').format(str(e)))
        
        return redirect('warehouse_inventory:inventory_movement', warehouse_id=warehouse.id)
    
    # Get inventory items for the warehouse
    inventory_items = WarehouseInventory.objects.select_related(
        'product'
    ).filter(warehouse=warehouse)
    
    # Get other warehouses for transfer
    other_warehouses = Warehouse.objects.exclude(id=warehouse_id).filter(is_active=True)
    
    # Movement types
    movement_types = [
        ('in', _('Stock In')),
        ('out', _('Stock Out')),
        ('transfer', _('Transfer')),
    ]
    
    context = {
        'warehouse': warehouse,
        'inventory_items': inventory_items,
        'other_warehouses': other_warehouses,
        'movement_types': movement_types,
    }
    return render(request, 'warehouse_inventory/movement.html', context)

@login_required
def search_inventory(request):
    """Search inventory across all warehouses."""
    query = request.GET.get('q', '')
    search_type = request.GET.get('type', 'all')
    
    results = []
    if query:
        # Base queryset
        inventory_items = WarehouseInventory.objects.select_related(
            'product', 'warehouse', 'added_from_order'
        )
        
        # Apply search filters based on type
        if search_type == 'order':
            results = inventory_items.filter(added_from_order__id=query)
        elif search_type == 'tracking':
            results = inventory_items.filter(tracking_number=query)
        elif search_type == 'product':
            results = inventory_items.filter(
                Q(product__name_en__icontains=query) |
                Q(product__name_ar__icontains=query) |
                Q(product__code__icontains=query)
            )
        else:
            results = inventory_items.filter(
                Q(product__name_en__icontains=query) |
                Q(product__name_ar__icontains=query) |
                Q(product__code__icontains=query) |
                Q(tracking_number=query) |
                Q(added_from_order__id=query)
            )
    
    context = {
        'query': query,
        'search_type': search_type,
        'results': results,
    }
    return render(request, 'warehouse_inventory/search.html', context)

@login_required
def tracking_details(request, tracking_number):
    """Display tracking details for an inventory item."""
    tracking = get_object_or_404(TrackingNumber, tracking_number=tracking_number)
    
    # Get movement history
    movements = InventoryMovement.objects.select_related(
        'warehouse', 'product', 'created_by'
    ).filter(
        warehouse=tracking.warehouse,
        product=tracking.product
    ).order_by('-created_at')
    
    context = {
        'tracking': tracking,
        'movements': movements,
    }
    return render(request, 'warehouse_inventory/tracking_details.html', context)

@login_required
def barcode_scan(request):
    """Handle barcode scanning for inventory management."""
    if request.method == 'POST':
        barcode = request.POST.get('barcode')
        warehouse_id = request.POST.get('warehouse_id')
        action = request.POST.get('action')
        quantity = request.POST.get('quantity')
        
        try:
            warehouse = Warehouse.objects.get(id=warehouse_id)
            product = Product.objects.get(barcode=barcode)
            
            if action == 'lookup':
                # Return product information
                inventory = WarehouseInventory.objects.filter(
                    warehouse=warehouse,
                    product=product
                ).first()
                
                return JsonResponse({
                    'success': True,
                    'product': {
                        'name': product.name_en,
                        'code': product.code,
                        'warehouse': warehouse.name,
                        'status': 'In Stock' if inventory and inventory.quantity > 0 else 'Out of Stock',
                        'quantity': inventory.quantity if inventory else 0,
                    }
                })
            
            elif action in ['add_stock', 'update_quantity']:
                if not quantity:
                    raise ValueError(_('Quantity is required.'))
                
                quantity = int(quantity)
                if quantity < 1:
                    raise ValueError(_('Quantity must be greater than zero.'))
                
                inventory, created = WarehouseInventory.objects.get_or_create(
                    warehouse=warehouse,
                    product=product,
                    defaults={'quantity': 0}
                )
                
                if action == 'add_stock':
                    # Add stock
                    movement = InventoryMovement.objects.create(
                        warehouse=warehouse,
                        product=product,
                        movement_type='in',
                        quantity_change=quantity,
                        reason=_('Stock added via barcode scan'),
                        created_by=request.user
                    )
                    
                    inventory.quantity += quantity
                    message = _('Stock added successfully.')
                    
                else:
                    # Update quantity
                    old_quantity = inventory.quantity
                    quantity_change = quantity - old_quantity
                    
                    movement = InventoryMovement.objects.create(
                        warehouse=warehouse,
                        product=product,
                        movement_type='in' if quantity_change > 0 else 'out',
                        quantity_change=quantity_change,
                        reason=_('Quantity updated via barcode scan'),
                        created_by=request.user
                    )
                    
                    inventory.quantity = quantity
                    message = _('Quantity updated successfully.')
                
                inventory.last_movement_date = movement.created_at
                inventory.save()
                
                return JsonResponse({
                    'success': True,
                    'message': message,
                    'new_quantity': inventory.quantity,
                })
            
            else:
                raise ValueError(_('Invalid action specified.'))
            
        except (Warehouse.DoesNotExist, Product.DoesNotExist):
            return JsonResponse({
                'success': False,
                'error': _('Invalid warehouse or product.')
            })
        except ValueError as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': _('An error occurred: {}').format(str(e))
            })
    
    # Get warehouses for the form
    warehouses = Warehouse.objects.filter(is_active=True)
    
    context = {
        'warehouses': warehouses,
    }
    return render(request, 'warehouse_inventory/barcode_scan.html', context)

@login_required
def warehouse_movements(request, warehouse_id):
    """Display movement history for a specific warehouse."""
    warehouse = get_object_or_404(Warehouse, id=warehouse_id)
    
    # Get movements
    movements = InventoryMovement.objects.select_related(
        'warehouse', 'product', 'created_by'
    ).filter(warehouse=warehouse).order_by('-created_at')
    
    # Apply filters
    movement_type = request.GET.get('type')
    if movement_type:
        movements = movements.filter(movement_type=movement_type)
    
    date_from = request.GET.get('date_from')
    if date_from:
        movements = movements.filter(created_at__date__gte=date_from)
    
    date_to = request.GET.get('date_to')
    if date_to:
        movements = movements.filter(created_at__date__lte=date_to)
    
    # Pagination
    paginator = Paginator(movements, 50)
    page = request.GET.get('page')
    movements = paginator.get_page(page)
    
    context = {
        'warehouse': warehouse,
        'movements': movements,
    }
    return render(request, 'warehouse_inventory/movements.html', context)

@login_required
def product_movements(request, product_id):
    """API endpoint to get movement history for a specific product."""
    warehouse_id = request.GET.get('warehouse')
    
    movements = InventoryMovement.objects.select_related(
        'warehouse', 'product', 'created_by'
    ).filter(product_id=product_id)
    
    if warehouse_id:
        movements = movements.filter(warehouse_id=warehouse_id)
    
    movements = movements.order_by('-created_at')[:20]
    
    data = {
        'movements': [{
            'type': movement.get_movement_type_display(),
            'quantity': movement.quantity_change,
            'date': movement.created_at.strftime('%Y-%m-%d %H:%M'),
            'reason': movement.reason,
        } for movement in movements]
    }
    
    return JsonResponse(data)

@login_required
def warehouse_list(request):
    """Display list of warehouses with management options."""
    warehouses = Warehouse.objects.all()
    
    context = {
        'warehouses': warehouses,
    }
    return render(request, 'warehouse_inventory/warehouse_list.html', context)

@login_required
def warehouse_create(request):
    """Create a new warehouse."""
    if request.method == 'POST':
        try:
            warehouse = Warehouse.objects.create(
                name=request.POST.get('name'),
                code=request.POST.get('code'),
                country=request.POST.get('country'),
                currency=request.POST.get('currency'),
                zone=request.POST.get('zone'),
                location=request.POST.get('location')
            )
            messages.success(request, _('Warehouse created successfully.'))
            return redirect('warehouse_inventory:warehouse_list')
        except Exception as e:
            messages.error(request, str(e))
    
    return render(request, 'warehouse_inventory/warehouse_form.html')

@login_required
def warehouse_edit(request, warehouse_id):
    """Edit an existing warehouse."""
    warehouse = get_object_or_404(Warehouse, id=warehouse_id)
    
    if request.method == 'POST':
        try:
            warehouse.name = request.POST.get('name')
            warehouse.code = request.POST.get('code')
            warehouse.country = request.POST.get('country')
            warehouse.currency = request.POST.get('currency')
            warehouse.zone = request.POST.get('zone')
            warehouse.location = request.POST.get('location')
            warehouse.save()
            
            messages.success(request, _('Warehouse updated successfully.'))
            return redirect('warehouse_inventory:warehouse_list')
        except Exception as e:
            messages.error(request, str(e))
    
    context = {
        'warehouse': warehouse,
    }
    return render(request, 'warehouse_inventory/warehouse_form.html', context)

@login_required
def warehouse_delete(request, warehouse_id):
    """Delete a warehouse."""
    warehouse = get_object_or_404(Warehouse, id=warehouse_id)
    
    if request.method == 'POST':
        try:
            if warehouse.inventory.exists():
                messages.error(request, _('Cannot delete warehouse with existing inventory.'))
                return redirect('warehouse_inventory:warehouse_list')
            
            warehouse.delete()
            messages.success(request, _('Warehouse deleted successfully.'))
            return redirect('warehouse_inventory:warehouse_list')
        except Exception as e:
            messages.error(request, str(e))
    
    context = {
        'warehouse': warehouse,
    }
    return render(request, 'warehouse_inventory/warehouse_delete.html', context) 