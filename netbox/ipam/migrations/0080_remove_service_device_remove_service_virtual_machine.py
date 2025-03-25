from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ipam', '0079_populate_service_parent'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='service',
            name='device',
        ),
        migrations.RemoveField(
            model_name='service',
            name='virtual_machine',
        ),
    ]
