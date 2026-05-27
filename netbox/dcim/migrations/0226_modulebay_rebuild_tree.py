from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('dcim', '0226_add_mptt_tree_indexes'),
    ]

    # Historical MPTT rebuild: now a no-op. The MPTT tree columns are removed
    # by a later migration and ltree paths are populated from parent FKs.
    operations = [
        migrations.RunPython(migrations.RunPython.noop, migrations.RunPython.noop),
    ]
