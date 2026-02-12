from django.db import migrations
from django.db.models import Count, OuterRef, Subquery

import utilities.fields


def _populate_count_for_type(
    apps, schema_editor, app_name: str, model_name: str, target_field: str, related_name: str = 'instances'
):
    """
    Update a CounterCache field on the specified model by annotating the count of related instances.
    """
    Model = apps.get_model(app_name, model_name)
    db_alias = schema_editor.connection.alias

    count_subquery = (
        Model.objects.using(db_alias)
        .filter(pk=OuterRef('pk'))
        .annotate(_instance_count=Count(related_name))
        .values('_instance_count')
    )
    Model.objects.using(db_alias).update(**{target_field: Subquery(count_subquery)})


def populate_device_type_device_count(apps, schema_editor):
    _populate_count_for_type(apps, schema_editor, 'dcim', 'DeviceType', 'device_count')


def populate_module_type_module_count(apps, schema_editor):
    _populate_count_for_type(apps, schema_editor, 'dcim', 'ModuleType', 'module_count')


def populate_rack_type_rack_count(apps, schema_editor):
    _populate_count_for_type(apps, schema_editor, 'dcim', 'RackType', 'rack_count', related_name='racks')


class Migration(migrations.Migration):
    dependencies = [
        ('dcim', '0218_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='devicetype',
            name='device_count',
            field=utilities.fields.CounterCacheField(
                default=0, editable=False, to_field='device_type', to_model='dcim.Device'
            ),
        ),
        migrations.RunPython(populate_device_type_device_count, migrations.RunPython.noop),
        migrations.AddField(
            model_name='moduletype',
            name='module_count',
            field=utilities.fields.CounterCacheField(
                default=0, editable=False, to_field='module_type', to_model='dcim.Module'
            ),
        ),
        migrations.RunPython(populate_module_type_module_count, migrations.RunPython.noop),
        migrations.AddField(
            model_name='racktype',
            name='rack_count',
            field=utilities.fields.CounterCacheField(
                default=0, editable=False, to_field='rack_type', to_model='dcim.Rack'
            ),
        ),
        migrations.RunPython(populate_rack_type_rack_count, migrations.RunPython.noop),
    ]
