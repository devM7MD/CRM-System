from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, SalesChannel, Seller
from orders.models import Order
from users.models import User
from django.db.models import Sum, Count, Q, Case, When, Value, IntegerField, F, Prefetch
from django.utils import timezone
from django.core.paginator import Paginator
from django.db import models
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
import csv
import decimal
from decimal import Decimal

from sourcing.models import SourcingRequest, SourcingComment, SourcingRequestDocument
from notifications.models import Notification
from followup.models import FollowupRecord

@login_required
def dashboard(request):
    """Display the seller dashboard."""
    if request.user.role != 'seller':
        return redirect('dashboard:index')
    
    try:
        # Get the seller profile for the user
        seller = Seller.objects.get(user=request.user)
        
        # Get recent orders
        recent_orders = Order.objects.filter(seller=seller).order_by('-date')[:5]
        
        # Get revenue statistics
        total_revenue = Order.objects.filter(
            seller=seller, 
            status__in=['completed', 'delivered']
        ).aggregate(
            total=Sum(models.F('price_per_unit') * models.F('quantity'))
        )['total'] or 0
        
        # Calculate revenue growth (compared to previous month)
        current_month = timezone.now().month
        current_year = timezone.now().year
        previous_month = current_month - 1 if current_month > 1 else 12
        previous_year = current_year if current_month > 1 else current_year - 1
        
        current_month_revenue = Order.objects.filter(
            seller=seller,
            status__in=['completed', 'delivered'],
            date__month=current_month,
            date__year=current_year
        ).aggregate(
            total=Sum(models.F('price_per_unit') * models.F('quantity'))
        )['total'] or 0
        
        previous_month_revenue = Order.objects.filter(
            seller=seller,
            status__in=['completed', 'delivered'],
            date__month=previous_month,
            date__year=previous_year
        ).aggregate(
            total=Sum(models.F('price_per_unit') * models.F('quantity'))
        )['total'] or 0
        
        if previous_month_revenue > 0:
            revenue_growth = ((current_month_revenue - previous_month_revenue) / previous_month_revenue) * 100
        else:
            revenue_growth = 100 if current_month_revenue > 0 else 0
        
        # Get order statistics
        order_count = Order.objects.filter(seller=seller).count()
        pending_order_count = Order.objects.filter(seller=seller, status='pending').count()
        processing_order_count = Order.objects.filter(seller=seller, status='processing').count()
        delivered_order_count = Order.objects.filter(seller=seller, status='delivered').count()
        cancelled_order_count = Order.objects.filter(seller=seller, status='cancelled').count()
        
        # Get monthly revenue data for chart
        monthly_revenue = []
        for month in range(1, 13):
            month_revenue = Order.objects.filter(
                seller=seller,
                status__in=['completed', 'delivered'],
                date__month=month,
                date__year=current_year
            ).aggregate(
                total=Sum(models.F('price_per_unit') * models.F('quantity'))
            )['total'] or 0
            
            monthly_revenue.append(month_revenue)
        
        # Get sourcing request statistics
        pending_sourcing_requests = SourcingRequest.objects.filter(
            seller=request.user,
            status__in=['draft', 'submitted', 'under_review']
        ).count()
        
        approved_sourcing_requests = SourcingRequest.objects.filter(
            seller=request.user,
            status__in=['approved', 'in_progress', 'shipped', 'delivered']
        ).count()
        
        # Get recent sourcing requests
        recent_sourcing_requests = SourcingRequest.objects.filter(
            seller=request.user
        ).exclude(
            status='draft'
        ).order_by('-created_at')[:3]
        
        # Get notifications
        notifications = Notification.objects.filter(
            user=request.user
        ).order_by('-created_at')[:5]
        
        context = {
            'recent_orders': recent_orders,
            'total_revenue': total_revenue,
            'revenue_growth': revenue_growth,
            'order_count': order_count,
            'pending_order_count': pending_order_count,
            'processing_order_count': processing_order_count,
            'delivered_order_count': delivered_order_count,
            'cancelled_order_count': cancelled_order_count,
            'monthly_revenue': monthly_revenue,
            'notifications': notifications,
            'pending_sourcing_requests': pending_sourcing_requests,
            'approved_sourcing_requests': approved_sourcing_requests,
            'recent_sourcing_requests': recent_sourcing_requests,
        }
        
        return render(request, 'sellers/dashboard.html', context)
    
    except Seller.DoesNotExist:
        # Create a new seller profile for this user
        seller = Seller.objects.create(
            user=request.user,
            name=request.user.full_name,
            phone=request.user.phone_number,
            email=request.user.email,
            store_link=""
        )
        messages.success(request, "Your seller profile has been created. Welcome!")
        
        # Show an empty dashboard
        context = {
            'recent_orders': [],
            'total_revenue': 0,
            'revenue_growth': 0,
            'order_count': 0,
            'pending_order_count': 0,
            'processing_order_count': 0,
            'delivered_order_count': 0,
            'cancelled_order_count': 0,
            'monthly_revenue': [0] * 12,
            'notifications': [],
            'pending_sourcing_requests': 0,
            'approved_sourcing_requests': 0,
            'recent_sourcing_requests': [],
        }
        
        return render(request, 'sellers/dashboard.html', context)

@login_required
def product_list(request):
    """List all products for the seller."""
    # Debug print
    print(f"User role: {request.user.role}, User ID: {request.user.id}")
    
    if request.user.role == 'seller':
        products = Product.objects.filter(seller=request.user).order_by('-created_at')
        # Debug print
        print(f"Seller products query: {products.query}")
        print(f"Number of products found: {products.count()}")
    else:
        products = Product.objects.all().order_by('-created_at')
        # Debug print
        print(f"All products count: {products.count()}")
        
    return render(request, 'sellers/products.html', {
        'products': products,
    })

@login_required
def product_create(request):
    """Create a new product."""
    if request.method == 'POST':
        print(f"Form submitted by user: {request.user.email}, role: {request.user.role}")
        print(f"Form data: {request.POST}")
        print(f"Files: {request.FILES}")
        
        # Process form data
        name_en = request.POST.get('name')
        name_ar = request.POST.get('name_ar', '')
        code = request.POST.get('code')
        description = request.POST.get('description', '')
        selling_price = request.POST.get('selling_price')
        purchase_price = request.POST.get('cost_price', None)
        product_link = request.POST.get('product_link', '')
        brand = request.POST.get('brand', '')
        category = request.POST.get('category', '')
        total_quantity = request.POST.get('total_quantity', 0)
        available_quantity = request.POST.get('available_quantity', 0)
        low_stock_threshold = request.POST.get('low_stock_threshold', 5)
        
        # Debug print
        print(f"Form data received: name={name_en}, code={code}, selling_price={selling_price}, brand={brand}, category={category}")
        
        # Validate required fields
        if not all([name_en, code, selling_price]):
            missing = []
            if not name_en: missing.append("Product Name")
            if not code: missing.append("Product Code")
            if not selling_price: missing.append("Selling Price")
            error_msg = f"Please fill in all required fields: {', '.join(missing)}"
            print(f"Validation error: {error_msg}")
            messages.error(request, error_msg)
            return render(request, 'sellers/product_create.html')
        
        try:
            # Convert numeric values
            try:
                selling_price = float(selling_price)
                if purchase_price:
                    purchase_price = float(purchase_price)
                if total_quantity:
                    total_quantity = int(total_quantity)
                if available_quantity:
                    available_quantity = int(available_quantity)
                if low_stock_threshold:
                    low_stock_threshold = int(low_stock_threshold)
            except (ValueError, TypeError) as e:
                print(f"Type conversion error: {str(e)}")
                messages.error(request, f"Invalid numeric value: {str(e)}")
                return render(request, 'sellers/product_create.html')
                
            # Create product object
            print(f"Creating product object with seller: {request.user.email} (ID: {request.user.id})")
            product = Product(
                name_en=name_en,
                name_ar=name_ar,
                code=code,
                description=description,
                selling_price=selling_price,
                purchase_price=purchase_price,
                product_link=product_link,
                brand=brand,
                category=category,
                total_quantity=total_quantity,
                available_quantity=available_quantity,
                low_stock_threshold=low_stock_threshold,
                seller=request.user
            )
            
            # Handle image upload
            if 'image' in request.FILES:
                product.image = request.FILES['image']
            
            # Debug print
            print(f"About to save product: {product.name_en}, {product.code}")
            
            product.save()
            
            # Debug print
            print(f"Product saved successfully with ID: {product.id}")
            
            success_message = f"Product {name_en} created successfully with ID: {product.id}"
            messages.success(request, success_message)
            print(f"Success message set: {success_message}")
            print(f"Redirecting to: sellers:inventory")
            
            # Redirect to inventory page instead of products page
            return redirect('sellers:inventory')
            
        except Exception as e:
            import traceback
            print(f"Error creating product: {str(e)}")
            print(traceback.format_exc())
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
    
    if request.method == 'POST':
        # Process form data
        name_en = request.POST.get('name')
        name_ar = request.POST.get('name_ar')
        code = request.POST.get('code')
        description = request.POST.get('description', '')
        selling_price = request.POST.get('selling_price')
        purchase_price = request.POST.get('cost_price', None)
        product_link = request.POST.get('product_link', '')
        total_quantity = request.POST.get('total_quantity', 0)
        available_quantity = request.POST.get('available_quantity', 0)
        
        # Validate required fields
        if not all([name_en, code, selling_price]):
            messages.error(request, "Please fill in all required fields.")
            return render(request, 'sellers/product_edit.html', {'product': product})
        
        try:
            # Update product object
            product.name_en = name_en
            product.name_ar = name_ar
            product.code = code
            product.description = description
            product.selling_price = selling_price
            product.purchase_price = purchase_price
            product.product_link = product_link
            product.total_quantity = total_quantity
            product.available_quantity = available_quantity
            
            # Handle image upload
            if 'image' in request.FILES:
                product.image = request.FILES['image']
            
            product.save()
            messages.success(request, f"Product {name_en} updated successfully.")
            return redirect('sellers:products')
            
        except Exception as e:
            messages.error(request, f"Error updating product: {str(e)}")
    
    return render(request, 'sellers/product_edit.html', {
        'product': product,
    })

