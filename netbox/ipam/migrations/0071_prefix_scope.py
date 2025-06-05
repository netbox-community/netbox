import django.db.models.deletion
from django.contrib.contenttypes.models import ContentType
from django.db import migrations, models


def copy_site_assignments(apps, schema_editor):
    """
    Copy site ForeignKey values to the scope GFK.
    """
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Prefix = apps.get_model('ipam', 'Prefix')
    Site = apps.get_model('dcim', 'Site')
    db_alias = schema_editor.connection.alias

    Prefix.objects.using(db_alias).filter(site__isnull=False).update(
        scope_type=ContentType.objects.get_for_model(Site),
        scope_id=models.F('site_id')
    )


class Migration(migrations.Migration):
    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('ipam', '0070_vlangroup_vlan_id_ranges'),
    ]

    operations = [
        # Add the `scope` GenericForeignKey
        migrations.AddField(
            model_name='prefix',
            name='scope_id',
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='prefix',
            name='scope_type',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='+',
                to='contenttypes.contenttype',
            ),
        ),
        # Copy over existing site assignments
        migrations.RunPython(code=copy_site_assignments, reverse_code=migrations.RunPython.noop),
    ]


def oc_prefix_scope(objectchange, reverting):
    site_ct = ContentType.objects.get_by_natural_key('dcim', 'site').pk
    for data in (objectchange.prechange_data, objectchange.postchange_data):
        if data is None:
            continue
        if site_id := data.get('site'):
            data.update({
                'scope_type': site_ct,
                'scope_id': site_id,
            })


objectchange_migrators = {
    'ipam.prefix': oc_prefix_scope,
}
