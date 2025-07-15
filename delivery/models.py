# delivery/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class DeliveryCompany(models.Model):
    """Delivery Company Model as specified in the delivery system readme."""
    name = models.CharField(max_length=255, verbose_name=_('Name'), default='')
    contact_person = models.CharField(max_length=255, blank=True, verbose_name=_('Contact Person'))
    phone = models.CharField(max_length=20, blank=True, verbose_name=_('Phone'))
    email = models.EmailField(blank=True, verbose_name=_('Email'))
    address = models.TextField(blank=True, verbose_name=_('Address'))
    status = models.CharField(
        max_length=20, 
        choices=[('active', _('Active')), ('inactive', _('Inactive'))],
        default='active',
        verbose_name=_('Status')
    )
    created_at = models.DateTimeField(default=timezone.now, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    def __str__(self):
        return self.name
    
    def get_status_display_class(self):
        """Returns CSS class for status badges"""
        if self.status == 'active':
            return 'bg-green-100 text-green-800'
        return 'bg-gray-100 text-gray-800'
    
    class Meta:
        verbose_name = _('Delivery Company')
        verbose_name_plural = _('Delivery Companies')
        ordering = ['name']

class Courier(models.Model):
    """Courier/Delivery Agent Model as specified in the delivery system readme."""
    name = models.CharField(max_length=255, verbose_name=_('Name'), default='')
    company = models.ForeignKey(DeliveryCompany, on_delete=models.CASCADE, related_name='couriers', verbose_name=_('Company'))
    phone = models.CharField(max_length=20, blank=True, verbose_name=_('Phone'))
    email = models.EmailField(blank=True, verbose_name=_('Email'))
    status = models.CharField(
        max_length=20, 
        choices=[
            ('active', _('Active')), 
            ('inactive', _('Inactive')), 
            ('suspended', _('Suspended'))
        ],
        default='active',
        verbose_name=_('Status')
    )
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True, verbose_name=_('Rating'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    
    # Service areas that this courier can deliver to
    service_areas = models.ManyToManyField('settings.Country', blank=True, related_name='couriers', verbose_name=_('Service Areas'))
    
    # Additional fields for tracking and performance
    available = models.BooleanField(default=True, verbose_name=_('Available'))
    current_location = models.CharField(max_length=255, blank=True, verbose_name=_('Current Location'))
    last_active = models.DateTimeField(null=True, blank=True, verbose_name=_('Last Active'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    
    # Connect to user account
    user = models.OneToOneField('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='courier_profile')
    
    # Vehicle information
    vehicle_type = models.CharField(max_length=100, blank=True, verbose_name=_('Vehicle Type'))
    license_plate = models.CharField(max_length=50, blank=True, verbose_name=_('License Plate'))
    
    class Meta:
        verbose_name = _('Courier')
        verbose_name_plural = _('Couriers')
        db_table = 'couriers'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.company.name})"
    
    def get_status_display_class(self):
        """Returns CSS class for status badges"""
        if self.status == 'active':
            return 'bg-green-100 text-green-800'
        elif self.status == 'inactive':
            return 'bg-gray-100 text-gray-800'
        elif self.status == 'suspended':
            return 'bg-red-100 text-red-800'
        return 'bg-gray-100 text-gray-800'

class DeliveryStatusHistory(models.Model):
    """Delivery Status History Model to track all status changes."""
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='delivery_status_history', verbose_name=_('Order'))
    status = models.CharField(max_length=50, verbose_name=_('Status'))
    updated_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='status_updates', verbose_name=_('Updated By'))
    notes = models.TextField(blank=True, verbose_name=_('Notes'))
    location = models.CharField(max_length=255, blank=True, verbose_name=_('Location'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))

    class Meta:
        verbose_name = _('Delivery Status History')
        verbose_name_plural = _('Delivery Status History')
        db_table = 'delivery_status_history'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order.order_code} - {self.status} - {self.created_at}"

# Compatible with the existing migrations
class DeliveryRecord(models.Model):
    """Simple Delivery Record Model based on the existing migrations."""
    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE, related_name='delivery', verbose_name=_('Order'))
    tracking_number = models.CharField(max_length=100, verbose_name=_('Tracking Number'))
    status = models.CharField(
        max_length=20, 
        choices=[
            ('assigned', _('Assigned')),
            ('picked_up', _('Picked Up')),
            ('in_transit', _('In Transit')),
            ('out_for_delivery', _('Out for Delivery')),
            ('delivered', _('Delivered')),
            ('failed', _('Failed')),
            ('returned', _('Returned'))
        ],
        default='assigned',
        verbose_name=_('Status')
    )
    driver = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Driver'))
    assigned_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Assigned At'))
    picked_up_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Picked Up At'))
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Delivered At'))
    delivery_notes = models.TextField(blank=True, verbose_name=_('Delivery Notes'))
    delivery_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Delivery Cost'))

    def __str__(self):
        return f"{self.order.order_code} - {self.tracking_number}"

    def get_status_display_class(self):
        """Returns CSS class for status badges"""
        if self.status == 'delivered':
            return 'bg-green-100 text-green-800'
        elif self.status == 'failed' or self.status == 'returned':
            return 'bg-red-100 text-red-800'
        elif self.status == 'in_transit':
            return 'bg-yellow-100 text-yellow-800'
        elif self.status == 'out_for_delivery':
            return 'bg-orange-100 text-orange-800'
        elif self.status == 'assigned' or self.status == 'picked_up':
            return 'bg-blue-100 text-blue-800'
        else:
            return 'bg-gray-100 text-gray-800'

