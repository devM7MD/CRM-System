from django.db import migrations

def add_admin_role(apps, schema_editor):
    """Add Admin role to build-in roles"""
    Role = apps.get_model('roles', 'Role')
    
    # Create Admin role if it doesn't exist
    Role.objects.get_or_create(
        name='Admin',
        defaults={
            'description': 'System administrator with full access',
            'is_protected': True,
            'is_default': False,
        }
    )

def remove_admin_role(apps, schema_editor):
    """Remove Admin role"""
    Role = apps.get_model('roles', 'Role')
    Role.objects.filter(name='Admin').delete()

class Migration(migrations.Migration):

    dependencies = [
        ('roles', '0003_add_signals'),
    ]

    operations = [
        migrations.RunPython(add_admin_role, remove_admin_role),
    ] 