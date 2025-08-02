from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
import json
import csv
from io import StringIO
from .models import Warehouse, WarehouseLocation, Stock, InventoryRecord, InventoryMovement
from sellers.models import Product
from django import forms
from django.contrib import messages

# Create your views here.

@login_required
def inventory_dashboard(request):
    """Inventory dashboard with statistics and low stock alerts."""
    # Get total product count, warehouses, and low stock items
    total_products = Product.objects.count()
    available_inventory = InventoryRecord.objects.aggregate(total=Sum('quantity'))['total'] or 0
    
    # Calculate low stock items correctly
    low_stock_items = 0
    for stock in Stock.objects.all():
        total_stock = InventoryRecord.objects.filter(product=stock.product).aggregate(total=Sum('quantity'))['total'] or 0
        if total_stock <= stock.min_quantity:
            low_stock_items += 1
    
    warehouses = Warehouse.objects.all()
    
    # Get recent inventory movements
    recent_movements = InventoryMovement.objects.select_related('product', 'from_warehouse', 'to_warehouse', 'created_by').order_by('-created_at')[:10]
    
    # Warehouse statistics
    warehouse_stats = []
    chart_data = {"labels": [], "data": []}
    
    for warehouse in warehouses:
        total_products_in_warehouse = InventoryRecord.objects.filter(warehouse=warehouse).count()
        total_quantity = InventoryRecord.objects.filter(warehouse=warehouse).aggregate(total=Sum('quantity'))['total'] or 0
        warehouse_stats.append({
            'warehouse': warehouse,
            'product_count': total_products_in_warehouse,
            'total_quantity': total_quantity
        })
        
        # Add to chart data
        chart_data["labels"].append(warehouse.name)
        chart_data["data"].append(total_quantity)
    
    # Convert chart data to JSON for use in template
    chart_json = json.dumps(chart_data)
    
    # Get products with stock information
    products_with_stock = Product.objects.all().order_by('-stock_quantity')[:10]
    
    context = {
        'total_products': total_products,
        'available_inventory': available_inventory,
        'low_stock_items': low_stock_items,
        'warehouses': warehouses,
        'recent_movements': recent_movements,
        'warehouse_stats': warehouse_stats,
        'chart_json': chart_json,
        'products_with_stock': products_with_stock
    }
    
    return render(request, 'inventory/dashboard.html', context)

@login_required
def inventory_products(request):
    """Inventory products list with filtering by warehouse and search options."""
    warehouse_id = request.GET.get('warehouse', '')
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    # Get product queryset
    products = Product.objects.all()
    
    # Filter by search query
    if search_query:
        products = products.filter(
            Q(name_en__icontains=search_query) |
            Q(name_ar__icontains=search_query) |
            Q(code__icontains=search_query)
        )
    
    # Get all warehouses for the dropdown
    warehouses = Warehouse.objects.all()
    
    # Get inventory records
    inventory_data = []
    for product in products:
        records = InventoryRecord.objects.filter(product=product)
        
        # Filter by warehouse if selected
        if warehouse_id:
            records = records.filter(warehouse_id=warehouse_id)
        
        # Calculate total quantity
        total_quantity = records.aggregate(total=Sum('quantity'))['total'] or 0
        
        # Check if product has stock settings
        try:
            stock = Stock.objects.get(product=product)
            min_quantity = stock.min_quantity
            max_quantity = stock.max_quantity
        except Stock.DoesNotExist:
            min_quantity = 0
            max_quantity = 0
        
        # Determine status
        if total_quantity <= 0:
            status = 'out_of_stock'
        elif total_quantity <= 10:  # Consider 10 or fewer units as low stock
            status = 'low_stock'
        else:
            status = 'in_stock'
        
        # Filter by status if requested
        if status_filter and status != status_filter:
            continue
        
        # Get warehouses where this product is stored
        product_warehouses = Warehouse.objects.filter(
            id__in=records.values_list('warehouse_id', flat=True)
        )
        
        # Get warehouse with the highest quantity
        main_warehouse = None
        if records.exists():
            main_warehouse = records.order_by('-quantity').first().warehouse
        
        inventory_data.append({
            'product': product,
            'total_quantity': total_quantity,
            'warehouses': product_warehouses,
            'main_warehouse': main_warehouse,
            'status': status,
            'min_quantity': min_quantity,
            'max_quantity': max_quantity
        })
    
    # Handle export request
    if request.GET.get('export') == 'csv':
        return export_products_csv(inventory_data, request)
    
    # Check if there's a movements parameter to show movements
    if request.GET.get('movements'):
        return redirect('inventory:movements')
    
    context = {
        'inventory_data': inventory_data,
        'warehouses': warehouses,
        'selected_warehouse_id': warehouse_id,
        'search_query': search_query,
        'status_filter': status_filter
    }
    
    return render(request, 'inventory/products.html', context)

