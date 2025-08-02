from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.core.exceptions import PermissionDenied
from .models import Role

@receiver(pre_delete, sender=Role)
def prevent_build_in_role_deletion(sender, instance, **kwargs):
    """Prevent deletion of build-in roles"""
    build_in_roles = [
        'Call Center Agent',
        'Call Center Manager',
        'Accountant', 
        'Stock Keeper',
        'Delivery Agent',
        'Packaging Agent',
        'Sourcing Agent',
        'Seller',
        'Follow-up Agent',
    ]
    
    if instance.name in build_in_roles:
        raise PermissionDenied(
            f"Cannot delete build-in role '{instance.name}'. This role is required by the system."
        ) 