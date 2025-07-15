from django.db import models
from django.utils.translation import gettext_lazy as _

class Warehouse(models.Model):
    """Warehouse model for storing inventory across different locations."""
    name = models.CharField(_('name'), max_length=255)
    location = models.CharField(_('location'), max_length=255)
    description = models.TextField(_('description'), blank=True, null=True)
    is_active = models.BooleanField(_('active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('warehouse')
        verbose_name_plural = _('warehouses')
        ordering = ['name']
    
    def __str__(self):
        return self.name 