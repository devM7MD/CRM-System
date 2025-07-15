# delivery/models.py
from django.db import models

class DeliveryCompany(models.Model):
    name_en = models.CharField(max_length=100)
    name_ar = models.CharField(max_length=100)
    countries = models.ManyToManyField('settings.Country')
    base_cost = models.DecimalField(max_digits=10, decimal_places=2)
    api_key = models.CharField(max_length=255, blank=True)
    api_secret = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

class DeliveryRecord(models.Model):
    STATUS_CHOICES = (
        ('assigned', 'Assigned'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('returned', 'Returned'),
    )
    
    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE, related_name='delivery')
    delivery_company = models.ForeignKey(DeliveryCompany, on_delete=models.CASCADE)
    driver = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    tracking_number = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')
    assigned_at = models.DateTimeField(auto_now_add=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    delivery_notes = models.TextField(blank=True)
    delivery_cost = models.DecimalField(max_digits=10, decimal_places=2)