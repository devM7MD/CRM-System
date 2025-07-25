from django.contrib import admin
from .models import Product, SalesChannel

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'code', 'seller', 'selling_price', 'created_at')
    list_filter = ('seller', 'created_at')
    search_fields = ('name_en', 'name_ar', 'code', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
@admin.register(SalesChannel)
class SalesChannelAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'url')
    search_fields = ('name_en', 'name_ar', 'url')
