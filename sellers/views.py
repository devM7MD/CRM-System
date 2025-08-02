from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from sellers.models import Product, SalesChannel
from orders.models import Order
from users.models import User
from django.http import JsonResponse

def has_seller_role(user):
    return (
        user.is_superuser or
        user.has_role('Super Admin') or
        user.has_role('Seller')
    )

@login_required
def dashboard(request):
    """Seller dashboard with real data from database."""
    if not has_seller_role(request.user):
        messages.error(request, "ليس لديك صلاحية للدخول لهذه الصفحة.")
        return redirect('dashboard:index')
    
    from django.db.models import Sum, Count, Q
    from django.utils import timezone
    from datetime import timedelta
    from orders.models import Order
    from sellers.models import Product
    from sourcing.models import SourcingRequest
    
    # Get real data for the current user (seller)
    all_orders = Order.objects.all()  # All orders in the system
    all_products = Product.objects.filter(seller=request.user)
    
    # Calculate order statistics
    orders_count = all_orders.count()
    completed_orders = all_orders.filter(status='confirmed').count()
    processing_orders = all_orders.filter(status__in=['pending', 'pending_confirmation']).count()
    cancelled_orders = all_orders.filter(status='cancelled').count()
    
    # Calculate inventory statistics
    total_inventory = all_products.count()
    available_inventory = all_products.filter(stock__gt=0).count()
    in_delivery_inventory = all_products.filter(stock=0).count()
    
    # Calculate sales data - sum of all order totals
    total_sales_amount = sum(order.total_price for order in all_orders)
    
    # Get sourcing requests
    sourcing_requests = SourcingRequest.objects.filter(seller=request.user)
    sourcing_requests_count = sourcing_requests.count()
    pending_requests = sourcing_requests.filter(status='pending').count()
    approved_requests = sourcing_requests.filter(status='approved').count()
    
    # Get recent orders and products
    recent_orders = all_orders.order_by('-date')[:5]
    products = all_products.order_by('-created_at')[:5]
    
    # Prepare sales performance data for chart (last 6 months)
    sales_data = []
    months = []
    for i in range(6):
        month_date = timezone.now() - timedelta(days=30*i)
        month_orders = all_orders.filter(
            date__year=month_date.year,
            date__month=month_date.month
        )
        month_sales = sum(order.total_price for order in month_orders)
        sales_data.append(float(month_sales))
        months.append(month_date.strftime('%b'))
    
    # Prepare top products data for chart
    top_products = all_products.annotate(
        order_count=Count('orders')
    ).order_by('-order_count')[:5]
    
    product_names = [product.name_en for product in top_products]
    product_sales = [product.order_count for product in top_products]
    
    return render(request, 'sellers/dashboard.html', {
        'products': products,
        'recent_orders': recent_orders,
        'total_inventory': total_inventory,
        'available_inventory': available_inventory,
        'in_delivery_inventory': in_delivery_inventory,
        'orders_count': orders_count,
        'completed_orders': completed_orders,
        'processing_orders': processing_orders,
        'cancelled_orders': cancelled_orders,
        'total_sales': f"AED {total_sales_amount:,.0f}",
        'sourcing_requests_count': sourcing_requests_count,
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
        'sales_data': sales_data,
        'months': months,
        'product_names': product_names,
        'product_sales': product_sales,
    })

@login_required
def product_list(request):
    """List all products for the seller."""
    if not has_seller_role(request.user):
        messages.error(request, "ليس لديك صلاحية للدخول لهذه الصفحة.")
        return redirect('dashboard:index')
    if request.user.has_role('Seller'):
        products = Product.objects.filter(seller=request.user).order_by('-created_at')
    else:
        products = Product.objects.all().order_by('-created_at')
        
    return render(request, 'sellers/products.html', {
        'products': products,
    })

@login_required
def product_create(request):
    """Create a new product."""
    if not has_seller_role(request.user):
        messages.error(request, "ليس لديك صلاحية للدخول لهذه الصفحة.")
        return redirect('dashboard:index')
    if request.method == 'POST':
        # Process form data
        name_en = request.POST.get('name')
        name_ar = request.POST.get('name_ar')
        code = request.POST.get('code')
        description = request.POST.get('description', '')
        selling_price = request.POST.get('selling_price')
        purchase_price = request.POST.get('cost_price', None)
        product_link = request.POST.get('product_link', '')
        
        # Validate required fields
        if not all([name_en, code, selling_price]):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Please fill in all required fields.'})
            messages.error(request, "Please fill in all required fields.")
            return render(request, 'sellers/product_create.html')
        
        try:
            # Create product object
            product = Product(
                name_en=name_en,
                name_ar=name_ar,
                code=code,
                description=description,
                selling_price=selling_price,
                purchase_price=purchase_price,
                product_link=product_link,
                seller=request.user
            )
            
            # Handle image upload
            if 'image' in request.FILES:
                product.image = request.FILES['image']
            
            product.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': f'Product {name_en} created successfully.'})
            
            messages.success(request, f"Product {name_en} created successfully.")
            return redirect('sellers:products')
            
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': f'Error creating product: {str(e)}'})
            messages.error(request, f"Error creating product: {str(e)}")
    
    # For GET requests, redirect to dashboard since we're using modal
    return redirect('sellers:dashboard')

