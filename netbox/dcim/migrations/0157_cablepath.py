import dcim.fields
import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0156_cable_remove_terminations'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cablepath',
            old_name='path',
            new_name='_nodes',
        ),
        migrations.AddField(
            model_name='cablepath',
            name='path',
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name='cablepath',
            name='is_complete',
            field=models.BooleanField(default=False),
        ),
    ]
