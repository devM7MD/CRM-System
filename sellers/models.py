from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum
from inventory.models import InventoryRecord

class Seller(models.Model):
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='seller_profile')
    name = models.CharField(max_length=200, verbose_name=_('Seller Name'))
    phone = models.CharField(max_length=20, verbose_name=_('Phone Number'))
    email = models.EmailField(verbose_name=_('Email'))
    store_link = models.URLField(blank=True, verbose_name=_('Store Link'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _('Seller')
        verbose_name_plural = _('Sellers')
        ordering = ['-created_at']

    def __str__(self):
        return self.name

def product_image_path(instance, filename):
    """Generate file path for product images"""
    import os
    from django.utils.text import slugify
    
    # Get file extension
    ext = filename.split('.')[-1]
    
    # Create filename with product name
    if instance.name_en:
        # Use English name if available, otherwise use code
        base_name = slugify(instance.name_en)
    else:
        base_name = instance.code
    
    # If instance has an ID, use it, otherwise use a timestamp
    if instance.id:
        filename = f"{base_name}_{instance.id}.{ext}"
    else:
        import time
        timestamp = int(time.time())
        filename = f"{base_name}_{timestamp}.{ext}"
    
    return os.path.join('products', filename)

class Product(models.Model):
    name_en = models.CharField(max_length=100)
    name_ar = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock_quantity = models.PositiveIntegerField(default=0, help_text=_('Current stock quantity'))
    image = models.ImageField(upload_to=product_image_path, blank=True, null=True)
    product_link = models.URLField(blank=True)
    seller = models.ForeignKey('users.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_quantity(self):
        total = InventoryRecord.objects.filter(product=self).aggregate(total=Sum('quantity'))['total']
        return total or 0

    @property
    def available_quantity(self):
        return self.total_quantity

class SalesChannel(models.Model):
    name_en = models.CharField(max_length=100)
    name_ar = models.CharField(max_length=100)
    url = models.URLField()
    country = models.ForeignKey('settings.Country', on_delete=models.CASCADE)
    seller = models.ForeignKey('users.User', on_delete=models.CASCADE)
    api_key = models.CharField(max_length=100, blank=True)
    api_secret = models.CharField(max_length=100, blank=True)