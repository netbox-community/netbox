from django.db import migrations
from django.db.models import Count

import utilities.fields


def populate_virtualchassis_members(apps, schema_editor):
    VirtualChassis = apps.get_model('dcim', 'VirtualChassis')

    vcs = VirtualChassis.objects.annotate(_member_count=Count('members', distinct=True))

    for vc in vcs:
        vc.member_count = vc._member_count

    VirtualChassis.objects.bulk_update(vcs, ['member_count'], batch_size=100)


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
