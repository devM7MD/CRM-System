from django.contrib import admin
from .models import FollowupRecord, CustomerFeedback

@admin.register(FollowupRecord)
class FollowupRecordAdmin(admin.ModelAdmin):
    list_display = ('order', 'scheduled_for', 'status', 'agent', 'created_at')
    list_filter = ('status', 'agent', 'scheduled_for')
    search_fields = ('order__code', 'order__customer_name', 'order__customer_phone')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(CustomerFeedback)
class CustomerFeedbackAdmin(admin.ModelAdmin):
    list_display = ('order', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('order__code', 'order__customer_name', 'comments')
    readonly_fields = ('created_at',)
