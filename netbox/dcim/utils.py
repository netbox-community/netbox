from django.contrib.contenttypes.models import ContentType

from .choices import CableStatusChoices
from .exceptions import CableTraceSplit
from .models import FrontPort, RearPort


def object_to_path_node(obj):
    return f'{obj._meta.model_name}:{obj.pk}'


def objects_to_path(*obj_list):
    return [object_to_path_node(obj) for obj in obj_list]


def path_node_to_object(repr):
    model_name, object_id = repr.split(':')
    model_class = ContentType.objects.get(model=model_name).model_class()
    return model_class.objects.get(pk=int(object_id))


def trace_path(node):
    destination = None
    path = []
    position_stack = []
    is_connected = True

    if node.cable is None:
        return [], None, False

    while node.cable is not None:
        if node.cable.status != CableStatusChoices.STATUS_CONNECTED:
            is_connected = False

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

    return path, destination, is_connected
