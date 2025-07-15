from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
import uuid

from orders.models import Order
from .models import DeliveryRecord, DeliveryStatusHistory


@receiver(post_save, sender=Order)
def create_delivery_record(sender, instance, created, **kwargs):
    """
    Automatically create a delivery record when an order is created 
    with status 'processing' or 'shipped'
    """
    if created and instance.status in ['processing', 'shipped']:
        # Check if delivery record already exists
        if not hasattr(instance, 'delivery'):
            # Generate a unique tracking number
            tracking_number = f"TRK-{uuid.uuid4().hex[:8].upper()}"
            
            # Create the delivery record
            DeliveryRecord.objects.create(
                order=instance,
                tracking_number=tracking_number,
                status='pending_assignment',
                created_at=timezone.now()
            )


@receiver(pre_save, sender=Order)
def sync_order_delivery_status(sender, instance, **kwargs):
    """
    Sync the order status with delivery status when appropriate
    """
    if instance.pk:  # Only for existing orders
        try:
            # Get the previous state of the order
            old_instance = Order.objects.get(pk=instance.pk)
            
            # If order status is changing to 'shipped'
            if old_instance.status != 'shipped' and instance.status == 'shipped':
                # Create or update delivery record
                try:
                    delivery = DeliveryRecord.objects.get(order=instance)
                    if delivery.status == 'pending_assignment':
                        delivery.status = 'ready_for_pickup'
                        delivery.save()
                        
                        # Create status history record
                        DeliveryStatusHistory.objects.create(
                            order=instance,
                            status='ready_for_pickup',
                            notes='Automatically updated when order was marked as shipped'
                        )
                except DeliveryRecord.DoesNotExist:
                    # Create new delivery record if it doesn't exist
                    tracking_number = f"TRK-{uuid.uuid4().hex[:8].upper()}"
                    DeliveryRecord.objects.create(
                        order=instance,
                        tracking_number=tracking_number,
                        status='ready_for_pickup',
                        created_at=timezone.now()
                    )
            
            # If order status is changing to 'cancelled'
            elif old_instance.status != 'cancelled' and instance.status == 'cancelled':
                # Update delivery record if it exists
                try:
                    delivery = DeliveryRecord.objects.get(order=instance)
                    # Only update if not already delivered or returned
                    if delivery.status not in ['delivered', 'returned']:
                        delivery.status = 'returned'
                        delivery.save()
                        
                        # Create status history record
                        DeliveryStatusHistory.objects.create(
                            order=instance,
                            status='returned',
                            notes='Order was cancelled'
                        )
                except DeliveryRecord.DoesNotExist:
                    pass
        except Order.DoesNotExist:
            pass


@receiver(post_save, sender=DeliveryRecord)
def update_order_on_delivery_status_change(sender, instance, **kwargs):
    """
    Update the order status when delivery status changes
    """
    # Map of delivery statuses to order statuses
    status_map = {
        'delivered': 'delivered',
        'returned': 'returned',
        'failed': 'processing',  # Failed deliveries should be processed again
    }
    
    # Check if the delivery status should update the order status
    if instance.status in status_map:
        order = instance.order
        new_order_status = status_map[instance.status]
        
        # Only update if the status is different
        if order.status != new_order_status:
            order.status = new_order_status
            order.save(update_fields=['status']) 