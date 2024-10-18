from django.db import migrations, models


def set_null_values(apps, schema_editor):
    """
    Replace empty strings with null values.
    """
    Cable = apps.get_model('dcim', 'Cable')
    ConsolePort = apps.get_model('dcim', 'ConsolePort')
    ConsolePortTemplate = apps.get_model('dcim', 'ConsolePortTemplate')
    ConsoleServerPort = apps.get_model('dcim', 'ConsoleServerPort')
    ConsoleServerPortTemplate = apps.get_model('dcim', 'ConsoleServerPortTemplate')
    Device = apps.get_model('dcim', 'Device')
    DeviceType = apps.get_model('dcim', 'DeviceType')
    FrontPort = apps.get_model('dcim', 'FrontPort')
    Interface = apps.get_model('dcim', 'Interface')
    InterfaceTemplate = apps.get_model('dcim', 'InterfaceTemplate')
    ModuleType = apps.get_model('dcim', 'ModuleType')
    PowerFeed = apps.get_model('dcim', 'PowerFeed')
    PowerOutlet = apps.get_model('dcim', 'PowerOutlet')
    PowerOutletTemplate = apps.get_model('dcim', 'PowerOutletTemplate')
    PowerPort = apps.get_model('dcim', 'PowerPort')
    PowerPortTemplate = apps.get_model('dcim', 'PowerPortTemplate')
    Rack = apps.get_model('dcim', 'Rack')
    RackType = apps.get_model('dcim', 'RackType')
    RearPort = apps.get_model('dcim', 'RearPort')

    Cable.objects.filter(length_unit='').update(length_unit=None)
    Cable.objects.filter(type='').update(type=None)
    ConsolePort.objects.filter(cable_end='').update(cable_end=None)
    ConsolePort.objects.filter(type='').update(type=None)
    ConsolePortTemplate.objects.filter(type='').update(type=None)
    ConsoleServerPort.objects.filter(cable_end='').update(cable_end=None)
    ConsoleServerPort.objects.filter(type='').update(type=None)
    ConsoleServerPortTemplate.objects.filter(type='').update(type=None)
    Device.objects.filter(airflow='').update(airflow=None)
    Device.objects.filter(face='').update(face=None)
    DeviceType.objects.filter(airflow='').update(airflow=None)
    DeviceType.objects.filter(subdevice_role='').update(subdevice_role=None)
    DeviceType.objects.filter(weight_unit='').update(weight_unit=None)
    FrontPort.objects.filter(cable_end='').update(cable_end=None)
    Interface.objects.filter(cable_end='').update(cable_end=None)
    Interface.objects.filter(mode='').update(mode=None)
    Interface.objects.filter(poe_mode='').update(poe_mode=None)
    Interface.objects.filter(poe_type='').update(poe_type=None)
    Interface.objects.filter(rf_channel='').update(rf_channel=None)
    Interface.objects.filter(rf_role='').update(rf_role=None)
    InterfaceTemplate.objects.filter(poe_mode='').update(poe_mode=None)
    InterfaceTemplate.objects.filter(poe_type='').update(poe_type=None)
    InterfaceTemplate.objects.filter(rf_role='').update(rf_role=None)
    ModuleType.objects.filter(airflow='').update(airflow=None)
    ModuleType.objects.filter(weight_unit='').update(weight_unit=None)
    PowerFeed.objects.filter(cable_end='').update(cable_end=None)
    PowerOutlet.objects.filter(cable_end='').update(cable_end=None)
    PowerOutlet.objects.filter(feed_leg='').update(feed_leg=None)
    PowerOutlet.objects.filter(type='').update(type=None)
    PowerOutletTemplate.objects.filter(feed_leg='').update(feed_leg=None)
    PowerOutletTemplate.objects.filter(type='').update(type=None)
    PowerPort.objects.filter(cable_end='').update(cable_end=None)
    PowerPort.objects.filter(type='').update(type=None)
    PowerPortTemplate.objects.filter(type='').update(type=None)
    Rack.objects.filter(airflow='').update(airflow=None)
    Rack.objects.filter(form_factor='').update(form_factor=None)
    Rack.objects.filter(outer_unit='').update(outer_unit=None)
    Rack.objects.filter(weight_unit='').update(weight_unit=None)
    RackType.objects.filter(outer_unit='').update(outer_unit=None)
    RackType.objects.filter(weight_unit='').update(weight_unit=None)
    RearPort.objects.filter(cable_end='').update(cable_end=None)


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0193_poweroutlet_color'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cable',
            name='length_unit',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='cable',
            name='type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='consoleport',
            name='cable_end',
            field=models.CharField(blank=True, max_length=1, null=True),
        ),
        migrations.AlterField(
            model_name='consoleport',
            name='type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='consoleporttemplate',
            name='type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='consoleserverport',
            name='cable_end',
            field=models.CharField(blank=True, max_length=1, null=True),
        ),
        migrations.AlterField(
            model_name='consoleserverport',
            name='type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='consoleserverporttemplate',
            name='type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='device',
            name='airflow',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='device',
            name='face',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='devicetype',
            name='airflow',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='devicetype',
            name='subdevice_role',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='devicetype',
            name='weight_unit',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='frontport',
            name='cable_end',
            field=models.CharField(blank=True, max_length=1, null=True),
        ),
        migrations.AlterField(
            model_name='interface',
            name='cable_end',
            field=models.CharField(blank=True, max_length=1, null=True),
        ),
        migrations.AlterField(
            model_name='interface',
            name='mode',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='interface',
            name='poe_mode',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='interface',
            name='poe_type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='interface',
            name='rf_channel',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='interface',
            name='rf_role',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='interfacetemplate',
            name='poe_mode',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='interfacetemplate',
            name='poe_type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='interfacetemplate',
            name='rf_role',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='moduletype',
            name='airflow',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='moduletype',
            name='weight_unit',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='powerfeed',
            name='cable_end',
            field=models.CharField(blank=True, max_length=1, null=True),
        ),
        migrations.AlterField(
            model_name='poweroutlet',
            name='cable_end',
            field=models.CharField(blank=True, max_length=1, null=True),
        ),
        migrations.AlterField(
            model_name='poweroutlet',
            name='feed_leg',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='poweroutlet',
            name='type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='poweroutlettemplate',
            name='feed_leg',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='poweroutlettemplate',
            name='type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='powerport',
            name='cable_end',
            field=models.CharField(blank=True, max_length=1, null=True),
        ),
        migrations.AlterField(
            model_name='powerport',
            name='type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='powerporttemplate',
            name='type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='rack',
            name='airflow',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='rack',
            name='form_factor',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='rack',
            name='outer_unit',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='rack',
            name='weight_unit',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='racktype',
            name='outer_unit',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='racktype',
            name='weight_unit',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='rearport',
            name='cable_end',
            field=models.CharField(blank=True, max_length=1, null=True),
        ),
        migrations.RunPython(
            code=set_null_values,
            reverse_code=migrations.RunPython.noop
        ),
    ]
