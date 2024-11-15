from django.db import migrations


def populate_mac_addresses(apps, schema_editor):
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Interface = apps.get_model('dcim', 'Interface')
    MACAddress = apps.get_model('dcim', 'MACAddress')
    interface_ct = ContentType.objects.get_for_model(Interface)

    mac_addresses = [
        MACAddress(
            mac_address=interface._mac_address,
            assigned_object_type=interface_ct,
            assigned_object_id=interface.pk
        )
        for interface in Interface.objects.filter(_mac_address__isnull=False)
    ]
    MACAddress.objects.bulk_create(mac_addresses, batch_size=100)


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0199_macaddress'),
    ]

    operations = [
        # Rename mac_address field to avoid conflict with property
        migrations.RenameField(
            model_name='interface',
            old_name='mac_address',
            new_name='_mac_address',
        ),
        migrations.RunPython(
            code=populate_mac_addresses,
            reverse_code=migrations.RunPython.noop
        ),
        migrations.RemoveField(
            model_name='interface',
            name='_mac_address',
        ),
    ]
