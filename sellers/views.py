from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, SalesChannel
from orders.models import Order
from users.models import User

@login_required
def dashboard(request):
    """Seller dashboard with stats and recent data."""
    # Only allow sellers to access this page
    if request.user.role != 'seller' and request.user.role not in ['admin', 'super_admin']:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('dashboard:index')
    
    # Get recent products
    if request.user.role == 'seller':
        products = Product.objects.filter(seller=request.user).order_by('-created_at')[:5]
        # Get all orders first, then calculate stats, then get recent ones
        all_orders = Order.objects.filter(seller=request.user).order_by('-date')
    else:
        products = Product.objects.all().order_by('-created_at')[:5]
        all_orders = Order.objects.all().order_by('-date')
    
    # Order statistics - using all_orders instead of recent_orders for stats
    order_stats = {
        'total': all_orders.count(),
        'pending': all_orders.filter(status='pending').count(),
        'delivered': all_orders.filter(status='delivered').count(),
        'cancelled': all_orders.filter(status='cancelled').count(),
    }
    
    # Get recent orders for display
    recent_orders = all_orders[:5]
    
    # Calculate inventory statistics for the dashboard
    if request.user.role == 'seller':
        all_products = Product.objects.filter(seller=request.user)
    else:
        all_products = Product.objects.all()
        
    total_inventory = sum(product.total_quantity for product in all_products)
    available_inventory = sum(product.available_quantity for product in all_products)
    in_delivery_inventory = total_inventory - available_inventory
    
    return render(request, 'sellers/dashboard.html', {
        'products': products,
        'recent_orders': recent_orders,
        'order_stats': order_stats,
        'total_inventory': total_inventory,
        'available_inventory': available_inventory,
        'in_delivery_inventory': in_delivery_inventory,
    })

@login_required
def product_list(request):
    """List all products for the seller."""
    if request.user.role == 'seller':
        products = Product.objects.filter(seller=request.user).order_by('-created_at')
    else:
        products = Product.objects.all().order_by('-created_at')
        
    return render(request, 'sellers/products.html', {
        'products': products,
    })

@login_required
def product_create(request):
    """Create a new product."""
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
            messages.success(request, f"Product {name_en} created successfully.")
            return redirect('sellers:products')
            
        except Exception as e:
            messages.error(request, f"Error creating product: {str(e)}")
    
    return render(request, 'sellers/product_create.html')

@login_required
def product_detail(request, product_id):
    """View a specific product."""
    product = get_object_or_404(Product, id=product_id)
    
    # Check permissions
    if request.user.role == 'seller' and product.seller != request.user:
        messages.error(request, "You don't have permission to view this product.")
        return redirect('sellers:products')
        
    return render(request, 'sellers/product_detail.html', {
        'product': product,
    })

@login_required
def product_edit(request, product_id):
    """Edit a specific product."""
    product = get_object_or_404(Product, id=product_id)
    
    # Check permissions
    if request.user.role == 'seller' and product.seller != request.user:
        messages.error(request, "You don't have permission to edit this product.")
        return redirect('sellers:products')
        
    return render(request, 'sellers/product_edit.html', {
        'product': product,
    })

@login_required
def order_list(request):
    """List orders for the seller."""
    if request.user.role == 'seller':
        orders = Order.objects.filter(seller=request.user).order_by('-date')
    else:
        orders = Order.objects.all().order_by('-date')
        
    return render(request, 'sellers/orders.html', {
        'orders': orders,
    })

@login_required
def order_detail(request, order_id):
    """View a specific order."""
    order = get_object_or_404(Order, id=order_id)
    
    # Check permissions
    if request.user.role == 'seller' and order.seller != request.user:
        messages.error(request, "You don't have permission to view this order.")
        return redirect('sellers:orders')
        
    return render(request, 'sellers/order_detail.html', {
        'order': order,
    })

@login_required
def sourcing_request_list(request):
    """List sourcing requests."""
    # Placeholder implementation
    return render(request, 'sellers/sourcing_requests.html')

@login_required
def sourcing_request_create(request):
    """Create a new sourcing request."""
    # Placeholder implementation
    return render(request, 'sellers/sourcing_request_create.html')

@login_required
def sourcing_request_detail(request, request_id):
    """View a specific sourcing request."""
    # Placeholder implementation
    return render(request, 'sellers/sourcing_request_detail.html', {
        'request_id': request_id,
    })

@login_required
def sales(request):
    """Seller sales overview and analytics."""
    # Only allow sellers to access this page
    if request.user.role != 'seller' and request.user.role not in ['admin', 'super_admin']:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('dashboard:index')
    
    # Get sales data for the seller
    # This is a placeholder view until we have actual sales data
    return render(request, 'sellers/sales.html', {
        'total_sales': "AED 42,651",  # Placeholder
        'monthly_sales': "AED 12,435",  # Placeholder
        'weekly_sales': "AED 3,245",  # Placeholder
        'daily_sales': "AED 432",  # Placeholder
        'sales_by_period': {
            'Jan': 2345,
            'Feb': 3456,
            'Mar': 4567,
            'Apr': 3456,
            'May': 5432,
            'Jun': 6789,
        },
        'top_products': [],  # Placeholder
    })

@login_required
def inventory(request):
    """Show inventory management page for seller products."""
    # Only allow sellers to access this page
    if request.user.role != 'seller' and request.user.role not in ['admin', 'super_admin']:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('dashboard:index')
    
    # Get all products with inventory information
    if request.user.role == 'seller':
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