# Future version with expanded functionality
class DeliveryRecordEnhanced(models.Model):
    """Enhanced Delivery Record Model based on the requirements."""
    STATUS_CHOICES = (
        ('pending_assignment', _('Pending Assignment')),
        ('assigned', _('Assigned')),
        ('ready_for_pickup', _('Ready for Pickup')),
        ('picked_up', _('Picked Up')),
        ('in_transit', _('In Transit')),
        ('out_for_delivery', _('Out for Delivery')),
        ('delivered', _('Delivered')),
        ('failed', _('Failed')),
        ('returned', _('Returned')),
    )
    
    PRIORITY_CHOICES = (
        ('low', _('Low')),
        ('normal', _('Normal')),
        ('high', _('High')),
        ('urgent', _('Urgent')),
    )
    
    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE, related_name='delivery_enhanced', verbose_name=_('Order'))
    tracking_number = models.CharField(max_length=100, unique=True, verbose_name=_('Tracking Number'))
    barcode = models.TextField(blank=True, verbose_name=_('Barcode'))
    
    # Relationships
    delivery_company = models.ForeignKey(DeliveryCompany, on_delete=models.CASCADE, verbose_name=_('Delivery Company'))
    courier = models.ForeignKey(Courier, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Courier'))
    call_agent = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_deliveries', verbose_name=_('Call Agent'))
    
    # Status fields
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_assignment', verbose_name=_('Status'))
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal', verbose_name=_('Priority'))
    
    # Timestamps
    assigned_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Assigned At'))
    pickup_date = models.DateTimeField(null=True, blank=True, verbose_name=_('Pickup Date'))
    delivery_date = models.DateTimeField(null=True, blank=True, verbose_name=_('Delivery Date'))
    estimated_delivery = models.DateTimeField(null=True, blank=True, verbose_name=_('Estimated Delivery'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    
    # Additional details
    delivery_notes = models.TextField(blank=True, verbose_name=_('Delivery Notes'))
    delivery_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('Delivery Cost'))
    delivery_proof = models.ImageField(upload_to='delivery_proofs/', null=True, blank=True, verbose_name=_('Delivery Proof'))
    customer_signature = models.ImageField(upload_to='customer_signatures/', null=True, blank=True, verbose_name=_('Customer Signature'))
    
    # Failure handling
    failure_reason = models.CharField(max_length=100, blank=True, verbose_name=_('Failure Reason'))
    retry_count = models.PositiveIntegerField(default=0, verbose_name=_('Retry Count'))
    next_attempt = models.DateTimeField(null=True, blank=True, verbose_name=_('Next Attempt'))

    class Meta:
        verbose_name = _('Enhanced Delivery Record')
        verbose_name_plural = _('Enhanced Delivery Records')
        db_table = 'delivery_records_enhanced'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order.order_code} - {self.tracking_number}"
    
    def get_status_display_class(self):
        """Returns CSS class for status badges"""
        if self.status == 'delivered':
            return 'bg-green-100 text-green-800'
        elif self.status == 'failed' or self.status == 'returned':
            return 'bg-red-100 text-red-800'
        elif self.status == 'in_transit':
            return 'bg-yellow-100 text-yellow-800'
        elif self.status == 'out_for_delivery':
            return 'bg-orange-100 text-orange-800'
        elif self.status == 'assigned' or self.status == 'picked_up':
            return 'bg-blue-100 text-blue-800'
        elif self.status == 'ready_for_pickup':
            return 'bg-purple-100 text-purple-800'
        else:
            return 'bg-gray-100 text-gray-800'
    
    def get_priority_display_class(self):
        """Returns CSS class for priority badges"""
        if self.priority == 'urgent':
            return 'bg-red-100 text-red-800'
        elif self.priority == 'high':
            return 'bg-orange-100 text-orange-800'
        elif self.priority == 'low':
            return 'bg-blue-100 text-blue-800'
        else:
            return 'bg-green-100 text-green-800'
    
    def update_status(self, new_status, user, notes='', location=''):
        """
        Update the delivery status and create a status history record
        Returns True if status was changed, False if unchanged
        """
        if self.status == new_status:
            return False
        
        old_status = self.status
        self.status = new_status
        
        # Update related timestamps based on status
        now = timezone.now()
        if new_status == 'picked_up':
            self.pickup_date = now
        elif new_status == 'delivered':
            self.delivery_date = now
        
        # Save the updated record
        self.save()
        
        # Create a status history record
        status_history = DeliveryStatusHistory.objects.create(
            order=self.order,
            status=new_status,
            updated_by=user,
            notes=notes,
            location=location
        )
        
        return True

# New models for Delivery Panel

class CourierSession(models.Model):
    """Courier Sessions Table for tracking courier logins and activity"""
    courier = models.ForeignKey(Courier, on_delete=models.CASCADE, related_name='sessions', verbose_name=_('Courier'))
    login_time = models.DateTimeField(auto_now_add=True, verbose_name=_('Login Time'))
    logout_time = models.DateTimeField(null=True, blank=True, verbose_name=_('Logout Time'))
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', _('Active')),
            ('break', _('Break')),
            ('offline', _('Offline'))
        ],
        default='active',
        verbose_name=_('Status')
    )
    location_lat = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True, verbose_name=_('Latitude'))
    location_lng = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True, verbose_name=_('Longitude'))
    last_activity = models.DateTimeField(auto_now=True, verbose_name=_('Last Activity'))
    device_info = models.TextField(blank=True, verbose_name=_('Device Info'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))

    class Meta:
        verbose_name = _('Courier Session')
        verbose_name_plural = _('Courier Sessions')
        db_table = 'courier_sessions'
        ordering = ['-login_time']

    def __str__(self):
        return f"{self.courier.name} - {self.login_time}"

