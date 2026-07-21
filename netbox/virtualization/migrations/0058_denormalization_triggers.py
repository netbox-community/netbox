"""
Maintain Cluster's denormalized scope columns (CachedScopeMixin: _site/_location/_region/_site_group)
via PostgreSQL triggers instead of the Python `dcim.signals.sync_cached_scope_fields` handler.
"""
from django.db import migrations

from utilities.migration import InstallDenormalizationTrigger


class Migration(migrations.Migration):

    dependencies = [
        ('virtualization', '0057_alter_cluster__region_alter_cluster__site_group'),
        # Source tables (dcim_site, dcim_location) must already exist.
        ('dcim', '0240_ltree_paths'),
    ]

    operations = [
        InstallDenormalizationTrigger(
            dependent_table='virtualization_cluster',
            source_table='dcim_site',
            fk_column='_site_id',
            mappings={'_region_id': 'region_id', '_site_group_id': 'group_id'},
        ),
        InstallDenormalizationTrigger(
            dependent_table='virtualization_cluster',
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
