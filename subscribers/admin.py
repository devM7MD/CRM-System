from django.contrib import admin
from .models import Subscriber

@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'phone_number', 'business_name', 'residence_country', 'subscription_type', 'is_active', 'created_at']
    list_filter = ['is_active', 'subscription_type', 'residence_country', 'created_at']
    search_fields = ['full_name', 'email', 'phone_number', 'business_name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'full_name', 'email', 'phone_number')
        }),
        ('Business Information', {
            'fields': ('business_name', 'residence_country', 'address', 'city', 'postal_code')
        }),
        ('Subscription Details', {
            'fields': ('subscription_type', 'is_active', 'subscription_date')
        }),
        ('Additional Information', {
            'fields': ('notes', 'preferences'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user') 