from django.db import migrations


def update_virtualmachines_site(apps, schema_editor):
    """
    Automatically set the site for all virtual machines.
    """
    VirtualMachine = apps.get_model('virtualization', 'VirtualMachine')

    virtual_machines = VirtualMachine.objects.filter(cluster__site__isnull=False)
    for vm in virtual_machines:
        vm.site = vm.cluster.site
    VirtualMachine.objects.bulk_update(virtual_machines, ['site'])


class Migration(migrations.Migration):

    dependencies = [
        ('virtualization', '0031_virtualmachine_site_device'),
    ]

    operations = [
        migrations.RunPython(
            code=update_virtualmachines_site,
            reverse_code=migrations.RunPython.noop
        ),
    ]