@login_required
def product_detail(request, product_id):
    """View a specific product."""
    if not has_seller_role(request.user):
        messages.error(request, "ليس لديك صلاحية للدخول لهذه الصفحة.")
        return redirect('dashboard:index')
    product = get_object_or_404(Product, id=product_id)
    
    # Check permissions
    user_role = request.user.primary_role.name if request.user.primary_role else None
    if user_role == 'Seller' and product.seller != request.user:
        messages.error(request, "You don't have permission to view this product.")
        return redirect('sellers:products')
        
    return render(request, 'sellers/product_detail.html', {
        'product': product,
    })

@login_required
def product_edit(request, product_id):
    """Edit a specific product."""
    if not has_seller_role(request.user):
        messages.error(request, "ليس لديك صلاحية للدخول لهذه الصفحة.")
        return redirect('dashboard:index')
    product = get_object_or_404(Product, id=product_id)
    
    # Check permissions
    user_role = request.user.primary_role.name if request.user.primary_role else None
    if user_role == 'Seller' and product.seller != request.user:
        messages.error(request, "You don't have permission to edit this product.")
        return redirect('sellers:products')
    
    if request.method == 'POST':
        # Update product data
        product.name_en = request.POST.get('name', product.name_en)
        product.name_ar = request.POST.get('name_ar', product.name_ar)
        product.description = request.POST.get('description', product.description)
        product.selling_price = request.POST.get('selling_price', product.selling_price)
        product.purchase_price = request.POST.get('purchase_price') or None
        product.product_link = request.POST.get('product_link', product.product_link)
        
        # Handle image upload
        if 'image' in request.FILES:
            product.image = request.FILES['image']
        
        product.save()
        messages.success(request, f'Product "{product.name_en}" updated successfully.')
        return redirect('sellers:product_detail', product_id=product.id)
        
    return render(request, 'sellers/product_edit.html', {
        'product': product,
    })

@login_required
def product_delete(request, product_id):
    """Delete a specific product."""
    if not has_seller_role(request.user):
        messages.error(request, "ليس لديك صلاحية للدخول لهذه الصفحة.")
        return redirect('dashboard:index')
    product = get_object_or_404(Product, id=product_id)
    
    # Check permissions
    user_role = request.user.primary_role.name if request.user.primary_role else None
    if user_role == 'Seller' and product.seller != request.user:
        messages.error(request, "You don't have permission to delete this product.")
        return redirect('sellers:products')
    
    if request.method == 'POST':
        product_name = product.name_en
        product.delete()
        messages.success(request, f'Product "{product_name}" deleted successfully.')
        return redirect('sellers:products')
    
    # If GET request, show confirmation page
    return render(request, 'sellers/product_delete_confirm.html', {
        'product': product,
    })

@login_required
def order_list(request):
    """List orders for the seller."""
    if not has_seller_role(request.user):
        messages.error(request, "ليس لديك صلاحية للدخول لهذه الصفحة.")
        return redirect('dashboard:index')
    
    # Get all orders - sellers can see all orders in the system
    # In a real system, you might want to filter by seller-specific logic
    orders = Order.objects.all().order_by('-date')
    
    # Apply search filter if provided
    search_query = request.GET.get('search', '')
    if search_query:
        orders = orders.filter(
            Q(order_code__icontains=search_query) |
            Q(customer__icontains=search_query) |
            Q(product__name_en__icontains=search_query) |
            Q(product__name_ar__icontains=search_query)
        )
    
    # Apply status filter if provided
    status_filter = request.GET.get('status', '')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(orders, 20)  # Show 20 orders per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get order statistics
    total_orders = orders.count()
    pending_orders = orders.filter(status='pending').count()
    confirmed_orders = orders.filter(status='confirmed').count()
    cancelled_orders = orders.filter(status='cancelled').count()
    
    return render(request, 'sellers/orders.html', {
        'page_obj': page_obj,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'confirmed_orders': confirmed_orders,
        'cancelled_orders': cancelled_orders,
        'search_query': search_query,
        'status_filter': status_filter,
    })

