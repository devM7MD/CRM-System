from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.contrib import messages
from django.utils import timezone
from .models import Order, OrderItem
from .forms import OrderForm, OrderItemFormSet, OrderStatusUpdateForm, OrderImportForm
from users.models import AuditLog, User
from sellers.models import Product
from settings.models import DeliveryCompany
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
import csv
import io
from datetime import datetime

@login_required
def order_list(request):
    """View for listing all orders based on user role."""
    # Different users see different sets of orders
    user_role = request.user.primary_role.name if request.user.primary_role else None
    
    # If user has no role, show all orders (default behavior)
    if not user_role:
        orders = Order.objects.all().order_by('-date')
    elif user_role in ['Super Admin', 'Admin']:
        orders = Order.objects.all().order_by('-date')
    elif user_role == 'Seller':
        # Sellers see orders with their email
        orders = Order.objects.filter(seller_email=request.user.email).order_by('-date')
    elif user_role in ['Call Center Manager', 'Call Center Agent']:
        # Call center sees pending and confirmed orders for follow-up
        orders = Order.objects.filter(
            status__in=['pending', 'processing', 'confirmed']
        ).order_by('-date')
    elif user_role == 'Packaging':
        # Packaging team sees orders ready for packaging
        orders = Order.objects.filter(
            status__in=['confirmed', 'processing']
        ).order_by('-date')
    elif user_role == 'Delivery':
        # Delivery team sees orders ready for delivery and in delivery
        orders = Order.objects.filter(
            status__in=['shipped', 'delivered']
        ).order_by('-date')
    else:
        # Other roles see all orders for reference
        orders = Order.objects.all().order_by('-date')
    
    # Filter options
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('q', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Apply filters
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    if search_query:
        orders = orders.filter(
            Q(order_code__icontains=search_query) | 
            Q(customer__icontains=search_query) | 
            Q(customer_phone__icontains=search_query) |
            Q(product__name_en__icontains=search_query)
        )
    
    if date_from:
        orders = orders.filter(date__date__gte=date_from)
    
    if date_to:
        orders = orders.filter(date__date__lte=date_to)
    
    return render(request, 'orders/order_list.html', {
        'orders': orders,
        'status_choices': Order.STATUS_CHOICES,
        'current_status': status_filter,
        'search_query': search_query,
        'date_from': date_from,
        'date_to': date_to,
        'total_orders': orders.count()
    })

@login_required
def order_detail(request, order_id):
    """Detail view for a specific order."""
    order = get_object_or_404(Order, id=order_id)
    
    # Check if user has permission to view this order
    user_role = request.user.primary_role.name if request.user.primary_role else None
    if user_role == 'Seller' and order.seller_email != request.user.email:
        messages.error(request, "You don't have permission to view this order.")
        return redirect('orders:order_list')
    
    # Status update form for authorized users
    status_form = OrderStatusUpdateForm(instance=order) if _can_update_status(request.user, order) else None
    
    return render(request, 'orders/order_detail.html', {
        'order': order,
        'items': order.items.all(),
        'status_form': status_form,
        'can_edit': _can_edit_order(request.user, order),
        'status_history': AuditLog.objects.filter(
            entity_type='Order',
            entity_id=str(order.id),
            action='status_change'
        ).order_by('-timestamp')
    })

@login_required
def create_order(request):
    """View for creating a new order."""
    # Only sellers and admins can create orders
    user_role = request.user.primary_role.name if request.user.primary_role else None
    if user_role not in ['Seller', 'Admin', 'Super Admin', 'Call Center Agent', 'Call Center Manager']:
        messages.error(request, "You don't have permission to create orders.")
        return redirect('orders:order_list')
    
    if request.method == 'POST':
        form = OrderForm(request.POST, user=request.user)
        formset = OrderItemFormSet(request.POST, prefix='items')
        
        if form.is_valid() and formset.is_valid():
            order = form.save(commit=False)
            
            # Set the seller email based on user role
            if user_role == 'Seller':
                order.seller_email = request.user.email
            elif form.cleaned_data.get('seller_email'):
                order.seller_email = form.cleaned_data['seller_email']
            
            # Generate order code if not provided
            if not order.order_code:
                order.order_code = _generate_order_code()
            
            order.save()
            
            # Save order items
            items = formset.save(commit=False)
            total_price = 0
            
            for item in items:
                item.order = order
                item.save()
                total_price += item.quantity * item.price
            
            # Create audit log
            AuditLog.objects.create(
                user=request.user,
                action='create',
                entity_type='Order',
                entity_id=str(order.id),
                description=f"Created new order {order.order_code}"
            )
            
            messages.success(request, f"Order {order.order_code} created successfully!")
            return redirect('orders:order_detail', order_id=order.id)
    else:
        form = OrderForm(user=request.user)
        formset = OrderItemFormSet(prefix='items')
    
    # Get available products
    products = Product.objects.all()
    
    return render(request, 'orders/create_order.html', {
        'form': form,
        'formset': formset,
        'products': products
    })

@login_required
def update_order(request, order_id):
    """View for updating an existing order."""
    order = get_object_or_404(Order, id=order_id)
    
    # Check if user has permission to edit this order
    if not _can_edit_order(request.user, order):
        messages.error(request, "You don't have permission to edit this order.")
        return redirect('orders:order_list')
    
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order, user=request.user)
        formset = OrderItemFormSet(request.POST, instance=order, prefix='items')
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            
            # Recalculate total price
            total_price = sum(item.quantity * item.price for item in order.items.all())
            
            # Create audit log
            AuditLog.objects.create(
                user=request.user,
                action='update',
                entity_type='Order',
                entity_id=str(order.id),
                description=f"Updated order {order.order_code}"
            )
            
            messages.success(request, f"Order {order.order_code} updated successfully!")
            return redirect('orders:order_detail', order_id=order.id)
    else:
        form = OrderForm(instance=order, user=request.user)
        formset = OrderItemFormSet(instance=order, prefix='items')
    
    # Get available products
    products = Product.objects.all()
    
    return render(request, 'orders/update_order.html', {
        'form': form,
        'formset': formset,
        'order': order,
        'products': products
    })

