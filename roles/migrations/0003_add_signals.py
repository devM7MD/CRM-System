from django.db import migrations

def add_signals(apps, schema_editor):
    """Add signal handlers for protecting build-in roles"""
    # This is handled by the signals.py file
    pass

def remove_signals(apps, schema_editor):
    """Remove signal handlers"""
    # This is handled by the signals.py file
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('roles', '0002_build_in_roles'),
    ]

    operations = [
        migrations.RunPython(add_signals, remove_signals),
    ] 