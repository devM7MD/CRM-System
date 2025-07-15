from django.contrib import admin
from .models import Supplier, SourcingRequest, SourcingRequestDocument, SourcingComment

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'email', 'phone', 'country', 'is_active')
    list_filter = ('country', 'is_active')
    search_fields = ('name', 'contact_person', 'email', 'phone')

@admin.register(SourcingRequest)
class SourcingRequestAdmin(admin.ModelAdmin):
    list_display = ('request_number', 'product_name', 'seller', 'supplier', 'status', 'created_at')
    list_filter = ('status', 'priority', 'seller', 'supplier', 'created_at')
    search_fields = ('request_number', 'product_name', 'seller__full_name', 'supplier__name')
    readonly_fields = ('request_number', 'created_at', 'updated_at')

@admin.register(SourcingRequestDocument)
class SourcingRequestDocumentAdmin(admin.ModelAdmin):
    list_display = ('sourcing_request', 'document_type', 'uploaded_by', 'uploaded_at')
    list_filter = ('document_type', 'uploaded_at')
    search_fields = ('sourcing_request__request_number', 'notes')

@admin.register(SourcingComment)
class SourcingCommentAdmin(admin.ModelAdmin):
    list_display = ('sourcing_request', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('sourcing_request__request_number', 'comment')
