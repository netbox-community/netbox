"""
Maintain denormalized device/rack/location/site columns via PostgreSQL triggers instead of Python
`post_save` handlers:

- CableTermination's _device/_rack/_location/_site (formerly netbox.denormalized).
- Each device component's _site/_location/_rack (formerly dcim.signals.handle_device_site_change /
  handle_rack_site_change / handle_location_site_change). These are derived solely from the parent
  Device, so a single Device-sourced trigger per component table covers direct device edits as well as
  the Rack/Location cascades (which write Device.site/location and thus fire this trigger).
"""
from django.db import migrations

from utilities.migration import InstallDenormalizationTrigger

# Device component tables carrying _site/_location/_rack denormalized from their parent Device.
COMPONENT_TABLES = (
    'dcim_consoleport',
    'dcim_consoleserverport',
    'dcim_devicebay',
    'dcim_frontport',
    'dcim_interface',
    'dcim_inventoryitem',
    'dcim_modulebay',
    'dcim_poweroutlet',
    'dcim_powerport',
    'dcim_rearport',
)


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
        # Device components: mirror the parent Device's site/location/rack onto each component.
        # The Rack/Location → Device cascades (dcim.signals) write Device.site/location, which fires
        # this same trigger, so no separate Rack/Location-sourced component triggers are needed.
        *[
            InstallDenormalizationTrigger(
                dependent_table=table,
                source_table='dcim_device',
                fk_column='device_id',
                mappings={'_site_id': 'site_id', '_location_id': 'location_id', '_rack_id': 'rack_id'},
            )
            for table in COMPONENT_TABLES
        ],
    ]
