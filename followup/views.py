from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import os
from django.conf import settings

# Create your views here.

@login_required
def dashboard(request):
    """Followup dashboard."""
    template_path = os.path.join(settings.BASE_DIR, 'templates', 'followup', 'dashboard.html')
    
    # Check if template exists
    if os.path.exists(template_path):
        print(f"Template exists at: {template_path}")
    else:
        print(f"Template does not exist at: {template_path}")
        
    return render(request, 'followup/dashboard.html')

@login_required
def order_list(request):
    """List of orders for followup."""
    template_path = os.path.join(settings.BASE_DIR, 'templates', 'followup', 'order_list.html')
    
    # Check if template exists
    if os.path.exists(template_path):
        print(f"Template exists at: {template_path}")
    else:
        print(f"Template does not exist at: {template_path}")
        
    return render(request, 'followup/order_list.html')
