from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0197_rename_mac_address_interface__mac_address_macaddress'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='interface',
            name='_mac_address',
        ),
    ]
