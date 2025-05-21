from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings
import uuid

class Supplier(models.Model):
    """Model for storing supplier information."""
    
    name = models.CharField(_('name'), max_length=150)
    contact_person = models.CharField(_('contact person'), max_length=150, blank=True, null=True)
    email = models.EmailField(_('email'), blank=True, null=True)
    phone = models.CharField(_('phone'), max_length=20, blank=True, null=True)
    address = models.TextField(_('address'), blank=True, null=True)
    country = models.CharField(_('country'), max_length=100)
    
    # Rating and quality metrics
    quality_score = models.DecimalField(_('quality score'), max_digits=3, decimal_places=1, default=0.0)
    delivery_score = models.DecimalField(_('delivery score'), max_digits=3, decimal_places=1, default=0.0)
    price_score = models.DecimalField(_('price score'), max_digits=3, decimal_places=1, default=0.0)
    total_orders = models.PositiveIntegerField(_('total orders'), default=0)
    
    # System fields
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='created_suppliers'
    )
    is_active = models.BooleanField(_('active'), default=True)
    
    class Meta:
        verbose_name = _('supplier')
        verbose_name_plural = _('suppliers')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def update_scores(self):
        """Calculate the average scores from all sourcing requests."""
        completed_requests = self.sourcing_requests.filter(status='completed')
        if completed_requests.count() > 0:
            self.quality_score = completed_requests.aggregate(models.Avg('quality_rating'))['quality_rating__avg'] or 0
            self.delivery_score = completed_requests.aggregate(models.Avg('delivery_rating'))['delivery_rating__avg'] or 0
            self.price_score = completed_requests.aggregate(models.Avg('price_rating'))['price_rating__avg'] or 0
            self.total_orders = completed_requests.count()
            self.save()