@login_required
def order_detail(request, order_id):
    """View a specific order."""
    if not has_seller_role(request.user):
        messages.error(request, "ليس لديك صلاحية للدخول لهذه الصفحة.")
        return redirect('dashboard:index')
    order = get_object_or_404(Order, id=order_id)
    
    # Check permissions
    user_role = request.user.primary_role.name if request.user.primary_role else None
    if user_role == 'Seller' and order.seller != request.user:
        messages.error(request, "You don't have permission to view this order.")
        return redirect('sellers:orders')
        
    return render(request, 'sellers/order_detail.html', {
        'order': order,
    })

@login_required
def sourcing_request_list(request):
    """List sourcing requests."""
    if not has_seller_role(request.user):
        messages.error(request, "ليس لديك صلاحية للدخول لهذه الصفحة.")
        return redirect('dashboard:index')
    # Check if user has Seller role or is Super Admin
    if not (request.user.has_role('Seller') or request.user.is_superuser or request.user.has_role('Super Admin')):
        messages.error(request, "You don't have permission to access this page.")
        return redirect('dashboard:index')
    
    # Import sourcing models
    from sourcing.models import SourcingRequest
    
    # Get sourcing requests for the current user
    sourcing_requests = SourcingRequest.objects.filter(seller=request.user).order_by('-created_at')
    
    return render(request, 'sellers/sourcing_requests.html', {
        'sourcing_requests': sourcing_requests,
    })

@login_required
def sourcing_request_create(request):
    """Create a new sourcing request."""
    if not has_seller_role(request.user):
        messages.error(request, "ليس لديك صلاحية للدخول لهذه الصفحة.")
        return redirect('dashboard:index')
    if request.method == 'POST':
        # Handle AJAX form submission
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            from sourcing.models import SourcingRequest
            from django.utils import timezone
            
            try:
                # Create sourcing request
                sourcing_request = SourcingRequest.objects.create(
                    seller=request.user,
                    product_name=request.POST.get('new_product_name') or 'Product Request',
                    carton_quantity=int(request.POST.get('carton_quantity', 1)),
                    source_country=request.POST.get('source_country', 'China'),
                    destination_country=request.POST.get('destination_country', 'UAE'),
                    finance_source=request.POST.get('finance_source', 'self_financed'),
                    priority=request.POST.get('priority', 'medium'),
                    status='submitted',
                    notes=request.POST.get('notes', ''),
                    submitted_at=timezone.now()
                )
                
                return JsonResponse({
                    'success': True,
                    'message': 'Sourcing request created successfully!',
                    'request_id': sourcing_request.id
                })
                
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                })
        
        # Handle regular form submission (fallback)
        return redirect('sellers:sourcing_requests')
    
    # GET request - show form page (for non-JS users)
    products = Product.objects.filter(seller=request.user).order_by('-created_at')
    
    return render(request, 'sellers/sourcing_request_create.html', {
        'products': products,
    })

@login_required
def sourcing_request_detail(request, request_id):
    """View a specific sourcing request."""
    if not has_seller_role(request.user):
        messages.error(request, "ليس لديك صلاحية للدخول لهذه الصفحة.")
        return redirect('dashboard:index')
    # Check if user has Seller role or is Super Admin
    if not (request.user.has_role('Seller') or request.user.is_superuser or request.user.has_role('Super Admin')):
        messages.error(request, "You don't have permission to access this page.")
        return redirect('dashboard:index')
    
    from sourcing.models import SourcingRequest
    from django.shortcuts import get_object_or_404
    
    sourcing_request = get_object_or_404(SourcingRequest, id=request_id, seller=request.user)
    
    return render(request, 'sellers/sourcing_request_detail.html', {
        'sourcing_request': sourcing_request,
    })

