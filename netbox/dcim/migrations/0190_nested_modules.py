import django.db.models.deletion
import mptt.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0189_moduletype_airflow_rack_airflow_racktype_airflow'),
        ('extras', '0120_customfield_related_object_filter'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='modulebaytemplate',
            options={'ordering': ('device_type', 'module_type', '_name')},
        ),
        migrations.RemoveConstraint(
            model_name='modulebay',
            name='dcim_modulebay_unique_device_name',
        ),
        migrations.AddField(
            model_name='modulebay',
            name='level',
            field=models.PositiveIntegerField(default=0, editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='modulebay',
            name='lft',
            field=models.PositiveIntegerField(default=0, editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='modulebay',
            name='module',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='dcim.module'),
        ),
        migrations.AddField(
            model_name='modulebay',
            name='parent',
            field=mptt.fields.TreeForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='dcim.modulebay'),
        ),
        migrations.AddField(
            model_name='modulebay',
            name='rght',
            field=models.PositiveIntegerField(default=0, editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='modulebay',
            name='tree_id',
            field=models.PositiveIntegerField(db_index=True, default=0, editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='modulebaytemplate',
            name='module_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='dcim.moduletype'),
        ),
        migrations.AlterField(
            model_name='modulebaytemplate',
            name='device_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='dcim.devicetype'),
        ),
        migrations.AddConstraint(
            model_name='modulebay',
            constraint=models.UniqueConstraint(fields=('device', 'module', 'name'), name='dcim_modulebay_unique_device_module_name'),
        ),
        migrations.AddConstraint(
            model_name='modulebaytemplate',
            constraint=models.UniqueConstraint(fields=('module_type', 'name'), name='dcim_modulebaytemplate_unique_module_type_name'),
        ),
    ]
