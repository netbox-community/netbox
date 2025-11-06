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


def update_object_prefix(prefix, child_model=IPAddress):
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


def delete_object_prefix(prefix, child_model, child_objects):
    if not prefix.parent or prefix.vrf != prefix.parent.vrf:
        # Prefix will be Set Null
        return

    # Set prefix to prefix parent
    for address in child_objects:
        address.prefix = prefix.parent

    # Run a bulk update
    child_model.objects.bulk_update(child_objects, ['prefix'], batch_size=100)


def update_ipaddress_prefix(prefix, delete=False):
    if delete:
        delete_object_prefix(prefix, IPAddress, prefix.ip_addresses.all())
    else:
        update_object_prefix(prefix, child_model=IPAddress)


def update_iprange_prefix(prefix, delete=False):
    if delete:
        delete_object_prefix(prefix, IPRange, prefix.ip_ranges.all())
    else:
        update_object_prefix(prefix, child_model=IPRange)


def update_prefix_parents(prefix, delete=False, created=False):
    if delete:
        # Set prefix to prefix parent
        prefixes = prefix.children.all()
        for address in prefixes:
            address.parent = prefix.parent

        # Run a bulk update
        Prefix.objects.bulk_update(prefixes, ['parent'], batch_size=100)
    else:
        # Build filter to get prefixes that will be impacted by this change:
        # * Parent prefix is this prefixes parent, and;
        # * Prefix is contained by this prefix, and;
        # * Prefix is either within this VRF or there is no VRF and this prefix is a container prefix
        filter = Q(
            parent=prefix.parent,
            vrf=prefix.vrf,
            prefix__net_contained=str(prefix.prefix)
        )
        is_container = False
        if prefix.status == PrefixStatusChoices.STATUS_CONTAINER and prefix.vrf is None:
            is_container = True
            filter |= Q(
                parent=prefix.parent,
                vrf=None,
                prefix__net_contained=str(prefix.prefix),
            )

        # Get all impacted prefixes.  Ensure we use distinct() to weed out duplicate prefixes from joins
        prefixes = Prefix.objects.filter(filter)
        # Include children
        if not created:
            prefixes |= prefix.children.all()

        for pfx in prefixes.distinct():
            # Update parent criteria:
            # * This prefix contains the child prefix, has a parent that is the prefixes parent and is "In-VRF"
            # * This prefix does not contain the child prefix
            if pfx.vrf != prefix.vrf and not (prefix.vrf is None and is_container):
                # Prefix is contained but not in-VRF
                # print(f'{pfx} is no longer "in-VRF"')
                pfx.parent = prefix.parent
            elif pfx.prefix in prefix.prefix and pfx.parent != prefix and pfx.parent == prefix.parent:
                # Prefix is in-scope
                # print(f'{pfx} is in {prefix}')
                pfx.parent = prefix
            elif pfx.prefix not in prefix.prefix and pfx.parent == prefix:
                # Prefix has fallen out of scope
                # print(f'{pfx} is not in {prefix}')
                pfx.parent = prefix.parent
        rows = Prefix.objects.bulk_update(prefixes, ['parent'], batch_size=100)
        print(rows)


@receiver(post_save, sender=Prefix)
def handle_prefix_saved(instance, created, **kwargs):

    # Prefix has changed (or new instance has been created)
    if created or instance.vrf_id != instance._vrf_id or instance.prefix != instance._prefix:

        update_ipaddress_prefix(instance)
        update_iprange_prefix(instance)
        update_prefix_parents(instance, created=created)
        update_parents_children(instance)
        update_children_depth(instance)

        # If this is not a new prefix, clean up parent/children of previous prefix
        if not created:
            old_prefix = Prefix(vrf_id=instance._vrf_id, prefix=instance._prefix)
            update_parents_children(old_prefix)
            update_children_depth(old_prefix)


@receiver(pre_delete, sender=Prefix)
def pre_handle_prefix_deleted(instance, **kwargs):
    update_ipaddress_prefix(instance, delete=True)
    update_iprange_prefix(instance, delete=True)
    update_prefix_parents(instance, delete=True)


@receiver(post_delete, sender=Prefix)
def handle_prefix_deleted(instance, **kwargs):

    update_parents_children(instance)
    update_children_depth(instance)


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
