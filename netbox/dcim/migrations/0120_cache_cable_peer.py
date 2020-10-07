import sys

from django.db import migrations, models
import django.db.models.deletion


def cache_cable_peers(apps, schema_editor):
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Cable = apps.get_model('dcim', 'Cable')
    ConsolePort = apps.get_model('dcim', 'ConsolePort')
    ConsoleServerPort = apps.get_model('dcim', 'ConsoleServerPort')
    PowerPort = apps.get_model('dcim', 'PowerPort')
    PowerOutlet = apps.get_model('dcim', 'PowerOutlet')
    Interface = apps.get_model('dcim', 'Interface')
    FrontPort = apps.get_model('dcim', 'FrontPort')
    RearPort = apps.get_model('dcim', 'RearPort')
    PowerFeed = apps.get_model('dcim', 'PowerFeed')

    models = (
        ConsolePort,
        ConsoleServerPort,
        PowerPort,
        PowerOutlet,
        Interface,
        FrontPort,
        RearPort,
        PowerFeed
    )

    if 'test' not in sys.argv:
        print("\n", end="")

    for model in models:
        if 'test' not in sys.argv:
            print(f"    Updating {model._meta.verbose_name} cable peers...", flush=True)
        ct = ContentType.objects.get_for_model(model)
        for cable in Cable.objects.filter(termination_a_type=ct):
            model.objects.filter(pk=cable.termination_a_id).update(
                _cable_peer_type_id=cable.termination_b_type_id,
                _cable_peer_id=cable.termination_b_id
            )
        for cable in Cable.objects.filter(termination_b_type=ct):
            model.objects.filter(pk=cable.termination_b_id).update(
                _cable_peer_type_id=cable.termination_a_type_id,
                _cable_peer_id=cable.termination_a_id
            )


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('dcim', '0119_inventoryitem_mptt_rebuild'),
    ]

    operations = [
        migrations.AddField(
            model_name='consoleport',
            name='_cable_peer_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='consoleport',
            name='_cable_peer_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='consoleserverport',
            name='_cable_peer_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='consoleserverport',
            name='_cable_peer_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='frontport',
            name='_cable_peer_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='frontport',
            name='_cable_peer_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='interface',
            name='_cable_peer_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='interface',
            name='_cable_peer_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='powerfeed',
            name='_cable_peer_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='powerfeed',
            name='_cable_peer_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='poweroutlet',
            name='_cable_peer_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='poweroutlet',
            name='_cable_peer_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='powerport',
            name='_cable_peer_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='powerport',
            name='_cable_peer_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='rearport',
            name='_cable_peer_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='rearport',
            name='_cable_peer_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='contenttypes.contenttype'),
        ),
        migrations.RunPython(
            code=cache_cable_peers,
            reverse_code=migrations.RunPython.noop
        ),
    ]
