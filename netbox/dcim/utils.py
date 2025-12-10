from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db import router, transaction


def compile_path_node(ct_id, object_id):
    return f'{ct_id}:{object_id}'


def decompile_path_node(repr):
    ct_id, object_id = repr.split(':')
    return int(ct_id), int(object_id)


def object_to_path_node(obj):
    """
    Return a representation of an object suitable for inclusion in a CablePath path. Node representation is in the
    form <ContentType ID>:<Object ID>.
    """
    ct = ContentType.objects.get_for_model(obj)
    return compile_path_node(ct.pk, obj.pk)


def path_node_to_object(repr):
    """
    Given the string representation of a path node, return the corresponding instance. If the object no longer
    exists, return None.
    """
    ct_id, object_id = decompile_path_node(repr)
    ct = ContentType.objects.get_for_id(ct_id)
    return ct.model_class().objects.filter(pk=object_id).first()


def create_cablepath(terminations):
    """
    Create CablePaths for all paths originating from the specified set of nodes.

    :param terminations: Iterable of CableTermination objects
    """
    from dcim.models import CablePath

    cp = CablePath.from_origin(terminations)
    if cp:
        cp.save()


def rebuild_paths(terminations):
    """
    Rebuild all CablePaths which traverse the specified nodes.
    """
    from dcim.models import CablePath

    for obj in terminations:
        cable_paths = CablePath.objects.filter(_nodes__contains=obj)

        with transaction.atomic(using=router.db_for_write(CablePath)):
            for cp in cable_paths:
                cp.delete()
                create_cablepath(cp.origins)


def update_interface_bridges(device, interface_templates, module=None):
    """
    Used for device and module instantiation. Iterates all InterfaceTemplates with a bridge assigned
    and applies it to the actual interfaces.
    """
    Interface = apps.get_model('dcim', 'Interface')

    for interface_template in interface_templates.exclude(bridge=None):
        interface = Interface.objects.get(device=device, name=interface_template.resolve_name(module=module))

        if interface_template.bridge:
            interface.bridge = Interface.objects.get(
                device=device,
                name=interface_template.bridge.resolve_name(module=module)
            )
            interface.full_clean()
            interface.save()


def update_device_components(device):
    """
    Update denormalized fields (_site, _location, _rack) for all component models
    associated with the specified device.

    :param device: Device instance whose components should be updated
    """
    from dcim.models import (
        ConsolePort, ConsoleServerPort, DeviceBay, FrontPort, Interface,
        InventoryItem, ModuleBay, PowerOutlet, PowerPort, RearPort,
    )

    COMPONENT_MODELS = (
        ConsolePort,
        ConsoleServerPort,
        DeviceBay,
        FrontPort,
        Interface,
        InventoryItem,
        ModuleBay,
        PowerOutlet,
        PowerPort,
        RearPort,
    )

    for model in COMPONENT_MODELS:
        model.objects.filter(device=device).update(
            _site=device.site,
            _location=device.location,
            _rack=device.rack,
        )