@login_required
def update_order_status(request, order_id):
    """View for updating an order's status."""
    order = get_object_or_404(Order, id=order_id)
    
    # Check if user has permission to update this order's status
    if not _can_update_status(request.user, order):
        messages.error(request, "You don't have permission to update this order's status.")
        return redirect('orders:order_detail', order_id=order.id)
    
    old_status = order.status
    
    if request.method == 'POST':
        form = OrderStatusUpdateForm(request.POST, instance=order)
        
        if form.is_valid():
            # Update order status
            order = form.save()
            
            # Track status change in audit log
            AuditLog.objects.create(
                user=request.user,
                action='status_change',
                entity_type='Order',
                entity_id=str(order.id),
                description=f"Changed order status from {old_status} to {order.status}"
            )
            
            messages.success(request, f"Order {order.order_code} status updated to {order.get_status_display()}!")
            
            # If this is an AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
                
            return redirect('orders:order_detail', order_id=order.id)
    
    # If this is an AJAX request that failed validation
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'errors': form.errors})
        
    return redirect('orders:order_detail', order_id=order.id)

@login_required
def order_dashboard(request):
    """Dashboard with order metrics and charts."""
    # Different users see different metrics
    user_role = request.user.primary_role.name if request.user.primary_role else None
    if user_role == 'Seller':
        orders = Order.objects.filter(seller_email=request.user.email)
    elif user_role in ['Super Admin', 'Admin']:
        orders = Order.objects.all()
    else:
        orders = Order.objects.all()
    
    # Get status counts for charts
    status_counts = {status: orders.filter(status=status_code).count() 
                    for status_code, status in Order.STATUS_CHOICES}
    
    # Get recent orders
    recent_orders = orders.order_by('-date')[:10]
    
    return render(request, 'orders/dashboard.html', {
        'total_orders': orders.count(),
        'status_counts': status_counts,
        'recent_orders': recent_orders,
    })

