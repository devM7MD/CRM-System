from django.contrib import admin
from django.utils.html import format_html
from .models import Role, Permission, RolePermission, UserRole, RoleAuditLog

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'role_type', 'is_active', 'is_default', 'user_count', 'created_at']
    list_filter = ['role_type', 'is_active', 'is_default', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'user_count']
    ordering = ['name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'role_type', 'description')
        }),
        ('Status', {
            'fields': ('is_active', 'is_default')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_count(self, obj):
        return obj.get_user_count()
    user_count.short_description = 'Users'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only set created_by on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'codename', 'permission_type', 'module', 'is_active']
    list_filter = ['permission_type', 'module', 'is_active', 'created_at']
    search_fields = ['name', 'codename', 'description']
    readonly_fields = ['created_at']
    ordering = ['module', 'permission_type', 'name']
    
    fieldsets = (
        ('Permission Details', {
            'fields': ('name', 'codename', 'description')
        }),
        ('Access Control', {
            'fields': ('permission_type', 'module')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

class RolePermissionInline(admin.TabularInline):
    model = RolePermission
    extra = 1
    fields = ['permission', 'granted', 'granted_by']
    readonly_fields = ['granted_at']

@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ['role', 'permission', 'granted', 'granted_at', 'granted_by']
    list_filter = ['granted', 'granted_at', 'role', 'permission__module']
    search_fields = ['role__name', 'permission__name']
    readonly_fields = ['granted_at']
    ordering = ['role__name', 'permission__name']

class UserRoleInline(admin.TabularInline):
    model = UserRole
    extra = 1
    fields = ['role', 'is_primary', 'is_active', 'expires_at']
    readonly_fields = ['assigned_at']

@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'is_primary', 'is_active', 'assigned_at', 'expires_at', 'assigned_by']
    list_filter = ['is_primary', 'is_active', 'assigned_at', 'role']
    search_fields = ['user__email', 'user__full_name', 'role__name']
    readonly_fields = ['assigned_at']
    ordering = ['user__full_name', 'role__name']
    
    fieldsets = (
        ('User and Role', {
            'fields': ('user', 'role')
        }),
        ('Assignment Details', {
            'fields': ('is_primary', 'is_active', 'expires_at')
        }),
        ('Metadata', {
            'fields': ('assigned_by', 'assigned_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only set assigned_by on creation
            obj.assigned_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(RoleAuditLog)
class RoleAuditLogAdmin(admin.ModelAdmin):
    list_display = ['action', 'user', 'role', 'target_user', 'timestamp', 'ip_address']
    list_filter = ['action', 'timestamp', 'role']
    search_fields = ['user__email', 'role__name', 'target_user__email', 'description']
    readonly_fields = ['action', 'user', 'role', 'target_user', 'permission', 'description', 'ip_address', 'user_agent', 'timestamp']
    ordering = ['-timestamp']
    
    def has_add_permission(self, request):
        return False  # Audit logs should only be created by the system
    
    def has_change_permission(self, request, obj=None):
        return False  # Audit logs should not be editable
    
    fieldsets = (
        ('Action Details', {
            'fields': ('action', 'description')
        }),
        ('Users Involved', {
            'fields': ('user', 'target_user')
        }),
        ('Related Objects', {
            'fields': ('role', 'permission')
        }),
        ('System Information', {
            'fields': ('ip_address', 'user_agent', 'timestamp'),
            'classes': ('collapse',)
        }),
    )
