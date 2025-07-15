# settings/models.py
from django.db import models

class Country(models.Model):
    name_en = models.CharField(max_length=100)
    name_ar = models.CharField(max_length=100)
    code = models.CharField(max_length=3, unique=True)  # ISO 3166-1 alpha-3 code
    currency = models.CharField(max_length=3)  # ISO 4217 currency code
    timezone = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

class DeliveryArea(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='delivery_areas')
    name_en = models.CharField(max_length=100)
    name_ar = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    additional_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Additional delivery cost for this area

class DeliveryCompany(models.Model):
    name_en = models.CharField(max_length=100)
    name_ar = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    countries = models.ManyToManyField(Country, related_name='delivery_companies')
    base_cost = models.DecimalField(max_digits=10, decimal_places=2)
    api_key = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name_en

class SystemSetting(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)  # Whether this setting can be viewed by all users

class AuditLog(models.Model):
    ACTION_TYPES = (
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
    )
    
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=ACTION_TYPES)
    table = models.CharField(max_length=100)  # The table/model that was affected
    record_id = models.CharField(max_length=100)  # The ID of the affected record
    old_value = models.TextField(blank=True)  # JSON representation of old values (for updates)
    new_value = models.TextField(blank=True)  # JSON representation of new values (for creates/updates)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)