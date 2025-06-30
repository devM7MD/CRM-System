from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Role, Permission

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'codename', 'category')
    list_filter = ('category',)
    search_fields = ('name', 'codename', 'description')
    ordering = ('category', 'name')
    fieldsets = (
        (None, {'fields': ('name', 'codename')}),
        (_('Details'), {'fields': ('category', 'description')}),
    )

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_system_role', 'created_at', 'updated_at')
    list_filter = ('is_system_role',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('permissions',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('name', 'slug', 'description', 'is_system_role')}),
        (_('Permissions'), {'fields': ('permissions',)}),
        (_('Required Fields'), {'fields': ('required_fields',)}),
        (_('Metadata'), {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Make system roles less editable."""
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and obj.is_system_role:
            readonly_fields.extend(['is_system_role', 'slug'])
        return readonly_fields
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of system roles."""
        if obj and obj.is_system_role:
            return False
        return super().has_delete_permission(request, obj)
