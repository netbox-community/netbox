from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0199_macaddress'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='interface',
            name='_mac_address',
        ),
    ]
