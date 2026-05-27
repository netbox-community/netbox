from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('dcim', '0203_device_role_nested'),
    ]

    # Historical MPTT rebuild: now a no-op. The legacy lft/rght/tree_id/level
    # columns are removed in a later migration and ltree paths are populated
    # from parent FKs after that.
    operations = [
        migrations.RunPython(migrations.RunPython.noop, migrations.RunPython.noop),
    ]
