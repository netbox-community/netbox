from django.db import migrations
import utilities.fields
import utilities.ordering


def _update_model_names(model):
    # Update each unique field value in bulk
    for name in model.objects.values_list('name', flat=True).order_by('name').distinct():
        model.objects.filter(name=name).update(_name=utilities.ordering.naturalize(name, max_length=100))


def naturalize_consoleporttemplates(apps, schema_editor):
    _update_model_names(apps.get_model('dcim', 'ConsolePortTemplate'))


def naturalize_consoleserverporttemplates(apps, schema_editor):
    _update_model_names(apps.get_model('dcim', 'ConsoleServerPortTemplate'))


def naturalize_powerporttemplates(apps, schema_editor):
    _update_model_names(apps.get_model('dcim', 'PowerPortTemplate'))


def naturalize_poweroutlettemplates(apps, schema_editor):
    _update_model_names(apps.get_model('dcim', 'PowerOutletTemplate'))


def naturalize_frontporttemplates(apps, schema_editor):
    _update_model_names(apps.get_model('dcim', 'FrontPortTemplate'))


def naturalize_rearporttemplates(apps, schema_editor):
    _update_model_names(apps.get_model('dcim', 'RearPortTemplate'))


def naturalize_devicebaytemplates(apps, schema_editor):
    _update_model_names(apps.get_model('dcim', 'DeviceBayTemplate'))


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0093_device_component_ordering'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='consoleporttemplate',
            options={'ordering': ('device_type', '_name')},
        ),
        migrations.AlterModelOptions(
            name='consoleserverporttemplate',
            options={'ordering': ('device_type', '_name')},
        ),
        migrations.AlterModelOptions(
            name='devicebaytemplate',
            options={'ordering': ('device_type', '_name')},
        ),
        migrations.AlterModelOptions(
            name='frontporttemplate',
            options={'ordering': ('device_type', '_name')},
        ),
        migrations.AlterModelOptions(
            name='poweroutlettemplate',
            options={'ordering': ('device_type', '_name')},
        ),
        migrations.AlterModelOptions(
            name='powerporttemplate',
            options={'ordering': ('device_type', '_name')},
        ),
        migrations.AlterModelOptions(
            name='rearporttemplate',
            options={'ordering': ('device_type', '_name')},
        ),
        migrations.AddField(
            model_name='consoleporttemplate',
            name='_name',
            field=utilities.fields.NaturalOrderingField('name', blank=True, max_length=100, naturalize_function=utilities.ordering.naturalize),
        ),
        migrations.AddField(
            model_name='consoleserverporttemplate',
            name='_name',
            field=utilities.fields.NaturalOrderingField('name', blank=True, max_length=100, naturalize_function=utilities.ordering.naturalize),
        ),
        migrations.AddField(
            model_name='devicebaytemplate',
            name='_name',
            field=utilities.fields.NaturalOrderingField('name', blank=True, max_length=100, naturalize_function=utilities.ordering.naturalize),
        ),
        migrations.AddField(
            model_name='frontporttemplate',
            name='_name',
            field=utilities.fields.NaturalOrderingField('name', blank=True, max_length=100, naturalize_function=utilities.ordering.naturalize),
        ),
        migrations.AddField(
            model_name='poweroutlettemplate',
            name='_name',
            field=utilities.fields.NaturalOrderingField('name', blank=True, max_length=100, naturalize_function=utilities.ordering.naturalize),
        ),
        migrations.AddField(
            model_name='powerporttemplate',
            name='_name',
            field=utilities.fields.NaturalOrderingField('name', blank=True, max_length=100, naturalize_function=utilities.ordering.naturalize),
        ),
        migrations.AddField(
            model_name='rearporttemplate',
            name='_name',
            field=utilities.fields.NaturalOrderingField('name', blank=True, max_length=100, naturalize_function=utilities.ordering.naturalize),
        ),
        migrations.RunPython(
            code=naturalize_consoleporttemplates,
            reverse_code=migrations.RunPython.noop
        ),
        migrations.RunPython(
            code=naturalize_consoleserverporttemplates,
            reverse_code=migrations.RunPython.noop
        ),
        migrations.RunPython(
            code=naturalize_powerporttemplates,
            reverse_code=migrations.RunPython.noop
        ),
        migrations.RunPython(
            code=naturalize_poweroutlettemplates,
            reverse_code=migrations.RunPython.noop
        ),
        migrations.RunPython(
            code=naturalize_frontporttemplates,
            reverse_code=migrations.RunPython.noop
        ),
        migrations.RunPython(
            code=naturalize_rearporttemplates,
            reverse_code=migrations.RunPython.noop
        ),
        migrations.RunPython(
            code=naturalize_devicebaytemplates,
            reverse_code=migrations.RunPython.noop
        ),
    ]
