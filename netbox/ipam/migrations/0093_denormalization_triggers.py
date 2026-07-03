"""
Maintain Prefix's denormalized site/region/site-group columns via PostgreSQL triggers instead of the
Python `post_save` handler formerly registered in netbox.denormalized (and dcim.signals.sync_cached_scope_fields).
"""
from django.db import migrations

from utilities.migration import InstallDenormalizationTrigger


class Migration(migrations.Migration):

    dependencies = [
        ('ipam', '0092_iprange_host_indexes'),
        # Source tables (dcim_site, dcim_location) must already exist.
        ('dcim', '0238_ltree_paths'),
    ]

    operations = [
        InstallDenormalizationTrigger(
            dependent_table='ipam_prefix',
            source_table='dcim_site',
            fk_column='_site_id',
            mappings={'_region_id': 'region_id', '_site_group_id': 'group_id'},
        ),
        InstallDenormalizationTrigger(
            dependent_table='ipam_prefix',
            source_table='dcim_location',
            fk_column='_location_id',
            mappings={'_site_id': 'site_id'},
            related_mappings=(
                {
                    'table': 'dcim_site',
                    'source_fk': 'site_id',
                    'mappings': {'_region_id': 'region_id', '_site_group_id': 'group_id'},
                },
            ),
        ),
    ]