# Helper functions
def _can_edit_order(user, order):
    """Check if user can edit the order."""
    user_role = user.primary_role.name if user.primary_role else None
    # Super admin and admin can edit any order
    if user_role in ['Super Admin', 'Admin']:
        return True
    
    # Seller can only edit their own orders in certain statuses
    if user_role == 'Seller' and order.seller_email == user.email:
        return order.status in ['pending', 'processing', 'confirmed']
    
    # Call center agents can edit certain order statuses
    if user_role in ['Call Center Manager', 'Call Center Agent']:
        return order.status in ['pending', 'processing', 'confirmed']
    
    return False

def _can_update_status(user, order):
    """Check if user can update the order status."""
    user_role = user.primary_role.name if user.primary_role else None
    # Super admin and admin can update any order status
    if user_role in ['Super Admin', 'Admin']:
        return True
    
    # Seller can update certain statuses of their own orders
    if user_role == 'Seller' and order.seller_email == user.email:
        return order.status in ['pending', 'processing', 'confirmed', 'cancelled']
    
    # Call center can update confirmation statuses
    if user_role in ['Call Center Manager', 'Call Center Agent']:
        return order.status in ['pending', 'processing', 'confirmed']
    
    # Packaging team can update packaging statuses
    if user_role == 'Packaging':
        return order.status in ['confirmed', 'processing', 'shipped']
    
    # Delivery team can update delivery statuses
    if user_role == 'Delivery':
        return order.status in ['shipped', 'delivered', 'returned']
    
    return False

