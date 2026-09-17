from collections import defaultdict, deque

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db import router, transaction
from django.db.models import Q
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


def _get_cablepath_origin_objects(nodes):
    """
    Fetch fresh origins in bulk by content type, indexed by their encoded path nodes.
    """
    ids_by_type = defaultdict(set)
    for node in nodes:
        type_id, object_id = decompile_path_node(node)
        ids_by_type[type_id].add(object_id)

    objects = {}
    for type_id, object_ids in ids_by_type.items():
        model = ContentType.objects.get_for_id(type_id).model_class()
        if model is not None:
            # Recovery also reads link; loading its direct relations avoids another query for every origin.
            relations = [
                field.name for field in model._meta.fields
                if field.many_to_one and field.name in ('cable', 'wireless_link')
            ]
            queryset = model.objects.select_related(*relations) if relations else model.objects.all()
            for object_id, obj in queryset.in_bulk(object_ids).items():
                objects[compile_path_node(type_id, object_id)] = obj
    return objects


def create_cablepaths(objects):
    """
    Trace and replace paths for the supplied origins, recovering co-origins whose current paths are removed.

    The supplied objects may span multiple connectors on one link. Grouping and recovery share one worklist.

    :param objects: Iterable of cabled objects (e.g. Interfaces)
    """
    from dcim.models import CablePath, PathEndpoint

    origin_groups = _group_cablepath_origins(objects)
    pending = deque(origin_groups)
    if not pending:
        return
    processed = set()

    # Keep a savepoint so callers can catch tracing failures inside an outer transaction.
    # This provides rollback, but does not serialize concurrent rebuilds.
    with transaction.atomic(using=router.db_for_write(CablePath)):
        while pending:
            # Do not let recovery replace origins already rebuilt by this call.
            origins = [
                obj for obj in pending.popleft()
                if object_to_path_node(obj) not in processed
            ]
            if not origins:
                continue

            # Trace first, so an unsupported topology raises before anything is deleted
            path = CablePath.from_origin(origins)
            nodes = {object_to_path_node(obj) for obj in origins}
            processed.update(nodes)

            # `overlap` takes the encoded nodes directly, and matches nothing for an empty set
            for old_path in CablePath.objects.filter(_nodes__overlap=list(nodes)):
                # `_nodes` matches a node anywhere in a path, including as another path's destination
                if not old_path.path or not nodes.intersection(old_path.path[0]):
                    continue

                # Recover only origins whose current path is being deleted, keeping different links separate
                remaining = [node for node in old_path.path[0] if node not in processed]
                # Refresh immediately before this deletion; earlier iterations can change _path references.
                origin_objects = _get_cablepath_origin_objects(remaining)
                by_link = defaultdict(list)
                for node in remaining:
                    origin = origin_objects.get(node)
                    if origin is None:
                        continue
                    # Absence of the back-reference is not evidence that a pointer was cleared
                    if isinstance(origin, PathEndpoint) and origin._path_id != old_path.pk:
                        continue
                    if link := origin.link:
                        by_link[link].append(origin)
                for linked_origins in by_link.values():
                    recovered_groups = _group_cablepath_origins(linked_origins)
                    pending.extend(recovered_groups)

                old_path.delete()

            if path:
                path.save()


def _group_cablepath_origins(objects):
    """
    Expand channelized interfaces and group origins on one link by connector, keeping channels separate.
    """
    from dcim.models import Interface

    # Expand any channelized interface into its channel subinterfaces. A channelized parent originates no path of its
    # own; instead, each channel subinterface traces independently from the single connector position it occupies.
    # Plain (non-channelized) origins pass through unchanged, keeping this expansion re-entrant so that
    # rebuild_paths() -> create_cablepaths(cp.origins) does not re-expand the channel subinterfaces it already holds.
    expanded = []
    for obj in objects:
        if isinstance(obj, Interface) and obj.channels:
            expanded.extend(obj.child_interfaces.filter(channel_id__isnull=False, cable__isnull=False))
        else:
            expanded.append(obj)

    origin_groups = []
    connectors = defaultdict(list)
    for obj in expanded:
        if isinstance(obj, Interface) and obj.channel_id:
            origin_groups.append([obj])
        else:
            connectors[obj.cable_connector].append(obj)
    origin_groups.extend(connectors.values())

    return origin_groups


