"""
Maintain CableTermination's denormalized device/rack/location/site columns via PostgreSQL triggers instead
of the Python `post_save` handler formerly registered in netbox.denormalized.
"""
from django.db import migrations

from utilities.migration import InstallDenormalizationTrigger


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0238_ltree_paths'),
    ]

    operations = [
        # When a Device's rack/location/site changes, propagate to its cable terminations.
        InstallDenormalizationTrigger(
            dependent_table='dcim_cabletermination',
            source_table='dcim_device',
            fk_column='_device_id',
            mappings={'_rack_id': 'rack_id', '_location_id': 'location_id', '_site_id': 'site_id'},
        ),
        # When a Rack's location/site changes, propagate to cable terminations assigned to it.
        InstallDenormalizationTrigger(
            dependent_table='dcim_cabletermination',
            source_table='dcim_rack',
            fk_column='_rack_id',
            mappings={'_location_id': 'location_id', '_site_id': 'site_id'},
        ),
        # When a Location's site changes, propagate to cable terminations assigned to it.
        InstallDenormalizationTrigger(
            dependent_table='dcim_cabletermination',
            source_table='dcim_location',
            fk_column='_location_id',
            mappings={'_site_id': 'site_id'},
        ),
    ]
