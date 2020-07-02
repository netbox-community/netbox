import sys

from django.db import migrations


def replicate_interfaces(apps, schema_editor):
    ContentType = apps.get_model('contenttypes', 'ContentType')
    TaggedItem = apps.get_model('extras', 'TaggedItem')
    Interface = apps.get_model('dcim', 'Interface')
    IPAddress = apps.get_model('ipam', 'IPAddress')
    VMInterface = apps.get_model('virtualization', 'VMInterface')

    interface_ct = ContentType.objects.get_for_model(Interface)
    vminterface_ct = ContentType.objects.get_for_model(VMInterface)

    # Replicate dcim.Interface instances assigned to VirtualMachines
    original_interfaces = Interface.objects.filter(virtual_machine__isnull=False)
    for interface in original_interfaces:
        vminterface = VMInterface(
            virtual_machine=interface.virtual_machine,
            name=interface.name,
            enabled=interface.enabled,
            mac_address=interface.mac_address,
            mtu=interface.mtu,
            mode=interface.mode,
            description=interface.description,
            untagged_vlan=interface.untagged_vlan,
        )
        vminterface.save()

        # Copy tagged VLANs
        vminterface.tagged_vlans.set(interface.tagged_vlans.all())

        # Reassign tags to the new instance
        TaggedItem.objects.filter(
            content_type=interface_ct, object_id=interface.pk
        ).update(
            content_type=vminterface_ct, object_id=vminterface.pk
        )

        # Update any assigned IPAddresses
        IPAddress.objects.filter(assigned_object_id=interface.pk).update(
            assigned_object_type=vminterface_ct,
            assigned_object_id=vminterface.pk
        )

    replicated_count = VMInterface.objects.count()
    if 'test' not in sys.argv:
        print(f"\n    Replicated {replicated_count} interfaces ", end='', flush=True)

    # Verify that all interfaces have been replicated
    assert replicated_count == original_interfaces.count(), "Replicated interfaces count does not match original count!"

    # Delete all interfaces not assigned to a Device
    Interface.objects.filter(device__isnull=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('ipam', '0037_ipaddress_assignment'),
        ('virtualization', '0015_vminterface'),
    ]

    operations = [
        migrations.RunPython(
            code=replicate_interfaces
        ),
    ]
