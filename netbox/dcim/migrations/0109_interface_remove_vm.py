from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0108_add_tags'),
        ('virtualization', '0016_replicate_interfaces'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='interface',
            name='virtual_machine',
        ),
        # device is now a required field
        migrations.AlterField(
            model_name='interface',
            name='device',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='interfaces', to='dcim.Device'),
            preserve_default=False,
        ),
    ]
