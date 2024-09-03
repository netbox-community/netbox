from django.db import migrations
from django.db.models import F, Sum


def convert_disk_size(apps, schema_editor):
    VirtualMachine = apps.get_model('virtualization', 'VirtualMachine')
    VirtualMachine.objects.filter(disk__isnull=False).update(disk=F('disk') * 1000)

    VirtualDisk = apps.get_model('virtualization', 'VirtualDisk')
    VirtualDisk.objects.filter(size__isnull=False).update(size=F('size') * 1000)

    # Recalculate disk size on all VMs with virtual disks
    id_list = VirtualDisk.objects.values_list('virtual_machine_id').distinct()
    virtual_machines = VirtualMachine.objects.filter(id__in=id_list)
    for vm in virtual_machines:
        vm.disk = vm.virtualdisks.aggregate(Sum('size', default=0))['size__sum']
    VirtualMachine.objects.bulk_update(virtual_machines, fields=['disk'])


class Migration(migrations.Migration):

    dependencies = [
        ('virtualization', '0039_virtualmachine_serial_number'),
    ]

    operations = [
        migrations.RunPython(
            code=convert_disk_size,
            reverse_code=migrations.RunPython.noop
        ),
    ]
