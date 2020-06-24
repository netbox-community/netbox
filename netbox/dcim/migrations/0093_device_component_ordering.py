from django.db import migrations
import utilities.fields
import utilities.ordering


def _update_model_names(model):
    # Update each unique field value in bulk
    for name in model.objects.values_list('name', flat=True).order_by('name').distinct():
        model.objects.filter(name=name).update(_name=utilities.ordering.naturalize(name, max_length=100))


def naturalize_consoleports(apps, schema_editor):
    _update_model_names(apps.get_model('dcim', 'ConsolePort'))


def naturalize_consoleserverports(apps, schema_editor):
    _update_model_names(apps.get_model('dcim', 'ConsoleServerPort'))


def naturalize_powerports(apps, schema_editor):
    _update_model_names(apps.get_model('dcim', 'PowerPort'))


def naturalize_poweroutlets(apps, schema_editor):
    _update_model_names(apps.get_model('dcim', 'PowerOutlet'))


def naturalize_frontports(apps, schema_editor):
    _update_model_names(apps.get_model('dcim', 'FrontPort'))


def naturalize_rearports(apps, schema_editor):
    _update_model_names(apps.get_model('dcim', 'RearPort'))


def naturalize_devicebays(apps, schema_editor):
    _update_model_names(apps.get_model('dcim', 'DeviceBay'))


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0092_fix_rack_outer_unit'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='consoleport',
            options={'ordering': ('device', '_name')},
        ),
        migrations.AlterModelOptions(
            name='consoleserverport',
            options={'ordering': ('device', '_name')},
        ),
        migrations.AlterModelOptions(
            name='devicebay',
            options={'ordering': ('device', '_name')},
        ),
        migrations.AlterModelOptions(
            name='frontport',
            options={'ordering': ('device', '_name')},
        ),
        migrations.AlterModelOptions(
            name='inventoryitem',
            options={'ordering': ('device__id', 'parent__id', '_name')},
        ),
        migrations.AlterModelOptions(
            name='poweroutlet',
            options={'ordering': ('device', '_name')},
        ),
        migrations.AlterModelOptions(
            name='powerport',
            options={'ordering': ('device', '_name')},
        ),
        migrations.AlterModelOptions(
            name='rearport',
            options={'ordering': ('device', '_name')},
        ),
        migrations.AddField(
            model_name='consoleport',
            name='_name',
            field=utilities.fields.NaturalOrderingField('name', blank=True, max_length=100, naturalize_function=utilities.ordering.naturalize),
        ),
        migrations.AddField(
            model_name='consoleserverport',
            name='_name',
            field=utilities.fields.NaturalOrderingField('name', blank=True, max_length=100, naturalize_function=utilities.ordering.naturalize),
        ),
        migrations.AddField(
            model_name='devicebay',
            name='_name',
            field=utilities.fields.NaturalOrderingField('name', blank=True, max_length=100, naturalize_function=utilities.ordering.naturalize),
        ),
        migrations.AddField(
            model_name='frontport',
            name='_name',
            field=utilities.fields.NaturalOrderingField('name', blank=True, max_length=100, naturalize_function=utilities.ordering.naturalize),
        ),
        migrations.AddField(
            model_name='inventoryitem',
            name='_name',
            field=utilities.fields.NaturalOrderingField('name', blank=True, max_length=100, naturalize_function=utilities.ordering.naturalize),
        ),
        migrations.AddField(
            model_name='poweroutlet',
            name='_name',
            field=utilities.fields.NaturalOrderingField('name', blank=True, max_length=100, naturalize_function=utilities.ordering.naturalize),
        ),
        migrations.AddField(
            model_name='powerport',
            name='_name',
            field=utilities.fields.NaturalOrderingField('name', blank=True, max_length=100, naturalize_function=utilities.ordering.naturalize),
        ),
        migrations.AddField(
            model_name='rearport',
            name='_name',
            field=utilities.fields.NaturalOrderingField('name', blank=True, max_length=100, naturalize_function=utilities.ordering.naturalize),
        ),
        migrations.RunPython(
            code=naturalize_consoleports,
            reverse_code=migrations.RunPython.noop
        ),
        migrations.RunPython(
            code=naturalize_consoleserverports,
            reverse_code=migrations.RunPython.noop
        ),
        migrations.RunPython(
            code=naturalize_powerports,
            reverse_code=migrations.RunPython.noop
        ),
        migrations.RunPython(
            code=naturalize_poweroutlets,
            reverse_code=migrations.RunPython.noop
        ),
        migrations.RunPython(
            code=naturalize_frontports,
            reverse_code=migrations.RunPython.noop
        ),
        migrations.RunPython(
            code=naturalize_rearports,
            reverse_code=migrations.RunPython.noop
        ),
        migrations.RunPython(
            code=naturalize_devicebays,
            reverse_code=migrations.RunPython.noop
        ),
    ]
