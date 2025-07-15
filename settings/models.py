# settings/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _

class Country(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    code = models.CharField(max_length=3, unique=True, verbose_name=_("Country Code"))  # ISO 3166-1 alpha-3 code
    currency = models.CharField(max_length=3, verbose_name=_("Currency Code"))  # ISO 4217 currency code
    timezone = models.CharField(max_length=50, verbose_name=_("Timezone"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    
    class Meta:
        verbose_name = _("Country")
        verbose_name_plural = _("Countries")
        ordering = ['name']
    
    def __str__(self):
        return self.name

class DeliveryArea(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='delivery_areas', verbose_name=_("Country"))
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    code = models.CharField(max_length=20, verbose_name=_("Area Code"))
    additional_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("Additional Cost"))  # Additional delivery cost for this area
    
    class Meta:
        verbose_name = _("Delivery Area")
        verbose_name_plural = _("Delivery Areas")
        ordering = ['country__name', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.country.name})"

class DeliveryCompany(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    code = models.CharField(max_length=20, unique=True, verbose_name=_("Company Code"))
    countries = models.ManyToManyField(Country, related_name='delivery_companies', verbose_name=_("Operating Countries"))
    base_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Base Shipping Cost"))
    api_key = models.CharField(max_length=255, blank=True, verbose_name=_("API Key"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    
    class Meta:
        verbose_name = _("Delivery Company")
        verbose_name_plural = _("Delivery Companies")
        ordering = ['name']
    
    def __str__(self):
        return self.name

class SystemFees(models.Model):
    """System-wide fee structure configuration."""
    upsell_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("Upsell Fees"))
    confirmation_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("Confirmation Fees"))
    cancellation_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("Cancellation Fees"))
    fulfillment_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("Fulfillment Fees"))
    shipping_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("Shipping Fees"))
    return_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("Return Fees"))
    warehouse_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("Warehouse Fees"))
    last_updated = models.DateTimeField(auto_now=True, verbose_name=_("Last Updated"))
    updated_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, verbose_name=_("Updated By"))
    
    class Meta:
        verbose_name = _("System Fees")
        verbose_name_plural = _("System Fees")
    
    @classmethod
    def get_default_fees(cls):
        """Get or create default system fees."""
        fees, created = cls.objects.get_or_create(pk=1)
        return fees
    
    def __str__(self):
        return _("System Fees Configuration")

class SystemSetting(models.Model):
    key = models.CharField(max_length=100, unique=True, verbose_name=_("Setting Key"))
    value = models.TextField(verbose_name=_("Value"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    is_public = models.BooleanField(default=False, verbose_name=_("Public"))  # Whether this setting can be viewed by all users
    
    class Meta:
        verbose_name = _("System Setting")
        verbose_name_plural = _("System Settings")
        ordering = ['key']
    
    def __str__(self):
        return self.key

class AuditLog(models.Model):
    ACTION_TYPES = (
        ('create', _('Create')),
        ('update', _('Update')),
        ('delete', _('Delete')),
        ('login', _('Login')),
        ('logout', _('Logout')),
    )
    
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, verbose_name=_("User"))
    action = models.CharField(max_length=20, choices=ACTION_TYPES, verbose_name=_("Action"))
    table = models.CharField(max_length=100, verbose_name=_("Table"))  # The table/model that was affected
    record_id = models.CharField(max_length=100, verbose_name=_("Record ID"))  # The ID of the affected record
    old_value = models.TextField(blank=True, verbose_name=_("Old Value"))  # JSON representation of old values (for updates)
    new_value = models.TextField(blank=True, verbose_name=_("New Value"))  # JSON representation of new values (for creates/updates)
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name=_("IP Address"))
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("Timestamp"))
    notes = models.TextField(blank=True, verbose_name=_("Notes"))
    
    class Meta:
        verbose_name = _("Audit Log")
        verbose_name_plural = _("Audit Logs")
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.action} - {self.table} - {self.timestamp}"