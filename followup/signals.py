from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth import get_user_model

from orders.models import Order
from .models import FollowupRecord, CustomerFeedback

User = get_user_model()

@receiver(pre_save, sender=Order)
def store_original_status(sender, instance, **kwargs):
    """Store the original status of an order before it's updated"""
    if instance.pk:
        try:
            original = Order.objects.get(pk=instance.pk)
            instance._original_status = original.status
        except Order.DoesNotExist:
            instance._original_status = None
    else:
        instance._original_status = None

@receiver(post_save, sender=Order)
def create_followup_record(sender, instance, created, **kwargs):
    """
    Automatically create a followup record when order status changes to one that
    requires follow-up (delivered, completed) or when a new order is created
    """
    # Get the first super_admin user to assign as the agent
    try:
        agent = User.objects.filter(role='super_admin').first()
        if not agent:
            agent = User.objects.filter(role='follow_up').first()
            if not agent:
                agent = User.objects.filter(is_superuser=True).first()
    except User.DoesNotExist:
        # If no appropriate user found, we can't create the follow-up
        return

    # For new orders with status that requires immediate follow-up
    if created and instance.status in ['pending']:
        # Create a follow-up record for new pending orders
        FollowupRecord.objects.create(
            order=instance,
            agent=agent,
            status='pending',
            scheduled_for=timezone.now() + timezone.timedelta(days=1)
        )
        return

    # For existing orders with status changes
    if not created and hasattr(instance, '_original_status'):
        old_status = instance._original_status
        new_status = instance.status
        
        # If status hasn't changed, do nothing
        if old_status == new_status:
            return
            
        # For orders that have been delivered or completed and need follow-up
        if new_status in ['delivered', 'completed'] and old_status not in ['delivered', 'completed']:
            # Check if there's already a follow-up record for this order
            existing_followups = FollowupRecord.objects.filter(
                order=instance, 
                status__in=['pending', 'in_progress']
            )
            
            if not existing_followups.exists():
                # Create a new follow-up record
                FollowupRecord.objects.create(
                    order=instance,
                    agent=agent,
                    status='pending',
                    scheduled_for=timezone.now() + timezone.timedelta(days=1)
                )
        
        # For cancelled orders, mark any existing follow-ups as cancelled
        if new_status == 'cancelled':
            FollowupRecord.objects.filter(
                order=instance, 
                status__in=['pending', 'in_progress']
            ).update(
                status='cancelled',
                updated_at=timezone.now()
            ) 