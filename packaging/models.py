# packaging/models.py
from django.db import models

class PackagingRecord(models.Model):
    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE, related_name='packaging')
    packager = models.ForeignKey('users.User', on_delete=models.CASCADE)
    packaging_started = models.DateTimeField(auto_now_add=True)
    packaging_completed = models.DateTimeField(null=True, blank=True)
    packaging_notes = models.TextField(blank=True)
    
    # Package details
    package_type = models.CharField(max_length=50)
    package_weight = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)  # in kg
    dimensions = models.CharField(max_length=50, blank=True)  # format: LxWxH in cm
    barcode = models.CharField(max_length=100, unique=True)