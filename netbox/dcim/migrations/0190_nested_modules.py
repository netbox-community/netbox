import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0189_moduletype_airflow_rack_airflow_racktype_airflow'),
        ('extras', '0119_eventrule_event_types'),
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
            name='module',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='dcim.module'),
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
