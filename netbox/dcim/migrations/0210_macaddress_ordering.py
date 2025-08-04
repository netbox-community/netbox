from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0209_device_component_denorm_site_location'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='macaddress',
            options={
                'ordering': ('mac_address', 'pk'),
                'verbose_name': 'MAC address',
                'verbose_name_plural': 'MAC addresses'
            },
        ),
    ]
