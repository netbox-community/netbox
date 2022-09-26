import django.contrib.postgres.fields
from django.db import migrations, models
import ipam.fields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_standardize_id_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='token',
            name='allowed_ips',
            field=django.contrib.postgres.fields.ArrayField(base_field=ipam.fields.IPNetworkField(), blank=True, null=True, size=None),
        ),
        migrations.AddField(
            model_name='token',
            name='last_used',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
