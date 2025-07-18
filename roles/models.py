from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Role(models.Model):
    """Role model for managing user roles and permissions"""
    
    ROLE_TYPES = (
        ('super_admin', _('Super Admin')),
        ('seller', _('Seller')),
    )
    
    name = models.CharField(_('Role Name'), max_length=100, unique=True)
    role_type = models.CharField(_('Role Type'), max_length=50, choices=ROLE_TYPES)
    description = models.TextField(_('Description'), blank=True, null=True)
    is_active = models.BooleanField(_('Active'), default=True)
    is_default = models.BooleanField(_('Default Role'), default=False)
    is_protected = models.BooleanField(_('Protected Role'), default=False, help_text=_('Protected roles cannot be deleted'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='created_roles'
    )
    
    class Meta:
        verbose_name = _('Role')
        verbose_name_plural = _('Roles')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_user_count(self):
        """Get the number of users with this role"""
        return self.users.count()
    
    def get_active_user_count(self):
        """Get the number of active users with this role"""
        return self.users.filter(is_active=True).count()
    
    def get_permission_count(self):
        """Get the number of permissions for this role"""
        return self.role_permissions.filter(granted=True).count()
    
    def delete(self, *args, **kwargs):
        """Override delete to prevent deletion of protected roles"""
        if self.is_protected:
            raise models.ProtectedError(
                f"Cannot delete protected role '{self.name}'. This role is required by the system.",
                self
            )
        super().delete(*args, **kwargs)

class Permission(models.Model):
    """Permission model for granular access control"""
    
    PERMISSION_TYPES = (
        ('create', _('Create')),
        ('read', _('Read')),
        ('update', _('Update')),
        ('delete', _('Delete')),
    )
    
    name = models.CharField(_('Permission Name'), max_length=100)
    codename = models.CharField(_('Code Name'), max_length=100, unique=True)
    description = models.TextField(_('Description'), blank=True, null=True)
    permission_type = models.CharField(_('Permission Type'), max_length=20, choices=PERMISSION_TYPES)
    module = models.CharField(_('Module'), max_length=50)  # e.g., 'dashboard', 'orders', 'inventory'
    is_active = models.BooleanField(_('Active'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Permission')
        verbose_name_plural = _('Permissions')
        unique_together = ['codename', 'permission_type', 'module']
        ordering = ['module', 'permission_type']
    
    def __str__(self):
        return f"{self.module} - {self.get_permission_type_display()} - {self.name}"

class RolePermission(models.Model):
    """Many-to-many relationship between roles and permissions"""
    
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='role_permissions')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name='role_permissions')
    granted = models.BooleanField(_('Granted'), default=True)
    granted_at = models.DateTimeField(auto_now_add=True)
    granted_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='granted_permissions'
    )
    
    class Meta:
        verbose_name = _('Role Permission')
        verbose_name_plural = _('Role Permissions')
        unique_together = ['role', 'permission']
    
    def __str__(self):
        status = "Granted" if self.granted else "Denied"
        return f"{self.role.name} - {self.permission.name} ({status})"

class UserRole(models.Model):
    """Many-to-many relationship between users and roles"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='users')
    is_primary = models.BooleanField(_('Primary Role'), default=False)
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_roles'
    )
    expires_at = models.DateTimeField(_('Expires At'), null=True, blank=True)
    is_active = models.BooleanField(_('Active'), default=True)
    
    class Meta:
        verbose_name = _('User Role')
        verbose_name_plural = _('User Roles')
        unique_together = ['user', 'role']
    
    def __str__(self):
        primary = " (Primary)" if self.is_primary else ""
        return f"{self.user.get_full_name()} - {self.role.name}{primary}"
    
    def is_expired(self):
        """Check if the role assignment has expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

class RoleAuditLog(models.Model):
    """Audit log for role-related actions"""
    
    ACTION_CHOICES = (
        ('role_created', _('Role Created')),
        ('role_updated', _('Role Updated')),
        ('role_deleted', _('Role Deleted')),
        ('permission_granted', _('Permission Granted')),
        ('permission_revoked', _('Permission Revoked')),
        ('user_role_assigned', _('User Role Assigned')),
        ('user_role_removed', _('User Role Removed')),
    )
    
    action = models.CharField(_('Action'), max_length=50, choices=ACTION_CHOICES)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='role_audit_logs')
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    target_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='target_role_audit_logs')
    permission = models.ForeignKey(Permission, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    description = models.TextField(_('Description'))
    ip_address = models.GenericIPAddressField(_('IP Address'), null=True, blank=True)
    user_agent = models.TextField(_('User Agent'), null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Role Audit Log')
        verbose_name_plural = _('Role Audit Logs')
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.timestamp} - {self.get_action_display()} - {self.user}"
