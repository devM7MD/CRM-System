from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid

class UserManager(BaseUserManager):
    """Custom user manager for the CRM system."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a user with the given email and password."""
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        
        # Automatically assign Seller role to new users
        self._assign_default_role(user, 'Seller')
        
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        user = self.create_user(email, password, **extra_fields)
        
        # Automatically assign Admin role to superusers
        self._assign_default_role(user, 'Admin')
        
        return user
    
    def _assign_default_role(self, user, role_name):
        """Assign a default role to a user"""
        try:
            from roles.models import Role, UserRole
            
            # Get the role
            role = Role.objects.filter(name=role_name, is_active=True).first()
            if role:
                # Check if user already has this role
                if not UserRole.objects.filter(user=user, role=role).exists():
                    # Assign the role as primary
                    UserRole.objects.create(
                        user=user,
                        role=role,
                        is_primary=True,
                        is_active=True
                    )
                    print(f"Assigned {role_name} role to {user.email}")
        except Exception as e:
            print(f"Error assigning role {role_name} to {user.email}: {e}")

class User(AbstractUser, PermissionsMixin):
    """Custom user model for the CRM system with role-based access control."""
    
    # Override username with email as primary identifier
    username = None
    email = models.EmailField(_('email address'), unique=True)
    
    # Personal information
    full_name = models.CharField(_('full name'), max_length=150)
    phone_number = models.CharField(_('phone number'), max_length=20)
    
    # Role and permissions - now handled through UserRole model
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff status'), default=False)
    
    # Tracking
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    last_login = models.DateTimeField(_('last login'), blank=True, null=True)
    
    # Profile
    profile_image = models.ImageField(_('profile image'), upload_to='profile_images/', null=True, blank=True)
    
    # Additional fields for business users
    company_name = models.CharField(_('company name'), max_length=150, blank=True, null=True)
    country = models.CharField(_('country'), max_length=100, blank=True, null=True)
    expected_daily_orders = models.PositiveIntegerField(_('expected daily orders'), default=0)
    
    # System fields
    user_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'phone_number']
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-date_joined']
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return self.full_name
    
    def get_short_name(self):
        return self.full_name.split()[0] if self.full_name else self.email
    
    def get_initials(self):
        """Get user initials for avatar display"""
        if self.full_name:
            names = self.full_name.split()
            if len(names) >= 2:
                return f"{names[0][0]}{names[-1][0]}".upper()
            return names[0][0].upper()
        return self.email[0].upper()
    
    @property
    def primary_role(self):
        """Get the user's primary role"""
        try:
            user_role = self.user_roles.filter(is_primary=True, is_active=True).first()
            return user_role.role if user_role else None
        except:
            return None
    
    def get_primary_role(self):
        """Get the user's primary role (legacy method)"""
        return self.primary_role
    
    def get_all_roles(self):
        """Get all active roles for the user"""
        return [user_role.role for user_role in self.user_roles.filter(is_active=True)]
    
    def has_role(self, role_name):
        """Check if user has the specified role"""
        return self.user_roles.filter(role__name=role_name, is_active=True).exists()
    
    def has_permission(self, permission_codename, module=None):
        """Check if user has the specified permission"""
        from roles.models import Permission
        
        # Superusers have all permissions
        if self.is_superuser:
            return True
        
        # Check through user's roles
        for user_role in self.user_roles.filter(is_active=True):
            if user_role.role.role_permissions.filter(
                permission__codename=permission_codename,
                granted=True
            ).exists():
                if module is None or user_role.role.role_permissions.filter(
                    permission__codename=permission_codename,
                    permission__module=module,
                    granted=True
                ).exists():
                    return True
        return False
    
    def can_create_roles(self):
        """Check if user can create roles (only super admin)"""
        return self.has_role('Super Admin') or self.is_superuser
    
    @property
    def has_role_call_center_manager(self):
        """Check if user has Call Center Manager role"""
        return self.has_role('Call Center Manager')
    
    @property
    def has_role_call_center_agent(self):
        """Check if user has Call Center Agent role"""
        return self.has_role('Call Center Agent')
    
    @property
    def has_role_accountant(self):
        """Check if user has Accountant role"""
        return self.has_role('Accountant')
    
    @property
    def has_role_admin(self):
        """Check if user has Admin role"""
        return self.has_role('Admin')
    
    @property
    def has_role_seller(self):
        """Check if user has Seller role"""
        return self.has_role('Seller')
    
    @property
    def has_role_super_admin(self):
        """Check if user has Super Admin role"""
        return self.has_role('Super Admin')

class UserPermission(models.Model):
    """Model to store custom permissions for users."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='custom_permissions')
    permission_name = models.CharField(_('permission name'), max_length=100)
    description = models.TextField(_('description'), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'permission_name')
        verbose_name = _('user permission')
        verbose_name_plural = _('user permissions')
    
    def __str__(self):
        return f"{self.user.email} - {self.permission_name}"

class AuditLog(models.Model):
    """Model to track critical actions in the system."""
    
    ACTION_CHOICES = (
        ('create', _('Create')),
        ('update', _('Update')),
        ('delete', _('Delete')),
        ('view', _('View')),
        ('login', _('Login')),
        ('logout', _('Logout')),
        ('password_change', _('Password Change')),
        ('permission_change', _('Permission Change')),
        ('status_change', _('Status Change')),
    )
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(_('action'), max_length=30, choices=ACTION_CHOICES)
    entity_type = models.CharField(_('entity type'), max_length=100)
    entity_id = models.CharField(_('entity ID'), max_length=100)
    description = models.TextField(_('description'))
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(_('IP address'), null=True, blank=True)
    user_agent = models.TextField(_('user agent'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('audit log')
        verbose_name_plural = _('audit logs')
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.timestamp} - {self.user} - {self.action} - {self.entity_type}"