from django.db import migrations


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
    print(f'\nUpdating {total_count} prefixes...')

    # Iterate through all VRFs and the global table
    vrfs = [None] + list(VRF.objects.values_list('pk', flat=True))
    for vrf in vrfs:

        stack = []
        update_queue = []

        # Iterate through all Prefixes in the VRF, growing and shrinking the stack as we go
        prefixes = Prefix.objects.filter(vrf=vrf).values('pk', 'prefix')
        for i, p in enumerate(prefixes):

            # Grow the stack if this is a child of the most recent prefix
            if not stack or p['prefix'] in stack[-1]['prefix']:
                push_to_stack(stack, p)

            # If this is a sibling or parent of the most recent prefix, pop nodes from the
            # stack until we reach a parent prefix (or the root)
            else:
                while stack and p['prefix'] not in stack[-1]['prefix'] and p['prefix'] != stack[-1]['prefix']:
                    node = stack.pop()
                    update_queue.append(
                        Prefix(
                            pk=node['pk'],
                            _depth=len(stack),
                            _children=node['children']
                        )
                    )
                push_to_stack(stack, p)

                # Flush the update queue once it reaches 100 Prefixes
                if len(update_queue) >= 100:
                    Prefix.objects.bulk_update(update_queue, ['_depth', '_children'])
                    update_queue = []
                    print(f'  [{i}/{total_count}]')

        # Clear out any prefixes remaining in the stack
        while stack:
            node = stack.pop()
            update_queue.append(
                Prefix(
                    pk=node['pk'],
                    _depth=len(stack),
                    _children=node['children']
                )
            )

        # Final flush of any remaining Prefixes
        Prefix.objects.bulk_update(update_queue, ['_depth', '_children'])


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
