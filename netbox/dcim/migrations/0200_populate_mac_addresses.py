import django.db.models.deletion
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db import migrations, models


def populate_mac_addresses(apps, schema_editor):
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Interface = apps.get_model('dcim', 'Interface')
    MACAddress = apps.get_model('dcim', 'MACAddress')
    db_alias = schema_editor.connection.alias
    interface_ct = ContentType.objects.get_for_model(Interface)

    mac_addresses = [
        MACAddress(
            mac_address=interface.mac_address,
            assigned_object_type=interface_ct,
            assigned_object_id=interface.pk
        )
        for interface in Interface.objects.using(db_alias).filter(mac_address__isnull=False)
    ]
    MACAddress.objects.using(db_alias).bulk_create(mac_addresses, batch_size=100)

    # TODO: Optimize interface updates
    for mac_address in mac_addresses:
        Interface.objects.using(db_alias).filter(
            pk=mac_address.assigned_object_id
        ).update(
            primary_mac_address=mac_address
        )


class Migration(migrations.Migration):
    dependencies = [
        ('dcim', '0199_macaddress'),
    ]

    operations = [
        migrations.AddField(
            model_name='interface',
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
            model_name='interface',
            name='mac_address',
        ),
    ]


# See peer migrator in virtualization.0048_populate_mac_addresses before making changes
def oc_interface_primary_mac_address(objectchange, reverting):
    MACAddress = apps.get_model('dcim', 'MACAddress')
    interface_ct = ContentType.objects.get_by_natural_key('dcim', 'interface')

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
                assigned_object_type=interface_ct,
                assigned_object_id=objectchange.changed_object_id,
            )
            after['primary_mac_address'] = mac.pk
        else:
            after['primary_mac_address'] = None
        # Delete the old MACAddress (if any)
        if before.get('mac_address'):
            MACAddress.objects.filter(
                mac_address=before['mac_address'],
                assigned_object_type=interface_ct,
                assigned_object_id=objectchange.changed_object_id,
            ).delete()
        before['primary_mac_address'] = None

    before.pop('mac_address', None)
    after.pop('mac_address', None)


objectchange_migrators = {
    'dcim.interface': oc_interface_primary_mac_address,
}
