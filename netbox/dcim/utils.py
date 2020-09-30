from django.contrib.contenttypes.models import ContentType

from .models import FrontPort, RearPort


def object_to_path_node(obj):
    return f'{obj._meta.model_name}:{obj.pk}'


def objects_to_path(*obj_list):
    return [object_to_path_node(obj) for obj in obj_list]


def path_node_to_object(repr):
    model_name, object_id = repr.split(':')
    model_class = ContentType.objects.get(model=model_name).model_class()
    return model_class.objects.get(pk=int(object_id))


def trace_paths(node):
    destination = None
    path = []
    position_stack = []

    if node.cable is None:
        return []

    while node.cable is not None:

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
                # No position indicated, so we have to trace _all_ peer FrontPorts
                paths = []
                for frontport in FrontPort.objects.filter(rear_port=peer_termination):
                    branches = trace_paths(frontport)
                    if branches:
                        for branch, destination in branches:
                            paths.append(([*path, object_to_path_node(frontport), *branch], destination))
                    else:
                        paths.append(([*path, object_to_path_node(frontport)], None))
                return paths

        # Anything else marks the end of the path
        else:
            destination = peer_termination
            break

    return [(path, destination)]
