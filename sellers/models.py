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
        db_table = 'sellers_seller'

    def __str__(self):
        return self.name

class Product(models.Model):
    name_en = models.CharField(max_length=100)
    name_ar = models.CharField(max_length=100, blank=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    product_link = models.URLField(blank=True)
    brand = models.CharField(max_length=100, blank=True, verbose_name=_('Brand'))
    category = models.CharField(max_length=100, blank=True, verbose_name=_('Category'))
    seller = models.ForeignKey('users.User', on_delete=models.CASCADE)
    total_quantity = models.PositiveIntegerField(default=0, verbose_name=_('Total Quantity'))
    available_quantity = models.PositiveIntegerField(default=0, verbose_name=_('Available Quantity'))
    low_stock_threshold = models.PositiveIntegerField(default=5, verbose_name=_('Low Stock Threshold'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sellers_product'

    def __str__(self):
        return self.name_en

    @property
    def in_delivery_quantity(self):
        return self.total_quantity - self.available_quantity

class SalesChannel(models.Model):
    PLATFORM_CHOICES = (
        ('shopify', 'Shopify'),
        ('woocommerce', 'WooCommerce'),
        ('magento', 'Magento'),
        ('amazon', 'Amazon'),
        ('ebay', 'eBay'),
        ('etsy', 'Etsy'),
        ('other', 'Other'),
    )
    
    name_en = models.CharField(max_length=100, verbose_name=_('Store Name (English)'))
    name_ar = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('Store Name (Arabic)'))
    url = models.URLField(verbose_name=_('Store URL'))
    channel_type = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default='other', verbose_name=_('Platform Type'))
    seller = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='sales_channels')
    api_key = models.CharField(max_length=255, blank=True, verbose_name=_('API Key'))
    api_secret = models.CharField(max_length=255, blank=True, verbose_name=_('API Secret'))
    logo = models.ImageField(upload_to='sales_channels/', blank=True, null=True, verbose_name=_('Store Logo'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))
    
    # Sync settings
    sync_products = models.BooleanField(default=True, verbose_name=_('Sync Products'))
    sync_orders = models.BooleanField(default=True, verbose_name=_('Sync Orders'))
    sync_inventory = models.BooleanField(default=True, verbose_name=_('Sync Inventory'))
    sync_shipping = models.BooleanField(default=True, verbose_name=_('Sync Shipping Updates'))
    
    # Sync timestamps
    last_sync = models.DateTimeField(blank=True, null=True, verbose_name=_('Last Sync'))
    last_product_sync = models.DateTimeField(blank=True, null=True, verbose_name=_('Last Product Sync'))
    last_order_sync = models.DateTimeField(blank=True, null=True, verbose_name=_('Last Order Sync'))
    last_inventory_sync = models.DateTimeField(blank=True, null=True, verbose_name=_('Last Inventory Sync'))
    last_shipping_sync = models.DateTimeField(blank=True, null=True, verbose_name=_('Last Shipping Sync'))
    
    # Stats for display
    order_count = models.PositiveIntegerField(default=0, verbose_name=_('Order Count'))
    product_count = models.PositiveIntegerField(default=0, verbose_name=_('Product Count'))
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('Total Revenue'))
    pending_sync = models.PositiveIntegerField(default=0, verbose_name=_('Pending Sync Items'))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _('Sales Channel')
        verbose_name_plural = _('Sales Channels')
        ordering = ['-created_at']
        db_table = 'sellers_saleschannel'

    def __str__(self):
        return self.name_en
    
    @property
    def store_url(self):
        """Property to access the url field with a more descriptive name."""
        return self.url
    
    @store_url.setter
    def store_url(self, value):
        """Setter for store_url property."""
        self.url = value
        
    @property
    def country_code(self):
        """Extract country code from the store URL"""
        try:
            from urllib.parse import urlparse
            domain = urlparse(self.url).netloc
            return domain.split('.')[-1]
        except:
            return 'us'