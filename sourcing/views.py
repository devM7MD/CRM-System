from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Supplier, SourcingRequest
from .forms import SupplierForm

# Create your views here.

@login_required
def sourcing_dashboard(request):
    """Sourcing dashboard view."""
    # Get statistics for the dashboard
    total_suppliers = Supplier.objects.filter(is_active=True).count()
    
    # Get recent requests
    recent_requests = SourcingRequest.objects.all().order_by('-created_at')[:5]
    
    # Get counts by status
    pending_requests = SourcingRequest.objects.filter(status='pending').count()
    approved_requests = SourcingRequest.objects.filter(status='approved').count()
    
    context = {
        'total_suppliers': total_suppliers,
        'recent_requests': recent_requests,
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
    }
    
    return render(request, 'sourcing/dashboard.html', context)

@login_required
def sourcing_request_list(request):
    """List all sourcing requests."""
    return render(request, 'sourcing/request_list.html')

@login_required
def sourcing_request_create(request):
    """Create a new sourcing request."""
    return render(request, 'sourcing/request_create.html')

@login_required
def sourcing_request_detail(request, request_id):
    """View details of a specific sourcing request."""
    return render(request, 'sourcing/request_detail.html', {'request_id': request_id})

@login_required
def suppliers_list(request):
    """List all suppliers."""
    suppliers = Supplier.objects.all().order_by('name')
    return render(request, 'sourcing/suppliers.html', {'suppliers': suppliers})

@login_required
def supplier_create(request):
    """Create a new supplier."""
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save(commit=False)
            supplier.created_by = request.user
            supplier.save()
            messages.success(request, f"Supplier '{supplier.name}' created successfully.")
            return redirect('sourcing:suppliers')
    else:
        form = SupplierForm()
    
    return render(request, 'sourcing/supplier_create.html', {'form': form})

@login_required
def supplier_detail(request, supplier_id):
    """View a specific supplier."""
    supplier = get_object_or_404(Supplier, id=supplier_id)
    sourcing_requests = SourcingRequest.objects.filter(supplier=supplier).order_by('-created_at')
    
    return render(request, 'sourcing/supplier_detail.html', {
        'supplier': supplier,
        'sourcing_requests': sourcing_requests,
    })

@login_required
def supplier_edit(request, supplier_id):
    """Edit a specific supplier."""
    supplier = get_object_or_404(Supplier, id=supplier_id)
    
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, f"Supplier '{supplier.name}' updated successfully.")
            return redirect('sourcing:supplier_detail', supplier_id=supplier.id)
    else:
        form = SupplierForm(instance=supplier)
    
    return render(request, 'sourcing/supplier_edit.html', {
        'form': form,
        'supplier': supplier,
    })
