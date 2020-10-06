from django.contrib.contenttypes.models import ContentType

from .choices import CableStatusChoices
from .exceptions import CableTraceSplit


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
    Given a path node representation, return the corresponding object.
    """
    ct_id, object_id = decompile_path_node(repr)
    model_class = ContentType.objects.get(pk=ct_id).model_class()
    return model_class.objects.get(pk=int(object_id))


def trace_path(node):
    from .models import FrontPort, RearPort

    destination = None
    path = []
    position_stack = []
    is_active = True

    if node is None or node.cable is None:
        return [], None, False

    while node.cable is not None:
        if node.cable.status != CableStatusChoices.STATUS_CONNECTED:
            is_active = False

        # Follow the cable to its far-end termination
        path.append(object_to_path_node(node.cable))
        peer_termination = node.get_cable_peer()

        # Follow a FrontPort to its corresponding RearPort
        if isinstance(peer_termination, FrontPort):
            path.append(object_to_path_node(peer_termination))
            node = peer_termination.rear_port
            if node.positions > 1:
                position_stack.append(peer_termination.rear_port_position)
            path.append(object_to_path_node(node))

        # Follow a RearPort to its corresponding FrontPort
        elif isinstance(peer_termination, RearPort):
            path.append(object_to_path_node(peer_termination))
            if peer_termination.positions == 1:
                node = FrontPort.objects.get(rear_port=peer_termination, rear_port_position=1)
                path.append(object_to_path_node(node))
            elif position_stack:
                position = position_stack.pop()
                node = FrontPort.objects.get(rear_port=peer_termination, rear_port_position=position)
                path.append(object_to_path_node(node))
            else:
                # No position indicated: path has split (probably invalid?)
                raise CableTraceSplit(peer_termination)

        # Anything else marks the end of the path
        else:
            destination = peer_termination
            break

    if destination is None:
        is_active = False

    return path, destination, is_active
