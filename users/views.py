from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from .forms import LoginForm, RegisterForm, UserCreationForm, UserChangeForm, PasswordChangeForm
from .models import User, AuditLog

def login_view(request):
    """Log in a user."""
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.filter(email=email).first()
            
            if user and user.check_password(password) and user.is_active:
                login(request, user)
                
                # Log the login action
                AuditLog.objects.create(
                    user=user,
                    action='login',
                    entity_type='user',
                    entity_id=str(user.id),
                    description=f"User {user.email} logged in",
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                user.last_login = timezone.now()
                user.save(update_fields=['last_login'])
                
                # Redirect to next parameter or dashboard
                next_url = request.GET.get('next', 'dashboard:index')
                return redirect(next_url)
            else:
                messages.error(request, "Invalid email or password.")
    else:
        form = LoginForm()
    
    return render(request, 'users/login.html', {'form': form})

def logout_view(request):
    """Log out the current user."""
    if request.user.is_authenticated:
        # Log the logout action
        AuditLog.objects.create(
            user=request.user,
            action='logout',
            entity_type='user',
            entity_id=str(request.user.id),
            description=f"User {request.user.email} logged out",
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
    
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('users:login')

def register_view(request):
    """Register a new user."""
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            
            # Create audit log for new registration
            AuditLog.objects.create(
                user=user,
                action='create',
                entity_type='user',
                entity_id=str(user.id),
                description=f"New user registration: {user.email}",
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            messages.success(request, "Account created successfully. Please log in.")
            return redirect('users:login')
        else:
            # If form has errors, display them to the user
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = RegisterForm()
    
    return render(request, 'users/register.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.has_role('Super Admin') or u.has_role('Admin') or u.is_superuser)
def user_list(request):
    """List all users (admin only)."""
    users = User.objects.all().order_by('-date_joined')
    
    # Filter by role if requested
    role = request.GET.get('role', '')
    if role:
        # Filter users by role using the new role system
        users = users.filter(user_roles__role__name=role)
    
    return render(request, 'users/list.html', {
        'users': users,
        'role_filter': role,
    })

@login_required
@user_passes_test(lambda u: u.has_role('Super Admin') or u.has_role('Admin') or u.is_superuser)
def user_create(request):
    """Create a new user (admin only)."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            
            # Log the creation
            AuditLog.objects.create(
                user=request.user,
                action='create',
                entity_type='user',
                entity_id=str(user.id),
                description=f"User {user.email} created by {request.user.email}",
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            messages.success(request, f"User {user.email} created successfully.")
            return redirect('users:list')
    else:
        form = UserCreationForm()
    
    return render(request, 'users/create.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.has_role('Super Admin') or u.has_role('Admin') or u.is_superuser)
def user_edit(request, user_id):
    """Edit an existing user (admin only)."""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = UserChangeForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            updated_user = form.save()
            
            # Log the update
            AuditLog.objects.create(
                user=request.user,
                action='update',
                entity_type='user',
                entity_id=str(updated_user.id),
                description=f"User {updated_user.email} updated by {request.user.email}",
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            messages.success(request, f"User {updated_user.email} updated successfully.")
            return redirect('users:list')
    else:
        form = UserChangeForm(instance=user)
    
    return render(request, 'users/edit.html', {'form': form, 'user_obj': user})

@login_required
@user_passes_test(lambda u: u.has_role('Super Admin') or u.has_role('Admin') or u.is_superuser)
def user_detail(request, user_id):
    """View user details (admin only)."""
    user = get_object_or_404(User, id=user_id)
    
    # Get user's audit logs
    audit_logs = AuditLog.objects.filter(user=user).order_by('-timestamp')[:20]
    
    return render(request, 'users/detail.html', {
        'user_obj': user,
        'audit_logs': audit_logs
    })

@login_required
def profile(request):
    """View and edit current user's profile."""
    user = request.user
    
    if request.method == 'POST':
        form = UserChangeForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect('users:profile')
    else:
        form = UserChangeForm(instance=user)
    
    return render(request, 'users/profile.html', {'form': form})

@login_required
def password_change(request):
    """Change user's password."""
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            
            # Log the password change
            AuditLog.objects.create(
                user=request.user,
                action='password_change',
                entity_type='user',
                entity_id=str(user.id),
                description=f"Password changed for {user.email}",
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            # Update the session to prevent logging out
            update_session_auth_hash(request, user)
            
            messages.success(request, "Your password has been changed successfully.")
            return redirect('users:profile')
    else:
        form = PasswordChangeForm(user=request.user)
    
    return render(request, 'users/password_change.html', {'form': form})
