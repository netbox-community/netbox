from django.db import migrations


def rebuild_mptt(apps, schema_editor):
    """
    Rebuild the MPTT tree for ModuleBay to apply new ordering by 'name'
    instead of 'module'.
    """
    ModuleBay = apps.get_model('dcim', 'ModuleBay')
    ModuleBay.objects.rebuild()


class Migration(migrations.Migration):
    dependencies = [
        ('dcim', '0225_gfk_indexes'),
    ]

    operations = [
        migrations.RunPython(code=rebuild_mptt, reverse_code=migrations.RunPython.noop),
    ]
