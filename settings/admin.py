from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Country, DeliveryArea, DeliveryCompany, SystemFees, SystemSetting, AuditLog

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'currency', 'timezone', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')
    ordering = ('name',)

@admin.register(DeliveryArea)
class DeliveryAreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'code', 'additional_cost')
    list_filter = ('country',)
    search_fields = ('name', 'code')

@admin.register(DeliveryCompany)
class DeliveryCompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'base_cost', 'is_active')
    list_filter = ('is_active', 'countries')
    search_fields = ('name', 'code')
    filter_horizontal = ('countries',)

@admin.register(SystemFees)
class SystemFeesAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'last_updated', 'updated_by')
    fieldsets = (
        (None, {
            'fields': ('updated_by',)
        }),
        (_('Fees Configuration'), {
            'fields': ('upsell_fees', 'confirmation_fees', 'cancellation_fees', 
                      'fulfillment_fees', 'shipping_fees', 'return_fees', 'warehouse_fees')
        }),
    )
    readonly_fields = ('last_updated',)

@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'is_public')
    search_fields = ('key', 'value', 'description')
    list_filter = ('is_public',)

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'table', 'record_id', 'user', 'timestamp')
    list_filter = ('action', 'table', 'timestamp')
    search_fields = ('table', 'record_id', 'user__username', 'notes')
    readonly_fields = ('action', 'table', 'record_id', 'user', 'timestamp', 'ip_address', 'old_value', 'new_value')
    date_hierarchy = 'timestamp'
