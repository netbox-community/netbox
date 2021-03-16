import sys

from django.db import migrations


def replicate_interfaces(apps, schema_editor):
    show_output = 'test' not in sys.argv

    ContentType = apps.get_model('contenttypes', 'ContentType')
    TaggedItem = apps.get_model('extras', 'TaggedItem')
    Interface = apps.get_model('dcim', 'Interface')
    IPAddress = apps.get_model('ipam', 'IPAddress')
    VMInterface = apps.get_model('virtualization', 'VMInterface')

    interface_ct = ContentType.objects.get_for_model(Interface)
    vminterface_ct = ContentType.objects.get_for_model(VMInterface)

    # Replicate dcim.Interface instances assigned to VirtualMachines
    original_interfaces = Interface.objects.prefetch_related('tagged_vlans').filter(
        virtual_machine__isnull=False
    )
    interfaces_count = len(original_interfaces)
    if show_output:
        print(f"\n    Replicating {interfaces_count} VM interfaces...", flush=True)
    new_interfaces = [
        VMInterface(
            virtual_machine=interface.virtual_machine,
            name=interface.name,
            enabled=interface.enabled,
            mac_address=interface.mac_address,
            mtu=interface.mtu,
            mode=interface.mode,
            description=interface.description,
            untagged_vlan=interface.untagged_vlan,
        ) for interface in original_interfaces
    ]
    VMInterface.objects.bulk_create(new_interfaces, batch_size=1000)

    # Pre-fetch the PKs of interfaces with tags/IP addresses
    interfaces_with_tags = TaggedItem.objects.filter(
        content_type=interface_ct
    ).values_list('object_id', flat=True)
    interfaces_with_ips = IPAddress.objects.filter(
        assigned_object_id__isnull=False
    ).values_list('assigned_object_id', flat=True)

    if show_output:
        print(f"    Replicating assigned objects...", flush=True)
    for i, interface in enumerate(original_interfaces):
        vminterface = new_interfaces[i]

        # Copy tagged VLANs
        if interface.tagged_vlans.exists():
            vminterface.tagged_vlans.set(interface.tagged_vlans.all())

        # Reassign tags to the new instance
        if interface.pk in interfaces_with_tags:
            TaggedItem.objects.filter(content_type=interface_ct, object_id=interface.pk).update(
                content_type=vminterface_ct,
                object_id=vminterface.pk
            )

        # Update any assigned IPAddresses
        if interface.pk in interfaces_with_ips:
            IPAddress.objects.filter(assigned_object_type=interface_ct, assigned_object_id=interface.pk).update(
                assigned_object_type=vminterface_ct,
                assigned_object_id=vminterface.pk
            )

        # Progress counter
        if show_output and not i % 1000:
            percentage = int(i / interfaces_count * 100)
            print(f"      {i}/{interfaces_count} ({percentage}%)", flush=True)

    # Verify that all interfaces have been replicated
    replicated_count = VMInterface.objects.count()
    assert replicated_count == original_interfaces.count(), "Replicated interfaces count does not match original count!"

    # Delete all interfaces not assigned to a Device
    Interface.objects.filter(device__isnull=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0082_3569_interface_fields'),
        ('ipam', '0037_ipaddress_assignment'),
        ('virtualization', '0015_vminterface'),
    ]

    operations = [
        migrations.RunPython(
            code=replicate_interfaces
        ),
    ]
