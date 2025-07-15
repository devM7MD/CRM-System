# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('settings', '0002_initial'),
    ]

    operations = [
        # Country model changes
        migrations.RenameField(
            model_name='country',
            old_name='name_en',
            new_name='name',
        ),
        migrations.RemoveField(
            model_name='country',
            name='name_ar',
        ),
        
        # DeliveryArea model changes
        migrations.RenameField(
            model_name='deliveryarea',
            old_name='name_en',
            new_name='name',
        ),
        migrations.RemoveField(
            model_name='deliveryarea',
            name='name_ar',
        ),
        
        # DeliveryCompany model changes
        migrations.RenameField(
            model_name='deliverycompany',
            old_name='name_en',
            new_name='name',
        ),
        migrations.RemoveField(
            model_name='deliverycompany',
            name='name_ar',
        ),
        
        # Update Meta options for ordering
        migrations.AlterModelOptions(
            name='country',
            options={'ordering': ['name'], 'verbose_name': 'Country', 'verbose_name_plural': 'Countries'},
        ),
        migrations.AlterModelOptions(
            name='deliveryarea',
            options={'ordering': ['country__name', 'name'], 'verbose_name': 'Delivery Area', 'verbose_name_plural': 'Delivery Areas'},
        ),
        migrations.AlterModelOptions(
            name='deliverycompany',
            options={'ordering': ['name'], 'verbose_name': 'Delivery Company', 'verbose_name_plural': 'Delivery Companies'},
        ),
    ] 