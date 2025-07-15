# orders/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid

def generate_order_code():
    return f"ORD-{uuid.uuid4().hex[:8].upper()}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('shipped', _('Shipped')),
        ('delivered', _('Delivered')),
        ('cancelled', _('Cancelled')),
    ]

    order_code = models.CharField(max_length=50, unique=True, verbose_name=_('Order Code'), default=generate_order_code)
    customer = models.ForeignKey('users.User', on_delete=models.PROTECT, related_name='orders', verbose_name=_('Customer'), null=True, blank=True)
    date = models.DateTimeField(default=timezone.now, verbose_name=_('Order Date'))
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT, related_name='orders', verbose_name=_('Product'), null=True, blank=True)
    quantity = models.PositiveIntegerField(verbose_name=_('Quantity'), default=1)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Price Per Unit'), default=0)
    seller = models.ForeignKey('sellers.Seller', on_delete=models.PROTECT, related_name='orders', verbose_name=_('Seller'), null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_('Status'))
    
    # Additional fields for detailed view
    customer_phone = models.CharField(max_length=20, blank=True, verbose_name=_('Customer Phone'))
    seller_phone = models.CharField(max_length=20, blank=True, verbose_name=_('Seller Phone'))
    seller_email = models.EmailField(blank=True, verbose_name=_('Seller Email'))
    store_link = models.URLField(blank=True, verbose_name=_('Store Link'))

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        ordering = ['-date']

    def __str__(self):
        return f"{self.order_code} - {self.customer.get_full_name() if self.customer else 'No Customer'}"

    @property
    def total_price(self):
        return self.quantity * self.price_per_unit

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('sellers.Product', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)