import sys
from django.db import migrations

from ipam.utils import rebuild_prefixes


def push_to_stack(stack, prefix):
    # Increment child count on parent nodes
    for n in stack:
        n['children'] += 1
    stack.append({
        'pk': prefix['pk'],
        'prefix': prefix['prefix'],
        'children': 0,
    })


def populate_prefix_hierarchy(apps, schema_editor):
    """
    Populate _depth and _children attrs for all Prefixes.
    """
    Prefix = apps.get_model('ipam', 'Prefix')
    VRF = apps.get_model('ipam', 'VRF')

    total_count = Prefix.objects.count()
    if 'test' not in sys.argv:
        print(f'\nUpdating {total_count} prefixes...')

    # Rebuild the global table
    rebuild_prefixes(None)

    # Iterate through all VRFs, rebuilding each
    for vrf in VRF.objects.all():
        rebuild_prefixes(vrf)


class Migration(migrations.Migration):

    dependencies = [
        ('ipam', '0047_prefix_depth_children'),
    ]

    operations = [
        migrations.RunPython(
            code=populate_prefix_hierarchy,
            reverse_code=migrations.RunPython.noop
        ),
    ]
