from django.shortcuts import render, redirect
from django.contrib.auth import logout

def dashboard(request):
    return render(request, 'pages/dashboard/index.html')

def users(request):
    return render(request, 'pages/users/list.html')

def roles(request):
    return render(request, 'pages/roles/list.html')

def orders(request):
    return render(request, 'pages/orders/list.html')

def delivery(request):
    return render(request, 'pages/delivery/list.html')

def sourcing(request):
    return render(request, 'pages/sourcing/list.html')

def warehouses(request):
    return render(request, 'pages/warehouses/list.html')

def inventory(request):
    return render(request, 'pages/inventory/list.html')

def finances(request):
    return render(request, 'pages/finances/list.html')

def marketplace(request):
    # Placeholder view for marketplace
    return render(request, 'pages/base.html', {'title': 'Marketplace'})

def affiliate(request):
    # Placeholder view for affiliate
    return render(request, 'pages/base.html', {'title': 'Affiliate'})

def atlasdrop(request):
    # Placeholder view for atlasdrop
    return render(request, 'pages/base.html', {'title': 'AtlasDrop'})

def settings(request):
    # Placeholder view for settings
    return render(request, 'pages/base.html', {'title': 'Settings'})

def logout_view(request):
    # logout(request)
    # Redirect to login page (assuming it's at the root)
    return redirect('/')