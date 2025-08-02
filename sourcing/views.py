from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Supplier, SourcingRequest
from .forms import SourcingRequestForm, ComprehensiveSourcingForm
from sellers.models import Product


@login_required
def comprehensive_sourcing_create(request):
    """Create a new comprehensive sourcing request."""
    if request.method == 'POST':
        form = ComprehensiveSourcingForm(request.POST)
        if form.is_valid():
            try:
                # Create a new SourcingRequest from form data
                sourcing_request = SourcingRequest()
                
                # Required fields
                sourcing_request.product_name = form.cleaned_data['product_name']
                sourcing_request.carton_quantity = form.cleaned_data['carton_quantity']
                sourcing_request.source_country = form.cleaned_data['source_country']
                sourcing_request.destination_country = form.cleaned_data['destination_country']
                
                # Map funding source to finance_source
                funding_source = form.cleaned_data['funding_source']
                if funding_source == 'seller_funds':
                    sourcing_request.finance_source = 'seller'
                elif funding_source == 'crm_funding':
                    sourcing_request.finance_source = 'company'
                
                # Optional fields
                if form.cleaned_data.get('supplier_name'):
                    sourcing_request.supplier_contact = form.cleaned_data['supplier_name']
                
                if form.cleaned_data.get('supplier_phone'):
                    sourcing_request.supplier_phone = form.cleaned_data['supplier_phone']
                
                if form.cleaned_data.get('target_unit_price'):
                    sourcing_request.cost_per_unit = form.cleaned_data['target_unit_price']
                    sourcing_request.currency = form.cleaned_data.get('currency', 'AED')
                
                # Combine product description and special instructions into notes
                notes_parts = []
                if form.cleaned_data.get('product_description'):
                    notes_parts.append(f"Product Description: {form.cleaned_data['product_description']}")
                
                if form.cleaned_data.get('quality_requirements'):
                    quality_reqs = ', '.join(form.cleaned_data['quality_requirements'])
                    notes_parts.append(f"Quality Requirements: {quality_reqs}")
                
                if form.cleaned_data.get('special_instructions'):
                    notes_parts.append(f"Special Instructions: {form.cleaned_data['special_instructions']}")
                
                if notes_parts:
                    sourcing_request.notes = '\n\n'.join(notes_parts)
                
                # Set default values
                sourcing_request.seller = request.user
                sourcing_request.status = 'submitted'
                sourcing_request.submitted_at = timezone.now()
                sourcing_request.priority = 'medium'
                sourcing_request.unit_quantity = 1  # Default to 1 unit per carton
                
                # Save to database
                sourcing_request.save()
                
                # Check if it's an AJAX request
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': 'Sourcing request created successfully!',
                        'request_id': sourcing_request.id,
                        'request_number': sourcing_request.request_number
                    })
                
                messages.success(request, f'Sourcing request {sourcing_request.request_number} created successfully!')
                return redirect('sourcing:request_detail', request_id=sourcing_request.id)
                
            except Exception as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': f'Error creating sourcing request: {str(e)}'
                    }, status=400)
                
                messages.error(request, f'Error creating sourcing request: {str(e)}')
        else:
            # Check if it's an AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': 'Form validation failed',
                    'errors': form.errors
                }, status=400)
    else:
        form = ComprehensiveSourcingForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'sourcing/comprehensive_request_create.html', context)


@login_required
def sourcing_dashboard(request):
    """Sourcing dashboard view."""
    # Get real data from database
    total_requests = SourcingRequest.objects.count()
    pending_requests = SourcingRequest.objects.filter(status='submitted').count()
    approved_requests = SourcingRequest.objects.filter(status='approved').count()
    total_suppliers = Supplier.objects.filter(is_active=True).count()
    
    # Recent requests
    recent_requests = SourcingRequest.objects.select_related('seller', 'supplier').order_by('-created_at')[:5]
    
    # Status distribution
    status_counts = SourcingRequest.objects.values('status').annotate(count=Count('status'))
    
    # Top suppliers by orders
    top_suppliers = Supplier.objects.filter(is_active=True).order_by('-total_orders')[:5]
    
    context = {
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
        'total_suppliers': total_suppliers,
        'recent_requests': recent_requests,
        'status_counts': status_counts,
        'top_suppliers': top_suppliers,
    }
    
    return render(request, 'sourcing/dashboard.html', context)


