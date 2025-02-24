from django.db.models import Q
from django.db.models.signals import post_delete, post_save, pre_delete
from django.dispatch import receiver

from dcim.models import Device
from virtualization.models import VirtualMachine
from .models import IPAddress, Prefix


def update_parents_children(prefix):
    """
    Update depth on prefix & containing prefixes
    """
    parents = prefix.get_parents(include_self=True).annotate_hierarchy()
    for parent in parents:
        parent._children = parent.hierarchy_children
    Prefix.objects.bulk_update(parents, ['_children'], batch_size=100)


def update_children_depth(prefix):
    """
    Update children count on prefix & contained prefixes
    """
    children = prefix.get_children(include_self=True).annotate_hierarchy()
    for child in children:
        child._depth = child.hierarchy_depth
    Prefix.objects.bulk_update(children, ['_depth'], batch_size=100)


def update_ipaddress_prefix(prefix, delete=False):
    if delete:
        # Get all possible addresses
        addresses = IPAddress.objects.filter(prefix=prefix)
        # Find a new containing prefix
        prefix = Prefix.objects.filter(
            prefix__net_contains_or_equals=prefix.prefix,
            vrf=prefix.vrf
        ).exclude(pk=prefix.pk).last()

        for address in addresses:
            # Set contained addresses to the containing prefix if it exists
            address.prefix = prefix
    else:
        # Get all possible modified addresses
        addresses = IPAddress.objects.filter(
            Q(address__net_contained_or_equal=prefix.prefix, vrf=prefix.vrf) |
            Q(prefix=prefix)
        )
        for address in addresses:
            if not address.prefix or (prefix.prefix in address.prefix.prefix and address.address in prefix.prefix):
                # Set to new Prefix as the prefix is a child of the old prefix and the address is contained in the
                # prefix
                address.prefix = prefix
            elif address.prefix and address.address not in prefix.prefix:
                # Find a new prefix as the prefix no longer contains the address
                address.prefix = Prefix.objects.filter(
                    prefix__net_contains_or_equals=address.address,
                    vrf=prefix.vrf
                ).last()
            else:
                # No-OP as the prefix does not require modification
                pass

    # Update the addresses
    IPAddress.objects.bulk_update(addresses, ['prefix'], batch_size=100)


@receiver(post_save, sender=Prefix)
def handle_prefix_saved(instance, created, **kwargs):

    # Prefix has changed (or new instance has been created)
    if created or instance.vrf_id != instance._vrf_id or instance.prefix != instance._prefix:

        update_ipaddress_prefix(instance)
        update_parents_children(instance)
        update_children_depth(instance)

        # If this is not a new prefix, clean up parent/children of previous prefix
        if not created:
            old_prefix = Prefix(vrf_id=instance._vrf_id, prefix=instance._prefix)
            update_parents_children(old_prefix)
            update_children_depth(old_prefix)


@receiver(pre_delete, sender=Prefix)
def pre_handle_prefix_deleted(instance, **kwargs):
    update_ipaddress_prefix(instance, True)


@receiver(post_delete, sender=Prefix)
def handle_prefix_deleted(instance, **kwargs):

    update_parents_children(instance)
    update_children_depth(instance)
    update_ipaddress_prefix(instance, delete=True)


@receiver(pre_delete, sender=IPAddress)
def clear_primary_ip(instance, **kwargs):
    """
    When an IPAddress is deleted, trigger save() on any Devices/VirtualMachines for which it was a primary IP.
    """
    field_name = f'primary_ip{instance.family}'
    if device := Device.objects.filter(**{field_name: instance}).first():
        device.snapshot()
        setattr(device, field_name, None)
        device.save()
    if virtualmachine := VirtualMachine.objects.filter(**{field_name: instance}).first():
        virtualmachine.snapshot()
        setattr(virtualmachine, field_name, None)
        virtualmachine.save()


@receiver(pre_delete, sender=IPAddress)
def clear_oob_ip(instance, **kwargs):
    """
    When an IPAddress is deleted, trigger save() on any Devices for which it was a OOB IP.
    """
    if device := Device.objects.filter(oob_ip=instance).first():
        device.snapshot()
        device.oob_ip = None
        device.save()