def _generate_order_code():
    """Generate a unique order code."""
    import random
    import string
    from django.utils import timezone
    
    date_part = timezone.now().strftime('%y%m%d')
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    code = f"ORD-{date_part}-{random_part}"
    
    # Ensure code is unique
    while Order.objects.filter(order_code=code).exists():
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        code = f"ORD-{date_part}-{random_part}"
    
    return code

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        # Different users see different sets of orders
        user_role = self.request.user.primary_role.name if self.request.user.primary_role else None
        
        # If user has no role, show all orders (default behavior)
        if not user_role:
            queryset = Order.objects.all().order_by('-date')
        elif user_role in ['Super Admin', 'Admin']:
            queryset = Order.objects.all().order_by('-date')
        elif user_role == 'Seller':
            queryset = Order.objects.filter(seller_email=self.request.user.email).order_by('-date')
        elif user_role in ['Call Center Manager', 'Call Center Agent']:
            # Call center sees pending and confirmed orders for follow-up
            queryset = Order.objects.filter(
                status__in=['pending', 'processing', 'confirmed']
            ).order_by('-date')
        elif user_role == 'Packaging':
            # Packaging team sees orders ready for packaging
            queryset = Order.objects.filter(
                status__in=['confirmed', 'processing']
            ).order_by('-date')
        elif user_role == 'Delivery':
            # Delivery team sees orders ready for delivery and in delivery
            queryset = Order.objects.filter(
                status__in=['shipped', 'delivered']
            ).order_by('-date')
        else:
            # Other roles see all orders for reference
            queryset = Order.objects.all().order_by('-date')

        # Apply filters
        search_query = self.request.GET.get('search')
        status_filter = self.request.GET.get('status')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')

        if search_query:
            queryset = queryset.filter(
                Q(order_code__icontains=search_query) |
                Q(customer__icontains=search_query) |
                Q(customer_phone__icontains=search_query) |
                Q(product__name_en__icontains=search_query)
            )

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        if date_from:
            queryset = queryset.filter(date__date__gte=date_from)

        if date_to:
            queryset = queryset.filter(date__date__lte=date_to)

        return queryset.select_related('product')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Order.STATUS_CHOICES
        
        # Get search parameters for form persistence
        context['search_query'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', '')
        context['date_from'] = self.request.GET.get('date_from', '')
        context['date_to'] = self.request.GET.get('date_to', '')
        
        # Get total count for display
        context['total_orders'] = self.get_queryset().count()
        
        return context

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'

class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'orders/create_order.html'
    success_url = reverse_lazy('orders:list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        order = form.save(commit=False)
        
        # Set the seller email based on user role
        user_role = self.request.user.primary_role.name if self.request.user.primary_role else None
        if user_role == 'Seller':
            order.seller_email = self.request.user.email
        elif form.cleaned_data.get('seller_email'):
            order.seller_email = form.cleaned_data['seller_email']
        
        # Generate order code if not provided
        if not order.order_code:
            order.order_code = _generate_order_code()
        
        order.save()
        
        # Create audit log
        AuditLog.objects.create(
            user=self.request.user,
            action='create',
            entity_type='Order',
            entity_id=str(order.id),
            description=f"Created new order {order.order_code}"
        )
        
        messages.success(self.request, f"Order {order.order_code} created successfully!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get available products
        products = Product.objects.all()
        context['products'] = products
        return context

class OrderUpdateView(LoginRequiredMixin, UpdateView):
    model = Order
    form_class = OrderForm
    template_name = 'orders/order_form.html'
    success_url = reverse_lazy('orders:list')

    def form_valid(self, form):
        messages.success(self.request, 'Order updated successfully.')
        return super().form_valid(form)

@login_required
def download_template(request):
    """Download CSV template for order import."""
    # Create the response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="orders_import_template.csv"'
    
    # Create CSV writer
    writer = csv.writer(response)
    
    # Write header row based on the template format
    writer.writerow([
        'NA',  # Order Code/Number
        'Name',  # Customer Name
        'Mobile number',  # Customer Phone
        'Address',  # Shipping Address
        'Proudact ID',  # Product ID (note: keeping the typo as in template)
        'Quantity',  # Quantity
        'Price',  # Price Per Unit
        'Proudact variant',  # Product variant (note: keeping the typo as in template)
        'Notes',  # Order Notes
        'Date of order'  # Order Date
    ])
    
    # Add a sample row
    writer.writerow([
        'ORD-12345678',  # Order Code
        'John Doe',  # Customer Name
        '+971501234567',  # Mobile number
        'Dubai, UAE',  # Address
        'PROD-001',  # Product ID
        '2',  # Quantity
        '150.00',  # Price
        'Red, Large',  # Product variant
        'Customer requested express delivery',  # Notes
        '2024-01-15'  # Date of order
    ])
    
    return response

@login_required
def import_orders(request):
    """Import orders from CSV file with improved error handling and validation."""
    if request.method == 'POST':
        form = OrderImportForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                file = request.FILES.get('file')
                if not file:
                    messages.error(request, 'No file was uploaded.')
                    return render(request, 'orders/import_orders.html', {'form': form})
                
                # Validate file type
                if not file.name.lower().endswith('.csv'):
                    messages.error(request, 'Please upload a CSV file (.csv extension).')
                    return render(request, 'orders/import_orders.html', {'form': form})
                
                # Check file size (max 5MB) 
                if file.size > 5 * 1024 * 1024:
                    messages.error(request, 'File size must be less than 5MB.')
                    return render(request, 'orders/import_orders.html', {'form': form})
                
                try:
                    # Try UTF-8 first
                    decoded_file = file.read().decode('utf-8')
                except UnicodeDecodeError:
                    # Try with different encoding
                    file.seek(0)  # Reset file pointer
                    try:
                        decoded_file = file.read().decode('latin-1')
                    except UnicodeDecodeError:
                        messages.error(request, 'Unable to read file. Please ensure it is a valid CSV file.')
                        return render(request, 'orders/import_orders.html', {'form': form})
                
                csv_data = csv.reader(io.StringIO(decoded_file))
                
                # Validate header row
                try:
                    header = next(csv_data)
                    if len(header) < 5:  # Minimum required columns
                        messages.error(request, 'CSV file must have at least 5 columns: Order Code, Customer Name, Product ID, Quantity, Price.')
                        return render(request, 'orders/import_orders.html', {'form': form})
                except StopIteration:
                    messages.error(request, 'CSV file is empty or invalid.')
                    return render(request, 'orders/import_orders.html', {'form': form})
                
                success_count = 0
                error_count = 0
                errors = []
                
                for row_num, row in enumerate(csv_data, start=2):  # Start from 2 because we skipped header
                    try:
                        # Skip empty rows
                        if not row or all(cell.strip() == '' for cell in row):
                            continue
                        
                        # Ensure we have minimum required data
                        if len(row) < 5:
                            errors.append(f"Row {row_num}: Insufficient columns (need at least 5)")
                            error_count += 1
                            continue
                        
                        # Parse row data with better validation
                        order_code = row[0].strip() if len(row) > 0 and row[0] else None
                        customer_name = row[1].strip() if len(row) > 1 and row[1] else 'Unknown Customer'
                        mobile_number = row[2].strip() if len(row) > 2 and row[2] else ''
                        address = row[3].strip() if len(row) > 3 and row[3] else ''
                        product_id = row[4].strip() if len(row) > 4 and row[4] else None
                        # Parse quantity
                        try:
                            quantity = int(row[5]) if len(row) > 5 and row[5] and row[5].strip() else 1
                        except ValueError:
                            quantity = 1
                        
                        # Parse price
                        try:
                            price = float(row[6]) if len(row) > 6 and row[6] and row[6].strip() else 0.0
                        except ValueError:
                            price = 0.0
                        product_variant = row[7].strip() if len(row) > 7 and row[7] else ''
                        notes = row[8].strip() if len(row) > 8 and row[8] else ''
                        order_date_str = row[9].strip() if len(row) > 9 and row[9] else ''
                        
                        # Validate required fields
                        if not customer_name or customer_name == 'Unknown Customer':
                            errors.append(f"Row {row_num}: Customer name is required")
                            error_count += 1
                            continue
                        
                        if quantity <= 0:
                            errors.append(f"Row {row_num}: Quantity must be greater than 0")
                            error_count += 1
                            continue
                        
                        if price < 0:
                            errors.append(f"Row {row_num}: Price cannot be negative")
                            error_count += 1
                            continue
                        
                        # Parse order date
                        try:
                            if order_date_str:
                                order_date = datetime.strptime(order_date_str, '%Y-%m-%d')
                            else:
                                order_date = timezone.now()
                        except ValueError:
                            order_date = timezone.now()
                        
                        # Find product by ID or name
                        product = None
                        if product_id:
                            try:
                                product = Product.objects.get(code=product_id)
                            except Product.DoesNotExist:
                                # Try to find by name if code doesn't exist
                                product = Product.objects.filter(name_en__icontains=product_id).first()
                        
                        # Check if order already exists
                        if order_code and Order.objects.filter(order_code=order_code).exists():
                            errors.append(f"Row {row_num}: Order code '{order_code}' already exists")
                            error_count += 1
                            continue
                        
                        # Create order
                        order = Order.objects.create(
                            order_code=order_code or _generate_order_code(),
                            customer=customer_name,
                            customer_phone=mobile_number,
                            shipping_address=address,
                            product=product,
                            quantity=quantity,
                            price_per_unit=price,
                            notes=notes,
                            date=order_date,
                            status='pending',
                            seller_email=request.user.email  # Set seller email to current user
                        )
                        
                        success_count += 1
                        
                        # Create audit log
                        AuditLog.objects.create(
                            user=request.user,
                            action='import',
                            entity_type='Order',
                            entity_id=str(order.id),
                            description=f"Imported order {order.order_code} from CSV"
                        )
                        
                    except Exception as e:
                        errors.append(f"Row {row_num}: {str(e)}")
                        error_count += 1
                
                # Show results
                if success_count > 0:
                    messages.success(request, f'Successfully imported {success_count} orders.')
                if error_count > 0:
                    messages.warning(request, f'Failed to import {error_count} orders. Check the errors below.')
                    for error in errors[:10]:  # Show first 10 errors
                        messages.error(request, error)
                    if len(errors) > 10:
                        messages.error(request, f'... and {len(errors) - 10} more errors.')
                
                return redirect('orders:list')
                
            except Exception as e:
                messages.error(request, f'Error processing file: {str(e)}')
                print(f"Import error: {e}")
        else:
            messages.error(request, 'Please correct the errors below.')
            print(f"Form errors: {form.errors}")
    else:
        form = OrderImportForm()
    
    return render(request, 'orders/import_orders.html', {'form': form})
