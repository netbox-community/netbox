from django.db import migrations
from django.db.models import Count

import utilities.fields


def populate_virtualmachine_counts(apps, schema_editor):
    VirtualMachine = apps.get_model('virtualization', 'VirtualMachine')

    vms = list(VirtualMachine.objects.annotate(_interface_count=Count('interfaces', distinct=True)))

    for vm in vms:
        vm.interface_count = vm._interface_count

    VirtualMachine.objects.bulk_update(vms, ['interface_count'], batch_size=100)


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
