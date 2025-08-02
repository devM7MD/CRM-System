# finance/models.py
from django.db import models
from django.utils import timezone
import uuid

def generate_payment_id():
    """Generate a unique payment ID for Truvo payments."""
    return f"TRU-{uuid.uuid4().hex[:12].upper()}"

class Payment(models.Model):
    PAYMENT_METHODS = (
        ('cash', 'Cash'),
        ('credit_card', 'Credit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('paypal', 'PayPal'),
        ('truvo', 'Truvo Payment'),
    )
    
    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('processing', 'Processing'),
    )
    
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)
    
    # Additional fields for better payment tracking
    seller = models.ForeignKey('users.User', on_delete=models.CASCADE, null=True, blank=True, related_name='seller_payments')
    customer_name = models.CharField(max_length=255, blank=True)
    customer_email = models.EmailField(blank=True)
    customer_phone = models.CharField(max_length=20, blank=True)
    
    # Payment processing details
    processor_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=3, default='AED')
    
    # Payment verification
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_payments')
    
    class Meta:
        ordering = ['-payment_date']
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
    
    def __str__(self):
        return f"Payment {self.transaction_id or self.id} - {self.amount} {self.currency}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate net amount if not set
        if not self.net_amount:
            self.net_amount = self.amount - self.processor_fee
        super().save(*args, **kwargs)

class TruvoPayment(models.Model):
    """Truvo Payment Integration Model"""
    
    PAYMENT_STATUS = (
        ('initiated', 'Initiated'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    )
    
    # Payment identification
    payment_id = models.CharField(max_length=100, unique=True, default=generate_payment_id)
    truvo_transaction_id = models.CharField(max_length=100, blank=True)
    
    # Payment details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='AED')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='initiated')
    
    # Customer information
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    
    # Order reference
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='truvo_payments', null=True, blank=True)
    seller = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='truvo_payments')
    
    # Payment processing
    payment_method = models.CharField(max_length=50, default='truvo')
    processor_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Additional data
    payment_url = models.URLField(blank=True)
    callback_url = models.URLField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Truvo Payment'
        verbose_name_plural = 'Truvo Payments'
    
    def __str__(self):
        return f"Truvo Payment {self.payment_id} - {self.amount} {self.currency}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate net amount
        if not self.net_amount:
            self.net_amount = self.amount - self.processor_fee
        
        # Update completed_at when status changes to completed
        if self.payment_status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    @property
    def is_successful(self):
        return self.payment_status == 'completed'
    
    @property
    def is_failed(self):
        return self.payment_status in ['failed', 'cancelled']
    
    @property
    def is_pending(self):
        return self.payment_status in ['initiated', 'processing']

class Invoice(models.Model):
    INVOICE_STATUS = (
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    )
    
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='invoices')
    invoice_number = models.CharField(max_length=50, unique=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=INVOICE_STATUS, default='draft')
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.order.order_code}"

class SellerFee(models.Model):
    seller = models.ForeignKey('users.User', on_delete=models.CASCADE)
    fee_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.seller.get_full_name()} - {self.fee_percentage}%"