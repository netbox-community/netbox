from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0213_platform_parent'),
    ]

    # Historical MPTT rebuild: now a no-op. Tree state will be populated from
    # parent FKs into an ltree path column by a later migration.
    operations = [
        migrations.RunPython(migrations.RunPython.noop, migrations.RunPython.noop),
    ]
