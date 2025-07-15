from django.db import models
from django.utils.translation import gettext_lazy as _

class Permission(models.Model):
    """Permission model for granular access control."""
    name = models.CharField(_('Name'), max_length=100)
    codename = models.CharField(_('Codename'), max_length=100, unique=True)
    description = models.TextField(_('Description'), blank=True)
    
    # Permission categories
    CATEGORY_CHOICES = (
        ('dashboard', _('Dashboard')),
        ('users', _('Users')),
        ('sellers', _('Sellers')),
        ('inventory', _('Inventory')),
        ('orders', _('Orders')),
        ('callcenter', _('Call Center')),
        ('packaging', _('Packaging')),
        ('delivery', _('Delivery')),
        ('finance', _('Finance')),
        ('warehouse', _('Warehouse')),
        ('settings', _('Settings')),
        ('notifications', _('Notifications')),
    )
    category = models.CharField(_('Category'), max_length=50, choices=CATEGORY_CHOICES)
    
    class Meta:
        verbose_name = _('permission')
        verbose_name_plural = _('permissions')
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.category})"

class Role(models.Model):
    """Custom role model for dynamic role-based access control."""
    name = models.CharField(_('Name'), max_length=100)
    slug = models.SlugField(_('Slug'), max_length=100, unique=True)
    description = models.TextField(_('Description'), blank=True)
    permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('permissions'),
        blank=True,
        related_name='roles'
    )
    is_system_role = models.BooleanField(_('System Role'), default=False, help_text=_('System roles cannot be deleted'))
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    # Role-specific fields configuration (stored as JSON)
    # This will define what fields are required for each role
    required_fields = models.JSONField(_('Required Fields'), default=dict, blank=True)
    
    class Meta:
        verbose_name = _('role')
        verbose_name_plural = _('roles')
        ordering = ['name']
    
    def __str__(self):
        return self.name
