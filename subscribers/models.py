from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from users.models import User

class Subscriber(models.Model):
    """Model to store subscriber information"""
    
    # Link to User model
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscriber_profile', null=True, blank=True)
    
    # Basic information
    full_name = models.CharField(_('full name'), max_length=150)
    email = models.EmailField(_('email address'), unique=True)
    phone_number = models.CharField(_('phone number'), max_length=20)
    
    # Business information
    business_name = models.CharField(_('business name'), max_length=150, blank=True, null=True)
    residence_country = models.CharField(_('residence country'), max_length=100, blank=True, null=True)
    
    # Additional fields
    address = models.TextField(_('address'), blank=True, null=True)
    city = models.CharField(_('city'), max_length=100, blank=True, null=True)
    postal_code = models.CharField(_('postal code'), max_length=20, blank=True, null=True)
    
    # Subscription details
    subscription_type = models.CharField(_('subscription type'), max_length=50, default='basic')
    is_active = models.BooleanField(_('active'), default=True)
    subscription_date = models.DateTimeField(_('subscription date'), default=timezone.now)
    
    # Notes and preferences
    notes = models.TextField(_('notes'), blank=True, null=True)
    preferences = models.JSONField(_('preferences'), default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('subscriber')
        verbose_name_plural = _('subscribers')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.full_name} ({self.email})"
    
    def get_display_name(self):
        """Get display name for the subscriber"""
        return self.full_name or self.email
    
    def get_contact_info(self):
        """Get formatted contact information"""
        return {
            'email': self.email,
            'phone': self.phone_number,
            'business': self.business_name,
            'country': self.residence_country
        }
    
    def is_recent_subscriber(self):
        """Check if subscriber joined in the last 30 days"""
        return (timezone.now() - self.created_at).days <= 30 