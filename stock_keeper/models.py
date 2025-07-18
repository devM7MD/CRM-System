# stock_keeper/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator
import uuid
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image

def generate_tracking_number():
    """Generate unique tracking number for inventory items."""
    return f"TRK-{uuid.uuid4().hex[:8].upper()}"

def generate_barcode():
    """Generate unique barcode for products."""
    return f"BC-{uuid.uuid4().hex[:12].upper()}"

class Warehouse(models.Model):
    """Enhanced warehouse model with location details."""
    name = models.CharField(max_length=100, verbose_name="Warehouse Name")
    country = models.CharField(max_length=100, verbose_name="Country")
    currency = models.CharField(max_length=10, default="AED", verbose_name="Currency")
    zone = models.CharField(max_length=100, verbose_name="Zone/Region")
    address = models.TextField(blank=True, verbose_name="Full Address")
    contact_person = models.CharField(max_length=100, blank=True, verbose_name="Contact Person")
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name="Contact Phone")
    contact_email = models.EmailField(blank=True, verbose_name="Contact Email")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Warehouse"
        verbose_name_plural = "Warehouses"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.country}"
    
    @property
    def total_items(self):
        """Get total number of items in this warehouse."""
        return self.warehouseinventory_set.aggregate(
            total=models.Sum('quantity')
        )['total'] or 0
    
    @property
    def low_stock_items(self):
        """Get items with low stock in this warehouse."""
        return self.warehouseinventory_set.filter(
            quantity__lte=models.F('product__min_stock_level')
        ).count()

class WarehouseInventory(models.Model):
    """Track product quantities in specific warehouses."""
    product = models.ForeignKey('sellers.Product', on_delete=models.CASCADE, related_name='warehouse_inventory')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    location_code = models.CharField(max_length=50, blank=True, verbose_name="Storage Location")
    min_stock_level = models.PositiveIntegerField(default=5, verbose_name="Minimum Stock Level")
    max_stock_level = models.PositiveIntegerField(default=100, verbose_name="Maximum Stock Level")
    last_movement = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('product', 'warehouse')
        verbose_name = "Warehouse Inventory"
        verbose_name_plural = "Warehouse Inventory"
    
    def __str__(self):
        return f"{self.product.name_en} - {self.warehouse.name} ({self.quantity})"
    
    @property
    def is_low_stock(self):
        """Check if stock is below minimum level."""
        return self.quantity <= self.min_stock_level
    
    @property
    def stock_status(self):
        """Get stock status for display."""
        if self.quantity == 0:
            return "out_of_stock"
        elif self.is_low_stock:
            return "low_stock"
        elif self.quantity >= self.max_stock_level:
            return "overstocked"
        else:
            return "normal"

class InventoryMovement(models.Model):
    """Track all inventory movements with detailed information."""
    MOVEMENT_TYPES = (
        ('stock_in', 'Stock In'),
        ('stock_out', 'Stock Out'),
        ('transfer', 'Transfer'),
        ('adjustment', 'Adjustment'),
        ('return', 'Return'),
        ('damage', 'Damage'),
        ('expiry', 'Expiry'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    tracking_number = models.CharField(max_length=50, unique=True, default=generate_tracking_number)
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Product and quantity details
    product = models.ForeignKey('sellers.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    
    # Warehouse details
    from_warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='outgoing_movements', null=True, blank=True)
    to_warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='incoming_movements', null=True, blank=True)
    from_location = models.CharField(max_length=50, blank=True)
    to_location = models.CharField(max_length=50, blank=True)
    
    # Reference information
    reference_number = models.CharField(max_length=100, blank=True)  # Order number, PO, etc.
    reference_type = models.CharField(max_length=50, blank=True)  # Order, Purchase, Transfer, etc.
    
    # User and timing
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='movements_created')
    processed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='movements_processed', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    # Additional details
    reason = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    condition = models.CharField(max_length=50, default='good')  # good, damaged, defective
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Inventory Movement"
        verbose_name_plural = "Inventory Movements"
    
    def __str__(self):
        return f"{self.tracking_number} - {self.movement_type} - {self.product.name_en}"
    
    def save(self, *args, **kwargs):
        if self.status == 'completed' and not self.processed_at:
            self.processed_at = timezone.now()
        super().save(*args, **kwargs)
    
    @property
    def movement_description(self):
        """Get human-readable movement description."""
        if self.movement_type == 'transfer':
            return f"Transfer {self.quantity} units from {self.from_warehouse.name} to {self.to_warehouse.name}"
        elif self.movement_type == 'stock_in':
            return f"Stock In {self.quantity} units to {self.to_warehouse.name}"
        elif self.movement_type == 'stock_out':
            return f"Stock Out {self.quantity} units from {self.from_warehouse.name}"
        else:
            return f"{self.movement_type.title()} {self.quantity} units"

class TrackingNumber(models.Model):
    """Manage tracking numbers and QR codes for inventory items."""
    tracking_number = models.CharField(max_length=50, unique=True, default=generate_tracking_number)
    product = models.ForeignKey('sellers.Product', on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    barcode = models.CharField(max_length=100, unique=True, default=generate_barcode)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Tracking Number"
        verbose_name_plural = "Tracking Numbers"
    
    def __str__(self):
        return f"{self.tracking_number} - {self.product.name_en}"
    
    def save(self, *args, **kwargs):
        if not self.qr_code:
            self.generate_qr_code()
        super().save(*args, **kwargs)
    
    def generate_qr_code(self):
        """Generate QR code for the tracking number."""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(self.tracking_number)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        
        filename = f'qr_code_{self.tracking_number}.png'
        self.qr_code.save(filename, File(buffer), save=False)

class StockKeeperSession(models.Model):
    """Track stock keeper work sessions."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    shift_start = models.DateTimeField(auto_now_add=True)
    shift_end = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Stock Keeper Session"
        verbose_name_plural = "Stock Keeper Sessions"
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.warehouse.name} - {self.shift_start.date()}"
    
    @property
    def duration(self):
        """Get session duration."""
        if self.shift_end:
            return self.shift_end - self.shift_start
        return timezone.now() - self.shift_start
    
    @property
    def movements_count(self):
        """Get number of movements processed in this session."""
        return self.user.movements_processed.filter(
            processed_at__gte=self.shift_start,
            processed_at__lte=self.shift_end or timezone.now()
        ).count()

class StockAlert(models.Model):
    """Manage stock alerts and notifications."""
    ALERT_TYPES = (
        ('low_stock', 'Low Stock'),
        ('out_of_stock', 'Out of Stock'),
        ('overstocked', 'Overstocked'),
        ('expiry', 'Expiry Warning'),
        ('damage', 'Damage Report'),
        ('transfer_request', 'Transfer Request'),
    )
    
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    product = models.ForeignKey('sellers.Product', on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Stock Alert"
        verbose_name_plural = "Stock Alerts"
    
    def __str__(self):
        return f"{self.alert_type} - {self.product.name_en} - {self.warehouse.name}"
    
    def resolve(self, user):
        """Mark alert as resolved."""
        self.is_resolved = True
        self.resolved_by = user
        self.resolved_at = timezone.now()
        self.save()
