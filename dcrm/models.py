from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
import datetime

class User(AbstractUser):
    """
    Extended User model with role-based access control
    """
    ROLE_CHOICES = (
        ('super_admin', 'Super Admin'),
        ('admin', 'Admin'),
        ('seller', 'Seller'),
        ('stock_keeper', 'Stock Keeper'),
        ('call_center_manager', 'Call Center Manager'),
        ('call_center_agent', 'Call Center Agent'),
        ('packaging', 'Pick & Pack'),
        ('delivery', 'Delivery'),
        ('follow_up', 'Follow-up Dashboard'),
        ('accountant', 'Accountant'),
    )
    
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='dcrm_user_set',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='dcrm_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='admin')  # or another appropriate default
    phone_number = models.CharField(max_length=20)
    business_name = models.CharField(max_length=255, blank=True, null=True)
    country = models.ForeignKey('Country', on_delete=models.SET_NULL, null=True, related_name='users')
    residence_country = models.ForeignKey('Country', on_delete=models.SET_NULL, null=True, related_name='resident_users')
    expected_daily_orders = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(1000)])
    id_document = models.ImageField(upload_to='id_documents/', blank=True, null=True)
    
    
    class Meta:
        permissions = [
            # Super Admin permissions
            ("manage_users", "Can manage all users"),
            ("manage_roles", "Can manage user roles"),
            ("view_audit_log", "Can view audit logs"),
            # Admin permissions
            ("view_financial_reports", "Can view financial reports"),
            ("approve_sourcing", "Can approve sourcing requests"),
            # Other role-specific permissions...
        ]

class AuditLog(models.Model):
    """
    Records system activities for auditing and security
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    model_affected = models.CharField(max_length=100)
    record_id = models.CharField(max_length=100)
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.timestamp}"

class Country(models.Model):
    """
    Country information including currency and timezone
    """
    name_en = models.CharField(max_length=100)
    name_ar = models.CharField(max_length=100)
    currency = models.CharField(max_length=3)  # Currency code (e.g., AED, SAR)
    timezone = models.CharField(max_length=50)  # e.g., GMT+4
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name_en
    
    class Meta:
        verbose_name_plural = "Countries"

class DeliveryCompany(models.Model):
    """
    Delivery companies that handle shipping
    """
    name_en = models.CharField(max_length=100)
    name_ar = models.CharField(max_length=100)
    countries = models.ManyToManyField(Country, related_name='delivery_companies')
    base_shipping_cost = models.DecimalField(max_digits=10, decimal_places=2)
    api_key = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name_en
    
    class Meta:
        verbose_name_plural = "Delivery Companies"

class Warehouse(models.Model):
    """
    Physical storage locations for inventory
    """
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='warehouses')
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    """
    Products sold in the system
    """
    code = models.CharField(max_length=20, unique=True, editable=False)
    name_en = models.CharField(max_length=255)
    name_ar = models.CharField(max_length=255)
    description = models.TextField()
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    product_link = models.URLField(blank=True, null=True)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.code:
            # Generate a product code like PROD-2023-001
            year = datetime.date.today().year
            last_product = Product.objects.filter(code__startswith=f'PROD-{year}').order_by('code').last()
            if last_product:
                last_number = int(last_product.code.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1
            self.code = f'PROD-{year}-{new_number:03d}'
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.code} - {self.name_en}"

class Inventory(models.Model):
    """
    Product inventory tracking
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='inventory')
    total_quantity = models.IntegerField(default=0)
    available_quantity = models.IntegerField(default=0)
    in_delivery_quantity = models.IntegerField(default=0)
    shelf_location = models.CharField(max_length=50, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.product.name_en} - {self.warehouse.name}"
    
    class Meta:
        verbose_name_plural = "Inventories"

class SalesChannel(models.Model):
    """
    E-commerce stores connected to the system
    """
    name_en = models.CharField(max_length=100)
    name_ar = models.CharField(max_length=100)
    url = models.URLField()
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales_channels')
    api_credentials = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name_en

class SourcingRequest(models.Model):
    """
    Requests to import or transfer products
    """
    STATUS_CHOICES = (
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    )
    
    PRIORITY_CHOICES = (
        ('normal', 'Normal'),
        ('urgent', 'Urgent'),
    )
    
    FINANCE_CHOICES = (
        ('seller_account', 'Seller Account'),
        ('company_account', 'Company Account'),
    )
    
    tracking_number = models.CharField(max_length=20, unique=True, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    carton_quantity = models.IntegerField()
    source_country = models.CharField(max_length=100)
    destination_country = models.ForeignKey(Country, on_delete=models.CASCADE)
    finance_source = models.CharField(max_length=20, choices=FINANCE_CHOICES)
    sourcing_agent = models.CharField(max_length=100)
    agent_phone = models.CharField(max_length=20)
    weight = models.DecimalField(max_digits=10, decimal_places=2, help_text="Weight in KG")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sourcing_requests')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Financial fields
    payment_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('partially_paid', 'Partially Paid'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue')
    ], default='pending')
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    due_date = models.DateField(null=True, blank=True)
    
    # Product receipt fields
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_sourcing')
    received_at = models.DateTimeField(null=True, blank=True)
    quality_check_passed = models.BooleanField(null=True, blank=True)
    quality_check_notes = models.TextField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if not self.tracking_number:
            # Generate a tracking number like TRK-2023-001
            year = datetime.date.today().year
            last_request = SourcingRequest.objects.filter(tracking_number__startswith=f'TRK-{year}').order_by('tracking_number').last()
            if last_request:
                last_number = int(last_request.tracking_number.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1
            self.tracking_number = f'TRK-{year}-{new_number:03d}'
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.tracking_number} - {self.product.name_en}"

