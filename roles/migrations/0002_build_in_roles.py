from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone

def create_build_in_roles(apps, schema_editor):
    """Create build-in roles that cannot be deleted"""
    Role = apps.get_model('roles', 'Role')
    Permission = apps.get_model('roles', 'Permission')
    RolePermission = apps.get_model('roles', 'RolePermission')
    
    # Delete Super Admin role if it exists
    Role.objects.filter(name='Super Admin').delete()
    
    # Create build-in roles
    roles_data = [
        {
            'name': 'Call Center Agent',
            'description': 'Handles customer calls and order processing',
            'is_protected': True,
            'is_default': False,
        },
        {
            'name': 'Call Center Manager',
            'description': 'Manages call center operations and team',
            'is_protected': True,
            'is_default': False,
        },
        {
            'name': 'Accountant',
            'description': 'Manages financial operations and reports',
            'is_protected': True,
            'is_default': False,
        },
        {
            'name': 'Stock Keeper',
            'description': 'Manages inventory and stock operations',
            'is_protected': True,
            'is_default': False,
        },
        {
            'name': 'Delivery Agent',
            'description': 'Handles delivery operations and tracking',
            'is_protected': True,
            'is_default': False,
        },
        {
            'name': 'Packaging Agent',
            'description': 'Handles packaging and preparation',
            'is_protected': True,
            'is_default': False,
        },
        {
            'name': 'Sourcing Agent',
            'description': 'Handles product sourcing and supplier management',
            'is_protected': True,
            'is_default': False,
        },
        {
            'name': 'Seller',
            'description': 'External seller with limited access',
            'is_protected': True,
            'is_default': False,
        },
        {
            'name': 'Follow-up Agent',
            'description': 'Handles customer follow-up and support',
            'is_protected': True,
            'is_default': False,
        },
    ]
    
    for role_data in roles_data:
        role, created = Role.objects.get_or_create(
            name=role_data['name'],
            defaults=role_data
        )
        if created:
            print(f"Created role: {role.name}")

def reverse_build_in_roles(apps, schema_editor):
    """Reverse the build-in roles creation"""
    Role = apps.get_model('roles', 'Role')
    
    # Delete build-in roles
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
    
    for role_name in build_in_roles:
        Role.objects.filter(name=role_name).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('roles', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_build_in_roles, reverse_build_in_roles),
    ] 