@login_required
def order_list(request):
    """List orders for the seller."""
    if request.user.role == 'seller':
        try:
            # Get the seller profile for the user
            seller = Seller.objects.get(user=request.user)
            orders = Order.objects.filter(seller=seller).order_by('-date')
        except Seller.DoesNotExist:
            # If seller profile doesn't exist, create it
            seller = Seller.objects.create(
                user=request.user,
                name=request.user.full_name,
                phone=request.user.phone_number,
                email=request.user.email,
                store_link=""
            )
            messages.success(request, "Your seller profile has been created. Welcome!")
            orders = Order.objects.filter(seller=seller).order_by('-date')
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
    if request.user.role == 'seller':
        try:
            # Get the seller profile for the user
            seller = Seller.objects.get(user=request.user)
            if order.seller != seller:
                messages.error(request, "You don't have permission to view this order.")
                return redirect('sellers:orders')
        except Seller.DoesNotExist:
            # If seller profile doesn't exist, they can't view any orders
            messages.error(request, "You don't have a seller profile set up yet.")
            return redirect('sellers:dashboard')
    
    # Get order items
    order_items = order.items.all().select_related('product')
    
    # Calculate totals
    subtotal = order.get_subtotal()
    tax = order.tax_amount or (subtotal * Decimal('0.05'))  # Use existing tax or calculate if missing
    total = order.total_price or subtotal + tax   # Use existing total or calculate if missing
    
    # Update order if totals were missing
    if not order.total_price or not order.tax_amount:
        order.tax_amount = tax
        order.total_price = total
        order.save()
        
    context = {
        'order': order,
        'order_items': order_items,
        'subtotal': subtotal,
        'tax': tax,
        'total': total
    }
    
    return render(request, 'sellers/order_detail.html', context)

@login_required
def sourcing_requests(request):
    """Display the seller's sourcing requests."""
    if request.user.role != 'seller':
        return redirect('dashboard:index')
    
    # Get filter parameters
    status = request.GET.get('status', '')
    search = request.GET.get('search', '')
    sort = request.GET.get('sort', '-created_at')
    
    # Filter sourcing requests
    sourcing_requests = SourcingRequest.objects.filter(seller=request.user)
    
    if status:
        sourcing_requests = sourcing_requests.filter(status=status)
    
    if search:
        sourcing_requests = sourcing_requests.filter(
            Q(request_number__icontains=search) | 
            Q(product_name__icontains=search) |
            Q(source_country__icontains=search) |
            Q(destination_country__icontains=search)
        )
    
    # Sort the results
    sourcing_requests = sourcing_requests.order_by(sort)
    
    # Pagination
    paginator = Paginator(sourcing_requests, 10)  # Show 10 requests per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get counts for stats
    total_requests = SourcingRequest.objects.filter(seller=request.user).count()
    pending_requests = SourcingRequest.objects.filter(
        seller=request.user, 
        status__in=['draft', 'submitted', 'under_review']
    ).count()
    approved_requests = SourcingRequest.objects.filter(
        seller=request.user,
        status__in=['approved', 'in_progress', 'shipped', 'delivered']
    ).count()
    rejected_requests = SourcingRequest.objects.filter(
        seller=request.user,
        status='rejected'
    ).count()
    
    context = {
        'sourcing_requests': page_obj,
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
        'rejected_requests': rejected_requests,
        'status': status,
        'search': search,
        'sort': sort,
    }
    
    return render(request, 'sellers/sourcing_requests.html', context)

@login_required
def create_sourcing_request(request):
    """Create a new sourcing request."""
    if request.user.role != 'seller':
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        # Check if draft
        is_draft = 'save_draft' in request.POST
        
        # Create a new sourcing request
        sourcing_request = SourcingRequest(
            seller=request.user,
            product_name=request.POST.get('product_name', ''),
            carton_quantity=int(request.POST.get('carton_quantity', 0)),
            source_country=request.POST.get('source_country', ''),
            destination_country=request.POST.get('destination_country', ''),
            finance_source=request.POST.get('finance_source', 'seller'),
            supplier_contact=request.POST.get('supplier_name', ''),
            supplier_phone=request.POST.get('supplier_phone', ''),
            cost_per_unit=float(request.POST.get('target_price', 0) or 0),
            currency=request.POST.get('currency', 'USD'),
            notes=request.POST.get('description', '') + '\n\n' + request.POST.get('special_instructions', ''),
            status='draft' if is_draft else 'submitted',
            unit_quantity=1  # Default to 1 unit per carton
        )
        
        # Set submitted_at if not a draft
        if not is_draft:
            sourcing_request.submitted_at = timezone.now()
        
        sourcing_request.save()
        
        if is_draft:
            messages.success(request, 'Sourcing request saved as draft.')
        else:
            messages.success(request, 'Sourcing request submitted successfully.')
        
        return redirect('sellers:sourcing_request_detail', sourcing_request.id)
    
    return render(request, 'sellers/sourcing_request_form.html')

@login_required
def sourcing_request_detail(request, request_id):
    """Display the details of a sourcing request."""
    if request.user.role != 'seller':
        return redirect('dashboard:index')
    
    sourcing_request = get_object_or_404(SourcingRequest, id=request_id, seller=request.user)
    comments = SourcingComment.objects.filter(sourcing_request=sourcing_request).order_by('created_at')
    documents = SourcingRequestDocument.objects.filter(sourcing_request=sourcing_request)
    
    context = {
        'sourcing_request': sourcing_request,
        'comments': comments,
        'documents': documents,
    }
    
    return render(request, 'sellers/sourcing_request_detail.html', context)

@login_required
def sourcing_request_edit(request, request_id):
    """Edit a sourcing request."""
    if request.user.role != 'seller':
        return redirect('dashboard:index')
    
    sourcing_request = get_object_or_404(SourcingRequest, id=request_id, seller=request.user)
    
    # Only allow editing draft requests
    if sourcing_request.status != 'draft':
        messages.error(request, 'Only draft requests can be edited.')
        return redirect('sellers:sourcing_request_detail', sourcing_request.id)
    
    if request.method == 'POST':
        # Check if draft
        is_draft = 'save_draft' in request.POST
        
        # Update the sourcing request
        sourcing_request.product_name = request.POST.get('product_name', '')
        sourcing_request.carton_quantity = int(request.POST.get('carton_quantity', 0))
        sourcing_request.source_country = request.POST.get('source_country', '')
        sourcing_request.destination_country = request.POST.get('destination_country', '')
        sourcing_request.finance_source = request.POST.get('finance_source', 'seller')
        sourcing_request.supplier_contact = request.POST.get('supplier_name', '')
        sourcing_request.supplier_phone = request.POST.get('supplier_phone', '')
        sourcing_request.cost_per_unit = float(request.POST.get('target_price', 0) or 0)
        sourcing_request.currency = request.POST.get('currency', 'USD')
        sourcing_request.notes = request.POST.get('description', '') + '\n\n' + request.POST.get('special_instructions', '')
        
        # Set status and submitted_at if not a draft
        if not is_draft:
            sourcing_request.status = 'submitted'
            sourcing_request.submitted_at = timezone.now()
        
        sourcing_request.save()
        
        if is_draft:
            messages.success(request, 'Sourcing request saved as draft.')
        else:
            messages.success(request, 'Sourcing request submitted successfully.')
        
        return redirect('sellers:sourcing_request_detail', sourcing_request.id)
    
    context = {
        'sourcing_request': sourcing_request,
        'request_id': request_id,
    }
    
    return render(request, 'sellers/sourcing_request_form.html', context)

