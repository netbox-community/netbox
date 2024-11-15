from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('virtualization', '0047_vminterface_rename_mac_address'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vminterface',
            name='_mac_address',
        ),
    ]