@login_required
def sourcing_request_create(request):
    """Create a new sourcing request."""
    # Get products for dropdowns
    products = Product.objects.all().order_by('name_en')
    
    if request.method == 'POST':
        form = SourcingRequestForm(request.POST, request.FILES)
        if form.is_valid():
            request_obj = form.save(commit=False)
            request_obj.seller = request.user
            request_obj.status = 'submitted'
            request_obj.submitted_at = timezone.now()
            
            # Handle form-specific fields
            request_type = form.cleaned_data.get('request_type')
            quantity = form.cleaned_data.get('quantity')
            target_date = form.cleaned_data.get('target_date')
            budget = form.cleaned_data.get('budget')
            
            # Set product name based on request type
            if request_type == 'new_product':
                request_obj.product_name = form.cleaned_data.get('new_product_name')
            elif request_type in ['replenishment', 'sample']:
                product_id = form.cleaned_data.get('product')
                if product_id:
                    try:
                        product = Product.objects.get(id=product_id)
                        request_obj.product_name = product.name_en
                    except Product.DoesNotExist:
                        pass
            
            # Set quantities
            request_obj.carton_quantity = quantity
            request_obj.unit_quantity = quantity
            
            # Set target date and budget in notes if provided
            notes_parts = []
            if target_date:
                notes_parts.append(f"Target Date: {target_date}")
            if budget:
                notes_parts.append(f"Budget: {budget} AED")
            
            if notes_parts:
                existing_notes = form.cleaned_data.get('notes', '')
                if existing_notes:
                    notes_parts.insert(0, existing_notes)
                request_obj.notes = '\n'.join(notes_parts)
            
            request_obj.save()
            
            # Check if it's an AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Sourcing request created successfully!',
                    'request_id': request_obj.id
                })
            
            messages.success(request, f'Sourcing request created successfully!')
            return redirect('sourcing:request_detail', request_id=request_obj.id)
        else:
            # Check if it's an AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': 'Form validation failed',
                    'errors': form.errors
                })
    else:
        form = SourcingRequestForm()
    
    # Update form choices with real data
    form.fields['product'].choices = [('', 'Select a product')] + [(p.id, f"{p.name_en} ({p.code})") for p in products]
    
    context = {
        'form': form,
        'products': products,
    }
    
    return render(request, 'sourcing/request_create.html', context)


