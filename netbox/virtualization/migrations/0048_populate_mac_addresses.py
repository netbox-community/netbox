import django.db.models.deletion
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db import migrations, models


def populate_mac_addresses(apps, schema_editor):
    ContentType = apps.get_model('contenttypes', 'ContentType')
    VMInterface = apps.get_model('virtualization', 'VMInterface')
    MACAddress = apps.get_model('dcim', 'MACAddress')
    db_alias = schema_editor.connection.alias
    vminterface_ct = ContentType.objects.get_for_model(VMInterface)

    mac_addresses = [
        MACAddress(
            mac_address=vminterface.mac_address,
            assigned_object_type=vminterface_ct,
            assigned_object_id=vminterface.pk
        )
        for vminterface in VMInterface.objects.using(db_alias).filter(mac_address__isnull=False)
    ]
    MACAddress.objects.using(db_alias).bulk_create(mac_addresses, batch_size=100)

    # TODO: Optimize interface updates
    for mac_address in mac_addresses:
        VMInterface.objects.using(db_alias).filter(pk=mac_address.assigned_object_id).update(
            primary_mac_address=mac_address
        )


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
                to='dcim.macaddress',
            ),
        ),
        migrations.RunPython(code=populate_mac_addresses, reverse_code=migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='vminterface',
            name='mac_address',
        ),
    ]


# See peer migrator in dcim.0200_populate_mac_addresses before making changes
def oc_vminterface_primary_mac_address(objectchange, reverting):
    MACAddress = apps.get_model('dcim', 'MACAddress')
    vminterface_ct = ContentType.objects.get_by_natural_key('virtualization', 'vminterface')

    # Swap data order if the change is being reverted
    if not reverting:
        before, after = objectchange.prechange_data, objectchange.postchange_data
    else:
        before, after = objectchange.postchange_data, objectchange.prechange_data

    if after.get('mac_address') != before.get('mac_address'):
        # Create & assign the new MACAddress (if any)
        if after.get('mac_address'):
            mac = MACAddress.objects.create(
                mac_address=after['mac_address'],
                assigned_object_type=vminterface_ct,
                assigned_object_id=objectchange.changed_object_id,
            )
            after['primary_mac_address'] = mac.pk
        else:
            after['primary_mac_address'] = None
        # Delete the old MACAddress (if any)
        if before.get('mac_address'):
            MACAddress.objects.filter(
                mac_address=before['mac_address'],
                assigned_object_type=vminterface_ct,
                assigned_object_id=objectchange.changed_object_id,
            ).delete()
        before['primary_mac_address'] = None

    before.pop('mac_address', None)
    after.pop('mac_address', None)


objectchange_migrators = {
    'virtualization.vminterface': oc_vminterface_primary_mac_address,
}
