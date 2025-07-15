from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .models import Warehouse

@login_required
def warehouse_list(request):
    """View all warehouses."""
    warehouses = Warehouse.objects.all()
    return render(request, 'warehouse/warehouse_list.html', {'warehouses': warehouses})

@login_required
def warehouse_detail(request, pk):
    """View warehouse details."""
    warehouse = get_object_or_404(Warehouse, pk=pk)
    return render(request, 'warehouse/warehouse_detail.html', {'warehouse': warehouse})

@login_required
def add_warehouse(request):
    """Add a new warehouse."""
    if request.method == 'POST':
        name = request.POST.get('name')
        location = request.POST.get('location')
        description = request.POST.get('description', '')
        
        if not name or not location:
            messages.error(request, _('Name and location are required.'))
            return redirect('warehouse:add_warehouse')
        
        warehouse = Warehouse.objects.create(
            name=name,
            location=location,
            description=description
        )
        
        messages.success(request, _('Warehouse created successfully.'))
        return redirect('warehouse:warehouse_list')
    
    return render(request, 'warehouse/add_warehouse.html')

@login_required
def edit_warehouse(request, pk):
    """Edit an existing warehouse."""
    warehouse = get_object_or_404(Warehouse, pk=pk)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        location = request.POST.get('location')
        description = request.POST.get('description', '')
        is_active = request.POST.get('is_active') == 'on'
        
        if not name or not location:
            messages.error(request, _('Name and location are required.'))
            return redirect('warehouse:edit_warehouse', pk=pk)
        
        warehouse.name = name
        warehouse.location = location
        warehouse.description = description
        warehouse.is_active = is_active
        warehouse.save()
        
        messages.success(request, _('Warehouse updated successfully.'))
        return redirect('warehouse:warehouse_detail', pk=pk)
    
    return render(request, 'warehouse/edit_warehouse.html', {'warehouse': warehouse})

@login_required
def delete_warehouse(request, pk):
    """Delete a warehouse."""
    warehouse = get_object_or_404(Warehouse, pk=pk)
    
    if request.method == 'POST':
        warehouse.delete()
        messages.success(request, _('Warehouse deleted successfully.'))
        return redirect('warehouse:warehouse_list')
    
    return render(request, 'warehouse/delete_warehouse.html', {'warehouse': warehouse})

@login_required
def warehouse_dashboard(request):
    """Warehouse dashboard view."""
    warehouses = Warehouse.objects.all()
    active_warehouses = warehouses.filter(is_active=True).count()
    
    context = {
        'warehouses': warehouses,
        'total_warehouses': warehouses.count(),
        'active_warehouses': active_warehouses
    }
    
    return render(request, 'warehouse/dashboard.html', context) 