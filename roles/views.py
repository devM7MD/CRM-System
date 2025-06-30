# Placeholder for roles views

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils.text import slugify
from django.db.models import Count
from django.core.paginator import Paginator
from .models import Role, Permission
from users.models import User
import json

def is_super_admin(user):
    """Check if user is a super admin."""
    return user.is_superuser or (user.role and user.role.slug == 'super-admin')

@login_required
@user_passes_test(is_super_admin)
def role_list(request):
    """List all roles with filtering options."""
    roles = Role.objects.annotate(user_count=Count('users'))
    
    # Pagination
    paginator = Paginator(roles, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'roles/role_list.html', {
        'page_obj': page_obj
    })

@login_required
@user_passes_test(is_super_admin)
def role_detail(request, slug):
    """View role details."""
    role = get_object_or_404(Role, slug=slug)
    users = User.objects.filter(role=role)[:10]  # Limit to 10 users
    
    return render(request, 'roles/role_detail.html', {
        'role': role,
        'users': users,
        'user_count': User.objects.filter(role=role).count()
    })

@login_required
@user_passes_test(is_super_admin)
def create_role(request):
    """Create a new role."""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        slug = slugify(name)
        
        # Check if role with this slug already exists
        if Role.objects.filter(slug=slug).exists():
            messages.error(request, f"A role with the name '{name}' already exists.")
            return redirect('roles:create_role')
        
        # Get selected permissions
        permission_ids = request.POST.getlist('permissions')
        
        # Get required fields configuration
        required_fields = {}
        for field in request.POST.getlist('required_fields'):
            required_fields[field] = True
        
        # Create the role
        role = Role.objects.create(
            name=name,
            slug=slug,
            description=description,
            required_fields=required_fields
        )
        
        # Add permissions
        if permission_ids:
            permissions = Permission.objects.filter(id__in=permission_ids)
            role.permissions.set(permissions)
        
        messages.success(request, f"Role '{name}' created successfully.")
        return redirect('roles:role_list')
    
    # Get all permissions grouped by category
    permissions = {}
    for category, category_name in Permission.CATEGORY_CHOICES:
        permissions[category] = {
            'name': category_name,
            'permissions': Permission.objects.filter(category=category)
        }
    
    # Define available fields that can be required for a role
    available_fields = [
        {'name': 'company_name', 'label': 'Company Name'},
        {'name': 'country', 'label': 'Country'},
        {'name': 'expected_daily_orders', 'label': 'Expected Daily Orders'},
        {'name': 'warehouse', 'label': 'Warehouse'},
        {'name': 'delivery_company', 'label': 'Delivery Company'},
        {'name': 'call_center_team', 'label': 'Call Center Team'},
        {'name': 'accounting_department', 'label': 'Accounting Department'},
    ]
    
    return render(request, 'roles/create_role.html', {
        'permissions': permissions,
        'available_fields': available_fields
    })

@login_required
@user_passes_test(is_super_admin)
def edit_role(request, slug):
    """Edit an existing role."""
    role = get_object_or_404(Role, slug=slug)
    
    # Prevent editing system roles
    if role.is_system_role and not request.user.is_superuser:
        messages.error(request, "System roles cannot be edited.")
        return redirect('roles:role_list')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        # Update role
        role.name = name
        role.description = description
        
        # Only update slug if it's not a system role
        if not role.is_system_role:
            new_slug = slugify(name)
            # Check if the new slug already exists for another role
            if new_slug != role.slug and Role.objects.filter(slug=new_slug).exists():
                messages.error(request, f"A role with the name '{name}' already exists.")
                return redirect('roles:edit_role', slug=role.slug)
            role.slug = new_slug
        
        # Get selected permissions
        permission_ids = request.POST.getlist('permissions')
        permissions = Permission.objects.filter(id__in=permission_ids)
        role.permissions.set(permissions)
        
        # Get required fields configuration
        required_fields = {}
        for field in request.POST.getlist('required_fields'):
            required_fields[field] = True
        role.required_fields = required_fields
        
        role.save()
        
        messages.success(request, f"Role '{name}' updated successfully.")
        return redirect('roles:role_detail', slug=role.slug)
    
    # Get all permissions grouped by category
    permissions = {}
    for category, category_name in Permission.CATEGORY_CHOICES:
        category_permissions = Permission.objects.filter(category=category)
        permissions[category] = {
            'name': category_name,
            'permissions': category_permissions,
            'selected': [p.id for p in category_permissions if p in role.permissions.all()]
        }
    
    # Define available fields that can be required for a role
    available_fields = [
        {'name': 'company_name', 'label': 'Company Name', 'required': role.required_fields.get('company_name', False)},
        {'name': 'country', 'label': 'Country', 'required': role.required_fields.get('country', False)},
        {'name': 'expected_daily_orders', 'label': 'Expected Daily Orders', 'required': role.required_fields.get('expected_daily_orders', False)},
        {'name': 'warehouse', 'label': 'Warehouse', 'required': role.required_fields.get('warehouse', False)},
        {'name': 'delivery_company', 'label': 'Delivery Company', 'required': role.required_fields.get('delivery_company', False)},
        {'name': 'call_center_team', 'label': 'Call Center Team', 'required': role.required_fields.get('call_center_team', False)},
        {'name': 'accounting_department', 'label': 'Accounting Department', 'required': role.required_fields.get('accounting_department', False)},
    ]
    
    return render(request, 'roles/edit_role.html', {
        'role': role,
        'permissions': permissions,
        'available_fields': available_fields
    })

@login_required
@user_passes_test(is_super_admin)
def delete_role(request, slug):
    """Delete a role."""
    role = get_object_or_404(Role, slug=slug)
    
    # Prevent deleting system roles
    if role.is_system_role:
        messages.error(request, "System roles cannot be deleted.")
        return redirect('roles:role_list')
    
    if request.method == 'POST':
        name = role.name
        
        # Check if there are users with this role
        if User.objects.filter(role=role).exists():
            messages.error(request, f"Cannot delete role '{name}' because it is assigned to users.")
            return redirect('roles:role_list')
        
        # Delete the role
        role.delete()
        messages.success(request, f"Role '{name}' deleted successfully.")
        return redirect('roles:role_list')
    
    return render(request, 'roles/delete_role.html', {'role': role})