class SourcingImage(models.Model):
    """
    Images associated with sourcing requests
    """
    sourcing_request = models.ForeignKey(SourcingRequest, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='sourcing/')
    is_product_photo = models.BooleanField(default=True)  # False means it's a shipment label
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Image for {self.sourcing_request.tracking_number}"

class Order(models.Model):
    """
    Customer orders
    """
    STATUS_CHOICES = (
        ('new', 'New'),
        ('confirmed', 'Confirmed'),
        ('no_response', 'No Response'),
        ('closed', 'Closed'),
        ('postponed', 'Postponed'),
        ('under_review', 'Under Review'),
        ('cancelled', 'Cancelled'),
        ('in_preparation', 'In Preparation'),
        ('ready_for_packaging', 'Ready for Packaging'),
        ('packaging_in_progress', 'Packaging in Progress'),
        ('ready_for_delivery', 'Ready for Delivery'),
        ('in_delivery', 'In Delivery'),
        ('delivered', 'Delivered'),
        ('returned', 'Returned'),
        ('failed_delivery', 'Failed Delivery'),
    )
    
    order_code = models.CharField(max_length=20, unique=True, editable=False)
    customer_name = models.CharField(max_length=255)
    customer_phone = models.CharField(max_length=20)
    customer_address = models.TextField()
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    sales_channel = models.ForeignKey(SalesChannel, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Call center fields
    call_center_agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='handled_orders')
    call_attempts = models.IntegerField(default=0)
    last_call_time = models.DateTimeField(null=True, blank=True)
    postponed_date = models.DateField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True, null=True)
    agent_notes = models.TextField(blank=True, null=True)
    
    # Delivery fields
    delivery_company = models.ForeignKey(DeliveryCompany, on_delete=models.SET_NULL, null=True, blank=True)
    tracking_link = models.URLField(blank=True, null=True)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    delivery_date = models.DateField(null=True, blank=True)
    returned_reason = models.TextField(blank=True, null=True)
    
    # Financial fields
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=[
        ('cash', 'Cash on Delivery'),
        ('card', 'Credit/Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('online_payment', 'Online Payment')
    ])
    payment_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
        ('partially_refunded', 'Partially Refunded')
    ], default='pending')
    
    def save(self, *args, **kwargs):
        if not self.order_code:
            # Generate an order code like ORD-2023-001
            year = datetime.date.today().year
            last_order = Order.objects.filter(order_code__startswith=f'ORD-{year}').order_by('order_code').last()
            if last_order:
                last_number = int(last_order.order_code.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1
            self.order_code = f'ORD-{year}-{new_number:03d}'
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.order_code} - {self.customer_name}"

class OrderItem(models.Model):
    """
    Individual items within an order
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    
    @property
    def total_price(self):
        return self.quantity * self.price_per_unit
    
    def __str__(self):
        return f"{self.product.name_en} x {self.quantity}"

class CallLog(models.Model):
    """
    Records of customer interactions
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='call_logs')
    agent = models.ForeignKey(User, on_delete=models.CASCADE)
    call_time = models.DateTimeField(auto_now_add=True)
    call_type = models.CharField(max_length=20, choices=[
        ('phone', 'Phone Call'),
        ('whatsapp', 'WhatsApp Message')
    ])
    result = models.CharField(max_length=20, choices=[
        ('confirmed', 'Confirmed'),
        ('no_answer', 'No Answer'),
        ('cancelled', 'Cancelled'),
        ('escalated', 'Escalated'),
        ('postponed', 'Postponed')
    ])
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Call to {self.order.customer_name} on {self.call_time}"

class Fee(models.Model):
    """
    System fees configuration
    """
    FEE_TYPES = (
        ('payment_gateway', 'Payment Gateway'),
        ('shipping', 'Shipping'),
        ('service', 'Service'),
    )
    
    CALCULATION_TYPES = (
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    )
    
    name = models.CharField(max_length=100)
    fee_type = models.CharField(max_length=20, choices=FEE_TYPES)
    calculation_type = models.CharField(max_length=10, choices=CALCULATION_TYPES)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    applies_to = models.ManyToManyField(Country, blank=True, related_name='fees')
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} - {self.get_fee_type_display()}"

class SellerFee(models.Model):
    """
    Custom fees for specific sellers
    """
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fees')
    fee = models.ForeignKey(Fee, on_delete=models.CASCADE)
    custom_value = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.seller.username} - {self.fee.name}"

class MarketingPlatform(models.Model):
    """
    Marketing platforms used by sellers
    """
    PLATFORM_CHOICES = (
        ('google_ads', 'Google Ads'),
        ('tiktok_ads', 'TikTok Ads'),
        ('meta_ads', 'Meta Ads'),
    )
    
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='marketing_platforms')
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    
    def __str__(self):
        return f"{self.seller.username} - {self.get_platform_display()}"

class PerformanceMetric(models.Model):
    """
    Performance tracking for various roles
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='performance_metrics')
    date = models.DateField()
    
    # Call center agent metrics
    calls_made = models.IntegerField(default=0)
    successful_confirmations = models.IntegerField(default=0)
    average_response_time = models.DurationField(null=True, blank=True)
    
    # Stock keeper metrics
    inventory_accuracy = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    average_order_preparation_time = models.DurationField(null=True, blank=True)
    error_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Delivery metrics
    deliveries_completed = models.IntegerField(default=0)
    successful_deliveries = models.IntegerField(default=0)
    average_delivery_time = models.DurationField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.date}"