class SourcingRequest(models.Model):
    """Model for sourcing requests from sellers."""
    
    STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('submitted', _('Submitted')),
        ('under_review', _('Under Review')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('in_progress', _('In Progress')),
        ('shipped', _('Shipped')),
        ('delivered', _('Delivered')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    )
    
    PRIORITY_CHOICES = (
        ('normal', _('Normal')),
        ('urgent', _('Urgent')),
        ('critical', _('Critical')),
    )
    
    FINANCE_SOURCE_CHOICES = (
        ('seller', _('Seller Account')),
        ('company', _('Company Account')),
    )
    
    # Identification
    request_number = models.CharField(_('request number'), max_length=20, unique=True, editable=False)
    
    # Foreign Keys
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='sourcing_requests',
        limit_choices_to={'role': 'seller'}
    )
    supplier = models.ForeignKey(
        Supplier, 
        on_delete=models.PROTECT, 
        related_name='sourcing_requests',
        null=True,
        blank=True
    )
    product = models.ForeignKey(
        'sellers.Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sourcing_requests'
    )
    
    # Request details
    product_name = models.CharField(_('product name'), max_length=200)
    carton_quantity = models.PositiveIntegerField(_('carton quantity'))
    unit_quantity = models.PositiveIntegerField(_('unit quantity'), default=0, help_text=_('Number of units per carton'))
    total_units = models.PositiveIntegerField(_('total units'), default=0)
    source_country = models.CharField(_('source country'), max_length=100)
    destination_country = models.CharField(_('destination country'), max_length=100)
    finance_source = models.CharField(_('finance source'), max_length=20, choices=FINANCE_SOURCE_CHOICES)
    supplier_contact = models.CharField(_('supplier contact'), max_length=100, blank=True, null=True)
    supplier_phone = models.CharField(_('supplier phone'), max_length=20, blank=True, null=True)
    
    # Financial details
    cost_per_unit = models.DecimalField(_('cost per unit'), max_digits=10, decimal_places=2, default=0)
    total_cost = models.DecimalField(_('total cost'), max_digits=10, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(_('shipping cost'), max_digits=10, decimal_places=2, default=0)
    customs_fees = models.DecimalField(_('customs fees'), max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(_('grand total'), max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(_('currency'), max_length=3, default='AED')
    
    # Logistics information
    weight = models.DecimalField(_('weight (kg)'), max_digits=8, decimal_places=2, default=0)
    dimensions = models.CharField(_('dimensions'), max_length=50, blank=True, null=True)
    tracking_number = models.CharField(_('tracking number'), max_length=100, blank=True, null=True)
    estimated_arrival = models.DateField(_('estimated arrival'), blank=True, null=True)
    actual_arrival = models.DateField(_('actual arrival'), blank=True, null=True)
    
    # Status and workflow
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='draft')
    priority = models.CharField(_('priority'), max_length=10, choices=PRIORITY_CHOICES, default='normal')
    notes = models.TextField(_('notes'), blank=True, null=True)
    
    # Timestamps and tracking
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    submitted_at = models.DateTimeField(_('submitted at'), blank=True, null=True)
    approved_at = models.DateTimeField(_('approved at'), blank=True, null=True)
    completed_at = models.DateTimeField(_('completed at'), blank=True, null=True)
    
    # Approval workflow
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='approved_sourcing_requests'
    )
    
    # Ratings (filled after completion)
    quality_rating = models.DecimalField(_('quality rating'), max_digits=3, decimal_places=1, default=0)
    delivery_rating = models.DecimalField(_('delivery rating'), max_digits=3, decimal_places=1, default=0)
    price_rating = models.DecimalField(_('price rating'), max_digits=3, decimal_places=1, default=0)
    
    class Meta:
        verbose_name = _('sourcing request')
        verbose_name_plural = _('sourcing requests')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.request_number
    
    def save(self, *args, **kwargs):
        # Generate the request number if it doesn't exist
        if not self.request_number:
            year = timezone.now().year
            month = timezone.now().month
            prefix = f"SOR-{year}-{month:02d}-"
            
            # Get the latest request number with this prefix
            latest = SourcingRequest.objects.filter(
                request_number__startswith=prefix
            ).order_by('-request_number').first()
            
            if latest:
                # Extract the number and increment
                last_num = int(latest.request_number.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
                
            self.request_number = f"{prefix}{new_num:04d}"
        
        # Calculate totals
        self.total_units = self.carton_quantity * self.unit_quantity
        self.grand_total = self.total_cost + self.shipping_cost + self.customs_fees
        
        # Update status timestamps
        if self.status == 'submitted' and not self.submitted_at:
            self.submitted_at = timezone.now()
        if self.status == 'approved' and not self.approved_at:
            self.approved_at = timezone.now()
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
            
            # Update supplier ratings if this is a new completion
            if self.supplier:
                self.supplier.update_scores()
                
        super().save(*args, **kwargs)

class SourcingRequestDocument(models.Model):
    """Model for storing documents related to sourcing requests."""
    
    DOCUMENT_TYPES = (
        ('invoice', _('Invoice')),
        ('packing_list', _('Packing List')),
        ('shipping_label', _('Shipping Label')),
        ('product_image', _('Product Image')),
        ('customs_document', _('Customs Document')),
        ('payment_receipt', _('Payment Receipt')),
        ('other', _('Other')),
    )
    
    sourcing_request = models.ForeignKey(
        SourcingRequest, 
        on_delete=models.CASCADE, 
        related_name='documents'
    )
    document_type = models.CharField(_('document type'), max_length=20, choices=DOCUMENT_TYPES)
    file = models.FileField(_('file'), upload_to='sourcing_documents/')
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='uploaded_sourcing_documents'
    )
    uploaded_at = models.DateTimeField(_('uploaded at'), auto_now_add=True)
    notes = models.TextField(_('notes'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('sourcing request document')
        verbose_name_plural = _('sourcing request documents')
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.get_document_type_display()} for {self.sourcing_request.request_number}"

class SourcingComment(models.Model):
    """Model for comments on sourcing requests."""
    
    sourcing_request = models.ForeignKey(
        SourcingRequest, 
        on_delete=models.CASCADE, 
        related_name='comments'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )
    comment = models.TextField(_('comment'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('sourcing comment')
        verbose_name_plural = _('sourcing comments')
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.user.get_full_name()} on {self.sourcing_request.request_number}"
