from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def sourcing_dashboard(request):
    """Sourcing dashboard view."""
    return render(request, 'sourcing/dashboard.html')

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
    return render(request, 'sourcing/suppliers.html')
