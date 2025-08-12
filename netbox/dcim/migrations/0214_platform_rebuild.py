from django.db import migrations
import mptt
import mptt.managers


def rebuild_mptt(apps, schema_editor):
    """
    Construct the MPTT hierarchy.
    """
    Platform = apps.get_model('dcim', 'Platform')
    manager = mptt.managers.TreeManager()
    manager.model = Platform
    mptt.register(Platform)
    manager.contribute_to_class(Platform, 'objects')
    manager.rebuild()


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0213_platform_parent'),
    ]

    operations = [
        migrations.RunPython(
            code=rebuild_mptt,
            reverse_code=migrations.RunPython.noop
        ),
    ]
