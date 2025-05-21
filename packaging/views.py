from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def dashboard(request):
    """Packaging dashboard."""
    return render(request, 'packaging/dashboard.html')

@login_required
def order_list(request):
    """List of orders for packaging."""
    return render(request, 'packaging/order_list.html')
