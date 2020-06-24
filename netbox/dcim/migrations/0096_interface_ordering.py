from django.db import migrations
import utilities.fields
import utilities.ordering


def _update_model_names(model):
    # Update each unique field value in bulk
    for name in model.objects.values_list('name', flat=True).order_by('name').distinct():
        model.objects.filter(name=name).update(_name=utilities.ordering.naturalize_interface(name, max_length=100))


def naturalize_interfacetemplates(apps, schema_editor):
    _update_model_names(apps.get_model('dcim', 'InterfaceTemplate'))


def naturalize_interfaces(apps, schema_editor):
    _update_model_names(apps.get_model('dcim', 'Interface'))


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0095_primary_model_ordering'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='interface',
            options={'ordering': ('device', '_name')},
        ),
        migrations.AlterModelOptions(
            name='interfacetemplate',
            options={'ordering': ('device_type', '_name')},
        ),
        migrations.AddField(
            model_name='interface',
            name='_name',
            field=utilities.fields.NaturalOrderingField('name', blank=True, max_length=100, naturalize_function=utilities.ordering.naturalize_interface),
        ),
        migrations.AddField(
            model_name='interfacetemplate',
            name='_name',
            field=utilities.fields.NaturalOrderingField('name', blank=True, max_length=100, naturalize_function=utilities.ordering.naturalize_interface),
        ),
        migrations.RunPython(
            code=naturalize_interfacetemplates,
            reverse_code=migrations.RunPython.noop
        ),
        migrations.RunPython(
            code=naturalize_interfaces,
            reverse_code=migrations.RunPython.noop
        ),
    ]
