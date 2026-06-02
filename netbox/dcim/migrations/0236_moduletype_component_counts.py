from django.db import migrations
from django.db.models import Count, OuterRef, Subquery

import utilities.fields


def populate_module_type_component_counts(apps, schema_editor):
    """
    Populate the component template counter fields for existing ModuleTypes.
    """
    ModuleType = apps.get_model('dcim', 'ModuleType')
    db_alias = schema_editor.connection.alias

    counters = {
        'console_port_template_count': 'consoleporttemplates',
        'console_server_port_template_count': 'consoleserverporttemplates',
        'power_port_template_count': 'powerporttemplates',
        'power_outlet_template_count': 'poweroutlettemplates',
        'interface_template_count': 'interfacetemplates',
        'front_port_template_count': 'frontporttemplates',
        'rear_port_template_count': 'rearporttemplates',
        'module_bay_template_count': 'modulebaytemplates',
    }

    for field_name, related_name in counters.items():
        count_subquery = (
            ModuleType.objects.using(db_alias)
            .filter(pk=OuterRef('pk'))
            .annotate(_count=Count(related_name))
            .values('_count')
        )
        ModuleType.objects.using(db_alias).update(**{field_name: Subquery(count_subquery)})


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0235_cabletermination_circuit_site_cache'),
    ]

    operations = [
        migrations.AddField(
            model_name='moduletype',
            name='console_port_template_count',
            field=utilities.fields.CounterCacheField(
                default=0, editable=False, to_field='module_type', to_model='dcim.ConsolePortTemplate'
            ),
        ),
        migrations.AddField(
            model_name='moduletype',
            name='console_server_port_template_count',
            field=utilities.fields.CounterCacheField(
                default=0, editable=False, to_field='module_type', to_model='dcim.ConsoleServerPortTemplate'
            ),
        ),
        migrations.AddField(
            model_name='moduletype',
            name='front_port_template_count',
            field=utilities.fields.CounterCacheField(
                default=0, editable=False, to_field='module_type', to_model='dcim.FrontPortTemplate'
            ),
        ),
        migrations.AddField(
            model_name='moduletype',
            name='interface_template_count',
            field=utilities.fields.CounterCacheField(
                default=0, editable=False, to_field='module_type', to_model='dcim.InterfaceTemplate'
            ),
        ),
        migrations.AddField(
            model_name='moduletype',
            name='module_bay_template_count',
            field=utilities.fields.CounterCacheField(
                default=0, editable=False, to_field='module_type', to_model='dcim.ModuleBayTemplate'
            ),
        ),
        migrations.AddField(
            model_name='moduletype',
            name='power_outlet_template_count',
            field=utilities.fields.CounterCacheField(
                default=0, editable=False, to_field='module_type', to_model='dcim.PowerOutletTemplate'
            ),
        ),
        migrations.AddField(
            model_name='moduletype',
            name='power_port_template_count',
            field=utilities.fields.CounterCacheField(
                default=0, editable=False, to_field='module_type', to_model='dcim.PowerPortTemplate'
            ),
        ),
        migrations.AddField(
            model_name='moduletype',
            name='rear_port_template_count',
            field=utilities.fields.CounterCacheField(
                default=0, editable=False, to_field='module_type', to_model='dcim.RearPortTemplate'
            ),
        ),
        migrations.RunPython(populate_module_type_component_counts, migrations.RunPython.noop),
    ]
