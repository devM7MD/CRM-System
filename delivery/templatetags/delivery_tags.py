from django import template
from django.utils import timezone
from datetime import timedelta

from delivery.models import DeliveryRecord

register = template.Library()

@register.filter
def status_badge_class(status):
    """Returns CSS class for status badges based on the status value."""
    status_classes = {
        'pending_assignment': 'bg-gray-100 text-gray-800',
        'assigned': 'bg-blue-100 text-blue-800',
        'ready_for_pickup': 'bg-purple-100 text-purple-800',
        'picked_up': 'bg-blue-100 text-blue-800',
        'in_transit': 'bg-yellow-100 text-yellow-800',
        'out_for_delivery': 'bg-orange-100 text-orange-800',
        'delivered': 'bg-green-100 text-green-800',
        'failed': 'bg-red-100 text-red-800',
        'returned': 'bg-red-100 text-red-800',
    }
    return status_classes.get(status, 'bg-gray-100 text-gray-800')

@register.filter
def priority_badge_class(priority):
    """Returns CSS class for priority badges based on the priority value."""
    priority_classes = {
        'low': 'bg-blue-100 text-blue-800',
        'normal': 'bg-green-100 text-green-800',
        'high': 'bg-orange-100 text-orange-800',
        'urgent': 'bg-red-100 text-red-800',
    }
    return priority_classes.get(priority, 'bg-green-100 text-green-800')

@register.filter
def estimated_delivery_status(delivery):
    """Returns a string indicating if delivery is on time, delayed, etc."""
    if not delivery.estimated_delivery:
        return ''
    
    if delivery.status == 'delivered':
        if delivery.delivery_date and delivery.delivery_date <= delivery.estimated_delivery:
            return 'on-time'
        elif delivery.delivery_date:
            return 'delayed'
    
    now = timezone.now()
    if now > delivery.estimated_delivery:
        return 'overdue'
    elif now > delivery.estimated_delivery - timedelta(hours=24):
        return 'due-soon'
    
    return 'on-schedule'

@register.simple_tag
def delivery_stats():
    """Returns common delivery statistics for use in templates."""
    stats = {
        'active': DeliveryRecord.objects.filter(
            status__in=['assigned', 'picked_up', 'in_transit', 'out_for_delivery']
        ).count(),
        'delivered': DeliveryRecord.objects.filter(status='delivered').count(),
        'failed': DeliveryRecord.objects.filter(status='failed').count(),
        'pending': DeliveryRecord.objects.filter(
            status__in=['pending_assignment', 'ready_for_pickup']
        ).count()
    }
    return stats 