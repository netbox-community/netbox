import django.db.models.functions.comparison
from django.db import migrations, models

import ipam.fields
import ipam.lookups


class Migration(migrations.Migration):
    dependencies = [
        ('ipam', '0093_alter_prefix__region_alter_prefix__site_group'),
    ]

    operations = [
        # Replace the host address index with a composite index which also covers the primary key, so that it can
        # satisfy the default ordering of IPAddress outright. Note that the existing index must be dropped rather
        # than retained alongside the new one: with both present, PostgreSQL continues to select the narrower index
        # and applies an incremental sort atop it.
        migrations.RemoveIndex(
            model_name='ipaddress',
            name='ipam_ipaddress_host',
        ),
        migrations.AddIndex(
            model_name='ipaddress',
            index=models.Index(
                django.db.models.functions.comparison.Cast(
                    ipam.lookups.Host('address'),
                    output_field=ipam.fields.IPAddressField(),
                ),
                models.F('id'),
                name='ipam_ipaddress_host',
            ),
        ),
    ]
