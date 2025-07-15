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
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'super_admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser, PermissionsMixin):
    """Custom user model for the CRM system with role-based access control."""
    
    ROLE_CHOICES = (
        ('super_admin', _('Super Admin')),
        ('admin', _('Admin')),
        ('seller', _('Seller')),
        ('stock_keeper', _('Stock Keeper')),
        ('call_center_manager', _('Call Center Manager')),
        ('call_center_agent', _('Call Center Agent')),
        ('packaging', _('Packaging')),
        ('delivery', _('Delivery')),
        ('follow_up', _('Follow-up')),
        ('accountant', _('Accountant')),
        ('sourcing', _('Sourcing')),
    )
    
    # Override username with email as primary identifier
    username = None
    email = models.EmailField(_('email address'), unique=True)
    
    # Personal information
    full_name = models.CharField(_('full name'), max_length=150)
    phone_number = models.CharField(_('phone number'), max_length=20)
    
    # Role and permissions
    role = models.CharField(_('role'), max_length=30, choices=ROLE_CHOICES, default='seller')
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
    
    def has_role(self, role):
        """Check if user has the specified role."""
        return self.role == role

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