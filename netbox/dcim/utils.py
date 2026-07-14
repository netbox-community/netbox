from collections import defaultdict

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db import router, transaction
from django.utils.translation import gettext as _

from dcim.constants import MODULE_TOKEN


def get_module_bay_positions(module_bay):
    """
    Given a module bay, traverse up the module hierarchy and return
    a list of bay position strings from root to leaf, resolving any
    {module} tokens in each position using the parent position
    (position inheritance).
    """
    positions = []
    while module_bay:
        pos = module_bay.position or ''
        if positions and MODULE_TOKEN in pos:
            pos = pos.replace(MODULE_TOKEN, positions[-1])
        positions.append(pos)
        if module_bay.module:
            module_bay = module_bay.module.module_bay
        else:
            module_bay = None
    positions.reverse()
    return positions


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
    # Bulk-created (no per-mapping ObjectChange) to match how every other component is instantiated.
    PortMapping.objects.bulk_create(mappings)


def reconcile_port_mappings(mapping_model, parent_field, parent, desired):
    """
    Reconcile a parent port's mappings against `desired`, writing only the difference so unchanged
    mappings keep their PK (and emit no changelog entry). Changed/removed rows are deleted before
    replacements are created, all in one transaction, so position swaps don't trip the unique
    constraint. Per-row create()/delete() let the change-logging signals fire naturally.

    Args:
        mapping_model: PortMapping or PortTemplateMapping.
        parent_field: 'front_port' or 'rear_port' — the side being edited; its '<parent_field>_position'
            is each mapping's stable identity within the set.
        parent: the parent instance (FrontPort/RearPort or their templates).
        desired: iterable of dicts of mapping field values EXCLUDING the parent FK, using '<field>_id'
            for the opposite-port FK, e.g. {'front_port_position': 1, 'rear_port_id': 5,
            'rear_port_position': 2}. save() derives device/device_type/module_type from the front port.
    """
    key_field = f'{parent_field}_position'
    other_field = 'rear_port' if parent_field == 'front_port' else 'front_port'
    value_fields = (f'{other_field}_id', f'{other_field}_position')

    def target(source):
        # The comparable "value" of a mapping: the opposite port and its position. Two mappings with
        # the same parent-side position but a different target represent a re-pointing of that slot.
        get = source.get if isinstance(source, dict) else lambda f: getattr(source, f)
        return tuple(get(f) for f in value_fields)

    desired_by_key = {d[key_field]: d for d in desired}

    with transaction.atomic(using=router.db_for_write(mapping_model)):
        # Lock the parent's existing mappings for the duration of the reconcile. Two requests editing
        # the same port would otherwise read the same snapshot and race, the second colliding on a
        # unique constraint when it recreates rows the first has already committed.
        existing = {
            getattr(m, key_field): m
            for m in mapping_model.objects.filter(**{parent_field: parent}).select_for_update()
        }

        # Delete rows that no longer exist or whose target changed (before creating, to free the slots)
        for key, mapping in existing.items():
            if key not in desired_by_key or target(mapping) != target(desired_by_key[key]):
                mapping.delete()

        # Create rows that are new or whose target changed
        for key, attrs in desired_by_key.items():
            if key not in existing or target(existing[key]) != target(attrs):
                mapping_model.objects.create(**{parent_field: parent, **attrs})
