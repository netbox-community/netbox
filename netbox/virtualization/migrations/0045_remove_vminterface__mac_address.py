from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('virtualization', '0044_rename_mac_address_vminterface__mac_address'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vminterface',
            name='_mac_address',
        ),
    ]