@login_required
def sourcing_request_list(request):
    """List all sourcing requests with filtering and pagination."""
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    search_query = request.GET.get('search', '')
    
    # Base queryset
    requests = SourcingRequest.objects.select_related('seller', 'supplier').order_by('-created_at')
    
    # Apply filters
    if status_filter:
        requests = requests.filter(status=status_filter)
    
    if priority_filter:
        requests = requests.filter(priority=priority_filter)
    
    if search_query:
        requests = requests.filter(
            Q(request_number__icontains=search_query) |
            Q(product_name__icontains=search_query) |
            Q(seller__first_name__icontains=search_query) |
            Q(seller__last_name__icontains=search_query) |
            Q(supplier__name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(requests, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter options
    status_choices = SourcingRequest.STATUS_CHOICES
    priority_choices = SourcingRequest.PRIORITY_CHOICES
    
    # Get products for the modal form
    products = Product.objects.all().order_by('name_en')
    
    context = {
        'page_obj': page_obj,
        'status_choices': status_choices,
        'priority_choices': priority_choices,
        'current_status': status_filter,
        'current_priority': priority_filter,
        'search_query': search_query,
        'products': products,
    }
    
    return render(request, 'sourcing/request_list.html', context)


@login_required
def sourcing_request_detail(request, request_id):
    """View sourcing request details."""
    request_obj = get_object_or_404(SourcingRequest, id=request_id)
    
    # Check if user has permission to view this request
    if not request.user.is_superuser and request_obj.seller != request.user:
        messages.error(request, 'You do not have permission to view this request.')
        return redirect('sourcing:requests')
    
    return render(request, 'sourcing/request_detail.html', {'request_obj': request_obj})


@login_required
def approve_sourcing_request(request, request_id):
    """Approve a sourcing request."""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    try:
        request_obj = get_object_or_404(SourcingRequest, id=request_id)
        
        if request_obj.status != 'submitted':
            return JsonResponse({'success': False, 'error': 'Request cannot be approved in its current status'})
        
        request_obj.status = 'approved'
        request_obj.approved_by = request.user
        request_obj.approved_at = timezone.now()
        request_obj.save()
        
        return JsonResponse({'success': True, 'message': 'Request approved successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def reject_sourcing_request(request, request_id):
    """Reject a sourcing request."""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    try:
        request_obj = get_object_or_404(SourcingRequest, id=request_id)
        
        if request_obj.status != 'submitted':
            return JsonResponse({'success': False, 'error': 'Request cannot be rejected in its current status'})
        
        request_obj.status = 'rejected'
        request_obj.save()
        
        return JsonResponse({'success': True, 'message': 'Request rejected successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def suppliers_list(request):
    """List all suppliers with filtering and pagination."""
    # Get filter parameters
    category_filter = request.GET.get('category', '')
    country_filter = request.GET.get('country', '')
    search_query = request.GET.get('search', '')
    
    # Base queryset
    suppliers = Supplier.objects.filter(is_active=True).order_by('-created_at')
    
    # Apply filters
    if category_filter and category_filter != 'all':
        suppliers = suppliers.filter(category=category_filter)
    
    if country_filter and country_filter != 'all':
        suppliers = suppliers.filter(country=country_filter)
    
    if search_query:
        suppliers = suppliers.filter(
            Q(name__icontains=search_query) |
            Q(contact_person__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(suppliers, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter options
    categories = Supplier.objects.values_list('category', flat=True).distinct()
    countries = Supplier.objects.values_list('country', flat=True).distinct()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'countries': countries,
        'current_category': category_filter,
        'current_country': country_filter,
        'search_query': search_query,
    }
    
    return render(request, 'sourcing/suppliers.html', context)


@login_required
@csrf_exempt
def add_supplier(request):
    """Add a new supplier."""
    if request.method == 'POST':
        try:
            # Get data from request
            if request.headers.get('Content-Type') == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST.dict()
            
            # Create new supplier
            supplier = Supplier(
                name=data.get('name', ''),
                contact_person=data.get('contact_person', ''),
                email=data.get('email', ''),
                phone=data.get('phone', ''),
                country=data.get('country', ''),
                category=data.get('category', 'General'),
                created_by=request.user
            )
            
            # Save to database
            supplier.save()
            
            # Return success response
            return JsonResponse({
                'success': True,
                'message': 'Supplier added successfully!',
                'supplier_id': supplier.id,
                'supplier_name': supplier.name
            })
            
        except Exception as e:
            # Return error response
            return JsonResponse({
                'success': False,
                'message': f'Error adding supplier: {str(e)}'
            }, status=400)
    
    # Return error for non-POST requests
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    }, status=405)


@login_required
@csrf_exempt
def view_supplier(request, supplier_id):
    """View supplier details."""
    try:
        supplier = get_object_or_404(Supplier, id=supplier_id, is_active=True)
        
        # Return supplier data as JSON
        return JsonResponse({
            'success': True,
            'supplier': {
                'id': supplier.id,
                'name': supplier.name,
                'contact_person': supplier.contact_person or '',
                'email': supplier.email or '',
                'phone': supplier.phone or '',
                'address': supplier.address or '',
                'country': supplier.country,
                'category': supplier.category,
                'quality_score': float(supplier.quality_score),
                'delivery_score': float(supplier.delivery_score),
                'price_score': float(supplier.price_score),
                'total_orders': supplier.total_orders,
                'created_at': supplier.created_at.strftime('%Y-%m-%d %H:%M')
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error retrieving supplier: {str(e)}'
        }, status=400)


@login_required
@csrf_exempt
def edit_supplier(request, supplier_id):
    """Edit supplier details."""
    supplier = get_object_or_404(Supplier, id=supplier_id, is_active=True)
    
    if request.method == 'GET':
        # Return supplier data for editing
        return JsonResponse({
            'success': True,
            'supplier': {
                'id': supplier.id,
                'name': supplier.name,
                'contact_person': supplier.contact_person or '',
                'email': supplier.email or '',
                'phone': supplier.phone or '',
                'address': supplier.address or '',
                'country': supplier.country,
                'category': supplier.category
            }
        })
    
    elif request.method == 'POST':
        try:
            # Get data from request
            if request.headers.get('Content-Type') == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST.dict()
            
            # Update supplier fields
            supplier.name = data.get('name', supplier.name)
            supplier.contact_person = data.get('contact_person', supplier.contact_person)
            supplier.email = data.get('email', supplier.email)
            supplier.phone = data.get('phone', supplier.phone)
            supplier.address = data.get('address', supplier.address)
            supplier.country = data.get('country', supplier.country)
            supplier.category = data.get('category', supplier.category)
            
            # Save changes
            supplier.save()
            
            # Return success response
            return JsonResponse({
                'success': True,
                'message': 'Supplier updated successfully!',
                'supplier_id': supplier.id,
                'supplier_name': supplier.name
            })
            
        except Exception as e:
            # Return error response
            return JsonResponse({
                'success': False,
                'message': f'Error updating supplier: {str(e)}'
            }, status=400)
    
    # Return error for other request methods
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    }, status=405)


@login_required
@csrf_exempt
def delete_supplier(request, supplier_id):
    """Delete a supplier (mark as inactive)."""
    if request.method == 'POST':
        try:
            supplier = get_object_or_404(Supplier, id=supplier_id)
            
            # Check if supplier has any associated sourcing requests
            active_requests = supplier.sourcing_requests.exclude(
                status__in=['completed', 'cancelled', 'rejected']
            ).count()
            
            if active_requests > 0:
                return JsonResponse({
                    'success': False,
                    'message': f'Cannot delete supplier: {supplier.name} has {active_requests} active sourcing requests.'
                }, status=400)
            
            # Mark supplier as inactive instead of deleting
            supplier.is_active = False
            supplier.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Supplier "{supplier.name}" deleted successfully.'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error deleting supplier: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    }, status=405)
