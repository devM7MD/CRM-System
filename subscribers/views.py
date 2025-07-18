from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from users.models import User
from .models import Subscriber
from .forms import SubscriberForm

@login_required
def subscribers_list(request):
    """Display all users and subscribers in a table format"""
    
    # Get search and filter parameters
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    country_filter = request.GET.get('country', '')
    sort_by = request.GET.get('sort_by', '-date_joined')
    
    # Start with all users
    users = User.objects.all()
    
    # Apply search filter
    if search_query:
        users = users.filter(
            Q(full_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone_number__icontains=search_query) |
            Q(company_name__icontains=search_query)
        )
    
    # Apply status filter
    if status_filter:
        if status_filter == 'active':
            users = users.filter(is_active=True)
        elif status_filter == 'inactive':
            users = users.filter(is_active=False)
    
    # Apply country filter
    if country_filter:
        users = users.filter(country__icontains=country_filter)
    
    # Apply sorting
    if sort_by == 'name':
        users = users.order_by('full_name')
    elif sort_by == 'email':
        users = users.order_by('email')
    elif sort_by == 'date_joined':
        users = users.order_by('date_joined')
    elif sort_by == '-date_joined':
        users = users.order_by('-date_joined')
    else:
        users = users.order_by('-date_joined')
    
    # Pagination
    paginator = Paginator(users, 25)  # Show 25 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get unique countries for filter dropdown
    countries = User.objects.exclude(country__isnull=True).exclude(country='').values_list('country', flat=True).distinct().order_by('country')
    
    # Get statistics
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    recent_users = User.objects.filter(date_joined__gte=timezone.now() - timezone.timedelta(days=30)).count()
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'country_filter': country_filter,
        'sort_by': sort_by,
        'countries': countries,
        'total_users': total_users,
        'active_users': active_users,
        'recent_users': recent_users,
    }
    
    return render(request, 'subscribers/subscribers.html', context)

@login_required
def add_user(request):
    """Add a new user/subscriber"""
    if request.method == 'POST':
        form = SubscriberForm(request.POST)
        if form.is_valid():
            subscriber = form.save()
            messages.success(request, f'User "{subscriber.full_name}" has been added successfully!')
            return redirect('subscribers:list')
    else:
        form = SubscriberForm()
    
    context = {
        'form': form,
        'title': 'Add New User'
    }
    
    return render(request, 'subscribers/add_user.html', context)

@login_required
def view_details(request, user_id):
    """View detailed information about a user"""
    user = get_object_or_404(User, id=user_id)
    
    # Get user's roles
    user_roles = user.user_roles.filter(is_active=True)
    
    # Get user's recent activity (last 10 logins)
    recent_activity = user.audit_logs.all()[:10]
    
    context = {
        'user': user,
        'user_roles': user_roles,
        'recent_activity': recent_activity,
    }
    
    return render(request, 'subscribers/user_detail.html', context)

@login_required
def edit_user(request, user_id):
    """Edit user information"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        # Update user fields
        user.full_name = request.POST.get('full_name', user.full_name)
        user.email = request.POST.get('email', user.email)
        user.phone_number = request.POST.get('phone_number', user.phone_number)
        user.company_name = request.POST.get('company_name', user.company_name)
        user.country = request.POST.get('country', user.country)
        user.is_active = request.POST.get('is_active') == 'on'
        
        user.save()
        messages.success(request, f'User "{user.full_name}" has been updated successfully!')
        return redirect('subscribers:list')
    
    context = {
        'user': user,
        'title': 'Edit User'
    }
    
    return render(request, 'subscribers/edit_user.html', context)

@login_required
def delete_user(request, user_id):
    """Delete a user"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user_name = user.full_name
        user.delete()
        messages.success(request, f'User "{user_name}" has been deleted successfully!')
        return redirect('subscribers:list')
    
    context = {
        'user': user,
        'title': 'Delete User'
    }
    
    return render(request, 'subscribers/delete_user.html', context)

@login_required
def toggle_user_status(request, user_id):
    """Toggle user active/inactive status"""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        user.is_active = not user.is_active
        user.save()
        
        status = 'activated' if user.is_active else 'deactivated'
        return JsonResponse({
            'success': True,
            'message': f'User has been {status} successfully!',
            'is_active': user.is_active
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
def export_users(request):
    """Export users data to CSV"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Full Name', 'Email', 'Phone Number', 'Business Name', 'Country', 'Date Joined', 'Status'])
    
    users = User.objects.all().order_by('-date_joined')
    for user in users:
        writer.writerow([
            user.full_name,
            user.email,
            user.phone_number,
            user.company_name or '',
            user.country or '',
            user.date_joined.strftime('%Y-%m-%d'),
            'Active' if user.is_active else 'Inactive'
        ])
    
    return response 