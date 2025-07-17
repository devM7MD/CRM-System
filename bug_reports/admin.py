from django.contrib import admin
from .models import BugReport, BugReportImage

class BugReportImageInline(admin.TabularInline):
    model = BugReportImage
    extra = 0
    readonly_fields = ['uploaded_at']

@admin.register(BugReport)
class BugReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'reporter', 'priority', 'status', 'created_at']
    list_filter = ['status', 'priority', 'created_at']
    search_fields = ['title', 'description', 'reporter__first_name', 'reporter__last_name']
    readonly_fields = ['created_at', 'updated_at', 'discord_message_id']
    inlines = [BugReportImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'reporter')
        }),
        ('Classification', {
            'fields': ('priority', 'status')
        }),
        ('Technical Details', {
            'fields': ('page_url', 'browser_info')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Discord Integration', {
            'fields': ('discord_message_id',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('reporter')
