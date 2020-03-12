from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('tenancy', '0006_custom_tag_models'),
    ]

    operations = [
        migrations.AddField(
            model_name='tenantgroup',
            name='parent',
            field=mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='tenancy.TenantGroup'),
        ),
        migrations.AddField(
            model_name='tenantgroup',
            name='level',
            field=models.PositiveIntegerField(default=0, editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tenantgroup',
            name='lft',
            field=models.PositiveIntegerField(default=1, editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tenantgroup',
            name='rght',
            field=models.PositiveIntegerField(default=2, editable=False),
            preserve_default=False,
        ),
        # tree_id will be set to a valid value during the following migration (which needs to be a separate migration)
        migrations.AddField(
            model_name='tenantgroup',
            name='tree_id',
            field=models.PositiveIntegerField(db_index=True, default=0, editable=False),
            preserve_default=False,
        ),
    ]
