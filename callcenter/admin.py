from django.contrib import admin
from .models import (
    CallLog, AgentPerformance, AgentSession, CustomerInteraction,
    OrderStatusHistory, OrderAssignment, ManagerNote, TeamPerformance
)

@admin.register(CallLog)
class CallLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'agent', 'call_time', 'status', 'duration', 'resolution_status']
    list_filter = ['status', 'resolution_status', 'call_time', 'agent']
    search_fields = ['order__id', 'agent__username', 'notes']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'call_time'

@admin.register(AgentPerformance)
class AgentPerformanceAdmin(admin.ModelAdmin):
    list_display = ['agent', 'date', 'total_calls_made', 'orders_confirmed', 'orders_cancelled', 'customer_satisfaction_avg']
    list_filter = ['date', 'agent']
    search_fields = ['agent__username']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'

@admin.register(AgentSession)
class AgentSessionAdmin(admin.ModelAdmin):
    list_display = ['agent', 'login_time', 'logout_time', 'status', 'concurrent_orders', 'last_activity']
    list_filter = ['status', 'login_time']
    search_fields = ['agent__username', 'workstation_id']
    readonly_fields = ['created_at', 'last_activity']
    date_hierarchy = 'login_time'

@admin.register(CustomerInteraction)
class CustomerInteractionAdmin(admin.ModelAdmin):
    list_display = ['order', 'agent', 'interaction_type', 'interaction_time', 'resolution_status', 'customer_satisfaction']
    list_filter = ['interaction_type', 'resolution_status', 'interaction_time']
    search_fields = ['order__id', 'agent__username', 'interaction_notes']
    readonly_fields = ['created_at']
    date_hierarchy = 'interaction_time'

@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['order', 'agent', 'previous_status', 'new_status', 'change_timestamp', 'customer_notified']
    list_filter = ['previous_status', 'new_status', 'change_timestamp']
    search_fields = ['order__id', 'agent__username', 'status_change_reason']
    readonly_fields = ['created_at']
    date_hierarchy = 'change_timestamp'

@admin.register(OrderAssignment)
class OrderAssignmentAdmin(admin.ModelAdmin):
    list_display = ['order', 'manager', 'agent', 'priority_level', 'assignment_date', 'expected_completion']
    list_filter = ['priority_level', 'assignment_date']
    search_fields = ['order__id', 'manager__username', 'agent__username', 'manager_notes']
    readonly_fields = ['created_at']
    date_hierarchy = 'assignment_date'

@admin.register(ManagerNote)
class ManagerNoteAdmin(admin.ModelAdmin):
    list_display = ['order', 'manager', 'agent', 'note_type', 'is_urgent', 'is_read_by_agent', 'created_at']
    list_filter = ['note_type', 'is_urgent', 'is_read_by_agent', 'created_at']
    search_fields = ['order__id', 'manager__username', 'agent__username', 'note_text']
    readonly_fields = ['created_at', 'read_at']
    date_hierarchy = 'created_at'

@admin.register(TeamPerformance)
class TeamPerformanceAdmin(admin.ModelAdmin):
    list_display = ['team', 'date', 'total_agents', 'orders_handled', 'orders_confirmed', 'team_confirmation_rate']
    list_filter = ['team', 'date']
    search_fields = ['team']
    readonly_fields = ['created_at']
    date_hierarchy = 'date'
