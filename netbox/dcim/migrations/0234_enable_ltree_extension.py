from django.contrib.postgres.operations import CreateExtension
from django.db import migrations


class Migration(migrations.Migration):
    """
    Enable the PostgreSQL ltree extension. Required by the next migration which
    adds the `path` column on hierarchical models.
    """

    dependencies = [
        ('dcim', '0233_device_render_config_permission'),
    ]

    operations = [
        CreateExtension('ltree'),
    ]
