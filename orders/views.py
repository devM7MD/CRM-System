from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
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

@login_required
def order_list(request):
    """View for listing all orders based on user role."""
    # Different users see different sets of orders
    if request.user.role == 'super_admin' or request.user.role == 'admin':
        orders = Order.objects.all().order_by('-created_at')
    elif request.user.role == 'seller':
        orders = Order.objects.filter(seller=request.user).order_by('-created_at')
    elif request.user.role in ['call_center_manager', 'call_center_agent']:
        # Call center sees pending and confirmed orders for follow-up
        orders = Order.objects.filter(
            status__in=['pending', 'confirmed', 'no_response', 'postponed']
        ).order_by('-created_at')
    elif request.user.role == 'packaging':
        # Packaging team sees orders ready for packaging
        orders = Order.objects.filter(
            status__in=['ready_for_packaging', 'packaging_in_progress']
        ).order_by('-created_at')
    elif request.user.role == 'delivery':
        # Delivery team sees orders ready for delivery and in delivery
        orders = Order.objects.filter(
            status__in=['ready_for_delivery', 'in_delivery', 'delivered', 'returned']
        ).order_by('-created_at')
    else:
        # Other roles see all orders for reference
        orders = Order.objects.all().order_by('-created_at')
    
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
            Q(code__icontains=search_query) | 
            Q(customer_name__icontains=search_query) | 
            Q(customer_phone__icontains=search_query)
        )
    
    return render(request, 'orders/order_list.html', {
        'orders': orders,
        'status_choices': Order.STATUS_CHOICES,
        'current_status': status_filter,
        'search_query': search_query
    })