@login_required
def sourcing_request_delete(request, request_id):
    """Delete a sourcing request."""
    if request.user.role != 'seller':
        return redirect('dashboard:index')
    
    sourcing_request = get_object_or_404(SourcingRequest, id=request_id, seller=request.user)
    
    # Only allow deleting draft requests
    if sourcing_request.status != 'draft':
        messages.error(request, 'Only draft requests can be deleted.')
        return redirect('sellers:sourcing_request_detail', sourcing_request.id)
    
    if request.method == 'POST':
        sourcing_request.delete()
        messages.success(request, 'Sourcing request deleted successfully.')
        return redirect('sellers:sourcing_requests')
    
    return redirect('sellers:sourcing_request_detail', sourcing_request.id)

@login_required
def sourcing_request_comment(request, request_id):
    """Add a comment to a sourcing request."""
    if request.user.role != 'seller':
        return redirect('dashboard:index')
    
    sourcing_request = get_object_or_404(SourcingRequest, id=request_id, seller=request.user)
    
    # Don't allow comments on draft, rejected, or completed requests
    if sourcing_request.status in ['draft', 'rejected', 'completed']:
        messages.error(request, 'Cannot comment on this request.')
        return redirect('sellers:sourcing_request_detail', sourcing_request.id)
    
    if request.method == 'POST':
        comment_text = request.POST.get('comment', '').strip()
        
        if comment_text:
            SourcingComment.objects.create(
                sourcing_request=sourcing_request,
                user=request.user,
                comment=comment_text
            )
            messages.success(request, 'Comment added successfully.')
        
    return redirect('sellers:sourcing_request_detail', sourcing_request.id)

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
    # Debug info
    print(f"Inventory view accessed by user: {request.user.email}, role: {request.user.role}")
    
    # Only allow sellers to access this page
    if request.user.role != 'seller' and request.user.role not in ['admin', 'super_admin']:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('dashboard:index')
    
    # Get all products with inventory information
    if request.user.role == 'seller':
        products = Product.objects.filter(seller=request.user).order_by('-created_at')
        print(f"Seller role detected, filtering products by seller ID: {request.user.id}")
    else:
        products = Product.objects.all().order_by('-created_at')
        print(f"Admin role detected, showing all products")
    
    # Check what products exist in the database
    all_products = Product.objects.all()
    print(f"All products in DB: {all_products.count()}")
    for p in all_products:
        print(f"DB Product: ID={p.id}, Name={p.name_en}, Seller ID={p.seller_id}")
    
    # Calculate inventory statistics
    total_inventory = sum(product.total_quantity for product in products)
    available_inventory = sum(product.available_quantity for product in products)
    in_delivery_inventory = total_inventory - available_inventory
    
    print(f"Rendering inventory.html with {products.count()} products")
    
    return render(request, 'sellers/inventory.html', {
        'products': products,
        'total_inventory': total_inventory,
        'available_inventory': available_inventory,
        'in_delivery_inventory': in_delivery_inventory,
        'user_role': request.user.role,
        'user_id': request.user.id
    })

@login_required
def product_delete(request, product_id):
    """Delete a product (SuperAdmin only)."""
    product = get_object_or_404(Product, id=product_id)
    
    # Check if user is a SuperAdmin
    if request.user.role != 'super_admin':
        messages.error(request, "Only SuperAdmins can delete products.")
        return redirect('sellers:product_detail', product_id=product_id)
    
    if request.method == 'POST':
        product_name = product.name_en
        try:
            product.delete()
            messages.success(request, f"Product '{product_name}' has been deleted successfully.")
            return redirect('sellers:products')
        except Exception as e:
            messages.error(request, f"Error deleting product: {str(e)}")
            return redirect('sellers:product_detail', product_id=product_id)
    
    # If it's a GET request, show confirmation page
    return render(request, 'sellers/product_delete.html', {
        'product': product,
    })

@login_required
def order_create(request):
    """Create a new order."""
    # Get available products based on user role
    if request.user.role == 'seller':
        products = Product.objects.filter(seller=request.user).order_by('name_en')
    else:
        products = Product.objects.all().order_by('name_en')
    
    if request.method == 'POST':
        # Basic validation
        customer_name = request.POST.get('customer_name')
        customer_email = request.POST.get('customer_email')
        customer_phone = request.POST.get('customer_phone')
        shipping_address = request.POST.get('shipping_address')
        
        if not all([customer_name, customer_phone, shipping_address]):
            messages.error(request, "Please fill in all required customer information.")
            return render(request, 'sellers/order_create.html', {
                'products': products,
            })
        
        try:
            # Get seller if user is a seller
            seller = None
            if request.user.role == 'seller':
                try:
                    seller = Seller.objects.get(user=request.user)
                except Seller.DoesNotExist:
                    # Create a seller profile if it doesn't exist
                    seller = Seller.objects.create(
                        user=request.user,
                        name=request.user.full_name,
                        phone=request.user.phone_number,
                        email=request.user.email,
                        store_link=""
                    )
                    messages.success(request, "Your seller profile has been created.")
            
            # Create a new order
            order = Order.objects.create(
                customer_name=customer_name,
                customer_email=customer_email,
                customer_phone=customer_phone,
                shipping_address=shipping_address,
                status='pending',
                seller=seller,
            )
            
            # Process order items - using array-style form fields
            product_ids = request.POST.getlist('product_id[]')
            quantities = request.POST.getlist('quantity[]')
            
            # Debug logging
            print(f"Product IDs: {product_ids}")
            print(f"Quantities: {quantities}")
            
            # Validate at least one product
            if not product_ids or not any(pid for pid in product_ids if pid):
                messages.error(request, "Please add at least one product to the order.")
                order.delete()  # Delete the incomplete order
                return render(request, 'sellers/order_create.html', {
                    'products': products,
                })
            
            total_price = 0
            items_added = 0
            
            for i, product_id in enumerate(product_ids):
                if product_id and i < len(quantities) and quantities[i]:
                    try:
                        product = Product.objects.get(id=product_id)
                        quantity = int(quantities[i])
                        price = product.selling_price
                        
                        if quantity <= 0:
                            continue
                            
                        # Create order item
                        order.items.create(
                            product=product,
                            quantity=quantity,
                            price=price
                        )
                        
                        total_price += quantity * price
                        items_added += 1
                        
                        # Update product inventory
                        if product.available_quantity >= quantity:
                            product.available_quantity -= quantity
                            product.save()
                    except Product.DoesNotExist:
                        messages.warning(request, f"Product with ID {product_id} not found. Skipping.")
                    except ValueError:
                        messages.warning(request, f"Invalid quantity value for product {product_id}. Skipping.")
            
            # Check if any items were added
            if items_added == 0:
                messages.error(request, "No valid items were added to the order.")
                order.delete()  # Delete the empty order
                return render(request, 'sellers/order_create.html', {
                    'products': products,
                })
            
            # Calculate tax (5%)
            tax_amount = total_price * 0.05
            
            # Update order total
            order.total_price = total_price + tax_amount
            order.tax_amount = tax_amount
            order.save()
            
            messages.success(request, f"Order #{order.order_code} created successfully with {items_added} items.")
            return redirect('sellers:order_detail', order_id=order.id)
            
        except Exception as e:
            messages.error(request, f"Error creating order: {str(e)}")
    
    return render(request, 'sellers/order_create.html', {
        'products': products,
    })

@login_required
def order_update(request, order_id):
    """Update the status of an order."""
    order = get_object_or_404(Order, id=order_id)
    
    # Get original status before any changes
    original_status = order.status
    
    # Check permissions - only admin and call center can directly update order status
    if request.user.role == 'seller':
        if request.method == 'POST':
            new_status = request.POST.get('status')
            if new_status and new_status in dict(Order.STATUS_CHOICES):
                # Create a follow-up record to indicate that a seller requested a status change
                # This will make it appear in the Super Admin panel for approval
                try:
                    # Find a super admin or follow-up agent to assign
                    agent = User.objects.filter(role='super_admin').first()
                    if not agent:
                        agent = User.objects.filter(role='follow_up').first()
                        if not agent:
                            agent = User.objects.filter(is_superuser=True).first()
                    
                    # Check if there's already a pending follow-up for this order
                    existing_followup = FollowupRecord.objects.filter(
                        order=order, 
                        status__in=['pending', 'in_progress']
                    ).first()
                    
                    if existing_followup:
                        # Update existing follow-up with the requested status change
                        existing_followup.feedback += f"\nSeller requested status change from {original_status} to {new_status}"
                        existing_followup.save()
                    else:
                        # Create new follow-up record
                        FollowupRecord.objects.create(
                            order=order,
                            agent=agent,
                            status='pending',
                            feedback=f"Seller requested status change from {original_status} to {new_status}",
                            scheduled_for=timezone.now()
                        )
                    
                    messages.success(request, "Your status update request has been sent to the admin for approval.")
                except Exception as e:
                    messages.error(request, f"Error submitting status change request: {str(e)}")
            else:
                messages.error(request, "Invalid status provided.")
            
            return redirect('sellers:order_detail', order_id=order.id)
        
        # Display message that sellers need approval for status changes
        messages.info(request, "Sellers cannot directly modify order status. Your change request will be submitted for approval.")
    
    # Admin and call center users can update status directly
    elif request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status and new_status in dict(Order.STATUS_CHOICES):
            try:
                order.status = new_status
                order.save()
                
                # Create an audit log entry for the status change
                try:
                    from users.models import AuditLog
                    AuditLog.objects.create(
                        user=request.user,
                        action='status_change',
                        entity_type='Order',
                        entity_id=str(order.id),
                        description=f"Changed order status from {original_status} to {new_status}"
                    )
                except:
                    # If AuditLog doesn't exist, continue without error
                    pass
                
                messages.success(request, f"Order #{order.order_code} status updated to {new_status}.")
                return redirect('sellers:order_detail', order_id=order.id)
            except Exception as e:
                messages.error(request, f"Error updating order: {str(e)}")
        else:
            messages.error(request, "Invalid status provided.")
    
    # Render the update form
    return render(request, 'sellers/order_update.html', {
        'order': order,
        'status_choices': Order.STATUS_CHOICES,
    })

