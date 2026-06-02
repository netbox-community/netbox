import django.contrib.postgres.indexes
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('dcim', '0233_device_render_config_permission'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='cablepath',
            index=django.contrib.postgres.indexes.GinIndex(fields=['_nodes'], name='dcim_cablep__nodes_b23b96_gin'),
        ),
    ]
