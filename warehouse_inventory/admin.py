from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Warehouse, WarehouseInventory, InventoryMovement, TrackingNumber

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'location', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'code', 'location')
    ordering = ('name',)

@admin.register(WarehouseInventory)
class WarehouseInventoryAdmin(admin.ModelAdmin):
    list_display = ('warehouse', 'product', 'quantity', 'tracking_number', 'last_movement_date')
    list_filter = ('warehouse', 'last_movement_date')
    search_fields = ('tracking_number', 'product__name', 'product__code')
    raw_id_fields = ('product', 'added_from_order')
    ordering = ('warehouse', 'product')
    date_hierarchy = 'created_at'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('warehouse', 'product')

@admin.register(InventoryMovement)
class InventoryMovementAdmin(admin.ModelAdmin):
    list_display = ('warehouse', 'product', 'movement_type', 'quantity_change', 
                   'created_by', 'created_at')
    list_filter = ('movement_type', 'warehouse', 'created_at')
    search_fields = ('product__name', 'product__code', 'reason', 'notes')
    raw_id_fields = ('product', 'created_by')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'warehouse', 'product', 'created_by', 'destination_warehouse'
        )

@admin.register(TrackingNumber)
class TrackingNumberAdmin(admin.ModelAdmin):
    list_display = ('tracking_number', 'warehouse', 'product', 'status', 'generated_at')
    list_filter = ('status', 'warehouse', 'generated_at')
    search_fields = ('tracking_number', 'product__name', 'product__code')
    raw_id_fields = ('product', 'order')
    ordering = ('-generated_at',)
    date_hierarchy = 'generated_at'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('warehouse', 'product', 'order') 