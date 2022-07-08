from django.db import migrations

from dcim.utils import compile_path_node


def populate_cable_paths(apps, schema_editor):
    """
    Replicate terminations from the Cable model into CableTermination instances.
    """
    CablePath = apps.get_model('dcim', 'CablePath')

    # Construct the new two-dimensional path, and add the origin & destination objects to the nodes list
    cable_paths = []
    for cablepath in CablePath.objects.all():

        # Origin
        origin = compile_path_node(cablepath.origin_type_id, cablepath.origin_id)
        cablepath.path.append([origin])
        cablepath._nodes.insert(0, origin)

        # Transit nodes
        cablepath.path.extend([
            [node] for node in cablepath._nodes[1:]
        ])

        # Destination
        if cablepath.destination_id:
            destination = compile_path_node(cablepath.destination_type_id, cablepath.destination_id)
            cablepath.path.append([destination])
            cablepath._nodes.append(destination)
            cablepath.is_complete = True

        cable_paths.append(cablepath)

    # Bulk update all CableTerminations
    CablePath.objects.bulk_update(cable_paths, fields=('path', '_nodes', 'is_complete'), batch_size=100)


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0158_populate_cable_terminations'),
    ]

    operations = [
        migrations.RunPython(
            code=populate_cable_paths,
            reverse_code=migrations.RunPython.noop
        ),
    ]