class WarehouseForm(forms.ModelForm):
    """Form for warehouse creation and editing."""
    class Meta:
        model = Warehouse
        fields = ['name', 'location', 'description', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

@login_required
def warehouse_list(request):
    """List of warehouses with inventory statistics."""
    warehouses = Warehouse.objects.all()
    
    # Handle add warehouse request
    if request.GET.get('add'):
        return add_warehouse(request)
    
    # Handle edit warehouse request
    if request.GET.get('edit'):
        warehouse_id = request.GET.get('edit')
        return edit_warehouse(request, warehouse_id)
    
    # Handle view warehouse request
    if request.GET.get('view'):
        warehouse_id = request.GET.get('view')
        return view_warehouse(request, warehouse_id)
    
    warehouse_data = []
    chart_data = {
        'labels': [],
        'current': [],
        'capacity': []
    }
    
    total_capacity = 0
    total_used = 0
    
    for warehouse in warehouses:
        # Calculate total products and quantity
        inventory_records = InventoryRecord.objects.filter(warehouse=warehouse)
        total_products = inventory_records.values('product').distinct().count()
        total_quantity = inventory_records.aggregate(total=Sum('quantity'))['total'] or 0
        
        # In a real system, capacity would be stored in the model
        # For now, we'll use a formula based on the warehouse name length as a demo
        capacity = 25000 if 'Main' in warehouse.name else 15000 if 'Secondary' in warehouse.name else 10000
        
        utilization = round((total_quantity / capacity) * 100, 1) if capacity > 0 else 0
        
        total_capacity += capacity
        total_used += total_quantity
            
        warehouse_data.append({
            'warehouse': warehouse,
            'products_count': total_products,
            'total_quantity': total_quantity,
            'capacity': capacity,
            'utilization': utilization
        })
        
        # Add to chart data
        chart_data['labels'].append(warehouse.name)
        chart_data['current'].append(total_quantity)
        chart_data['capacity'].append(capacity)
    
    # Calculate total utilization
    total_utilization = round((total_used / total_capacity) * 100, 1) if total_capacity > 0 else 0
    
    # Convert chart data to JSON for use in template
    chart_json = json.dumps(chart_data)
    
    # Handle export request
    if request.GET.get('export') == 'csv':
        return export_warehouses_csv(warehouse_data, request)
    
    context = {
        'warehouse_data': warehouse_data,
        'chart_json': chart_json,
        'total_warehouses': warehouses.count(),
        'total_capacity': total_capacity,
        'total_utilization': total_utilization
    }
    
    return render(request, 'inventory/warehouses.html', context)

@login_required
def add_warehouse(request):
    """Add a new warehouse."""
    if request.method == 'POST':
        form = WarehouseForm(request.POST)
        if form.is_valid():
            warehouse = form.save()
            messages.success(request, f'Warehouse "{warehouse.name}" added successfully!')
            return redirect('inventory:warehouses')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = WarehouseForm()
    
    context = {
        'form': form,
        'title': 'Add Warehouse',
        'is_add': True
    }
    return render(request, 'inventory/warehouse_form.html', context)

@login_required
def edit_warehouse(request, warehouse_id):
    """Edit an existing warehouse."""
    warehouse = get_object_or_404(Warehouse, id=warehouse_id)
    
    if request.method == 'POST':
        form = WarehouseForm(request.POST, instance=warehouse)
        if form.is_valid():
            warehouse = form.save()
            messages.success(request, f'Warehouse "{warehouse.name}" updated successfully!')
            return redirect('inventory:warehouses')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = WarehouseForm(instance=warehouse)
    
    context = {
        'form': form,
        'warehouse': warehouse,
        'title': f'Edit Warehouse: {warehouse.name}',
        'is_edit': True
    }
    return render(request, 'inventory/warehouse_form.html', context)

@login_required
def view_warehouse(request, warehouse_id):
    """View warehouse details and inventory."""
    warehouse = get_object_or_404(Warehouse, id=warehouse_id)
    
    # Get inventory records for this warehouse
    inventory_records = InventoryRecord.objects.filter(warehouse=warehouse).select_related('product')
    
    # Calculate stats
    total_products = inventory_records.values('product').distinct().count()
    total_quantity = inventory_records.aggregate(total=Sum('quantity'))['total'] or 0
    
    # In a real system, capacity would be stored in the model
    capacity = 25000 if 'Main' in warehouse.name else 15000 if 'Secondary' in warehouse.name else 10000
    utilization = round((total_quantity / capacity) * 100, 1) if capacity > 0 else 0
    
    context = {
        'warehouse': warehouse,
        'inventory_records': inventory_records,
        'total_products': total_products,
        'total_quantity': total_quantity,
        'capacity': capacity,
        'utilization': utilization
    }
    return render(request, 'inventory/warehouse_detail.html', context)

@login_required
def inventory_movements(request):
    """View all inventory movements with filtering options."""
    # Get filter parameters
    warehouse_id = request.GET.get('warehouse', '')
    movement_type = request.GET.get('type', '')
    product_id = request.GET.get('product', '')
    from_date = request.GET.get('from_date', '')
    to_date = request.GET.get('to_date', '')
    
    # Base queryset
    movements = InventoryMovement.objects.all().select_related(
        'product', 'from_warehouse', 'to_warehouse', 'created_by'
    ).order_by('-created_at')
    
    # Apply filters
    if warehouse_id:
        movements = movements.filter(
            Q(from_warehouse_id=warehouse_id) | Q(to_warehouse_id=warehouse_id)
        )
    
    if movement_type:
        movements = movements.filter(movement_type=movement_type)
    
    if product_id:
        movements = movements.filter(product_id=product_id)
    
    if from_date:
        try:
            from_datetime = timezone.datetime.strptime(from_date, '%Y-%m-%d')
            movements = movements.filter(created_at__gte=from_datetime)
        except ValueError:
            pass
    
    if to_date:
        try:
            to_datetime = timezone.datetime.strptime(to_date, '%Y-%m-%d')
            to_datetime = to_datetime.replace(hour=23, minute=59, second=59)
            movements = movements.filter(created_at__lte=to_datetime)
        except ValueError:
            pass
    
    # Get all warehouses for the dropdown
    warehouses = Warehouse.objects.all()
    
    # Get all movement types for the dropdown
    movement_types = dict(InventoryMovement.MOVEMENT_TYPES)
    
    # Handle export request
    if request.GET.get('export') == 'csv':
        return export_movements(request)
    
    context = {
        'movements': movements,
        'warehouses': warehouses,
        'movement_types': movement_types,
        'selected_warehouse_id': warehouse_id,
        'selected_movement_type': movement_type,
        'selected_product_id': product_id,
        'from_date': from_date,
        'to_date': to_date
    }
    
    return render(request, 'inventory/movements.html', context)

def export_products_csv(inventory_data, request):
    """Export products data as CSV."""
    try:
        # Create a file-like buffer to receive CSV data
        buffer = StringIO()
        writer = csv.writer(buffer)
        
        # Write header row
        writer.writerow(['ID', 'Product Name', 'Code', 'Stock', 'Min Quantity', 'Max Quantity', 'Status', 'Warehouses'])
        
        # Write data rows
        for item in inventory_data:
            writer.writerow([
                item['product'].id,
                item['product'].name_en,
                item['product'].code,
                item['total_quantity'],
                item['min_quantity'],
                item['max_quantity'],
                item['status'].replace('_', ' ').title(),
                ', '.join([w.name for w in item['warehouses']])
            ])
        
        # Create the HTTP response with CSV data
        response = HttpResponse(buffer.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="inventory_products.csv"'
        
        return response
    except Exception as e:
        print(f"Error exporting products: {e}")
        messages.error(request, f"Error exporting products: {str(e)}")
        return redirect('inventory:products')

def export_warehouses_csv(warehouse_data, request):
    """Export warehouses data as CSV."""
    try:
        # Create a file-like buffer to receive CSV data
        buffer = StringIO()
        writer = csv.writer(buffer)
        
        # Write header row
        writer.writerow(['Name', 'Location', 'Products Count', 'Current Stock', 'Capacity', 'Utilization (%)', 'Status', 'Description'])
        
        # Write data rows
        for item in warehouse_data:
            writer.writerow([
                item['warehouse'].name,
                item['warehouse'].location,
                item['products_count'],
                item['total_quantity'],
                item['capacity'],
                item['utilization'],
                'Active' if item['warehouse'].is_active else 'Inactive',
                item['warehouse'].description
            ])
        
        # Create the HTTP response with CSV data
        response = HttpResponse(buffer.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="warehouses.csv"'
        
        return response
    except Exception as e:
        print(f"Error exporting warehouses: {e}")
        messages.error(request, f"Error exporting warehouses: {str(e)}")
        return redirect('inventory:warehouses')

@login_required
def export_movements(request):
    """Export inventory movements as CSV."""
    # Get movements, possibly filtered
    movements = InventoryMovement.objects.all().order_by('-created_at')
    
    # Apply filters if provided
    warehouse_id = request.GET.get('warehouse')
    if warehouse_id:
        movements = movements.filter(Q(from_warehouse_id=warehouse_id) | Q(to_warehouse_id=warehouse_id))
    
    movement_type = request.GET.get('type')
    if movement_type:
        movements = movements.filter(movement_type=movement_type)
    
    product_id = request.GET.get('product')
    if product_id:
        movements = movements.filter(product_id=product_id)
    
    from_date = request.GET.get('from_date')
    if from_date:
        try:
            from_datetime = timezone.datetime.strptime(from_date, '%Y-%m-%d')
            movements = movements.filter(created_at__gte=from_datetime)
        except ValueError:
            pass
    
    to_date = request.GET.get('to_date')
    if to_date:
        try:
            to_datetime = timezone.datetime.strptime(to_date, '%Y-%m-%d')
            to_datetime = to_datetime.replace(hour=23, minute=59, second=59)
            movements = movements.filter(created_at__lte=to_datetime)
        except ValueError:
            pass
    
    # Create a file-like buffer to receive CSV data
    buffer = StringIO()
    writer = csv.writer(buffer)
    
    # Write header row
    writer.writerow(['ID', 'Date', 'Product', 'Type', 'Quantity', 'From Warehouse', 'To Warehouse', 'Created By', 'Reference'])
    
    # Write data rows
    for movement in movements:
        writer.writerow([
            movement.id,
            movement.created_at.strftime('%Y-%m-%d %H:%M'),
            movement.product.name_en,
            movement.get_movement_type_display(),
            movement.quantity,
            movement.from_warehouse.name if movement.from_warehouse else '',
            movement.to_warehouse.name if movement.to_warehouse else '',
            movement.created_by.full_name,
            movement.reference
        ])
    
    # Create the HTTP response with CSV data
    response = HttpResponse(buffer.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="inventory_movements.csv"'
    
    return response

class ProductForm(forms.ModelForm):
    warehouse = forms.ModelChoiceField(
        queryset=Warehouse.objects.filter(is_active=True),
        required=False,
        empty_label="Select a warehouse (optional)",
        help_text="Select the warehouse where this product will be stored"
    )
    
    class Meta:
        model = Product
        fields = [
            'name_en', 'name_ar', 'code', 'selling_price', 'purchase_price',
            'stock_quantity', 'image', 'description', 'product_link', 'seller'
        ]
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'sr-only',
                'accept': 'image/*',
                'id': 'id_image'
            })
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter sellers based on user role
        if user:
            try:
                from users.models import User
                from roles.models import UserRole
                
                user_role = user.primary_role.name if user.primary_role else None
                
                if user_role == 'Seller':
                    # Sellers can only see themselves
                    self.fields['seller'].queryset = User.objects.filter(id=user.id)
                    self.fields['seller'].initial = user
                elif user_role in ['Super Admin', 'Admin', 'Manager']:
                    # Admins and managers can see all sellers
                    seller_users = User.objects.filter(
                        user_roles__role__name='Seller',
                        user_roles__is_active=True
                    ).distinct()
                    self.fields['seller'].queryset = seller_users
                else:
                    # Other roles see all users
                    self.fields['seller'].queryset = User.objects.filter(is_active=True)
            except ImportError:
                # If roles app is not available, show all users
                self.fields['seller'].queryset = User.objects.filter(is_active=True)
        else:
            # If no user provided, show all active users
            try:
                from users.models import User
                self.fields['seller'].queryset = User.objects.filter(is_active=True)
            except ImportError:
                pass
        
        # Set initial warehouse value for editing
        if self.instance and self.instance.pk:
            # Get the warehouse from the first inventory record for this product
            try:
                from inventory.models import InventoryRecord
                inventory_record = InventoryRecord.objects.filter(product=self.instance).first()
                if inventory_record:
                    self.fields['warehouse'].initial = inventory_record.warehouse.id
            except ImportError:
                pass
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Check if this is a new upload (has content_type) or existing image
            if hasattr(image, 'content_type'):
                # This is a new file upload
                # Check file size (10MB limit)
                if image.size > 10 * 1024 * 1024:
                    raise forms.ValidationError("Image file size must be under 10MB.")
                
                # Check file type
                allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
                if image.content_type not in allowed_types:
                    raise forms.ValidationError("Please upload a valid image file (JPEG, PNG, or GIF).")
                
                # Validate image dimensions
                try:
                    from PIL import Image
                    img = Image.open(image)
                    width, height = img.size
                    if width > 4000 or height > 4000:
                        raise forms.ValidationError("Image dimensions must be under 4000x4000 pixels.")
                except Exception as e:
                    raise forms.ValidationError("Invalid image file. Please upload a valid image.")
            else:
                # This is an existing image (ImageFieldFile), just return it
                pass
        
        return image
    
    def clean(self):
        cleaned_data = super().clean()
        # Add any cross-field validation here if needed
        return cleaned_data

@login_required
def add_product(request):
    """Add a new product to inventory."""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            try:
                # Save the product first without the image to get the ID
                product = form.save(commit=False)
                
                # Set the seller if not already set
                if not product.seller:
                    product.seller = request.user
                
                # Handle image upload - ensure it goes to media/products folder
                if 'image' in request.FILES:
                    uploaded_image = request.FILES['image']
                    # The model's upload_to function will handle the naming and path
                    product.image = uploaded_image
                
                # Save the product (this will trigger the upload_to function)
                product.save()
                
                # Create inventory record for the stock quantity
                if product.stock_quantity > 0:
                    # Use selected warehouse or get the first warehouse or create a default one
                    warehouse = form.cleaned_data.get('warehouse')
                    if not warehouse:
                        warehouse = Warehouse.objects.first()
                        if not warehouse:
                            warehouse = Warehouse.objects.create(
                                name="Main Warehouse",
                                location="Default Location"
                            )
                    
                    # Create inventory record
                    InventoryRecord.objects.create(
                        product=product,
                        warehouse=warehouse,
                        quantity=product.stock_quantity
                    )
                
                messages.success(request, f'Product "{product.name_en}" added successfully with {product.stock_quantity} units in stock!')
                return redirect('inventory:products')
                
            except Exception as e:
                messages.error(request, f'Error saving product: {str(e)}')
                print(f"Error saving product: {e}")
        else:
            # Debug information
            print("Form errors:", form.errors)
            print("Form data:", request.POST)
            print("Files:", request.FILES)
            print("Form fields:", form.fields.keys())
            print("Form is bound:", form.is_bound)
            print("Form is valid:", form.is_valid())
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductForm(user=request.user)
    
    context = {
        'form': form,
        'warehouses': Warehouse.objects.all(),
    }
    return render(request, 'inventory/add_product.html', context)

@login_required
def edit_product(request, product_id):
    """Edit an existing product in inventory."""
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product, user=request.user)
        if form.is_valid():
            try:
                # Save the product first without the image to get the updated data
                product = form.save(commit=False)
                
                # Set the seller if not already set
                if not product.seller:
                    product.seller = request.user
                
                # Handle image upload - the model's upload_to function will handle the naming
                if 'image' in request.FILES:
                    product.image = request.FILES['image']
                
                # Save the product (this will trigger the upload_to function)
                product.save()
                
                # Update inventory record for the stock quantity
                old_stock_quantity = form.initial.get('stock_quantity', 0) if form.initial else 0
                new_stock_quantity = form.cleaned_data.get('stock_quantity', 0)
                
                if new_stock_quantity != old_stock_quantity:
                    # Use selected warehouse or get the first warehouse or create a default one
                    warehouse = form.cleaned_data.get('warehouse')
                    if not warehouse:
                        warehouse = Warehouse.objects.first()
                        if not warehouse:
                            warehouse = Warehouse.objects.create(
                                name="Main Warehouse",
                                location="Default Location"
                            )
                    
                    # Update or create inventory record
                    inventory_record, created = InventoryRecord.objects.get_or_create(
                        product=product,
                        warehouse=warehouse,
                        defaults={'quantity': new_stock_quantity}
                    )
                    
                    if not created:
                        inventory_record.quantity = new_stock_quantity
                        inventory_record.save()
                
                messages.success(request, f'Product "{product.name_en}" updated successfully!')
                return redirect('inventory:products')
                
            except Exception as e:
                messages.error(request, f'Error updating product: {str(e)}')
                print(f"Error updating product: {e}")
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductForm(instance=product, user=request.user)
    
    context = {
        'product': product,
        'form': form,
        'warehouses': Warehouse.objects.all(),
    }
    return render(request, 'inventory/edit_product.html', context)

@login_required
def deduct_stock(request, product_id):
    """Deduct stock when a product is purchased."""
    if request.method == 'POST':
        try:
            product = get_object_or_404(Product, id=product_id)
            quantity = int(request.POST.get('quantity', 1))
            
            if product.stock_quantity >= quantity:
                product.stock_quantity -= quantity
                product.save()
                
                # Create inventory movement record
                InventoryMovement.objects.create(
                    product=product,
                    movement_type='order',
                    quantity=quantity,
                    created_by=request.user,
                    reference=f"Purchase - {quantity} units"
                )
                
                return JsonResponse({
                    'success': True,
                    'new_stock': product.stock_quantity,
                    'message': f'Stock deducted successfully. New stock: {product.stock_quantity}'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': f'Insufficient stock. Available: {product.stock_quantity}, Requested: {quantity}'
                }, status=400)
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error deducting stock: {str(e)}'
            }, status=500)
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

