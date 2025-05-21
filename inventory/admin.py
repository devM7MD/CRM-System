from django.contrib import admin
from .models import Warehouse, WarehouseLocation, Stock, InventoryRecord, InventoryMovement

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'location')

@admin.register(WarehouseLocation)
class WarehouseLocationAdmin(admin.ModelAdmin):
    list_display = ('warehouse', 'zone', 'shelf')
    list_filter = ('warehouse', 'zone')
    search_fields = ('warehouse__name', 'zone', 'shelf')

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('product', 'min_quantity', 'max_quantity', 'total_quantity', 'is_low_stock')
    list_filter = ('product__seller',)
    search_fields = ('product__name_en', 'product__code')

@admin.register(InventoryRecord)
class InventoryRecordAdmin(admin.ModelAdmin):
    list_display = ('product', 'warehouse', 'location', 'quantity', 'last_updated')
    list_filter = ('warehouse', 'product__seller')
    search_fields = ('product__name_en', 'product__code', 'warehouse__name')

@admin.register(InventoryMovement)
class InventoryMovementAdmin(admin.ModelAdmin):
    list_display = ('product', 'from_warehouse', 'to_warehouse', 'quantity', 'movement_type', 'created_at')
    list_filter = ('movement_type', 'from_warehouse', 'to_warehouse', 'created_at')
    search_fields = ('product__name_en', 'product__code', 'reference', 'notes')
    readonly_fields = ('created_at',)
