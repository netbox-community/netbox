"""
Install denormalized device → component triggers for the cooling device components (CoolingPort,
CoolingOutlet), mirroring the triggers created for the other device components in migration 0239.
"""
from django.db import migrations

from utilities.migration import InstallDenormalizationTrigger

# Cooling device component tables carrying _site/_location/_rack denormalized from their parent Device.
COMPONENT_TABLES = (
    'dcim_coolingport',
    'dcim_coolingoutlet',
)


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0241_device_cooling_method_device_cooling_outlet_count_and_more'),
    ]

    operations = [
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
