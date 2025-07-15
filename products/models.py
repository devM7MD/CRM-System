from django.db import models
from django.utils.translation import gettext_lazy as _

class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name=_('Product Name'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    sku = models.CharField(max_length=50, unique=True, verbose_name=_('SKU'))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Price'))
    stock = models.PositiveIntegerField(default=0, verbose_name=_('Stock'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        ordering = ['-created_at']

    def __str__(self):
        return self.name
