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
        ('confirmed', _('Confirmed')),
        ('shipped', _('Shipped')),
        ('delivered', _('Delivered')),
        ('cancelled', _('Cancelled')),
        ('returned', _('Returned')),
    ]

    order_code = models.CharField(max_length=50, unique=True, verbose_name=_('Order Code'), default=generate_order_code)
    customer = models.CharField(max_length=255, verbose_name=_('Customer'), help_text=_('Customer full name'), default='Unknown Customer')
    date = models.DateTimeField(default=timezone.now, verbose_name=_('Order Date'))
    product = models.ForeignKey('sellers.Product', on_delete=models.PROTECT, related_name='orders', verbose_name=_('Product'), null=True, blank=True)
    quantity = models.PositiveIntegerField(verbose_name=_('Quantity'), default=1)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Price Per Unit (AED)'), default=0, help_text=_('Price in UAE Dirhams'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_('Status'))
    
    # Additional fields for detailed view
    customer_phone = models.CharField(max_length=20, blank=True, verbose_name=_('Customer Phone'))
    seller_email = models.EmailField(blank=True, verbose_name=_('Seller Email'))
    store_link = models.URLField(blank=True, verbose_name=_('Store Link'))
    
    # Shipping information
    shipping_address = models.TextField(blank=True, verbose_name=_('Shipping Address'))
    city = models.CharField(max_length=100, blank=True, verbose_name=_('City'))
    state = models.CharField(max_length=100, blank=True, verbose_name=_('State/Province'))
    zip_code = models.CharField(max_length=20, blank=True, verbose_name=_('ZIP Code'))
    country = models.CharField(max_length=100, blank=True, verbose_name=_('Country'))
    
    # Order details
    notes = models.TextField(blank=True, verbose_name=_('Order Notes'))
    internal_notes = models.TextField(blank=True, verbose_name=_('Internal Notes'))
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        ordering = ['-date']

    def __str__(self):
        return f"{self.order_code} - {self.customer}"

    @property
    def total_price(self):
        """Calculate total price in AED"""
        return self.quantity * self.price_per_unit

    @property
    def total_price_aed(self):
        """Get total price formatted in AED"""
        return f"AED {self.total_price:,.2f}"

    @property
    def price_per_unit_aed(self):
        """Get price per unit formatted in AED"""
        return f"AED {self.price_per_unit:,.2f}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('sellers.Product', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Price (AED)'))
    
    class Meta:
        verbose_name = _('Order Item')
        verbose_name_plural = _('Order Items')
    
    def __str__(self):
        return f"{self.order.order_code} - {self.product.name_en} x {self.quantity}"
    
    @property
    def total_price(self):
        return self.quantity * self.price
    
    @property
    def total_price_aed(self):
        return f"AED {self.total_price:,.2f}"