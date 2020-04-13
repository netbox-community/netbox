from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0100_mptt_remove_indexes'),
    ]

    operations = [
        migrations.AddField(
            model_name='rackgroup',
            name='parent',
            field=mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='dcim.RackGroup'),
        ),
        migrations.AddField(
            model_name='rackgroup',
            name='level',
            field=models.PositiveIntegerField(default=0, editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='rackgroup',
            name='lft',
            field=models.PositiveIntegerField(default=1, editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='rackgroup',
            name='rght',
            field=models.PositiveIntegerField(default=2, editable=False),
            preserve_default=False,
        ),
        # tree_id will be set to a valid value during the following migration (which needs to be a separate migration)
        migrations.AddField(
            model_name='rackgroup',
            name='tree_id',
            field=models.PositiveIntegerField(db_index=True, default=0, editable=False),
            preserve_default=False,
        ),
    ]
