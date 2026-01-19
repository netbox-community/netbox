from collections import defaultdict

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db import router, transaction

from dcim.constants import MODULE_PATH_TOKEN, MODULE_TOKEN, MODULE_TOKEN_SEPARATOR


def resolve_module_placeholders(text, positions):
    """
    Substitute {module} and {module_path} placeholders in text with position values.

    Args:
        text: String potentially containing {module} or {module_path} placeholders
        positions: List of position strings from the module tree (root to leaf)

    Returns:
        Text with placeholders replaced according to these rules:

        {module_path}: Always expands to full path (positions joined by MODULE_TOKEN_SEPARATOR).
                       Can only appear once in the text.

        {module}: If used once, expands to the PARENT module bay position only (last in positions).
                  If used multiple times, each token is replaced level-by-level.

    This design (Option 2 per sigprof's feedback) allows two approaches:
    1. Use {module_path} for automatic full-path expansion (hardcodes '/' separator)
    2. Use {module} in position fields to build custom paths with user-controlled separators
    """
    if not text:
        return text

    result = text

    # Handle {module_path} - always expands to full path
    if MODULE_PATH_TOKEN in result:
        full_path = MODULE_TOKEN_SEPARATOR.join(positions) if positions else ''
        result = result.replace(MODULE_PATH_TOKEN, full_path)

    # Handle {module} - parent-only for single token, level-by-level for multiple
    if MODULE_TOKEN in result:
        token_count = result.count(MODULE_TOKEN)
        if token_count == 1 and positions:
            # Single {module}: substitute with parent (immediate) bay position only
            parent_position = positions[-1] if positions else ''
            result = result.replace(MODULE_TOKEN, parent_position, 1)
        else:
            # Multiple {module}: substitute level-by-level (existing behavior)
            for pos in positions:
                result = result.replace(MODULE_TOKEN, pos, 1)

    return result


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


def create_cablepaths(objects):
    """
    Create CablePaths for all paths originating from the specified set of nodes.

    :param objects: Iterable of cabled objects (e.g. Interfaces)
    """
    from dcim.models import CablePath

    # Arrange objects by cable connector. All objects with a null connector are grouped together.
    origins = defaultdict(list)
    for obj in objects:
        origins[obj.cable_connector].append(obj)

    for connector, objects in origins.items():
        if cp := CablePath.from_origin(objects):
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
                create_cablepaths(cp.origins)


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


def create_port_mappings(device, device_type, module=None):
    """
    Replicate all front/rear port mappings from a DeviceType to the given device.
    """
    from dcim.models import FrontPort, PortMapping, RearPort

    templates = device_type.port_mappings.prefetch_related('front_port', 'rear_port')

    # Cache front & rear ports for efficient lookups by name
    front_ports = {
        fp.name: fp for fp in FrontPort.objects.filter(device=device)
    }
    rear_ports = {
        rp.name: rp for rp in RearPort.objects.filter(device=device)
    }

    # Replicate PortMappings
    mappings = []
    for template in templates:
        front_port = front_ports.get(template.front_port.resolve_name(module=module))
        rear_port = rear_ports.get(template.rear_port.resolve_name(module=module))
        mappings.append(
            PortMapping(
                device_id=front_port.device_id,
                front_port=front_port,
                front_port_position=template.front_port_position,
                rear_port=rear_port,
                rear_port_position=template.rear_port_position,
            )
        )
    PortMapping.objects.bulk_create(mappings)
