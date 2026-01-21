from django.db import migrations
import mptt.managers
import mptt.models


def rebuild_mptt(apps, schema_editor):
    """
    Rebuild the MPTT tree for ModuleBay to apply new ordering.
    """
    ModuleBay = apps.get_model('dcim', 'ModuleBay')

    # Set MPTTMeta with the correct order_insertion_by
    class MPTTMeta:
        order_insertion_by = ('module', 'name',)

    ModuleBay.MPTTMeta = MPTTMeta
    ModuleBay._mptt_meta = mptt.models.MPTTOptions(MPTTMeta)

    manager = mptt.managers.TreeManager()
    manager.model = ModuleBay
    manager.contribute_to_class(ModuleBay, 'objects')
    manager.rebuild()


class Migration(migrations.Migration):
    dependencies = [
        ('dcim', '0225_gfk_indexes'),
    ]

    operations = [
        migrations.RunPython(code=rebuild_mptt, reverse_code=migrations.RunPython.noop),
    ]