@login_required
def order_cancel(request, order_id):
    """Cancel an order."""
    order = get_object_or_404(Order, id=order_id)
    
    # Check permissions
    if request.user.role == 'seller':
        try:
            # Get the seller profile for the user
            seller = Seller.objects.get(user=request.user)
            if order.seller != seller:
                messages.error(request, "You don't have permission to cancel this order.")
                return redirect('sellers:orders')
        except Seller.DoesNotExist:
            # If seller profile doesn't exist, they can't cancel any orders
            messages.error(request, "You don't have a seller profile set up yet.")
            return redirect('sellers:dashboard')
        
        # For sellers, show a message explaining the need for call center approval
        messages.info(request, "Order cancellation requires call center approval. Please contact the call center to request cancellation of this order.")
        return redirect('sellers:order_detail', order_id=order.id)
    
    # Only admin and call center staff can proceed past this point
    if request.method == 'POST':
        try:
            order.status = 'cancelled'
            order.save()
            messages.success(request, f"Order #{order.order_code} has been cancelled.")
            return redirect('sellers:orders')
        except Exception as e:
            messages.error(request, f"Error cancelling order: {str(e)}")
    
    # Render the cancellation confirmation page
    return render(request, 'sellers/order_cancel.html', {
        'order': order,
    })

# Delivery views
@login_required
def delivery_tracking(request):
    """View for tracking all deliveries."""
    if request.user.role != 'seller':
        return redirect('dashboard:index')
    
    # Get the seller's orders
    try:
        seller = Seller.objects.get(user=request.user)
        all_orders = Order.objects.filter(seller=seller).order_by('-date')
        
        # Get filter parameters
        status_filter = request.GET.get('status', 'all')
        date_filter = request.GET.get('date', 'all')
        courier_filter = request.GET.get('courier', 'all')
        search_query = request.GET.get('search', '')
        
        # Calculate statistics first (based on all orders)
        delivered_count = all_orders.filter(status='delivered').count()
        in_transit_count = all_orders.filter(status='shipped').count()
        pending_count = all_orders.filter(status__in=['pending', 'processing']).count()
        issues_count = all_orders.filter(status='cancelled').count()
        
        # Apply status filter
        filtered_orders = all_orders
        if status_filter != 'all':
            filtered_orders = filtered_orders.filter(status=status_filter)
            
        # Apply date filter
        if date_filter == 'today':
            filtered_orders = filtered_orders.filter(date=timezone.now().date())
        elif date_filter == 'this_week':
            start_of_week = timezone.now().date() - timezone.timedelta(days=timezone.now().weekday())
            filtered_orders = filtered_orders.filter(date__gte=start_of_week)
        elif date_filter == 'this_month':
            start_of_month = timezone.now().date().replace(day=1)
            filtered_orders = filtered_orders.filter(date__gte=start_of_month)
        elif date_filter == 'last_month':
            this_month_start = timezone.now().date().replace(day=1)
            last_month_end = this_month_start - timezone.timedelta(days=1)
            last_month_start = last_month_end.replace(day=1)
            filtered_orders = filtered_orders.filter(date__gte=last_month_start, date__lte=last_month_end)
            
        # Apply search filter
        if search_query:
            filtered_orders = filtered_orders.filter(
                Q(order_code__icontains=search_query) | 
                Q(customer_name__icontains=search_query) |
                Q(shipping_address__icontains=search_query)
            )
        
        # Create delivery data for the view
        raw_deliveries = []
        for order in filtered_orders:
            # Generate tracking number and courier based on order info
            tracking_number = f"TRK-{order.id}-{order.order_code}"
            
            courier = "DHL Express"
            if "UAE" in order.shipping_address or "Dubai" in order.shipping_address:
                courier = "Aramex"
            elif "UK" in order.shipping_address or "London" in order.shipping_address:
                courier = "Royal Mail"
            elif "US" in order.shipping_address:
                courier = "USPS"
                
            # Skip orders that don't match courier filter
            if courier_filter != 'all' and courier_filter.lower() not in courier.lower():
                continue
                
            # Calculate ETA based on status and date
            eta = None
            if order.status == 'pending':
                eta = order.date + timezone.timedelta(days=7)
            elif order.status == 'processing':
                eta = order.date + timezone.timedelta(days=5)
            elif order.status == 'shipped':
                eta = order.date + timezone.timedelta(days=3)
            elif order.status == 'delivered':
                eta = order.date + timezone.timedelta(days=0)
                
            # Create delivery info from order
            raw_deliveries.append({
                'id': order.id,
                'order_id': order.order_code,
                'tracking_number': tracking_number,
                'courier': courier,
                'customer_name': order.customer_name,
                'customer_location': order.shipping_address,
                'shipping_date': order.date + timezone.timedelta(days=1) if order.status != 'pending' else None,
                'status': order.status,
                'eta': eta
            })
            
        # Pagination
        paginator = Paginator(raw_deliveries, 10)  # Show 10 deliveries per page
        page = request.GET.get('page', 1)
        
        try:
            deliveries = paginator.page(page)
        except:
            deliveries = paginator.page(1)
        
    except Seller.DoesNotExist:
        deliveries = []
        delivered_count = 0
        in_transit_count = 0
        pending_count = 0
        issues_count = 0
        paginator = None
        messages.warning(request, "Seller profile not found.")
    
    context = {
        'deliveries': deliveries,
        'page_title': 'Delivery Tracking',
        'delivered_count': delivered_count,
        'in_transit_count': in_transit_count,
        'pending_count': pending_count,
        'issues_count': issues_count,
        'paginator': paginator
    }
    
    return render(request, 'sellers/delivery_tracking.html', context)

