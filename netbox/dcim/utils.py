from collections import defaultdict

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db import router, transaction
from django.utils.translation import gettext as _

from dcim.constants import MODULE_TOKEN


def inherit_module_token(position, parent_positions):
    """
    Resolve a single {module} token in a bay position by inheriting from the position
    one level deeper in a module bay hierarchy. Returns position unchanged unless
    parent_positions is non-empty and position contains {module}, in which case the
    token is substituted with parent_positions[-1].

    Used by resolve_position_chain(), the single inheritance implementation shared by
    get_module_bay_positions() and the module move planner.
    """
    if parent_positions and MODULE_TOKEN in position:
        return position.replace(MODULE_TOKEN, parent_positions[-1])
    return position


def get_module_bay_raw_positions(module_bay):
    """
    Given a module bay, traverse up the module hierarchy and return the stored
    (unresolved) bay position strings from root to leaf.

    Raises ValueError if the module bay hierarchy contains a cycle.
    """
    positions = []
    visited = set()
    while module_bay:
        if module_bay.pk in visited:
            raise ValueError(_("Module bay hierarchy contains a cycle."))
        visited.add(module_bay.pk)
        positions.append(module_bay.position or '')
        module_bay = module_bay.module.module_bay if module_bay.module else None
    positions.reverse()
    return positions


def resolve_position_chain(raw_positions):
    """
    Apply leaf-to-root {module} token inheritance over a root-to-leaf list of raw bay
    positions: each position inherits from the resolved position one level deeper, and
    the leaf's own token is never resolved. Shared by get_module_bay_positions() and
    the module move planner so a planned chain always equals what a fresh walk
    computes once the planned positions are stored.
    """
    resolved = []
    for position in reversed(raw_positions):
        resolved.append(inherit_module_token(position, resolved))
    resolved.reverse()
    return resolved


def get_module_bay_positions(module_bay):
    """
    Given a module bay, traverse up the module hierarchy and return a list of bay
    position strings from root to leaf, resolving any {module} tokens in each
    position using the parent position (position inheritance).

    Raises ValueError if the module bay hierarchy contains a cycle.
    """
    return resolve_position_chain(get_module_bay_raw_positions(module_bay))


def resolve_module_placeholder(value, positions):
    """
    Resolve {module} placeholder tokens in a string using the given
    list of module bay positions (ordered root to leaf).

    A single {module} token resolves to the leaf (immediate parent) bay's position.
    Multiple tokens must match the tree depth and resolve level-by-level.

    Returns the resolved string.
    Raises ValueError if token count is greater than 1 and doesn't match tree depth.
    """
    if MODULE_TOKEN not in value:
        return value

    token_count = value.count(MODULE_TOKEN)
    if token_count == 1:
        return value.replace(MODULE_TOKEN, positions[-1])
    if token_count == len(positions):
        for pos in positions:
            value = value.replace(MODULE_TOKEN, pos, 1)
        return value
    raise ValueError(
        _("Cannot install module with placeholder values in a module bay tree "
          "{level} levels deep but {tokens} placeholders given.").format(
            level=len(positions), tokens=token_count
        )
    )


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


def create_port_mappings(device, device_or_module_type, module=None):
    """
    Replicate all front/rear port mappings from a DeviceType or ModuleType to the given device.
    """
    from dcim.models import FrontPort, PortMapping, RearPort

    templates = device_or_module_type.port_mappings.prefetch_related('front_port', 'rear_port')

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
