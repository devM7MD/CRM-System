from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_code', 'customer', 'status', 'seller_email', 'total_price_aed', 'date')
    list_filter = ('status', 'seller_email', 'date')
    search_fields = ('order_code', 'customer', 'customer_phone', 'seller_email')
    readonly_fields = ('order_code', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('order_code', 'customer', 'customer_phone', 'date', 'status')
        }),
        ('Product Details', {
            'fields': ('product', 'quantity', 'price_per_unit')
        }),
        ('Seller Information', {
            'fields': ('seller_email', 'store_link')
        }),
        ('Shipping Information', {
            'fields': ('shipping_address', 'city', 'state', 'zip_code', 'country')
        }),
        ('Notes', {
            'fields': ('notes', 'internal_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'total_price_aed')
    list_filter = ('order__status',)
    search_fields = ('order__order_code', 'product__name')