class DeliveryAttempt(models.Model):
    """Delivery Attempts Table for tracking all delivery attempts"""
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='delivery_attempts', verbose_name=_('Order'))
    courier = models.ForeignKey(Courier, on_delete=models.CASCADE, related_name='delivery_attempts', verbose_name=_('Courier'))
    attempt_number = models.PositiveIntegerField(default=1, verbose_name=_('Attempt Number'))
    attempt_time = models.DateTimeField(auto_now_add=True, verbose_name=_('Attempt Time'))
    status = models.CharField(
        max_length=20,
        choices=[
            ('successful', _('Successful')),
            ('failed', _('Failed')),
            ('rescheduled', _('Rescheduled'))
        ],
        default='failed',
        verbose_name=_('Status')
    )
    failure_reason = models.CharField(max_length=255, blank=True, verbose_name=_('Failure Reason'))
    customer_feedback = models.TextField(blank=True, verbose_name=_('Customer Feedback'))
    proof_image = models.ImageField(upload_to='delivery_attempts/', null=True, blank=True, verbose_name=_('Proof Image'))
    signature_data = models.TextField(blank=True, verbose_name=_('Signature Data'))
    notes = models.TextField(blank=True, verbose_name=_('Notes'))
    next_attempt_date = models.DateTimeField(null=True, blank=True, verbose_name=_('Next Attempt Date'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))

    class Meta:
        verbose_name = _('Delivery Attempt')
        verbose_name_plural = _('Delivery Attempts')
        db_table = 'delivery_attempts'
        ordering = ['-attempt_time']

    def __str__(self):
        return f"{self.order.order_code} - Attempt #{self.attempt_number}"

class CourierLocation(models.Model):
    """Courier Locations Table for tracking real-time courier locations"""
    courier = models.ForeignKey(Courier, on_delete=models.CASCADE, related_name='locations', verbose_name=_('Courier'))
    latitude = models.DecimalField(max_digits=10, decimal_places=8, verbose_name=_('Latitude'))
    longitude = models.DecimalField(max_digits=11, decimal_places=8, verbose_name=_('Longitude'))
    accuracy = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name=_('Accuracy'))
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_('Timestamp'))
    battery_level = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('Battery Level'))
    connection_type = models.CharField(
        max_length=20,
        choices=[
            ('wifi', _('WiFi')),
            ('cellular', _('Cellular')),
            ('offline', _('Offline'))
        ],
        default='cellular',
        verbose_name=_('Connection Type')
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))

    class Meta:
        verbose_name = _('Courier Location')
        verbose_name_plural = _('Courier Locations')
        db_table = 'courier_locations'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.courier.name} - {self.timestamp}"

class DeliveryProof(models.Model):
    """Delivery Proof Table for storing delivery verification data"""
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='delivery_proofs', verbose_name=_('Order'))
    courier = models.ForeignKey(Courier, on_delete=models.CASCADE, related_name='delivery_proofs', verbose_name=_('Courier'))
    proof_type = models.CharField(
        max_length=20,
        choices=[
            ('photo', _('Photo')),
            ('signature', _('Signature')),
            ('barcode', _('Barcode')),
            ('otp', _('OTP'))
        ],
        default='photo',
        verbose_name=_('Proof Type')
    )
    proof_data = models.TextField(blank=True, verbose_name=_('Proof Data'))
    capture_time = models.DateTimeField(auto_now_add=True, verbose_name=_('Capture Time'))
    location_lat = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True, verbose_name=_('Latitude'))
    location_lng = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True, verbose_name=_('Longitude'))
    verified = models.BooleanField(default=False, verbose_name=_('Verified'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))

    class Meta:
        verbose_name = _('Delivery Proof')
        verbose_name_plural = _('Delivery Proofs')
        db_table = 'delivery_proofs'
        ordering = ['-capture_time']

    def __str__(self):
        return f"{self.order.order_code} - {self.proof_type} - {self.capture_time}"