@login_required
def sales(request):
    """Seller sales overview and analytics."""
    if not has_seller_role(request.user):
        messages.error(request, "ليس لديك صلاحية للدخول لهذه الصفحة.")
        return redirect('dashboard:index')
    # Check if user has Seller role or is Super Admin
    if not (request.user.has_role('Seller') or request.user.is_superuser or request.user.has_role('Super Admin')):
        messages.error(request, "You don't have permission to access this page.")
        return redirect('dashboard:index')
    
    from django.db.models import Sum, Count, Avg
    from django.utils import timezone
    from datetime import datetime, timedelta
    import calendar
    
    # Get seller instance
    seller_instance = getattr(request.user, 'seller_profile', None)
    
    if seller_instance:
        # Get all orders for this seller
        all_orders = Order.objects.filter(seller=seller_instance)
        
        # Calculate total sales
        total_sales = all_orders.aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        # Calculate monthly sales (current month)
        current_month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_sales = all_orders.filter(
            date__gte=current_month_start
        ).aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        # Calculate weekly sales (current week)
        current_week_start = timezone.now() - timedelta(days=timezone.now().weekday())
        current_week_start = current_week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        weekly_sales = all_orders.filter(
            date__gte=current_week_start
        ).aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        # Calculate daily sales (today)
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        daily_sales = all_orders.filter(
            date__gte=today_start
        ).aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        # Calculate sales by month for the last 6 months
        sales_by_period = {}
        for i in range(6):
            month_date = timezone.now() - timedelta(days=30*i)
            month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if i > 0:
                month_end = month_start + timedelta(days=32)
                month_end = month_end.replace(day=1) - timedelta(days=1)
            else:
                month_end = timezone.now()
            
            month_sales = all_orders.filter(
                date__gte=month_start,
                date__lte=month_end
            ).aggregate(
                total=Sum('total_amount')
            )['total'] or 0
            
            month_name = month_start.strftime('%b')
            sales_by_period[month_name] = month_sales
        
        # Get top selling products
        top_products = []
        products = Product.objects.filter(seller=request.user)
        
        for product in products:
            product_orders = all_orders.filter(product=product)
            sales_volume = product_orders.count()
            revenue = product_orders.aggregate(
                total=Sum('total_amount')
            )['total'] or 0
            
            if sales_volume > 0:
                # Calculate growth (simple comparison with previous period)
                previous_period_start = timezone.now() - timedelta(days=60)
                previous_period_end = timezone.now() - timedelta(days=30)
                current_period_start = timezone.now() - timedelta(days=30)
                
                previous_sales = product_orders.filter(
                    date__gte=previous_period_start,
                    date__lte=previous_period_end
                ).count()
                
                current_sales = product_orders.filter(
                    date__gte=current_period_start
                ).count()
                
                if previous_sales > 0:
                    growth = ((current_sales - previous_sales) / previous_sales) * 100
                else:
                    growth = 100 if current_sales > 0 else 0
                
                top_products.append({
                    'name': product.name_en or product.name_ar or 'Unnamed Product',
                    'sku': product.code,
                    'image': product.image,
                    'sales_volume': sales_volume,
                    'revenue': f"AED {revenue:,.0f}",
                    'growth': round(growth, 1)
                })
        
        # Sort by sales volume and take top 5
        top_products.sort(key=lambda x: x['sales_volume'], reverse=True)
        top_products = top_products[:5]
        
    else:
        # No seller profile, return empty data
        total_sales = 0
        monthly_sales = 0
        weekly_sales = 0
        daily_sales = 0
        sales_by_period = {
            'Jan': 0, 'Feb': 0, 'Mar': 0, 'Apr': 0, 'May': 0, 'Jun': 0
        }
        top_products = []
    
    # Format currency values
    context = {
        'total_sales': f"AED {total_sales:,.0f}",
        'monthly_sales': f"AED {monthly_sales:,.0f}",
        'weekly_sales': f"AED {weekly_sales:,.0f}",
        'daily_sales': f"AED {daily_sales:,.0f}",
        'sales_by_period': sales_by_period,
        'top_products': top_products,
    }
    
    return render(request, 'sellers/sales.html', context)

@login_required
def inventory(request):
    """Show inventory management page for seller products."""
    if not has_seller_role(request.user):
        messages.error(request, "ليس لديك صلاحية للدخول لهذه الصفحة.")
        return redirect('dashboard:index')
    # Handle export request
    if request.GET.get('export') == 'csv':
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="inventory_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Product Name', 'SKU', 'Description', 'Available Quantity', 'Total Quantity', 'Selling Price', 'Purchase Price', 'Product Link', 'Status', 'Created Date'])
        
        seller_instance = getattr(request.user, 'seller_profile', None)
        if seller_instance:
            products = Product.objects.filter(seller=request.user).order_by('-created_at')
        else:
            products = Product.objects.all().order_by('-created_at')
        
        for product in products:
            writer.writerow([
                product.name_en or product.name_ar or 'Unnamed Product',
                product.code,
                product.description[:100] + '...' if len(product.description) > 100 else product.description,
                product.available_quantity,
                product.total_quantity,
                product.selling_price,
                product.purchase_price or 'N/A',
                product.product_link or 'N/A',
                'In Stock' if product.available_quantity > 0 else 'Out of Stock',
                product.created_at.strftime('%Y-%m-%d')
            ])
        
        return response
    
    # Get all products with inventory information
    seller_instance = getattr(request.user, 'seller_profile', None)
    if seller_instance:
        products = Product.objects.filter(seller=request.user).order_by('-created_at')
    else:
        products = Product.objects.all().order_by('-created_at')
    
    # Calculate inventory statistics
    total_inventory = sum(product.total_quantity for product in products)
    available_inventory = sum(product.available_quantity for product in products)
    in_delivery_inventory = total_inventory - available_inventory
    
    return render(request, 'sellers/inventory.html', {
        'products': products,
        'total_inventory': total_inventory,
        'available_inventory': available_inventory,
        'in_delivery_inventory': in_delivery_inventory,
    })
