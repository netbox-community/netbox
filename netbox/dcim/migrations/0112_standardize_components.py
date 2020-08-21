from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0111_component_template_description'),
    ]

    operations = [
        # Set max_length=64 for all name fields
        migrations.AlterField(
            model_name='consoleport',
            name='name',
            field=models.CharField(max_length=64),
        ),
        migrations.AlterField(
            model_name='consoleporttemplate',
            name='name',
            field=models.CharField(max_length=64),
        ),
        migrations.AlterField(
            model_name='consoleserverport',
            name='name',
            field=models.CharField(max_length=64),
        ),
        migrations.AlterField(
            model_name='consoleserverporttemplate',
            name='name',
            field=models.CharField(max_length=64),
        ),
        migrations.AlterField(
            model_name='devicebay',
            name='name',
            field=models.CharField(max_length=64),
        ),
        migrations.AlterField(
            model_name='devicebaytemplate',
            name='name',
            field=models.CharField(max_length=64),
        ),
        migrations.AlterField(
            model_name='inventoryitem',
            name='name',
            field=models.CharField(max_length=64),
        ),
        migrations.AlterField(
            model_name='poweroutlet',
            name='name',
            field=models.CharField(max_length=64),
        ),
        migrations.AlterField(
            model_name='poweroutlettemplate',
            name='name',
            field=models.CharField(max_length=64),
        ),
        migrations.AlterField(
            model_name='powerport',
            name='name',
            field=models.CharField(max_length=64),
        ),
        migrations.AlterField(
            model_name='powerporttemplate',
            name='name',
            field=models.CharField(max_length=64),
        ),

        # Update related_name for necessary component and component template models
        migrations.AlterField(
            model_name='consoleporttemplate',
            name='device_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='consoleporttemplates', to='dcim.DeviceType'),
        ),
        migrations.AlterField(
            model_name='consoleserverporttemplate',
            name='device_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='consoleserverporttemplates', to='dcim.DeviceType'),
        ),
        migrations.AlterField(
            model_name='devicebay',
            name='device',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='devicebays', to='dcim.Device'),
        ),
        migrations.AlterField(
            model_name='devicebaytemplate',
            name='device_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='devicebaytemplates', to='dcim.DeviceType'),
        ),
        migrations.AlterField(
            model_name='frontporttemplate',
            name='device_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='frontporttemplates', to='dcim.DeviceType'),
        ),
        migrations.AlterField(
            model_name='interfacetemplate',
            name='device_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interfacetemplates', to='dcim.DeviceType'),
        ),
        migrations.AlterField(
            model_name='inventoryitem',
            name='device',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inventoryitems', to='dcim.Device'),
        ),
        migrations.AlterField(
            model_name='poweroutlettemplate',
            name='device_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='poweroutlettemplates', to='dcim.DeviceType'),
        ),
        migrations.AlterField(
            model_name='powerporttemplate',
            name='device_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='powerporttemplates', to='dcim.DeviceType'),
        ),
        migrations.AlterField(
            model_name='rearporttemplate',
            name='device_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rearporttemplates', to='dcim.DeviceType'),
        ),
    ]
