import django.db.models.deletion
import mptt.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0212_interface_tx_power_negative'),
    ]

    operations = [
        # Add parent & MPTT fields
        migrations.AddField(
            model_name='platform',
            name='parent',
            field=mptt.fields.TreeForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='children',
                to='dcim.platform'
            ),
        ),
        migrations.AddField(
            model_name='platform',
            name='level',
            field=models.PositiveIntegerField(default=0, editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='platform',
            name='lft',
            field=models.PositiveIntegerField(default=0, editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='platform',
            name='rght',
            field=models.PositiveIntegerField(default=0, editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='platform',
            name='tree_id',
            field=models.PositiveIntegerField(db_index=True, default=0, editable=False),
            preserve_default=False,
        ),
        # Add comments field
        migrations.AddField(
            model_name='platform',
            name='comments',
            field=models.TextField(blank=True),
        ),
    ]
