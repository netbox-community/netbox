from django.db import migrations
from django.db.models import F, Sum
from netbox.settings import DISK_BASE_UNIT


def convert_disk_size(apps, schema_editor):
    VirtualDisk = apps.get_model('virtualization', 'VirtualDisk')
    VirtualMachine = apps.get_model('virtualization', 'VirtualMachine')
    db_alias = schema_editor.connection.alias

    VirtualMachine.objects.using(db_alias).filter(disk__isnull=False).update(disk=F('disk') * DISK_BASE_UNIT)
    VirtualDisk.objects.using(db_alias).filter(size__isnull=False).update(size=F('size') * DISK_BASE_UNIT)

    # Recalculate disk size on all VMs with virtual disks
    id_list = VirtualDisk.objects.using(db_alias).values_list('virtual_machine_id').distinct()
    virtual_machines = VirtualMachine.objects.using(db_alias).filter(id__in=id_list)
    for vm in virtual_machines:
        vm.disk = vm.virtualdisks.aggregate(Sum('size', default=0))['size__sum']
    VirtualMachine.objects.using(db_alias).bulk_update(virtual_machines, fields=['disk'])


class Migration(migrations.Migration):
    dependencies = [
        ('virtualization', '0039_virtualmachine_serial_number'),
    ]

    operations = [
        migrations.RunPython(code=convert_disk_size, reverse_code=migrations.RunPython.noop),
    ]
