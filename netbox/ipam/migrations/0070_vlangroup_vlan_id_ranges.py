import django.contrib.postgres.fields
import django.contrib.postgres.fields.ranges
from django.db import migrations, models
from django.db.backends.postgresql.psycopg_any import NumericRange

import ipam.models.vlans


def set_vid_ranges(apps, schema_editor):
    """
    Convert the min_vid & max_vid fields to a range in the new vid_ranges ArrayField.
    """
    VLANGroup = apps.get_model('ipam', 'VLANGroup')
    for group in VLANGroup.objects.all():
        group.vid_ranges = [NumericRange(group.min_vid, group.max_vid, bounds='[]')]
        group._total_vlan_ids = group.max_vid - group.min_vid + 1
        group.save()


class Migration(migrations.Migration):
    dependencies = [
        ('ipam', '0069_gfk_indexes'),
    ]

    operations = [
        migrations.AddField(
            model_name='vlangroup',
            name='vid_ranges',
            field=django.contrib.postgres.fields.ArrayField(
                base_field=django.contrib.postgres.fields.ranges.IntegerRangeField(),
                default=ipam.models.vlans.default_vid_ranges,
                size=None,
            ),
        ),
        migrations.AddField(
            model_name='vlangroup',
            name='_total_vlan_ids',
            field=models.PositiveBigIntegerField(default=4094),
        ),
        migrations.RunPython(code=set_vid_ranges, reverse_code=migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='vlangroup',
            name='max_vid',
        ),
        migrations.RemoveField(
            model_name='vlangroup',
            name='min_vid',
        ),
    ]
