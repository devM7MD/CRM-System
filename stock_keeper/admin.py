# stock_keeper/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Warehouse, WarehouseInventory, InventoryMovement, 
    TrackingNumber, StockKeeperSession, StockAlert
)

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'zone', 'currency', 'total_items', 'low_stock_items', 'is_active', 'created_at']
    list_filter = ['country', 'zone', 'currency', 'is_active', 'created_at']
    search_fields = ['name', 'country', 'zone', 'contact_person', 'contact_email']
    readonly_fields = ['total_items', 'low_stock_items', 'created_at', 'updated_at']
    ordering = ['name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'country', 'zone', 'currency')
        }),
        ('Contact Information', {
            'fields': ('contact_person', 'contact_phone', 'contact_email', 'address')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(WarehouseInventory)
class WarehouseInventoryAdmin(admin.ModelAdmin):
    list_display = ['product', 'warehouse', 'quantity', 'location_code', 'stock_status_display', 'is_low_stock', 'last_movement']
    list_filter = ['warehouse', 'is_low_stock', 'last_movement', 'created_at']
    search_fields = ['product__name_en', 'product__name_ar', 'warehouse__name', 'location_code']
    readonly_fields = ['is_low_stock', 'stock_status', 'last_movement', 'created_at', 'updated_at']
    ordering = ['warehouse', 'product']
    
    def stock_status_display(self, obj):
        status_colors = {
            'out_of_stock': 'red',
            'low_stock': 'orange',
            'normal': 'green',
            'overstocked': 'blue'
        }
        color = status_colors.get(obj.stock_status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.stock_status.replace('_', ' ').title()
        )
    stock_status_display.short_description = 'Stock Status'
    
    fieldsets = (
        ('Product & Warehouse', {
            'fields': ('product', 'warehouse')
        }),
        ('Stock Information', {
            'fields': ('quantity', 'location_code', 'min_stock_level', 'max_stock_level')
        }),
        ('Status Information', {
            'fields': ('is_low_stock', 'stock_status', 'last_movement')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(InventoryMovement)
class InventoryMovementAdmin(admin.ModelAdmin):
    list_display = ['tracking_number', 'movement_type', 'product', 'quantity', 'warehouses_display', 'status', 'created_by', 'created_at']
    list_filter = ['movement_type', 'status', 'warehouse', 'created_at', 'processed_at']
    search_fields = ['tracking_number', 'product__name_en', 'reference_number', 'reason']
    readonly_fields = ['tracking_number', 'created_at', 'processed_at', 'movement_description']
    ordering = ['-created_at']
    
    def warehouses_display(self, obj):
        if obj.movement_type == 'transfer':
            return f"{obj.from_warehouse.name} → {obj.to_warehouse.name}"
        elif obj.movement_type == 'stock_in':
            return f"→ {obj.to_warehouse.name}"
        elif obj.movement_type == 'stock_out':
            return f"{obj.from_warehouse.name} →"
        return "-"
    warehouses_display.short_description = 'Warehouses'
    
    fieldsets = (
        ('Movement Information', {
            'fields': ('tracking_number', 'movement_type', 'status', 'product', 'quantity')
        }),
        ('Warehouse Details', {
            'fields': ('from_warehouse', 'to_warehouse', 'from_location', 'to_location')
        }),
        ('Reference Information', {
            'fields': ('reference_number', 'reference_type', 'reason', 'notes')
        }),
        ('User Information', {
            'fields': ('created_by', 'processed_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'processed_at')
        }),
        ('Additional Details', {
            'fields': ('condition', 'movement_description'),
            'classes': ('collapse',)
        }),
    )

@admin.register(TrackingNumber)
class TrackingNumberAdmin(admin.ModelAdmin):
    list_display = ['tracking_number', 'product', 'warehouse', 'barcode', 'qr_code_display', 'is_active', 'created_at']
    list_filter = ['warehouse', 'is_active', 'created_at']
    search_fields = ['tracking_number', 'barcode', 'product__name_en']
    readonly_fields = ['tracking_number', 'barcode', 'qr_code_display', 'created_at']
    ordering = ['-created_at']
    
    def qr_code_display(self, obj):
        if obj.qr_code:
            return format_html(
                '<img src="{}" alt="QR Code" style="max-width: 50px; max-height: 50px;" />',
                obj.qr_code.url
            )
        return "No QR Code"
    qr_code_display.short_description = 'QR Code'
    
    fieldsets = (
        ('Tracking Information', {
            'fields': ('tracking_number', 'barcode', 'product', 'warehouse')
        }),
        ('QR Code', {
            'fields': ('qr_code_display',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(StockKeeperSession)
class StockKeeperSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'warehouse', 'shift_start', 'shift_end', 'duration_display', 'movements_count', 'is_active']
    list_filter = ['warehouse', 'is_active', 'shift_start', 'shift_end']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'warehouse__name']
    readonly_fields = ['duration_display', 'movements_count', 'shift_start']
    ordering = ['-shift_start']
    
    def duration_display(self, obj):
        duration = obj.duration
        if duration:
            hours = duration.total_seconds() // 3600
            minutes = (duration.total_seconds() % 3600) // 60
            return f"{int(hours)}h {int(minutes)}m"
        return "Active"
    duration_display.short_description = 'Duration'
    
    fieldsets = (
        ('Session Information', {
            'fields': ('user', 'warehouse', 'shift_start', 'shift_end')
        }),
        ('Statistics', {
            'fields': ('duration_display', 'movements_count')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

@admin.register(StockAlert)
class StockAlertAdmin(admin.ModelAdmin):
    list_display = ['alert_type', 'priority', 'product', 'warehouse', 'is_resolved', 'created_at']
    list_filter = ['alert_type', 'priority', 'warehouse', 'is_resolved', 'created_at']
    search_fields = ['product__name_en', 'warehouse__name', 'message']
    readonly_fields = ['created_at', 'resolved_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Alert Information', {
            'fields': ('alert_type', 'priority', 'product', 'warehouse')
        }),
        ('Message', {
            'fields': ('message',)
        }),
        ('Resolution', {
            'fields': ('is_resolved', 'resolved_by', 'resolved_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('product', 'warehouse', 'resolved_by')
