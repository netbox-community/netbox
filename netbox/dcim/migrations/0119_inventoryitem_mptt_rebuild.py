from django.db import migrations
import mptt
import mptt.managers


def rebuild_mptt(apps, schema_editor):
    manager = mptt.managers.TreeManager()
    InventoryItem = apps.get_model('dcim', 'InventoryItem')
    manager.model = InventoryItem
    mptt.register(InventoryItem)
    manager.contribute_to_class(InventoryItem, 'objects')
    manager.rebuild()


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0118_inventoryitem_mptt'),
    ]

    operations = [
        migrations.RunPython(
            code=rebuild_mptt,
            reverse_code=migrations.RunPython.noop
        ),
    ]
