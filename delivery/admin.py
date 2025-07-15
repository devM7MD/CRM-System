from django.contrib import admin
from .models import DeliveryCompany, Courier, DeliveryRecord, DeliveryStatusHistory, DeliveryRecordEnhanced

@admin.register(DeliveryCompany)
class DeliveryCompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'phone', 'email', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'contact_person', 'email', 'phone')
    date_hierarchy = 'created_at'

@admin.register(Courier)
class CourierAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'phone', 'email', 'status', 'rating', 'available')
    list_filter = ('status', 'available', 'company', 'created_at')
    search_fields = ('name', 'email', 'phone')
    date_hierarchy = 'created_at'
    filter_horizontal = ('service_areas',)

@admin.register(DeliveryRecord)
class DeliveryRecordAdmin(admin.ModelAdmin):
    list_display = ('order', 'tracking_number', 'status', 'assigned_at', 'delivered_at')
    list_filter = ('status', 'assigned_at')
    search_fields = ('order__order_code', 'tracking_number')
    date_hierarchy = 'assigned_at'

@admin.register(DeliveryRecordEnhanced)
class DeliveryRecordEnhancedAdmin(admin.ModelAdmin):
    list_display = ('order', 'tracking_number', 'delivery_company', 'courier', 'status', 'priority', 'assigned_at', 'delivery_date')
    list_filter = ('status', 'priority', 'delivery_company', 'created_at')
    search_fields = ('order__order_code', 'tracking_number', 'courier__name')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')

@admin.register(DeliveryStatusHistory)
class DeliveryStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'updated_by', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order__order_code', 'notes')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)
