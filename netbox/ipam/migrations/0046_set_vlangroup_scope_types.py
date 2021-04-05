from django.db import migrations


def set_scope_types(apps, schema_editor):
    """
    Set 'site' as the scope type for all VLANGroups with a scope ID defined.
    """
    ContentType = apps.get_model('contenttypes', 'ContentType')
    VLANGroup = apps.get_model('ipam', 'VLANGroup')

    site_ct = ContentType.objects.get(app_label='dcim', model='site').pk
    VLANGroup.objects.filter(scope_id__isnull=False).update(
        scope_type=site_ct
    )


class Migration(migrations.Migration):

    dependencies = [
        ('ipam', '0045_vlangroup_scope'),
    ]

    operations = [
        migrations.RunPython(
            code=set_scope_types
        ),
    ]
