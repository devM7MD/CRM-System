from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_code', 'customer', 'status', 'seller', 'total_price', 'date')
    list_filter = ('status', 'seller', 'date')
    search_fields = ('order_code', 'customer__first_name', 'customer__last_name', 'customer_phone')
    readonly_fields = ()  # No created_at or updated_at fields on Order
    inlines = [OrderItemInline]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    list_filter = ('order__status',)
    search_fields = ('order__order_code', 'product__name')
