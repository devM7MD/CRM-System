from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid
from django.conf import settings
import os

class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        # Try to get a superadmin role, but don't fail if it doesn't exist
        try:
            from roles.models import Role
            superadmin_role = Role.objects.filter(slug='super_admin').first()
            if superadmin_role:
                extra_fields['role'] = superadmin_role
        except:
            # If roles app isn't fully set up yet, just continue without a role
            pass

        return self._create_user(email, password, **extra_fields)

class User(AbstractUser, PermissionsMixin):
    """Custom user model for the CRM system with role-based access control."""
    
    # Override username with email as primary identifier
    username = None
    email = models.EmailField(_('email address'), unique=True)
    
    # Personal information
    full_name = models.CharField(_('full name'), max_length=150, blank=True, default='')
    phone_number = models.CharField(_('phone number'), max_length=20, blank=True, default='')
    profile_image = models.ImageField(_('profile image'), upload_to='profile_images/', blank=True, null=True)
    
    # Business information
    company_name = models.CharField(_('company name'), max_length=100, blank=True, default='')
    country = models.CharField(_('country'), max_length=100, blank=True, default='')
    expected_daily_orders = models.PositiveIntegerField(_('expected daily orders'), default=0)
    
    # Role-based access control - using string reference to avoid circular import
    role = models.ForeignKey(
        'roles.Role',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name=_('role')
    )
    
    # Additional role-specific fields
    call_center_team = models.CharField(_('call center team'), max_length=50, blank=True, null=True, default='')
    accounting_department = models.CharField(_('accounting department'), max_length=50, blank=True, null=True, default='')
    
    # Metadata
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    is_active = models.BooleanField(_('active'), default=True)
    
    # Set email as the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = UserManager()
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        """Return the full name of the user."""
        return self.full_name or self.email
    
    def get_short_name(self):
        """Return the short name for the user."""
        return self.full_name.split(' ')[0] if self.full_name else self.email
    
    def save(self, *args, **kwargs):
        """Override save method to handle profile image deletion."""
        if self.pk:
            try:
                old_instance = User.objects.get(pk=self.pk)
                if old_instance.profile_image and self.profile_image != old_instance.profile_image:
                    if os.path.isfile(old_instance.profile_image.path):
                        os.remove(old_instance.profile_image.path)
            except User.DoesNotExist:
                pass
        super().save(*args, **kwargs)

class UserPermission(models.Model):
    """Custom permissions for users beyond their role."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='custom_permissions')
    permission = models.ForeignKey('roles.Permission', on_delete=models.CASCADE, null=True)
    granted = models.BooleanField(default=True)  # True for grant, False for deny (override role permission)
    
    # Temporary field to maintain compatibility during migration
    permission_name = models.CharField(_('permission name'), max_length=100, blank=True, null=True)
    
    class Meta:
        unique_together = ('user', 'permission')
    
    def __str__(self):
        action = "granted" if self.granted else "denied"
        perm_name = self.permission.name if self.permission else self.permission_name
        return f"{self.user.email} - {perm_name} - {action}"

class AuditLog(models.Model):
    """Audit log for tracking user actions."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='audit_logs', null=True)
    action = models.CharField(max_length=50)  # e.g., 'create', 'update', 'delete', 'login', 'logout'
    entity_type = models.CharField(max_length=50)  # e.g., 'user', 'order', 'product'
    entity_id = models.CharField(max_length=50)  # ID of the affected entity
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True, default='')
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        user_email = self.user.email if self.user else "System"
        return f"{user_email} - {self.action} - {self.timestamp}"