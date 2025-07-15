from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def dashboard(request):
    """Delivery dashboard."""
    return render(request, 'delivery/dashboard.html')

@login_required
def order_list(request):
    """List of orders for delivery."""
    return render(request, 'delivery/order_list.html')
