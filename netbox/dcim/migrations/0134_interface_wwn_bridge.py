import dcim.fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0133_port_colors'),
    ]

    operations = [
        migrations.AddField(
            model_name='interface',
            name='wwn',
            field=dcim.fields.WWNField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='interface',
            name='bridge',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='bridge_interfaces', to='dcim.interface'),
        ),
    ]
