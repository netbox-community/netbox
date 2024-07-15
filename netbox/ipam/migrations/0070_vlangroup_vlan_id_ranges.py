import django.contrib.postgres.fields
import django.contrib.postgres.fields.ranges
from django.db import migrations, models
from django.db.backends.postgresql.psycopg_any import NumericRange

import ipam.models.vlans


def move_min_max(apps, schema_editor):
    VLANGroup = apps.get_model('ipam', 'VLANGroup')
    for group in VLANGroup.objects.all():
        if group.min_vid or group.max_vid:
            group.vlan_id_ranges = [
                NumericRange(group.min_vid, group.max_vid, bounds='[]')
            ]

            group._total_vlan_ids = 0
            for vlan_range in group.vlan_id_ranges:
                group._total_vlan_ids += int(vlan_range.upper) - int(vlan_range.lower) + 1

            group.save()


class Migration(migrations.Migration):

    dependencies = [
        ('ipam', '0069_gfk_indexes'),
    ]

    operations = [
        migrations.AddField(
            model_name='vlangroup',
            name='vlan_id_ranges',
            field=django.contrib.postgres.fields.ArrayField(
                base_field=django.contrib.postgres.fields.ranges.IntegerRangeField(),
                default=ipam.models.vlans.default_vlan_id_ranges,
                size=None
            ),
        ),
        migrations.AddField(
            model_name='vlangroup',
            name='_total_vlan_ids',
            field=models.PositiveBigIntegerField(default=4094),
        ),
        migrations.RunPython(
            code=move_min_max,
            reverse_code=migrations.RunPython.noop
        ),
        migrations.RemoveField(
            model_name='vlangroup',
            name='max_vid',
        ),
        migrations.RemoveField(
            model_name='vlangroup',
            name='min_vid',
        ),
    ]