def get_cable_end_terminations(cable_ends):
    """
    Return the current termination objects for each (cable ID, end) key, preserving connector order.

    Use the CableTermination's connector for grouping. This does not repair persisted endpoint fields;
    inconsistent cached links or positions can still prevent tracing.
    """
    from dcim.models import CableTermination

    groups = {key: [] for key in cable_ends}
    if not groups:
        return groups

    cables_by_end = defaultdict(list)
    for cable_id, cable_end in groups:
        cables_by_end[cable_end].append(cable_id)
    query = Q()
    # Cable ends are A or B, so this needs at most two clauses regardless of the number of cables.
    for cable_end, cable_ids in cables_by_end.items():
        query |= Q(cable_id__in=cable_ids, cable_end=cable_end)
    terminations = CableTermination.objects.filter(query).order_by(
        'cable_id', 'cable_end', 'connector', 'pk'
    ).prefetch_related('termination__cable')
    for termination in terminations:
        # A stale GenericForeignKey can still reference an object which no longer exists.
        if (obj := termination.termination) is not None:
            # Partition this fetched instance by its authoritative connector, without saving the endpoint.
            obj.cable_connector = termination.connector
            groups[(termination.cable_id, termination.cable_end)].append(obj)
    return groups


def get_cablepath_origin_groups(objects):
    """
    Resolve originating objects to current cable ends in bulk. Channels and uncabled origins remain singletons.
    """
    from dcim.models import CableTermination, Interface

    objects = {object_to_path_node(obj): obj for obj in objects}
    if not objects:
        return {}

    ids_by_type = defaultdict(list)
    for node, obj in objects.items():
        if not (isinstance(obj, Interface) and obj.channel_id):
            type_id, object_id = decompile_path_node(node)
            ids_by_type[type_id].append(object_id)

    # Resolve membership from CableTermination, never from the endpoint's cached cable/end fields.
    keys = {}
    if ids_by_type:
        query = Q()
        for type_id, object_ids in ids_by_type.items():
            query |= Q(termination_type_id=type_id, termination_id__in=object_ids)
        for type_id, object_id, cable_id, cable_end in CableTermination.objects.filter(query).values_list(
            'termination_type_id', 'termination_id', 'cable_id', 'cable_end'
        ):
            keys[compile_path_node(type_id, object_id)] = (cable_id, cable_end)

    cable_ends = get_cable_end_terminations(keys.values())
    groups = {}
    for node, obj in objects.items():
        if node in keys:
            groups[keys[node]] = cable_ends[keys[node]]
        else:
            groups[node] = [obj]
    return groups


