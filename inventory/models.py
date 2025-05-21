# inventory/models.py
from django.db import models

class Warehouse(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class WarehouseLocation(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='locations')
    zone = models.CharField(max_length=20)
    shelf = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.warehouse.name} - Zone {self.zone}, Shelf {self.shelf}"

class Stock(models.Model):
    """Model to track product stock levels and thresholds."""
    product = models.ForeignKey('sellers.Product', on_delete=models.CASCADE, related_name='stock')
    min_quantity = models.PositiveIntegerField(default=10, help_text="Minimum stock level before reordering")
    max_quantity = models.PositiveIntegerField(default=100, help_text="Maximum stock level to maintain")
    reorder_quantity = models.PositiveIntegerField(default=50, help_text="Quantity to reorder when stock is low")
    last_reorder_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"Stock settings for {self.product.name_en}"
    
    @property
    def is_low_stock(self):
        """Check if the product has low stock in any warehouse."""
        total_quantity = sum(record.quantity for record in self.product.inventoryrecord_set.all())
        return total_quantity <= self.min_quantity
    
    @property
    def total_quantity(self):
        """Get the total quantity across all warehouses."""
        return sum(record.quantity for record in self.product.inventoryrecord_set.all())

class InventoryRecord(models.Model):
    product = models.ForeignKey('sellers.Product', on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    location = models.ForeignKey(WarehouseLocation, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField()
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('product', 'warehouse', 'location')
    
    def __str__(self):
        return f"{self.product.name_en} - {self.warehouse.name} - {self.quantity} units"

class InventoryMovement(models.Model):
    MOVEMENT_TYPES = (
        ('receive', 'Receive'),
        ('transfer', 'Transfer'),
        ('adjustment', 'Adjustment'),
        ('order', 'Order'),
        ('return', 'Return'),
    )
    
    product = models.ForeignKey('sellers.Product', on_delete=models.CASCADE)
    from_warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='outgoing_movements')
    to_warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='incoming_movements', null=True, blank=True)
    quantity = models.IntegerField()
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    reference = models.CharField(max_length=100, blank=True)  # Order number, sourcing request, etc.
    created_by = models.ForeignKey('users.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        if self.movement_type == 'transfer' and self.to_warehouse:
            return f"{self.movement_type.capitalize()}: {self.quantity} of {self.product.name_en} from {self.from_warehouse.name} to {self.to_warehouse.name}"
        else:
            return f"{self.movement_type.capitalize()}: {self.quantity} of {self.product.name_en} at {self.from_warehouse.name}"