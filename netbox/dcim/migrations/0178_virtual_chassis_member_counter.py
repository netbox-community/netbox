from django.db import migrations
from django.db.models import Count

import utilities.fields
from utilities.counters import update_counts


def populate_virtualchassis_members(apps, schema_editor):
    VirtualChassis = apps.get_model('dcim', 'VirtualChassis')

    update_counts(VirtualChassis, 'member_count', 'members')


class Migration(migrations.Migration):
    dependencies = [
        ('dcim', '0177_devicetype_component_counters'),
    ]

    operations = [
        migrations.AddField(
            model_name='virtualchassis',
            name='member_count',
            field=utilities.fields.CounterCacheField(
                default=0, to_field='virtual_chassis', to_model='dcim.Device'
            ),
        ),
        migrations.RunPython(
            code=populate_virtualchassis_members,
            reverse_code=migrations.RunPython.noop
        ),
    ]
