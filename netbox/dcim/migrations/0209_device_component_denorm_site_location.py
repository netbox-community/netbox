import django.db.models.deletion
from django.db import migrations, models
from django.db.models import OuterRef, Subquery


def populate_denormalized_data(apps, schema_editor):
    Device = apps.get_model('dcim', 'Device')
    component_models = (
        apps.get_model('dcim', 'ConsolePort'),
        apps.get_model('dcim', 'ConsoleServerPort'),
        apps.get_model('dcim', 'PowerPort'),
        apps.get_model('dcim', 'PowerOutlet'),
        apps.get_model('dcim', 'Interface'),
        apps.get_model('dcim', 'FrontPort'),
        apps.get_model('dcim', 'RearPort'),
        apps.get_model('dcim', 'DeviceBay'),
        apps.get_model('dcim', 'ModuleBay'),
        apps.get_model('dcim', 'InventoryItem'),
    )

    for model in component_models:
        subquery = Device.objects.filter(pk=OuterRef('device_id'))
        model.objects.update(
            _site=Subquery(subquery.values('site_id')[:1]),
            _location=Subquery(subquery.values('location_id')[:1]),
            _rack=Subquery(subquery.values('rack_id')[:1]),
        )


class Migration(migrations.Migration):
    dependencies = [
        ('dcim', '0208_devicerole_uniqueness'),
    ]

    operations = [
        migrations.AddField(
            model_name='consoleport',
            name='_location',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='+',
                to='dcim.location',
            ),
        ),
        migrations.AddField(
            model_name='consoleport',
            name='_rack',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dcim.rack'
            ),
        ),
        migrations.AddField(
            model_name='consoleport',
            name='_site',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dcim.site'
            ),
        ),
        migrations.AddField(
            model_name='consoleserverport',
            name='_location',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='+',
                to='dcim.location',
            ),
        ),
        migrations.AddField(
            model_name='consoleserverport',
            name='_rack',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dcim.rack'
            ),
        ),
        migrations.AddField(
            model_name='consoleserverport',
            name='_site',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dcim.site'
            ),
        ),
        migrations.AddField(
            model_name='devicebay',
            name='_location',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='+',
                to='dcim.location',
            ),
        ),
        migrations.AddField(
            model_name='devicebay',
            name='_rack',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dcim.rack'
            ),
        ),
        migrations.AddField(
            model_name='devicebay',
            name='_site',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dcim.site'
            ),
        ),
        migrations.AddField(
            model_name='frontport',
            name='_location',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='+',
                to='dcim.location',
            ),
        ),
        migrations.AddField(
            model_name='frontport',
            name='_rack',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dcim.rack'
            ),
        ),
        migrations.AddField(
            model_name='frontport',
            name='_site',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dcim.site'
            ),
        ),
        migrations.AddField(
            model_name='interface',
            name='_location',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='+',
                to='dcim.location',
            ),
        ),
        migrations.AddField(
            model_name='interface',
            name='_rack',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dcim.rack'
            ),
        ),
        migrations.AddField(
            model_name='interface',
            name='_site',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dcim.site'
            ),
        ),
        migrations.AddField(
            model_name='inventoryitem',
            name='_location',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='+',
                to='dcim.location',
            ),
        ),
        migrations.AddField(
            model_name='inventoryitem',
            name='_rack',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dcim.rack'
            ),
        ),
        migrations.AddField(
            model_name='inventoryitem',
            name='_site',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dcim.site'
            ),
        ),
        migrations.AddField(
            model_name='modulebay',
            name='_location',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='+',
                to='dcim.location',
            ),
        ),
        migrations.AddField(
            model_name='modulebay',
            name='_rack',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dcim.rack'
            ),
        ),
        migrations.AddField(
            model_name='modulebay',
            name='_site',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dcim.site'
            ),
        ),
        migrations.AddField(
            model_name='poweroutlet',
            name='_location',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='+',
                to='dcim.location',
            ),
        ),
        migrations.AddField(
            model_name='poweroutlet',
            name='_rack',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dcim.rack'
            ),
        ),
        migrations.AddField(
            model_name='poweroutlet',
            name='_site',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dcim.site'
            ),
        ),
        migrations.AddField(
            model_name='powerport',
            name='_location',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='+',
                to='dcim.location',
            ),
        ),
        migrations.AddField(
            model_name='powerport',
            name='_rack',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dcim.rack'
            ),
        ),
        migrations.AddField(
            model_name='powerport',
            name='_site',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dcim.site'
            ),
        ),
        migrations.AddField(
            model_name='rearport',
            name='_location',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='+',
                to='dcim.location',
            ),
        ),
        migrations.AddField(
            model_name='rearport',
            name='_rack',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dcim.rack'
            ),
        ),
        migrations.AddField(
            model_name='rearport',
            name='_site',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dcim.site'
            ),
        ),
        migrations.RunPython(populate_denormalized_data),
    ]
