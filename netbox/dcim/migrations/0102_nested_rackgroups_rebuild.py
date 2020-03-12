from django.db import migrations


def rebuild_mptt(apps, schema_editor):
    RackGroup = apps.get_model('dcim', 'RackGroup')
    for i, rackgroup in enumerate(RackGroup.objects.all(), start=1):
        RackGroup.objects.filter(pk=rackgroup.pk).update(tree_id=i)


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0101_nested_rackgroups'),
    ]

    operations = [
        migrations.RunPython(
            code=rebuild_mptt,
            reverse_code=migrations.RunPython.noop
        ),
    ]