def rebuild_paths(terminations):
    """
    Rebuild paths traversing the given nodes from their origins' current cable-end membership.
    """
    from dcim.models import CablePath

    nodes = [object_to_path_node(obj) for obj in terminations]
    if not nodes:
        return

    # Snapshot the entire operation before replacement can retire another candidate. The transaction includes
    # candidate deletion as well as all replacements; a failure must restore both. It does not serialize rebuilds.
    with transaction.atomic(using=router.db_for_write(CablePath)):
        cable_paths = list(CablePath.objects.filter(_nodes__overlap=nodes))
        origin_nodes = dict.fromkeys(
            node for cable_path in cable_paths for node in (cable_path.path[0] if cable_path.path else ())
        )
        origin_objects = _get_cablepath_origin_objects(origin_nodes)
        origins = [origin_objects[node] for node in origin_nodes if node in origin_objects]
        origin_groups = get_cablepath_origin_groups(origins)

        # A historical hop can name a parent which now originates paths through its channels.
        affected_nodes = set()
        for origin in origins:
            expanded_groups = _group_cablepath_origins([origin])
            for group in expanded_groups:
                affected_nodes.update(object_to_path_node(obj) for obj in group)

        # Current membership determines each complete group, but only candidate origins determine its scope.
        # Do not retrace unrelated connectors on the same cable end.
        rebuild_inputs = []
        scheduled = set()
        for current_origins in origin_groups.values():
            selected_origins = []
            current_groups = _group_cablepath_origins(current_origins)
            for group in current_groups:
                group_nodes = {object_to_path_node(obj) for obj in group}
                if group_nodes & affected_nodes and not group_nodes.issubset(scheduled):
                    selected_origins.extend(group)
                    # A parent's channels can also appear as individual candidate origins.
                    scheduled.update(group_nodes)
            if selected_origins:
                # Keep one call per end so all requested groups precede recovery in the same worklist.
                rebuild_inputs.append(selected_origins)

        # Use the model method to clear current endpoint references, including those on disconnected origins.
        for cable_path in cable_paths:
            cable_path.delete()
        for origins in rebuild_inputs:
            create_cablepaths(origins)


def rebuild_cable_paths(cable):
    """
    Delete and rebuild every CablePath traversing the given Cable, tracing freshly from the Cable's current
    terminations in both directions. Used when the channelization of a terminated interface changes (e.g. a channel
    subinterface is added, moved, or removed) without the Cable itself being modified.
    """
    from dcim.choices import CableEndChoices
    from dcim.models import CablePath, CableTermination, PathEndpoint

    with transaction.atomic(using=router.db_for_write(CablePath)):
        # Delete existing paths individually so each clears its `_path` back-reference on the originating endpoints.
        for cp in CablePath.objects.filter(_nodes__contains=cable):
            cp.delete()

        a_terminations, b_terminations = [], []
        for ct in CableTermination.objects.filter(cable=cable):
            if ct.cable_end == CableEndChoices.SIDE_A:
                a_terminations.append(ct.termination)
            else:
                b_terminations.append(ct.termination)

        for nodes in (a_terminations, b_terminations):
            if not nodes:
                continue
            if isinstance(nodes[0], PathEndpoint):
                create_cablepaths(nodes)
            else:
                rebuild_paths(nodes)


def update_interface_parents(device, interface_templates, module=None):
    """
    Used for device and module instantiation. Iterates all InterfaceTemplates with a parent assigned and applies it to
    the actual interfaces. Must run after all interfaces have been instantiated (so that every parent interface exists)
    and before update_interface_bridges() (so that channel subinterfaces validate against a populated parent).
    """
    Interface = apps.get_model('dcim', 'Interface')

    for interface_template in interface_templates.exclude(parent=None):
        interface = Interface.objects.get(device=device, name=interface_template.resolve_name(module=module))
        interface.parent = Interface.objects.get(
            device=device,
            name=interface_template.parent.resolve_name(module=module)
        )
        interface.full_clean()
        interface.save()


def update_interface_bridges(device, interface_templates, module=None):
    """
    Used for device and module instantiation. Iterates all InterfaceTemplates with a bridge assigned
    and applies it to the actual interfaces.
    """
    Interface = apps.get_model('dcim', 'Interface')

    for interface_template in interface_templates.exclude(bridge=None):
        interface = Interface.objects.get(
            device=device,
            name=interface_template.resolve_name(module=module, device=device)
        )

        if interface_template.bridge:
            interface.bridge = Interface.objects.get(
                device=device,
                name=interface_template.bridge.resolve_name(module=module, device=device)
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
        front_port = front_ports.get(template.front_port.resolve_name(module=module, device=device))
        rear_port = rear_ports.get(template.rear_port.resolve_name(module=module, device=device))
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
