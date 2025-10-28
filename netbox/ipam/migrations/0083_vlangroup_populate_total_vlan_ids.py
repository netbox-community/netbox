from django.db import migrations


def populate_vlangroup_total_vlan_ids(apps, schema_editor):
    VLANGroup = apps.get_model('ipam', 'VLANGroup')
    db_alias = schema_editor.connection.alias

    vlan_groups = VLANGroup.objects.using(db_alias).only('id', 'vid_ranges')
    for group in vlan_groups:
        total_vlan_ids = 0
        if group.vid_ranges:
            for r in group.vid_ranges:
                # Half-open [lo, hi): length is (hi - lo).
                if r is not None and r.lower is not None and r.upper is not None:
                    total_vlan_ids += r.upper - r.lower
        group._total_vlan_ids = total_vlan_ids
    VLANGroup.objects.using(db_alias).bulk_update(vlan_groups, ['_total_vlan_ids'], batch_size=100)


class Migration(migrations.Migration):
    dependencies = [
        ('ipam', '0082_add_prefix_network_containment_indexes'),
    ]

    operations = [
        migrations.RunPython(populate_vlangroup_total_vlan_ids, migrations.RunPython.noop),
    ]
