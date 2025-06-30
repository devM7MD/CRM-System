from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class OrderPayment(models.Model):
    """Model for tracking order payments."""
    PAYMENT_STATUS = [
        ('paid', _('Paid')),
        ('postponed', _('Postponed')),
        ('pending', _('Pending Payment')),
    ]
    
    PAYMENT_METHODS = [
        ('bank_transfer', _('Bank Transfer')),
        ('paypal', _('PayPal')),
        ('cash', _('Cash')),
        ('other', _('Other')),
    ]
    
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name=_('Order')
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default='pending',
        verbose_name=_('Payment Status'),
        db_column='payment_status'
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        default='bank_transfer',
        verbose_name=_('Payment Method')
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_('Amount')
    )
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Transaction ID')
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_('Notes')
    )
    payment_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Payment Date')
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_payments',
        verbose_name=_('Created By')
    )
    
    class Meta:
        verbose_name = _('Order Payment')
        verbose_name_plural = _('Order Payments')
        ordering = ['-payment_date']
        db_table = 'finance_payment'
    
    def __str__(self):
        return f"Payment for Order {self.order.code} - {self.get_payment_status_display()}"


class OrderFees(models.Model):
    """Model for tracking order fees."""
    order = models.OneToOneField(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='fees',
        verbose_name=_('Order')
    )
    upsell_fees = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_('Upsell Fees')
    )
    confirmation_fees = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_('Confirmation Fees')
    )
    cancellation_fees = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_('Cancellation Fees')
    )
    fulfillment_fees = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_('Fulfillment Fees')
    )
    shipping_fees = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_('Shipping Fees')
    )
    return_fees = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_('Return Fees')
    )
    warehouse_fees = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_('Warehouse Fees')
    )
    
    class Meta:
        verbose_name = _('Order Fees')
        verbose_name_plural = _('Order Fees')
        db_table = 'finance_orderfees'
    
    def __str__(self):
        return f"Fees for Order {self.order.code}"
    
    def get_total_fees(self):
        """Calculate total fees for an order."""
        return (
            self.upsell_fees +
            self.confirmation_fees +
            self.cancellation_fees +
            self.fulfillment_fees +
            self.shipping_fees +
            self.return_fees +
            self.warehouse_fees
        ) 