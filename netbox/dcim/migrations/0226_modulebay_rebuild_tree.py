from django.db import migrations
import mptt
import mptt.managers


def rebuild_mptt(apps, schema_editor):
    """
    Rebuild the MPTT tree for ModuleBay to apply new ordering by 'name'
    instead of 'module'.
    """
    ModuleBay = apps.get_model('dcim', 'ModuleBay')

    # Set MPTTMeta with the correct order_insertion_by
    class MPTTMeta:
        order_insertion_by = ('module', 'name',)

    ModuleBay.MPTTMeta = MPTTMeta

    manager = mptt.managers.TreeManager()
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