@login_required
def delivery_detail(request, delivery_id):
    """View details of a specific delivery."""
    if request.user.role != 'seller':
        return redirect('dashboard:index')
    
    # Get order data based on delivery_id
    try:
        # In a real app, you would have a Delivery model
        # For now, we'll simulate with Order data
        seller = Seller.objects.get(user=request.user)
        order = get_object_or_404(Order, id=delivery_id, seller=seller)
        
        # Build tracking history from order data
        tracking_history = []
        
        if order.status == 'pending':
            tracking_history = [
                {
                    'date': order.date,
                    'status': 'Order Received',
                    'location': 'Seller Warehouse',
                    'description': 'Order has been received and is being processed'
                }
            ]
        elif order.status == 'processing':
            tracking_history = [
                {
                    'date': order.date,
                    'status': 'Order Received',
                    'location': 'Seller Warehouse',
                    'description': 'Order has been received and is being processed'
                },
                {
                    'date': order.date + timezone.timedelta(days=1),
                    'status': 'Processing',
                    'location': 'Seller Warehouse',
                    'description': 'Order is being prepared for shipping'
                }
            ]
        elif order.status == 'shipped':
            tracking_history = [
                {
                    'date': order.date,
                    'status': 'Order Received',
                    'location': 'Seller Warehouse',
                    'description': 'Order has been received and is being processed'
                },
                {
                    'date': order.date + timezone.timedelta(days=2),
                    'status': 'Shipped',
                    'location': 'Distribution Center',
                    'description': 'Order has been shipped and is in transit'
                }
            ]
        elif order.status == 'delivered':
            tracking_history = [
                {
                    'date': order.date,
                    'status': 'Order Received',
                    'location': 'Seller Warehouse',
                    'description': 'Order has been received and is being processed'
                },
                {
                    'date': order.date + timezone.timedelta(days=1),
                    'status': 'Processing',
                    'location': 'Seller Warehouse',
                    'description': 'Order is being prepared for shipping'
                },
                {
                    'date': order.date + timezone.timedelta(days=2),
                    'status': 'Shipped',
                    'location': 'Distribution Center',
                    'description': 'Order has been shipped and is in transit'
                },
                {
                    'date': order.date + timezone.timedelta(days=5),
                    'status': 'Delivered',
                    'location': order.shipping_address,
                    'description': 'Order has been delivered successfully'
                }
            ]
        elif order.status == 'cancelled':
            tracking_history = [
                {
                    'date': order.date,
                    'status': 'Order Received',
                    'location': 'Seller Warehouse',
                    'description': 'Order has been received and is being processed'
                },
                {
                    'date': order.date + timezone.timedelta(days=1),
                    'status': 'Cancelled',
                    'location': 'Seller Warehouse',
                    'description': 'Order has been cancelled'
                }
            ]
        
        # Generate tracking number based on order
        tracking_number = f"TRK-{order.id}-{order.order_code}"
        
        # Determine courier based on shipping address
        courier = "DHL Express"
        if "UAE" in order.shipping_address or "Dubai" in order.shipping_address:
            courier = "Aramex"
        elif "UK" in order.shipping_address or "London" in order.shipping_address:
            courier = "Royal Mail"
        elif "US" in order.shipping_address:
            courier = "USPS"
            
        # Create delivery info from order
        delivery = {
            'id': order.id,
            'order_id': order.order_code,
            'tracking_number': tracking_number,
            'courier': courier,
            'customer_name': order.customer_name,
            'customer_email': order.customer_email,
            'customer_phone': order.customer_phone,
            'shipping_address': order.shipping_address,
            'order_date': order.date,
            'shipping_date': order.date + timezone.timedelta(days=2) if order.status != 'pending' else None,
            'delivery_date': order.date + timezone.timedelta(days=5) if order.status == 'delivered' else None,
            'status': order.status,
            'tracking_history': tracking_history,
            'items': order.items.all() if hasattr(order, 'items') else [],
            'subtotal': order.total_price or (order.price_per_unit * order.quantity),
            'shipping_cost': Decimal('15.00'),  # Use Decimal instead of float
            'total_cost': (order.total_price or (order.price_per_unit * order.quantity)) + Decimal('15.00')  # Use Decimal
        }
        
    except (Seller.DoesNotExist, Order.DoesNotExist):
        # If not found, redirect to the delivery tracking page
        messages.error(request, "Delivery information not found.")
        return redirect('sellers:delivery_tracking')
    
    context = {
        'delivery': delivery,
        'page_title': f'Delivery Details - {order.order_code}'
    }
    
    return render(request, 'sellers/delivery_detail.html', context)

# Finance views
def get_payment_methods(user):
    """Helper function to get payment methods for a user.
    In a real application, this would fetch from a PaymentMethod model.
    For now we'll simulate with some placeholder data."""
    
    # In a real application, this would query the database
    # For now, we'll create some simulated payment methods
    # In a production environment, this should be replaced with actual model queries
    
    # This is a simplified version just for demonstration
    # You would need to create a proper PaymentMethod model in models.py
    payment_methods = [
        {
            'id': 'bank1',
            'type': 'bank',
            'description': 'Emirates NBD ****5678',
            'is_default': True
        },
        {
            'id': 'paypal1', 
            'type': 'paypal',
            'description': f'{user.email}',
            'is_default': False
        }
    ]
    
    return payment_methods

@login_required
def finances(request):
    """Finance dashboard for seller."""
    if request.user.role != 'seller':
        return redirect('dashboard:index')
    
    # Get seller data
    try:
        seller = Seller.objects.get(user=request.user)
    except Seller.DoesNotExist:
        seller = Seller.objects.create(
            user=request.user,
            name=request.user.full_name,
            phone=request.user.phone_number,
            email=request.user.email,
            store_link=""
        )
    
    # Get orders for revenue calculation
    orders = Order.objects.filter(seller=seller)
    
    # Calculate total revenue
    total_revenue = orders.filter(
        status__in=['completed', 'delivered']
    ).aggregate(
        total=Sum(models.F('price_per_unit') * models.F('quantity'))
    )['total'] or 0
    
    # Calculate revenue growth
    current_month = timezone.now().month
    current_year = timezone.now().year
    previous_month = current_month - 1 if current_month > 1 else 12
    previous_year = current_year if current_month > 1 else current_year - 1
    
    current_month_revenue = orders.filter(
        status__in=['completed', 'delivered'],
        date__month=current_month,
        date__year=current_year
    ).aggregate(
        total=Sum(models.F('price_per_unit') * models.F('quantity'))
    )['total'] or 0
    
    previous_month_revenue = orders.filter(
        status__in=['completed', 'delivered'],
        date__month=previous_month,
        date__year=previous_year
    ).aggregate(
        total=Sum(models.F('price_per_unit') * models.F('quantity'))
    )['total'] or 0
    
    if previous_month_revenue > 0:
        revenue_growth = ((current_month_revenue - previous_month_revenue) / previous_month_revenue) * 100
    else:
        revenue_growth = 100 if current_month_revenue > 0 else 0
    
    # Calculate available balance (70% of total revenue minus withdrawals)
    total_withdrawals = 0  # Replace with actual withdrawal calculation when available
    available_balance = (total_revenue * 0.7) - total_withdrawals
    
    # Calculate pending balance (30% of total revenue)
    pending_balance = total_revenue * 0.3
    
    # Get monthly revenue data for chart
    monthly_revenue = []
    for month in range(1, 13):
        month_revenue = orders.filter(
            status__in=['completed', 'delivered'],
            date__month=month,
            date__year=current_year
        ).aggregate(
            total=Sum(models.F('price_per_unit') * models.F('quantity'))
        )['total'] or 0
        
        monthly_revenue.append(month_revenue)
    
    # Get recent transactions
    recent_transactions = []
    
    # Add recent order payments
    for order in orders.filter(status__in=['completed', 'delivered']).order_by('-date')[:5]:
        amount = order.total_price or (order.price_per_unit * order.quantity)
        if amount <= 0:
            continue
            
        recent_transactions.append({
            'id': f"ORD-{order.id}",
            'description': f"Order #{order.order_code} Payment",
            'date': order.date,
            'type': 'Order Payment',
            'status': 'Completed',
            'amount': amount,
            'is_positive': True
        })
    
    # Sort transactions by date
    recent_transactions = sorted(recent_transactions, key=lambda x: x['date'], reverse=True)[:5]
    
    # Get payment methods
    payment_methods = get_payment_methods(request.user)
    
    context = {
        'total_revenue': total_revenue,
        'revenue_growth': revenue_growth,
        'available_balance': available_balance,
        'pending_balance': pending_balance,
        'total_withdrawals': total_withdrawals,
        'monthly_revenue': monthly_revenue,
        'recent_transactions': recent_transactions,
        'payment_methods': payment_methods,
    }
    
    return render(request, 'sellers/finances.html', context)

def redirect_to_payment_methods():
    """Helper function to redirect to the payment methods page."""
    from django.urls import reverse
    return redirect(f"{reverse('sellers:finance_transactions')}?action=manage_payment_methods")

