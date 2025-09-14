from django.db.models import Q
from django.db.models.signals import post_delete, post_save, pre_delete
from django.dispatch import receiver
from netaddr.ip import IPNetwork

from dcim.models import Device
from virtualization.models import VirtualMachine
from .choices import PrefixStatusChoices
from .models import IPAddress, Prefix, IPRange


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


def update_object_prefix(prefix, delete=False, parent_model=Prefix, child_model=IPAddress):
    if delete:
        # Get all possible addresses
        addresses = child_model.objects.filter(prefix=prefix)
        prefix = parent_model.objects.filter(
            prefix__net_contains_or_equals=prefix.prefix,
            vrf=prefix.vrf
        ).exclude(pk=prefix.pk).last()

        for address in addresses:
            # Set contained addresses to the containing prefix if it exists
            address.prefix = prefix
    else:
        filter = Q(prefix=prefix)

        if child_model == IPAddress:
            filter |= Q(address__net_contained_or_equal=prefix.prefix, vrf=prefix.vrf)
        elif child_model == IPRange:
            filter |= Q(
                start_address__net_contained_or_equal=prefix.prefix,
                end_address__net_contained_or_equal=prefix.prefix,
                vrf=prefix.vrf
            )

        addresses = child_model.objects.filter(filter)
        for address in addresses:
            # If addresses prefix is not set then this model is the only option
            if not address.prefix:
                address.prefix = prefix
            # This address has a different VRF so the prefix cannot be the parent prefix
            elif address.prefix != address.find_prefix(address):
                address.prefix = address.find_prefix(address)
            else:
                pass

    # Update the addresses
    child_model.objects.bulk_update(addresses, ['prefix'], batch_size=100)


def update_ipaddress_prefix(prefix, delete=False):
    update_object_prefix(prefix, delete, child_model=IPAddress)


def update_iprange_prefix(prefix, delete=False):
    update_object_prefix(prefix, delete, child_model=IPRange)


def update_prefix_parents(prefix, delete=False):
    if delete:
        # Get all possible addresses
        prefixes = prefix.children.all()

        for pfx in prefixes:
            # Set contained addresses to the containing prefix if it exists
            pfx.parent = prefix.parent
    else:
        # Get all possible addresses
        prefixes = prefix.children.all() | Prefix.objects.filter(
            Q(
                parent=prefix.parent,
                vrf=prefix.vrf,
                prefix__net_contained=str(prefix.prefix)
            ) | Q(
                parent=prefix.parent,
                vrf=None,
                status=PrefixStatusChoices.STATUS_CONTAINER,
                prefix__net_contained=str(prefix.prefix),
            )
        )

        if isinstance(prefix.prefix, str):
            prefix.prefix = IPNetwork(prefix.prefix)
        for pfx in prefixes:
            if isinstance(pfx.prefix, str):
                pfx.prefix = IPNetwork(pfx.prefix)

            if pfx.parent == prefix and pfx.prefix.ip not in prefix.prefix:
                # Find new parents for orphaned prefixes
                parent = Prefix.objects.exclude(pk=pfx.pk).filter(
                    Q(
                        vrf=pfx.vrf,
                        prefix__net_contains=str(pfx.prefix)
                    ) | Q(
                        vrf=None,
                        status=PrefixStatusChoices.STATUS_CONTAINER,
                        prefix__net_contains=str(pfx.prefix),
                    )
                ).last()
                # Set contained addresses to the containing prefix if it exists
                pfx.parent = parent
            elif pfx.parent == prefix and pfx.vrf != prefix.vrf:
                # Find new parents for orphaned prefixes
                parent = Prefix.objects.exclude(pk=pfx.pk).filter(
                    Q(
                        vrf=pfx.vrf,
                        prefix__net_contains=str(pfx.prefix)
                    ) | Q(
                        vrf=None,
                        status=PrefixStatusChoices.STATUS_CONTAINER,
                        prefix__net_contains=str(pfx.prefix),
                    )
                ).last()
                # Set contained addresses to the containing prefix if it exists
                pfx.parent = parent
            elif pfx.parent != prefix and pfx.vrf == prefix.vrf and pfx.prefix in prefix.prefix:
                # Set the parent to the prefix
                pfx.parent = prefix
            else:
                # No-OP as the prefix does not require modification
                pass

    # Update the prefixes
    Prefix.objects.bulk_update(prefixes, ['parent'], batch_size=100)


@receiver(post_save, sender=Prefix)
def handle_prefix_saved(instance, created, **kwargs):

    # Prefix has changed (or new instance has been created)
    if created or instance.vrf_id != instance._vrf_id or instance.prefix != instance._prefix:

        update_ipaddress_prefix(instance)
        update_iprange_prefix(instance)
        update_prefix_parents(instance)
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
    update_iprange_prefix(instance, True)
    update_prefix_parents(instance, delete=True)


@receiver(post_delete, sender=Prefix)
def handle_prefix_deleted(instance, **kwargs):

    update_parents_children(instance)
    update_children_depth(instance)
    update_ipaddress_prefix(instance, delete=True)
    update_iprange_prefix(instance, delete=True)
    update_prefix_parents(instance, delete=True)


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
