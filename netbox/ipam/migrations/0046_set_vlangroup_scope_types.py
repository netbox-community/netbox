from django.db import migrations


def set_scope_types(apps, schema_editor):
    """
    Set 'site' as the scope type for all VLANGroups with a scope ID defined.
    """
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Site = apps.get_model('dcim', 'Site')
    VLANGroup = apps.get_model('ipam', 'VLANGroup')

    VLANGroup.objects.filter(scope_id__isnull=False).update(
        scope_type=ContentType.objects.get_for_model(Site)
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
