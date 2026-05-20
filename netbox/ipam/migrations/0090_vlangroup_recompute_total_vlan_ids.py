from django.db import migrations


def recompute_vlangroup_total_vlan_ids(apps, schema_editor):
    # PostgreSQL canonicalizes int4range values to '[)' on insert, so vid_ranges
    # at rest is already canonical. Only total_vlan_ids needs fixing: the
    # pre-fix VLANGroup.save() miscounted it for ranges supplied with
    # non-canonical bounds (e.g. NumericRange(lo, hi, bounds='[]')).
    VLANGroup = apps.get_model('ipam', 'VLANGroup')
    db_alias = schema_editor.connection.alias

    stale_groups = []
    for group in VLANGroup.objects.using(db_alias).only('id', 'vid_ranges', 'total_vlan_ids').iterator(chunk_size=500):
        total_vlan_ids = sum(
            r.upper - r.lower for r in (group.vid_ranges or []) if r.lower is not None and r.upper is not None
        )
        if group.total_vlan_ids != total_vlan_ids:
            group.total_vlan_ids = total_vlan_ids
            stale_groups.append(group)

    if stale_groups:
        VLANGroup.objects.using(db_alias).bulk_update(stale_groups, ['total_vlan_ids'], batch_size=100)


class Migration(migrations.Migration):
    dependencies = [
        ('ipam', '0089_default_ordering_indexes'),
    ]

    operations = [
        migrations.RunPython(recompute_vlangroup_total_vlan_ids, migrations.RunPython.noop),
    ]
