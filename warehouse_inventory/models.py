from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.conf import settings
from django.utils import timezone
# Comment out qrcode imports to avoid dependency issues
# import qrcode
# import io
# import base64

class Warehouse(models.Model):
    """Model for warehouses."""
    name = models.CharField(max_length=255, verbose_name=_('Warehouse Name'))
    code = models.CharField(max_length=10, unique=True, verbose_name=_('Warehouse Code'))
    country = models.CharField(max_length=100, verbose_name=_('Country'))
    currency = models.CharField(max_length=3, verbose_name=_('Currency'))
    zone = models.CharField(max_length=100, verbose_name=_('Zone'))
    location = models.CharField(max_length=255, verbose_name=_('Location'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Warehouse')
        verbose_name_plural = _('Warehouses')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"

    def get_total_products(self):
        """Get total number of unique products in warehouse."""
        return self.inventory.count()

    def get_total_quantity(self):
        """Get total quantity of all products in warehouse."""
        return self.inventory.aggregate(total=models.Sum('quantity'))['total'] or 0

    def get_low_stock_items(self):
        """Get items with quantity below minimum stock level."""
        return self.inventory.filter(quantity__lt=models.F('product__min_stock_level'))

class WarehouseInventory(models.Model):
    """Model for inventory items in warehouses."""
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='inventory',
        verbose_name=_('Warehouse')
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='warehouse_inventory',
        verbose_name=_('Product')
    )
    quantity = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_('Quantity')
    )
    tracking_number = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        verbose_name=_('Tracking Number')
    )
    added_from_order = models.ForeignKey(
        'orders.Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inventory_items',
        verbose_name=_('Added from Order')
    )
    last_movement_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Last Movement Date')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Warehouse Inventory')
        verbose_name_plural = _('Warehouse Inventories')
        unique_together = ['warehouse', 'product']
        # Fix the ordering issue
        ordering = ['product']

    def __str__(self):
        return f"{self.product} - {self.warehouse.name}"

    def save(self, *args, **kwargs):
        """Generate tracking number if not set."""
        if not self.tracking_number:
            self.tracking_number = self.generate_tracking_number()
        super().save(*args, **kwargs)

    def generate_tracking_number(self):
        """Generate a unique tracking number."""
        prefix = f"TRK-{self.warehouse.code}-"
        base_number = timezone.now().strftime('%y%m%d%H%M%S')
        suffix = f"-{self.product.code[:3]}"
        return f"{prefix}{base_number}{suffix}"
    
    # Comment out get_qr_code method
    # def get_qr_code(self):
    #     """Generate QR code for tracking."""
    #     qr = qrcode.QRCode(
    #         version=1,
    #         error_correction=qrcode.constants.ERROR_CORRECT_L,
    #         box_size=10,
    #         border=4,
    #     )
    #     qr.add_data(self.tracking_number)
    #     qr.make(fit=True)
    # 
    #     img = qr.make_image(fill_color="black", back_color="white")
    #     buffer = io.BytesIO()
    #     img.save(buffer, format='PNG')
    #     return f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}"

    def get_movement_history(self):
        """Get movement history for this inventory item."""
        return self.movements.order_by('-created_at')

    def get_last_movement(self):
        """Get the last movement record."""
        return self.movements.order_by('-created_at').first()

    def is_low_stock(self):
        """Check if quantity is below minimum stock level."""
        return self.quantity < self.product.min_stock_level

class InventoryMovement(models.Model):
    """Model for tracking inventory movements."""
    MOVEMENT_TYPES = [
        ('in', _('Stock In')),
        ('out', _('Stock Out')),
        ('transfer', _('Transfer')),
    ]

    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='movements',
        verbose_name=_('Warehouse')
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='movements',
        verbose_name=_('Product')
    )
    movement_type = models.CharField(
        max_length=10,
        choices=MOVEMENT_TYPES,
        verbose_name=_('Movement Type')
    )
    quantity_change = models.IntegerField(verbose_name=_('Quantity Change'))
    reason = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Reason')
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_('Notes')
    )
    destination_warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incoming_transfers',
        verbose_name=_('Destination Warehouse')
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='inventory_movements',
        verbose_name=_('Created By')
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Inventory Movement')
        verbose_name_plural = _('Inventory Movements')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.product} ({self.quantity_change})"

    def save(self, *args, **kwargs):
        """Update last movement date on inventory."""
        super().save(*args, **kwargs)
        inventory = WarehouseInventory.objects.get(
            warehouse=self.warehouse,
            product=self.product
        )
        inventory.last_movement_date = self.created_at
        inventory.save(update_fields=['last_movement_date'])

class TrackingNumber(models.Model):
    """Model for tracking numbers."""
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('shipped', _('Shipped')),
        ('delivered', _('Delivered')),
        ('cancelled', _('Cancelled')),
    ]

    tracking_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('Tracking Number')
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='tracking_numbers',
        verbose_name=_('Warehouse')
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='tracking_numbers',
        verbose_name=_('Product')
    )
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tracking_numbers',
        verbose_name=_('Order')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name=_('Status')
    )
    generated_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Tracking Number')
        verbose_name_plural = _('Tracking Numbers')
        ordering = ['-generated_at']

    def __str__(self):
        return self.tracking_number
    
    # Comment out get_qr_code method
    # def get_qr_code(self):
    #     """Generate QR code for tracking."""
    #     qr = qrcode.QRCode(
    #         version=1,
    #         error_correction=qrcode.constants.ERROR_CORRECT_L,
    #         box_size=10,
    #         border=4,
    #     )
    #     qr.add_data(self.tracking_number)
    #     qr.make(fit=True)
    # 
    #     img = qr.make_image(fill_color="black", back_color="white")
    #     buffer = io.BytesIO()
    #     img.save(buffer, format='PNG')
    #     return f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}" 