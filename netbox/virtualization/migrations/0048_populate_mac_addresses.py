import django.db.models.deletion
from django.db import migrations, models


def populate_mac_addresses(apps, schema_editor):
    ContentType = apps.get_model('contenttypes', 'ContentType')
    VMInterface = apps.get_model('virtualization', 'VMInterface')
    MACAddress = apps.get_model('dcim', 'MACAddress')
    vminterface_ct = ContentType.objects.get_for_model(VMInterface)

    mac_addresses = [
        MACAddress(
            mac_address=vminterface.mac_address,
            assigned_object_type=vminterface_ct,
            assigned_object_id=vminterface.pk
        )
        for vminterface in VMInterface.objects.filter(mac_address__isnull=False)
    ]
    MACAddress.objects.bulk_create(mac_addresses, batch_size=100)

    # TODO: Optimize interface updates
    for mac_address in mac_addresses:
        VMInterface.objects.filter(pk=mac_address.assigned_object_id).update(primary_mac_address=mac_address)


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0199_macaddress'),
        ('virtualization', '0047_natural_ordering'),
    ]

    operations = [
        migrations.AddField(
            model_name='vminterface',
            name='primary_mac_address',
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='+',
                to='dcim.macaddress'
            ),
        ),
        migrations.RunPython(
            code=populate_mac_addresses,
            reverse_code=migrations.RunPython.noop
        ),
        migrations.RemoveField(
            model_name='vminterface',
            name='mac_address',
        ),
    ]
