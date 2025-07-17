from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from .models import Role, Permission, RolePermission, UserRole, RoleAuditLog
from users.models import User

def role_required(role_name):
    """Decorator to check if user has a specific role"""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            # Allow superusers and users with Admin role
            if (request.user.is_superuser or 
                request.user.has_role('Admin') or 
                request.user.has_role(role_name)):
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, f"You don't have permission to access this page. Required role: {role_name}")
                return redirect('dashboard:index')
        return wrapper
    return decorator

@login_required
def role_list(request):
    """List all roles"""
    # Only allow superusers and admin users to view roles
    if not (request.user.is_superuser or request.user.has_role('Admin')):
        messages.error(request, "You don't have permission to access this page.")
        return redirect('dashboard:index')
    
    roles = Role.objects.all().order_by('name')
    
    # Search functionality
    search = request.GET.get('search', '')
    if search:
        roles = roles.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(role_type__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(roles, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'roles': page_obj,
        'search': search,
        'total_roles': roles.count(),
    }
    return render(request, 'roles/role_list.html', context)

@login_required
@role_required('Super Admin')
def role_create(request):
    """Create a new role"""
    if request.method == 'POST':
        name = request.POST.get('name')
        role_type = request.POST.get('role_type')
        description = request.POST.get('description', '')
        
        if not name or not role_type:
            messages.error(request, 'Role name and type are required.')
            return redirect('roles:role_create')
        
        # Check if role name already exists
        if Role.objects.filter(name=name).exists():
            messages.error(request, 'A role with this name already exists.')
            return redirect('roles:role_create')
        
        try:
            role = Role.objects.create(
                name=name,
                role_type=role_type,
                description=description,
                created_by=request.user
            )
            
            # Create audit log
            RoleAuditLog.objects.create(
                action='role_created',
                user=request.user,
                role=role,
                description=f'Role "{role.name}" was created by {request.user.get_full_name()}',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            messages.success(request, f'Role "{role.name}" created successfully.')
            return redirect('roles:role_detail', role_id=role.id)
            
        except Exception as e:
            messages.error(request, f'Error creating role: {str(e)}')
            return redirect('roles:role_create')
    
    context = {
        'role_types': Role.ROLE_TYPES,
    }
    return render(request, 'roles/role_form.html', context)

@login_required
@role_required('Super Admin')
def role_edit(request, role_id):
    """Edit an existing role"""
    role = get_object_or_404(Role, id=role_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        role_type = request.POST.get('role_type')
        description = request.POST.get('description', '')
        is_active = request.POST.get('is_active') == 'on'
        
        if not name or not role_type:
            messages.error(request, 'Role name and type are required.')
            return redirect('roles:role_edit', role_id=role_id)
        
        # Check if role name already exists (excluding current role)
        if Role.objects.filter(name=name).exclude(id=role_id).exists():
            messages.error(request, 'A role with this name already exists.')
            return redirect('roles:role_edit', role_id=role_id)
        
        try:
            old_name = role.name
            role.name = name
            role.role_type = role_type
            role.description = description
            role.is_active = is_active
            role.save()
            
            # Create audit log
            RoleAuditLog.objects.create(
                action='role_updated',
                user=request.user,
                role=role,
                description=f'Role "{old_name}" was updated to "{role.name}" by {request.user.get_full_name()}',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            messages.success(request, f'Role "{role.name}" updated successfully.')
            return redirect('roles:role_detail', role_id=role.id)
            
        except Exception as e:
            messages.error(request, f'Error updating role: {str(e)}')
            return redirect('roles:role_edit', role_id=role_id)
    
    context = {
        'role': role,
        'role_types': Role.ROLE_TYPES,
    }
    return render(request, 'roles/role_form.html', context)

@login_required
@role_required('Super Admin')
def role_detail(request, role_id):
    """View role details and permissions"""
    role = get_object_or_404(Role, id=role_id)
    role_permissions = role.role_permissions.all().order_by('permission__module', 'permission__permission_type')
    users_with_role = role.users.filter(is_active=True)
    
    # Get all available permissions for this role
    all_permissions = Permission.objects.filter(is_active=True).order_by('module', 'permission_type')
    
    context = {
        'role': role,
        'role_permissions': role_permissions,
        'users_with_role': users_with_role,
        'all_permissions': all_permissions,
    }
    return render(request, 'roles/role_detail.html', context)

@login_required
@role_required('Super Admin')
def role_delete(request, role_id):
    """Delete a role"""
    role = get_object_or_404(Role, id=role_id)
    
    if request.method == 'POST':
        try:
            role_name = role.name
            role.delete()
            
            # Create audit log
            RoleAuditLog.objects.create(
                action='role_deleted',
                user=request.user,
                description=f'Role "{role_name}" was deleted by {request.user.get_full_name()}',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            messages.success(request, f'Role "{role_name}" deleted successfully.')
            return redirect('roles:role_list')
            
        except Exception as e:
            messages.error(request, f'Error deleting role: {str(e)}')
            return redirect('roles:role_detail', role_id=role_id)
    
    context = {
        'role': role,
    }
    return render(request, 'roles/role_confirm_delete.html', context)

@login_required
@role_required('Super Admin')
def update_role_permissions(request, role_id):
    """Update permissions for a role"""
    if request.method == 'POST':
        role = get_object_or_404(Role, id=role_id)
        permissions_data = request.POST.getlist('permissions')
        
        try:
            # Clear existing permissions
            role.role_permissions.all().delete()
            
            # Add new permissions
            for permission_id in permissions_data:
                if permission_id:
                    permission = Permission.objects.get(id=permission_id)
                    RolePermission.objects.create(
                        role=role,
                        permission=permission,
                        granted=True,
                        granted_by=request.user
                    )
            
            # Create audit log
            RoleAuditLog.objects.create(
                action='permission_granted',
                user=request.user,
                role=role,
                description=f'Permissions updated for role "{role.name}" by {request.user.get_full_name()}',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            messages.success(request, f'Permissions for role "{role.name}" updated successfully.')
            
        except Exception as e:
            messages.error(request, f'Error updating permissions: {str(e)}')
        
        return redirect('roles:role_detail', role_id=role_id)
    
    return redirect('roles:role_list')

@login_required
@role_required('Super Admin')
def assign_user_role(request, user_id):
    """Assign a role to a user"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        role_id = request.POST.get('role')
        is_primary = request.POST.get('is_primary') == 'on'
        
        if not role_id:
            messages.error(request, 'Please select a role.')
            return redirect('users:user_detail', user_id=user_id)
        
        try:
            role = Role.objects.get(id=role_id)
            
            # If this is a primary role, remove primary from other roles
            if is_primary:
                UserRole.objects.filter(user=user, is_primary=True).update(is_primary=False)
            
            # Create or update user role
            user_role, created = UserRole.objects.get_or_create(
                user=user,
                role=role,
                defaults={
                    'is_primary': is_primary,
                    'assigned_by': request.user
                }
            )
            
            if not created:
                user_role.is_primary = is_primary
                user_role.save()
            
            # Create audit log
            action = 'user_role_assigned' if created else 'user_role_updated'
            RoleAuditLog.objects.create(
                action=action,
                user=request.user,
                role=role,
                target_user=user,
                description=f'Role "{role.name}" was assigned to {user.get_full_name()} by {request.user.get_full_name()}',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            messages.success(request, f'Role "{role.name}" assigned to {user.get_full_name()} successfully.')
            
        except Exception as e:
            messages.error(request, f'Error assigning role: {str(e)}')
        
        return redirect('users:user_detail', user_id=user_id)
    
    roles = Role.objects.filter(is_active=True).order_by('name')
    user_roles = user.user_roles.all()
    
    context = {
        'user': user,
        'roles': roles,
        'user_roles': user_roles,
    }
    return render(request, 'roles/assign_user_role.html', context)
