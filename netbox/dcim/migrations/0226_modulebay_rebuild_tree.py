from django.db import migrations
import mptt
import mptt.managers


def rebuild_mptt(apps, schema_editor):
    """
    Rebuild the MPTT tree for ModuleBay to apply new ordering by 'name'
    instead of 'module'.
    """
    manager = mptt.managers.TreeManager()
    ModuleBay = apps.get_model('dcim', 'ModuleBay')
    manager.model = ModuleBay
    mptt.register(ModuleBay)
    manager.contribute_to_class(ModuleBay, 'objects')
    manager.rebuild()


class Migration(migrations.Migration):
    dependencies = [
        ('dcim', '0225_gfk_indexes'),
    ]

    operations = [
        migrations.RunPython(code=rebuild_mptt, reverse_code=migrations.RunPython.noop),
    ]