@login_required
@csrf_exempt
def delete_product(request, product_id):
    """Delete a product from inventory."""
    if request.method == 'POST':
        try:
            product = get_object_or_404(Product, id=product_id)
            product_name = product.name_en
            
            print(f"Attempting to delete product: {product_name} (ID: {product_id})")
            
            # Check if product is referenced by orders
            from orders.models import OrderItem
            order_items = OrderItem.objects.filter(product=product)
            if order_items.exists():
                order_item_count = order_items.count()
                print(f"Product is referenced by {order_item_count} order items")
                return JsonResponse({
                    'success': False,
                    'message': f'Cannot delete product "{product_name}" because it is referenced by {order_item_count} order item(s). Please remove or update the order items first.'
                }, status=400)
            
            # Check if product is referenced by orders (direct relationship)
            if hasattr(product, 'orders') and product.orders.exists():
                order_count = product.orders.count()
                print(f"Product is referenced by {order_count} orders")
                return JsonResponse({
                    'success': False,
                    'message': f'Cannot delete product "{product_name}" because it is referenced by {order_count} order(s). Please remove or update the orders first.'
                }, status=400)
            
            print(f"No references found, deleting product {product_name}")
            # If no references, delete the product
            product.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Product "{product_name}" deleted successfully.'
            })
        except Exception as e:
            print(f"Error deleting product: {e}")
            return JsonResponse({
                'success': False,
                'message': f'Error deleting product: {str(e)}'
            }, status=500)
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)
