"""
Maintain Prefix's denormalized site/region/site-group columns via PostgreSQL triggers instead of the
Python `post_save` handler formerly registered in netbox.denormalized.
"""
from django.db import migrations

from utilities.migration import InstallDenormalizationTrigger


class Migration(migrations.Migration):

    dependencies = [
        ('ipam', '0090_vlangroup_recompute_total_vlan_ids'),
        # Source tables (dcim_site, dcim_location) must already exist.
        ('dcim', '0238_ltree_paths'),
    ]

    operations = [
        # When a Site's region/group changes, propagate to prefixes assigned to it.
        InstallDenormalizationTrigger(
            dependent_table='ipam_prefix',
            source_table='dcim_site',
            fk_column='_site_id',
            mappings={'_region_id': 'region_id', '_site_group_id': 'group_id'},
        ),
        # When a Location's site changes, propagate to prefixes assigned to it.
        InstallDenormalizationTrigger(
            dependent_table='ipam_prefix',
            source_table='dcim_location',
            fk_column='_location_id',
            mappings={'_site_id': 'site_id'},
        ),
    ]
