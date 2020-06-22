from django.db import migrations
import utilities.fields
import utilities.ordering


def _update_model_names(model):
    # Update each unique field value in bulk
    for name in model.objects.values_list('name', flat=True).order_by('name').distinct():
        model.objects.filter(name=name).update(_name=utilities.ordering.naturalize(name, max_length=100))


def naturalize_sites(apps, schema_editor):
    _update_model_names(apps.get_model('dcim', 'Site'))


def naturalize_racks(apps, schema_editor):
    _update_model_names(apps.get_model('dcim', 'Rack'))


def naturalize_devices(apps, schema_editor):
    _update_model_names(apps.get_model('dcim', 'Device'))


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0094_device_component_template_ordering'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='device',
            options={'ordering': ('_name', 'pk')},
        ),
        migrations.AlterModelOptions(
            name='rack',
            options={'ordering': ('site', 'group', '_name', 'pk')},
        ),
        migrations.AlterModelOptions(
            name='site',
            options={'ordering': ('_name',)},
        ),
        migrations.AddField(
            model_name='device',
            name='_name',
            field=utilities.fields.NaturalOrderingField('name', blank=True, max_length=100, naturalize_function=utilities.ordering.naturalize, null=True),
        ),
        migrations.AddField(
            model_name='rack',
            name='_name',
            field=utilities.fields.NaturalOrderingField('name', blank=True, max_length=100, naturalize_function=utilities.ordering.naturalize),
        ),
        migrations.AddField(
            model_name='site',
            name='_name',
            field=utilities.fields.NaturalOrderingField('name', blank=True, max_length=100, naturalize_function=utilities.ordering.naturalize),
        ),
        migrations.RunPython(
            code=naturalize_sites,
            reverse_code=migrations.RunPython.noop
        ),
        migrations.RunPython(
            code=naturalize_racks,
            reverse_code=migrations.RunPython.noop
        ),
        migrations.RunPython(
            code=naturalize_devices,
            reverse_code=migrations.RunPython.noop
        ),
    ]