@login_required
def finance_transactions(request):
    """View all financial transactions."""
    if request.user.role != 'seller':
        return redirect('dashboard:index')
    
    # Get payment methods for the user
    payment_methods = get_payment_methods(request.user)
    
    # Handle different actions from GET parameters first
    action = request.GET.get('action', '')
    
    # Handle different actions
    if action == 'manage_payment_methods':
        return render(request, 'sellers/payment_methods.html', {
            'page_title': 'Manage Payment Methods',
            'payment_methods': payment_methods
        })
    
    # Handle POST requests
    if request.method == 'POST':
        action = request.POST.get('action', '')
        
        if action == 'save_payment_method':
            method_type = request.POST.get('method_type', '')
            make_default = 'make_default' in request.POST
            
            if method_type == 'bank':
                # Save bank account details
                account_holder = request.POST.get('account_holder', '')
                bank_name = request.POST.get('bank_name', '')
                account_number = request.POST.get('account_number', '')
                routing_number = request.POST.get('routing_number', '')
                
                if not all([account_holder, bank_name, account_number, routing_number]):
                    messages.error(request, "Please fill in all required fields.")
                else:
                    # In a real application, this would save to the database
                    messages.success(request, "Bank account payment method added successfully.")
                    if make_default:
                        messages.info(request, "This payment method has been set as default.")
                    return redirect_to_payment_methods()
                
            elif method_type == 'paypal':
                # Save PayPal details
                paypal_email = request.POST.get('paypal_email', '')
                
                if not paypal_email:
                    messages.error(request, "Please enter your PayPal email address.")
                    return redirect_to_payment_methods()
                else:
                    # In a real application, this would save to the database
                    messages.success(request, "PayPal payment method added successfully.")
                    if make_default:
                        messages.info(request, "This payment method has been set as default.")
                    return redirect_to_payment_methods()
                    
            elif method_type == 'card':
                # Save credit card details
                card_holder = request.POST.get('card_holder', '')
                card_number = request.POST.get('card_number', '')
                expiry_date = request.POST.get('expiry_date', '')
                cvc = request.POST.get('cvc', '')
                
                if not all([card_holder, card_number, expiry_date, cvc]):
                    messages.error(request, "Please fill in all required fields.")
                else:
                    # In a real application, this would save to the database (securely)
                    messages.success(request, "Credit card payment method added successfully.")
                    if make_default:
                        messages.info(request, "This payment method has been set as default.")
                    return redirect_to_payment_methods()
        
        elif action == 'set_default_payment':
            method_id = request.POST.get('method', '')
            if method_id:
                # In a real application, this would update the database
                # For now, we'll simulate with a success message
                messages.success(request, "Payment method set as default successfully.")
            else:
                messages.error(request, "Invalid payment method.")
            return redirect_to_payment_methods()
                
        elif action == 'edit_payment_method':
            method_id = request.POST.get('method', '')
            if method_id:
                # Find the method to edit
                method_to_edit = None
                for method in payment_methods:
                    if method['id'] == method_id:
                        method_to_edit = method
                        break
                
                if method_to_edit:
                    # For bank account
                    if method_to_edit['type'] == 'bank':
                        return render(request, 'sellers/edit_payment_method.html', {
                            'page_title': 'Edit Payment Method',
                            'method': method_to_edit,
                            'method_type': 'bank'
                        })
                    # For PayPal
                    elif method_to_edit['type'] == 'paypal':
                        return render(request, 'sellers/edit_payment_method.html', {
                            'page_title': 'Edit Payment Method',
                            'method': method_to_edit,
                            'method_type': 'paypal'
                        })
                    # For credit card
                    else:
                        return render(request, 'sellers/edit_payment_method.html', {
                            'page_title': 'Edit Payment Method',
                            'method': method_to_edit,
                            'method_type': 'card'
                        })
                else:
                    messages.error(request, "Payment method not found.")
            else:
                messages.error(request, "Invalid payment method.")
            return redirect_to_payment_methods()
                
        elif action == 'remove_payment_method':
            method_id = request.POST.get('method', '')
            if method_id:
                # In a real application, this would delete from the database
                # For now, we'll simulate with a success message
                messages.success(request, "Payment method removed successfully.")
            else:
                messages.error(request, "Invalid payment method.")
            return redirect_to_payment_methods()
                
        elif action == 'update_payment_method':
            method_id = request.POST.get('method_id', '')
            method_type = request.POST.get('method_type', '')
            
            if method_id and method_type:
                # In a real application, this would update the database
                # Handle each method type appropriately
                if method_type == 'bank':
                    account_holder = request.POST.get('account_holder', '')
                    bank_name = request.POST.get('bank_name', '')
                    account_number = request.POST.get('account_number', '')
                    routing_number = request.POST.get('routing_number', '')
                    
                    if not all([account_holder, bank_name, account_number, routing_number]):
                        messages.error(request, "Please fill in all required fields.")
                        return redirect_to_payment_methods()
                    
                    messages.success(request, "Bank account details updated successfully.")
                    return redirect(f"{reverse('sellers:finance_transactions')}?action=manage_payment_methods")
                    
                elif method_type == 'paypal':
                    paypal_email = request.POST.get('paypal_email', '')
                    
                    if not paypal_email:
                        messages.error(request, "Please enter your PayPal email address.")
                        return redirect_to_payment_methods()
                    
                    messages.success(request, "PayPal details updated successfully.")
                    return redirect(f"{reverse('sellers:finance_transactions')}?action=manage_payment_methods")
                    
                elif method_type == 'card':
                    card_holder = request.POST.get('card_holder', '')
                    card_number = request.POST.get('card_number', '')
                    expiry_date = request.POST.get('expiry_date', '')
                    
                    if not all([card_holder, card_number, expiry_date]):
                        messages.error(request, "Please fill in all required fields.")
                        return redirect_to_payment_methods()
                    
                    messages.success(request, "Credit card details updated successfully.")
                    return redirect_to_payment_methods()
            else:
                messages.error(request, "Invalid payment method.")
            return redirect_to_payment_methods()
    
    # Handle different actions from GET parameters
    action = request.GET.get('action', '')
    
    # Handle different actions
    if action == 'schedule_payout':
        # Get seller balance for the payout form
        try:
            seller = Seller.objects.get(user=request.user)
            # Get orders for revenue calculation
            orders = Order.objects.filter(seller=seller)
            total_revenue = orders.filter(
                status__in=['completed', 'delivered']
            ).aggregate(
                total=Sum(models.F('price_per_unit') * models.F('quantity'))
            )['total'] or 0
            
            # Calculate available and pending balance
            total_withdrawals = 0  # Replace with actual withdrawal calculation when available
            available_balance = (total_revenue * 0.7) - total_withdrawals
            pending_balance = total_revenue * 0.3
            
            return render(request, 'sellers/schedule_payout.html', {
                'page_title': 'Schedule Payout',
                'available_balance': available_balance,
                'pending_balance': pending_balance,
                'payment_methods': payment_methods
            })
        except Seller.DoesNotExist:
            messages.warning(request, "Seller profile not found.")
            return redirect('sellers:finances')
        
    elif action == 'manage_payment_methods':
        return render(request, 'sellers/payment_methods.html', {
            'page_title': 'Manage Payment Methods',
            'payment_methods': payment_methods
        })
        
    elif action == 'add_payment_method':
        return render(request, 'sellers/add_payment_method.html', {
            'page_title': 'Add Payment Method'
        })
    
    # Get all transactions for the seller
    try:
        seller = Seller.objects.get(user=request.user)
        # Get orders as transactions
        orders = Order.objects.filter(seller=seller)
        
        # Filter by transaction type if provided
        transaction_type = request.GET.get('type', '')
        date_from = request.GET.get('date_from', '')
        date_to = request.GET.get('date_to', '')
        
        # Apply transaction type filter
        filtered_orders = orders
        if transaction_type == 'order_payment':
            # Only include order payments
            filtered_orders = orders.filter(status__in=['completed', 'delivered'])
        elif transaction_type == 'refund':
            # Only include refunds
            filtered_orders = orders.filter(status='cancelled')
        
        # Apply date filters
        if date_from:
            try:
                from datetime import datetime
                date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
                filtered_orders = filtered_orders.filter(date__gte=date_from)
            except ValueError:
                pass
                
        if date_to:
            try:
                from datetime import datetime
                date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
                filtered_orders = filtered_orders.filter(date__lte=date_to)
            except ValueError:
                pass
        
        transactions = []
        total_income = 0
        total_payouts = 0
        
        # Add order payments as transactions
        for order in filtered_orders:
            amount = order.total_price or (order.price_per_unit * order.quantity)
            
            # Skip $0 transactions
            if amount <= 0:
                continue
                
            transaction_type = 'Order Payment'
            is_positive = True
            
            # If it's a cancelled order, treat it as a refund
            if order.status == 'cancelled':
                transaction_type = 'Refund'
                is_positive = False
            
            transactions.append({
                'id': f"ORD-{order.id}",
                'description': f"Order #{order.order_code} Payment",
                'date': order.date,
                'type': transaction_type,
                'status': 'Completed' if order.status in ['completed', 'delivered'] else 'Pending' if order.status == 'processing' else 'Cancelled',
                'amount': amount,
                'is_positive': is_positive
            })
            
            if is_positive and order.status in ['completed', 'delivered']:
                total_income += amount
            elif not is_positive:
                total_payouts += amount
        
        # Calculate available balance
        available_balance = (total_income * 0.7) - total_payouts
        
        # Sort by date, most recent first
        transactions = sorted(transactions, key=lambda x: x['date'], reverse=True)
        
    except Seller.DoesNotExist:
        transactions = []
        total_income = 0
        total_payouts = 0
        available_balance = 0
        messages.warning(request, "Seller profile not found.")
    
    context = {
        'transactions': transactions,
        'total_income': total_income,
        'total_payouts': total_payouts,
        'available_balance': available_balance,
        'page_title': 'Financial Transactions',
        'payment_methods': payment_methods
    }
    
    return render(request, 'sellers/finance_transactions.html', context)

