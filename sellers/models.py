from django.db import models
from django.utils.translation import gettext_lazy as _

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

class Product(models.Model):
    name_en = models.CharField(max_length=100)
    name_ar = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='products/')
    product_link = models.URLField(blank=True)
    seller = models.ForeignKey('users.User', on_delete=models.CASCADE)
    total_quantity = models.PositiveIntegerField(default=0, verbose_name=_('Total Quantity'))
    available_quantity = models.PositiveIntegerField(default=0, verbose_name=_('Available Quantity'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class SalesChannel(models.Model):
    name_en = models.CharField(max_length=100)
    name_ar = models.CharField(max_length=100)
    url = models.URLField()
    country = models.ForeignKey('settings.Country', on_delete=models.CASCADE)
    seller = models.ForeignKey('users.User', on_delete=models.CASCADE)
    api_key = models.CharField(max_length=100, blank=True)
    api_secret = models.CharField(max_length=100, blank=True)