@login_required
def order_detail(request, order_id):
    """Detail view for a specific order."""
    order = get_object_or_404(Order, id=order_id)
    
    # Check if user has permission to view this order
    if request.user.role == 'seller' and order.seller != request.user:
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
    if request.user.role not in ['seller', 'admin', 'super_admin', 'call_center_agent', 'call_center_manager']:
        messages.error(request, "You don't have permission to create orders.")
        return redirect('orders:order_list')
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        formset = OrderItemFormSet(request.POST, prefix='items')
        
        if form.is_valid() and formset.is_valid():
            order = form.save(commit=False)
            
            # Set the seller based on user role
            if request.user.role == 'seller':
                order.seller = request.user
            elif 'seller' in request.POST and request.user.role in ['admin', 'super_admin', 'call_center_agent', 'call_center_manager']:
                order.seller = User.objects.get(id=request.POST['seller'])
            
            # Generate order code
            order.code = _generate_order_code()
            order.save()
            
            # Save order items
            items = formset.save(commit=False)
            total_price = 0
            
            for item in items:
                item.order = order
                item.save()
                total_price += item.quantity * item.price
            
            # Update total price
            order.total_price = total_price
            order.save()
            
            # Create audit log
            AuditLog.objects.create(
                user=request.user,
                action='create',
                entity_type='Order',
                entity_id=str(order.id),
                description=f"Created new order {order.code}"
            )
            
            messages.success(request, f"Order {order.code} created successfully!")
            return redirect('orders:order_detail', order_id=order.id)
    else:
        form = OrderForm()
        formset = OrderItemFormSet(prefix='items')
    
    # Get available products based on user role
    if request.user.role == 'seller':
        products = Product.objects.filter(seller=request.user)
        sellers = None
    else:
        products = Product.objects.all()
        sellers = User.objects.filter(role='seller')
    
    return render(request, 'orders/create_order.html', {
        'form': form,
        'formset': formset,
        'products': products,
        'sellers': sellers
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
        form = OrderForm(request.POST, instance=order)
        formset = OrderItemFormSet(request.POST, instance=order, prefix='items')
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            
            # Recalculate total price
            total_price = sum(item.quantity * item.price for item in order.items.all())
            order.total_price = total_price
            order.save()
            
            # Create audit log
            AuditLog.objects.create(
                user=request.user,
                action='update',
                entity_type='Order',
                entity_id=str(order.id),
                description=f"Updated order {order.code}"
            )
            
            messages.success(request, f"Order {order.code} updated successfully!")
            return redirect('orders:order_detail', order_id=order.id)
    else:
        form = OrderForm(instance=order)
        formset = OrderItemFormSet(instance=order, prefix='items')
    
    # Get available products based on user role
    if request.user.role == 'seller':
        products = Product.objects.filter(seller=request.user)
    else:
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
            
            # Add tracking number if provided (for delivery status)
            if 'tracking_number' in request.POST and request.POST['tracking_number'].strip():
                order.tracking_number = request.POST['tracking_number']
                
                # Set delivery company if provided
                if 'delivery_company' in request.POST and request.POST['delivery_company']:
                    order.delivery_company = DeliveryCompany.objects.get(id=request.POST['delivery_company'])
                
                # Set delivery date for 'delivered' status
                if order.status == 'delivered':
                    order.delivery_date = timezone.now()
                
                order.save()
            
            messages.success(request, f"Order {order.code} status updated to {order.get_status_display()}!")
            
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
    if request.user.role == 'seller':
        orders = Order.objects.filter(seller=request.user)
    elif request.user.role in ['super_admin', 'admin']:
        orders = Order.objects.all()
    else:
        orders = Order.objects.all()
    
    # Get status counts for charts
    status_counts = {status: orders.filter(status=status_code).count() 
                    for status_code, status in Order.STATUS_CHOICES}
    
    # Get recent orders
    recent_orders = orders.order_by('-created_at')[:10]
    
    return render(request, 'orders/dashboard.html', {
        'total_orders': orders.count(),
        'status_counts': status_counts,
        'recent_orders': recent_orders,
    })

# Helper functions
def _can_edit_order(user, order):
    """Check if user can edit the order."""
    # Super admin and admin can edit any order
    if user.role in ['super_admin', 'admin']:
        return True
    
    # Seller can only edit their own orders in certain statuses
    if user.role == 'seller' and order.seller == user:
        return order.status in ['pending', 'confirmed', 'no_response', 'postponed']
    
    # Call center agents can edit certain order statuses
    if user.role in ['call_center_manager', 'call_center_agent']:
        return order.status in ['pending', 'confirmed', 'no_response', 'postponed']
    
    return False

def _can_update_status(user, order):
    """Check if user can update the order status."""
    # Super admin and admin can update any order status
    if user.role in ['super_admin', 'admin']:
        return True
    
    # Seller can update certain statuses of their own orders
    if user.role == 'seller' and order.seller == user:
        return order.status in ['pending', 'confirmed', 'no_response', 'postponed', 'under_review', 'cancelled']
    
    # Call center can update confirmation statuses
    if user.role in ['call_center_manager', 'call_center_agent']:
        return order.status in ['pending', 'confirmed', 'no_response', 'postponed']
    
    # Packaging team can update packaging statuses
    if user.role == 'packaging':
        return order.status in ['ready_for_packaging', 'packaging_in_progress', 'ready_for_delivery']
    
    # Delivery team can update delivery statuses
    if user.role == 'delivery':
        return order.status in ['ready_for_delivery', 'in_delivery', 'delivered', 'returned']
    
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
    while Order.objects.filter(code=code).exists():
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        code = f"ORD-{date_part}-{random_part}"
    
    return code

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        queryset = Order.objects.all()
        search_query = self.request.GET.get('search')
        status_filter = self.request.GET.get('status')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        seller_filter = self.request.GET.get('seller')

        if search_query:
            queryset = queryset.filter(
                Q(order_code__icontains=search_query) |
                Q(customer__first_name__icontains=search_query) |
                Q(customer__last_name__icontains=search_query) |
                Q(product__name__icontains=search_query)
            )

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        if date_from:
            queryset = queryset.filter(date__gte=date_from)

        if date_to:
            queryset = queryset.filter(date__lte=date_to)

        if seller_filter:
            queryset = queryset.filter(seller_id=seller_filter)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Order.STATUS_CHOICES
        context['sellers'] = Order.objects.values_list('seller', flat=True).distinct()
        return context

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'

class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'orders/order_form.html'
    success_url = reverse_lazy('orders:list')

    def form_valid(self, form):
        messages.success(self.request, 'Order created successfully.')
        return super().form_valid(form)

class OrderUpdateView(LoginRequiredMixin, UpdateView):
    model = Order
    form_class = OrderForm
    template_name = 'orders/order_form.html'
    success_url = reverse_lazy('orders:list')

    def form_valid(self, form):
        messages.success(self.request, 'Order updated successfully.')
        return super().form_valid(form)

def import_orders(request):
    if request.method == 'POST':
        form = OrderImportForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Orders imported successfully.')
                return redirect('orders:list')
            except Exception as e:
                messages.error(request, f'Error importing orders: {str(e)}')
    else:
        form = OrderImportForm()
    
    return render(request, 'orders/import_orders.html', {'form': form})