@login_required
def finance_reports(request):
    """View financial reports."""
    if request.user.role != 'seller':
        return redirect('dashboard:index')
    
    # Check if we need to export the report
    export = request.GET.get('export', 'false').lower() == 'true'
    report_type = request.GET.get('type', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # This is a placeholder - implement actual reports later
    reports = []  # Will be generated from transaction data
    
    # If export parameter is provided, generate a CSV report
    if export and report_type:
        import csv
        from django.http import HttpResponse
        from django.utils.translation import gettext as _
        from datetime import datetime
        
        # Create response object
        response = HttpResponse(content_type='text/csv')
        filename = f"{report_type}_{datetime.now().strftime('%Y%m%d')}.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Create CSV writer
        writer = csv.writer(response)
        
        # Write appropriate headers based on report type
        if report_type == 'revenue_summary':
            writer.writerow([_('Period'), _('Revenue'), _('Growth %'), _('Orders'), _('Average Order Value')])
            # Example data rows (replace with actual data in production)
            writer.writerow(['Jan 2023', '$1,245.00', '+12.5%', '15', '$83.00'])
            writer.writerow(['Feb 2023', '$1,845.00', '+48.2%', '22', '$83.86'])
            writer.writerow(['Mar 2023', '$2,145.00', '+16.3%', '25', '$85.80'])
            
        elif report_type == 'transaction_history':
            writer.writerow([_('Date'), _('Transaction ID'), _('Type'), _('Amount'), _('Status')])
            # Example data rows (replace with actual data in production)
            writer.writerow(['2023-03-15', 'TRX-12345', _('Order Payment'), '$85.00', _('Completed')])
            writer.writerow(['2023-03-10', 'TRX-12344', _('Order Payment'), '$92.50', _('Completed')])
            writer.writerow(['2023-03-05', 'TRX-12343', _('Payout'), '-$150.00', _('Completed')])
            
        elif report_type == 'tax_report':
            writer.writerow([_('Period'), _('Gross Revenue'), _('Tax Collected'), _('Tax Rate'), _('Net Revenue')])
            # Example data rows (replace with actual data in production)
            writer.writerow(['Q1 2023', '$5,235.00', '$261.75', '5%', '$4,973.25'])
            writer.writerow(['Q2 2023', '$6,412.00', '$320.60', '5%', '$6,091.40'])
            
        elif report_type == 'payout_schedule':
            writer.writerow([_('Date'), _('Amount'), _('Status'), _('Payment Method'), _('Reference')])
            # Example data rows (replace with actual data in production)
            writer.writerow(['2023-04-01', '$450.00', _('Scheduled'), _('Bank Account'), 'PAY-001'])
            writer.writerow(['2023-03-01', '$320.00', _('Completed'), _('Bank Account'), 'PAY-002'])
            
        return response
    
    context = {
        'reports': reports,
        'page_title': 'Financial Reports'
    }
    
    return render(request, 'sellers/finance_reports.html', context)

# Sales Channels views
@login_required
def sales_channels(request):
    """Display the seller's sales channels."""
    if request.user.role != 'seller':
        return redirect('dashboard:index')
    
    # Get the sales channels for the current seller
    channels = SalesChannel.objects.filter(seller=request.user).order_by('-created_at')
    
    context = {
        'channels': channels,
    }
    
    return render(request, 'sellers/sales_channels.html', context)

@login_required
def sales_channel_create(request):
    """Create a new sales channel."""
    if request.user.role != 'seller':
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        # Process form data
        name_en = request.POST.get('store_name')
        url = request.POST.get('store_url')  # using url as the field name in the database
        platform = request.POST.get('platform')
        api_key = request.POST.get('api_key')
        api_secret = request.POST.get('api_secret')
        
        # Process sync settings
        sync_products = 'sync_products' in request.POST
        sync_orders = 'sync_orders' in request.POST
        sync_inventory = 'sync_inventory' in request.POST
        sync_shipping = 'sync_shipping' in request.POST
        
        # Handle logo upload
        logo = None
        if 'store_logo' in request.FILES:
            logo = request.FILES['store_logo']
        
        # Validate required fields
        if not all([name_en, url, platform]):
            messages.error(request, "Please fill in all required fields.")
            return render(request, 'sellers/sales_channel_create.html')
        
        try:
            # Create sales channel object
            channel = SalesChannel(
                name_en=name_en,
                url=url,  # using url field not store_url
                channel_type=platform,
                api_key=api_key,
                api_secret=api_secret,
                logo=logo,
                is_active=True,
                seller=request.user,
                sync_products=sync_products,
                sync_orders=sync_orders,
                sync_inventory=sync_inventory,
                sync_shipping=sync_shipping
            )
            channel.save()
            
            messages.success(request, f"Sales channel '{name_en}' has been created successfully.")
            return redirect('sellers:sales_channel_detail', channel_id=channel.id)
        except Exception as e:
            messages.error(request, f"Error creating sales channel: {str(e)}")
    
    return render(request, 'sellers/sales_channel_create.html')

@login_required
def sales_channel_detail(request, channel_id):
    """View details of a specific sales channel."""
    if request.user.role != 'seller':
        return redirect('dashboard:index')
    
    # Get the sales channel and verify it belongs to the current seller
    channel = get_object_or_404(SalesChannel, id=channel_id, seller=request.user)
    
    # Get orders for this sales channel
    channel_orders = Order.objects.filter(sales_channel=channel).order_by('-date')[:10]
    
    context = {
        'channel': channel,
        'channel_orders': channel_orders,
    }
    
    return render(request, 'sellers/sales_channel_detail.html', context)

@login_required
def sales_channel_edit(request, channel_id):
    """Edit an existing sales channel."""
    if request.user.role != 'seller':
        return redirect('dashboard:index')
    
    # Get the sales channel and verify it belongs to the current seller
    channel = get_object_or_404(SalesChannel, id=channel_id, seller=request.user)
    
    if request.method == 'POST':
        # Process form data
        name_en = request.POST.get('store_name')
        url = request.POST.get('store_url')  # using url field
        api_key = request.POST.get('api_key')
        api_secret = request.POST.get('api_secret')
        
        # Update channel status
        is_active = 'is_active' in request.POST
        
        # Process sync settings
        sync_products = 'sync_products' in request.POST
        sync_orders = 'sync_orders' in request.POST
        sync_inventory = 'sync_inventory' in request.POST
        sync_shipping = 'sync_shipping' in request.POST
        
        # Handle logo upload or removal
        if 'store_logo' in request.FILES:
            channel.logo = request.FILES['store_logo']
        elif request.POST.get('remove_logo') == 'true' and channel.logo:
            channel.logo.delete()
            channel.logo = None
        
        # Validate required fields
        if not all([name_en, url]):
            messages.error(request, "Please fill in all required fields.")
            return render(request, 'sellers/sales_channel_edit.html', {'channel': channel})
        
        try:
            # Update sales channel object
            channel.name_en = name_en
            channel.url = url  # using url field
            
            # Only update API credentials if provided
            if api_key:
                channel.api_key = api_key
            if api_secret:
                channel.api_secret = api_secret
            
            channel.is_active = is_active
            channel.sync_products = sync_products
            channel.sync_orders = sync_orders
            channel.sync_inventory = sync_inventory
            channel.sync_shipping = sync_shipping
            
            channel.save()
            
            messages.success(request, f"Sales channel '{name_en}' has been updated successfully.")
            return redirect('sellers:sales_channel_detail', channel_id=channel.id)
        except Exception as e:
            messages.error(request, f"Error updating sales channel: {str(e)}")
    
    context = {
        'channel': channel,
    }
    
    return render(request, 'sellers/sales_channel_edit.html', context)

@login_required
def sales_channel_delete(request, channel_id):
    """Delete a sales channel."""
    if request.user.role != 'seller':
        return redirect('dashboard:index')
    
    # Get the sales channel and verify it belongs to the current seller
    channel = get_object_or_404(SalesChannel, id=channel_id, seller=request.user)
    
    if request.method == 'POST':
        try:
            channel_name = channel.name_en
            
            # Delete the channel
            channel.delete()
            
            messages.success(request, f"Sales channel '{channel_name}' has been deleted successfully.")
            return redirect('sellers:sales_channels')
        except Exception as e:
            messages.error(request, f"Error deleting sales channel: {str(e)}")
            return redirect('sellers:sales_channel_detail', channel_id=channel.id)
    
    # If not a POST request, redirect to detail page
    return redirect('sellers:sales_channel_detail', channel_id=channel.id)

# Settings view
@login_required
def settings(request):
    """Seller account settings."""
    if request.user.role != 'seller':
        return redirect('dashboard:index')
    
    # Get the seller profile
    seller = get_object_or_404(Seller, user=request.user)
    
    # This is a placeholder - implement actual form handling later
    if request.method == 'POST':
        # Process form submission
        pass
    
    context = {
        'seller': seller,
        'page_title': 'Account Settings'
    }
    
    return render(request, 'sellers/settings.html', context)

@login_required
def profile_settings(request):
    """Seller profile settings."""
    if request.user.role != 'seller':
        return redirect('dashboard:index')
    
    # Get the seller profile
    seller = get_object_or_404(Seller, user=request.user)
    
    if request.method == 'POST':
        # Process form submission for profile updates
        # This is a placeholder - implement actual form handling
        messages.success(request, _("Profile updated successfully."))
        return redirect('sellers:profile_settings')
    
    context = {
        'seller': seller,
        'page_title': 'Profile Settings'
    }
    
    return render(request, 'sellers/profile_settings.html', context)

@login_required
def security_settings(request):
    """Seller security settings."""
    if request.user.role != 'seller':
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        # Process form submission for security updates
        # This is a placeholder - implement actual form handling
        messages.success(request, _("Security settings updated successfully."))
        return redirect('sellers:security_settings')
    
    context = {
        'page_title': 'Security Settings'
    }
    
    return render(request, 'sellers/security_settings.html', context)

@login_required
def notification_settings(request):
    """Seller notification settings."""
    if request.user.role != 'seller':
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        # Process form submission for notification preferences
        # This is a placeholder - implement actual form handling
        messages.success(request, _("Notification preferences updated successfully."))
        return redirect('sellers:notification_settings')
    
    context = {
        'page_title': 'Notification Settings'
    }
    
    return render(request, 'sellers/notification_settings.html', context)

@login_required
def export_inventory(request):
    """Export inventory as CSV."""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="inventory.csv"'
    
    # Get all products with inventory information
    if request.user.role == 'seller':
        products = Product.objects.filter(seller=request.user).order_by('-created_at')
    else:
        products = Product.objects.all().order_by('-created_at')
    
    writer = csv.writer(response)
    writer.writerow(['Product Name', 'SKU', 'Available Quantity', 'Total Quantity', 'Status'])
    
    for product in products:
        status = "In Stock"
        if product.available_quantity == 0:
            status = "Out of Stock"
        elif product.available_quantity < 10:
            status = "Low Stock"
            
        writer.writerow([
            product.name_en,
            product.code,
            product.available_quantity,
            product.total_quantity,
            status
        ])
    
    return response

@login_required
def export_transactions(request):
    """Export financial transactions as CSV."""
    import csv
    from django.http import HttpResponse
    from django.utils.translation import gettext as _
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="financial_transactions.csv"'
    
    # Apply the same filters as in the finance_transactions view
    transaction_type = request.GET.get('type', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Get all transactions for the seller
    try:
        seller = Seller.objects.get(user=request.user)
        # Get orders as transactions
        orders = Order.objects.filter(seller=seller)
        
        # Apply transaction type filter
        filtered_orders = orders
        if transaction_type == 'order_payment':
            # Only include order payments
            filtered_orders = orders.filter(status__in=['completed', 'delivered'])
        elif transaction_type == 'refund':
            # Only include refunds
            filtered_orders = orders.filter(status='cancelled')
        elif transaction_type == 'payout':
            # Currently no payout data in the system
            filtered_orders = Order.objects.none()
        
        # Apply date filters
        if date_from:
            try:
                from datetime import datetime
                date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
                filtered_orders = filtered_orders.filter(date__gte=date_from)
            except ValueError:
                pass
                
        if date_to:
            try:
                from datetime import datetime
                date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
                filtered_orders = filtered_orders.filter(date__lte=date_to)
            except ValueError:
                pass
        
        transactions = []
        
        # Add order payments as transactions
        for order in filtered_orders:
            amount = order.total_price or (order.price_per_unit * order.quantity)
            
            # Skip $0 transactions
            if amount <= 0:
                continue
                
            transaction_type = 'Order Payment'
            is_positive = True
            
            # If it's a cancelled order, treat it as a refund
            if order.status == 'cancelled':
                transaction_type = 'Refund'
                is_positive = False
            
            transactions.append({
                'id': f"ORD-{order.id}",
                'description': f"Order #{order.order_code} Payment",
                'date': order.date,
                'type': _(transaction_type),
                'status': _('Completed') if order.status in ['completed', 'delivered'] else _('Pending') if order.status == 'processing' else _('Cancelled'),
                'amount': amount,
                'is_positive': is_positive
            })
        
        # Sort by date, most recent first
        transactions = sorted(transactions, key=lambda x: x['date'], reverse=True)
        
    except Seller.DoesNotExist:
        # Return an empty CSV if seller doesn't exist
        writer = csv.writer(response)
        writer.writerow(['Transaction ID', 'Description', 'Date', 'Type', 'Status', 'Amount'])
    
    return response

@login_required
def product_update_stock(request, product_id):
    """Update stock levels for a product."""
    product = get_object_or_404(Product, id=product_id)
    
    # Check permissions
    if request.user.role == 'seller' and product.seller != request.user:
        messages.error(request, "You don't have permission to update this product's stock.")
        return redirect('sellers:products')
    
    if request.method == 'POST':
        try:
            total_quantity = int(request.POST.get('total_quantity', 0))
            available_quantity = int(request.POST.get('available_quantity', 0))
            
            # Validate the quantities
            if available_quantity > total_quantity:
                messages.error(request, "Available quantity cannot be greater than total quantity.")
                return render(request, 'sellers/product_update_stock.html', {'product': product})
            
            # Update the product
            product.total_quantity = total_quantity
            product.available_quantity = available_quantity
            product.save()
            
            messages.success(request, f"Stock for {product.name_en} updated successfully.")
            return redirect('sellers:products')
            
        except ValueError:
            messages.error(request, "Please enter valid quantities.")
    
    return render(request, 'sellers/product_update_stock.html', {'product': product})

@login_required
def export_deliveries(request):
    """Export deliveries as CSV."""
    import csv
    from django.http import HttpResponse
    from django.utils.translation import gettext as _
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="deliveries.csv"'
    
    # Use the same filtering logic as in delivery_tracking view
    try:
        seller = Seller.objects.get(user=request.user)
        orders = Order.objects.filter(seller=seller).order_by('-date')
        
        # Get filter parameters
        status_filter = request.GET.get('status', 'all')
        date_filter = request.GET.get('date', 'all')
        courier_filter = request.GET.get('courier', 'all')
        search_query = request.GET.get('search', '')
        
        # Apply status filter
        if status_filter != 'all':
            orders = orders.filter(status=status_filter)
            
        # Apply date filter
        if date_filter == 'today':
            orders = orders.filter(date=timezone.now().date())
        elif date_filter == 'this_week':
            start_of_week = timezone.now().date() - timezone.timedelta(days=timezone.now().weekday())
            orders = orders.filter(date__gte=start_of_week)
        elif date_filter == 'this_month':
            start_of_month = timezone.now().date().replace(day=1)
            orders = orders.filter(date__gte=start_of_month)
        elif date_filter == 'last_month':
            this_month_start = timezone.now().date().replace(day=1)
            last_month_end = this_month_start - timezone.timedelta(days=1)
            last_month_start = last_month_end.replace(day=1)
            orders = orders.filter(date__gte=last_month_start, date__lte=last_month_end)
            
        # Apply search filter
        if search_query:
            orders = orders.filter(
                Q(order_code__icontains=search_query) | 
                Q(customer_name__icontains=search_query) |
                Q(shipping_address__icontains=search_query)
            )
        
        # Write CSV headers
        writer = csv.writer(response)
        writer.writerow([
            _('Order ID'), 
            _('Tracking Number'), 
            _('Courier'), 
            _('Customer'), 
            _('Shipping Address'),
            _('Order Date'),
            _('Shipping Date'),
            _('Status'),
            _('ETA')
        ])
        
        # Write data rows
        for order in orders:
            # Generate tracking number and courier based on order info
            tracking_number = f"TRK-{order.id}-{order.order_code}"
            
            courier = "DHL Express"
            if "UAE" in order.shipping_address or "Dubai" in order.shipping_address:
                courier = "Aramex"
            elif "UK" in order.shipping_address or "London" in order.shipping_address:
                courier = "Royal Mail"
            elif "US" in order.shipping_address:
                courier = "USPS"
                
            # Skip orders that don't match courier filter
            if courier_filter != 'all' and courier_filter.lower() not in courier.lower():
                continue
                
            # Calculate ETA based on status and date
            eta = None
            if order.status == 'pending':
                eta = order.date + timezone.timedelta(days=7)
            elif order.status == 'processing':
                eta = order.date + timezone.timedelta(days=5)
            elif order.status == 'shipped':
                eta = order.date + timezone.timedelta(days=3)
            elif order.status == 'delivered':
                eta = order.date + timezone.timedelta(days=0)
                
            # Format dates for CSV
            order_date = order.date.strftime('%m/%d/%Y') if order.date else ''
            shipping_date = (order.date + timezone.timedelta(days=1)).strftime('%m/%d/%Y') if order.status != 'pending' and order.date else ''
            eta_date = eta.strftime('%m/%d/%Y') if eta else ''
            
            # Translate status for CSV
            status_text = order.status
            if order.status == 'delivered':
                status_text = _('Delivered')
            elif order.status == 'shipped':
                status_text = _('In Transit')
            elif order.status == 'processing':
                status_text = _('Processing')
            elif order.status == 'cancelled':
                status_text = _('Cancelled')
            else:
                status_text = _('Pending')
            
            # Write row
            writer.writerow([
                order.order_code,
                tracking_number,
                courier,
                order.customer_name,
                order.shipping_address,
                order_date,
                shipping_date,
                status_text,
                eta_date
            ])
            
    except Seller.DoesNotExist:
        # Return an empty CSV if seller doesn't exist
        writer = csv.writer(response)
        writer.writerow([
            _('Order ID'), 
            _('Tracking Number'), 
            _('Courier'), 
            _('Customer'), 
            _('Shipping Address'),
            _('Order Date'),
            _('Shipping Date'),
            _('Status'),
            _('ETA')
        ])
    
    return response
