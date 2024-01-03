from django.db import migrations
from django.db.models import Count

import utilities.fields
from utilities.counters import update_counts


def populate_virtualmachine_counts(apps, schema_editor):
    VirtualMachine = apps.get_model('virtualization', 'VirtualMachine')

    update_counts(VirtualMachine, 'interface_count', 'interfaces')


class Migration(migrations.Migration):
    dependencies = [
        ('virtualization', '0034_standardize_description_comments'),
    ]

    operations = [
        migrations.AddField(
            model_name='virtualmachine',
            name='interface_count',
            field=utilities.fields.CounterCacheField(
                default=0, to_field='virtual_machine', to_model='virtualization.VMInterface'
            ),
        ),
        migrations.RunPython(
            code=populate_virtualmachine_counts,
            reverse_code=migrations.RunPython.noop
        ),
    ]
