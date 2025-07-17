from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    CallCenterAgent, AgentSession, CallLog, CustomerInteraction,
    OrderAssignment, ManagerNote, OrderStatusHistory, AgentPerformance, TeamPerformance
)

@admin.register(CallCenterAgent)
class CallCenterAgentAdmin(admin.ModelAdmin):
    list_display = ['user', 'employee_id', 'status', 'availability', 'team', 'current_orders_count', 'created_at']
    list_filter = ['status', 'availability', 'team', 'created_at']
    search_fields = ['user__full_name', 'user__email', 'employee_id', 'team']
    readonly_fields = ['current_orders_count', 'created_at', 'updated_at']
    ordering = ['user__full_name']
    
    fieldsets = (
        ('Agent Information', {
            'fields': ('user', 'employee_id', 'phone_extension', 'team')
        }),
        ('Status & Availability', {
            'fields': ('status', 'availability', 'max_concurrent_orders', 'current_orders_count')
        }),
        ('Management', {
            'fields': ('supervisor', 'skills')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(AgentSession)
class AgentSessionAdmin(admin.ModelAdmin):
    list_display = ['agent', 'login_time', 'logout_time', 'status', 'session_duration', 'workstation_id']
    list_filter = ['status', 'login_time', 'agent__team']
    search_fields = ['agent__user__full_name', 'workstation_id', 'ip_address']
    readonly_fields = ['login_time', 'last_activity', 'created_at']
    ordering = ['-login_time']
    
    def session_duration(self, obj):
        duration = obj.get_session_duration()
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours}h {minutes}m"
    session_duration.short_description = "Duration"

@admin.register(CallLog)
class CallLogAdmin(admin.ModelAdmin):
    list_display = ['order_link', 'agent', 'call_time', 'duration_formatted', 'status', 'resolution_status', 'customer_satisfaction']
    list_filter = ['status', 'resolution_status', 'call_time', 'agent__call_center_profile__team']
    search_fields = ['order__order_number', 'agent__full_name', 'notes']
    readonly_fields = ['id', 'call_time', 'created_at', 'updated_at']
    ordering = ['-call_time']
    
    def order_link(self, obj):
        if obj.order:
            url = reverse('admin:orders_order_change', args=[obj.order.id])
            return format_html('<a href="{}">{}</a>', url, obj.order.order_number)
        return '-'
    order_link.short_description = 'Order'
    
    def duration_formatted(self, obj):
        return obj.get_duration_formatted()
    duration_formatted.short_description = 'Duration'

@admin.register(CustomerInteraction)
class CustomerInteractionAdmin(admin.ModelAdmin):
    list_display = ['order_link', 'agent', 'interaction_type', 'interaction_time', 'duration_minutes', 'resolution_status', 'customer_satisfaction']
    list_filter = ['interaction_type', 'resolution_status', 'interaction_time', 'agent__call_center_profile__team']
    search_fields = ['order__order_number', 'agent__full_name', 'interaction_notes']
    readonly_fields = ['interaction_time', 'created_at']
    ordering = ['-interaction_time']
    
    def order_link(self, obj):
        if obj.order:
            url = reverse('admin:orders_order_change', args=[obj.order.id])
            return format_html('<a href="{}">{}</a>', url, obj.order.order_number)
        return '-'
    order_link.short_description = 'Order'

@admin.register(OrderAssignment)
class OrderAssignmentAdmin(admin.ModelAdmin):
    list_display = ['order_link', 'assigned_agent', 'assigned_by', 'assignment_date', 'priority', 'is_active', 'completed_at']
    list_filter = ['priority', 'is_active', 'assignment_date', 'assigned_agent__call_center_profile__team']
    search_fields = ['order__order_number', 'assigned_agent__full_name', 'assigned_by__full_name']
    readonly_fields = ['assignment_date', 'created_at', 'updated_at']
    ordering = ['-assignment_date']
    
    def order_link(self, obj):
        if obj.order:
            url = reverse('admin:orders_order_change', args=[obj.order.id])
            return format_html('<a href="{}">{}</a>', url, obj.order.order_number)
        return '-'
    order_link.short_description = 'Order'

@admin.register(ManagerNote)
class ManagerNoteAdmin(admin.ModelAdmin):
    list_display = ['order_link', 'manager', 'agent', 'note_type', 'is_urgent', 'is_read_by_agent', 'created_at']
    list_filter = ['note_type', 'is_urgent', 'is_read_by_agent', 'created_at', 'manager', 'agent']
    search_fields = ['order__order_number', 'manager__full_name', 'agent__full_name', 'note_text']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def order_link(self, obj):
        if obj.order:
            url = reverse('admin:orders_order_change', args=[obj.order.id])
            return format_html('<a href="{}">{}</a>', url, obj.order.order_number)
        return '-'
    order_link.short_description = 'Order'

@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['order_link', 'agent', 'previous_status', 'new_status', 'change_timestamp', 'customer_notified']
    list_filter = ['previous_status', 'new_status', 'change_timestamp', 'customer_notified', 'agent__call_center_profile__team']
    search_fields = ['order__order_number', 'agent__full_name', 'status_change_reason']
    readonly_fields = ['change_timestamp', 'created_at']
    ordering = ['-change_timestamp']
    
    def order_link(self, obj):
        if obj.order:
            url = reverse('admin:orders_order_change', args=[obj.order.id])
            return format_html('<a href="{}">{}</a>', url, obj.order.order_number)
        return '-'
    order_link.short_description = 'Order'

@admin.register(AgentPerformance)
class AgentPerformanceAdmin(admin.ModelAdmin):
    list_display = ['agent', 'date', 'total_orders_handled', 'orders_confirmed', 'confirmation_rate', 'average_call_duration', 'customer_satisfaction_avg']
    list_filter = ['date', 'agent__call_center_profile__team']
    search_fields = ['agent__full_name', 'agent__email']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-date', 'agent__full_name']
    
    def confirmation_rate(self, obj):
        return f"{obj.get_confirmation_rate():.1f}%"
    confirmation_rate.short_description = 'Confirmation Rate'
    
    fieldsets = (
        ('Agent & Date', {
            'fields': ('agent', 'date')
        }),
        ('Order Metrics', {
            'fields': ('total_orders_handled', 'orders_confirmed', 'orders_cancelled', 'orders_postponed')
        }),
        ('Call Metrics', {
            'fields': ('total_calls_made', 'successful_calls', 'average_call_duration')
        }),
        ('Performance Metrics', {
            'fields': ('customer_satisfaction_avg', 'resolution_rate', 'first_call_resolution_rate')
        }),
        ('Time Metrics', {
            'fields': ('total_work_time_minutes', 'break_time_minutes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(TeamPerformance)
class TeamPerformanceAdmin(admin.ModelAdmin):
    list_display = ['team_name', 'date', 'total_agents', 'active_agents', 'total_orders_handled', 'team_confirmation_rate', 'team_satisfaction_avg']
    list_filter = ['team_name', 'date']
    search_fields = ['team_name']
    readonly_fields = ['created_at']
    ordering = ['-date', 'team_name']
    
    fieldsets = (
        ('Team Information', {
            'fields': ('team_name', 'date')
        }),
        ('Agent Counts', {
            'fields': ('total_agents', 'active_agents')
        }),
        ('Order Metrics', {
            'fields': ('total_orders_handled', 'orders_confirmed', 'orders_cancelled')
        }),
        ('Performance Metrics', {
            'fields': ('average_handle_time', 'team_confirmation_rate', 'team_satisfaction_avg')
        }),
        ('Top Performer', {
            'fields': ('top_performer_agent',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

# Custom admin site configuration
admin.site.site_header = "Call Center Management System"
admin.site.site_title = "Call Center Admin"
admin.site.index_title = "Call Center Administration"
