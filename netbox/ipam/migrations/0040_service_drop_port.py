from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ipam', '0039_service_ports_array'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='service',
            name='port',
        ),
    ]
