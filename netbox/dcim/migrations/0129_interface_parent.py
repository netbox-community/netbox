from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0128_device_location_populate'),
    ]

    operations = [
        migrations.AddField(
            model_name='interface',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='child_interfaces', to='dcim.interface'),
        ),
    ]
