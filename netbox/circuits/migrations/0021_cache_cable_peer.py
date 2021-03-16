import sys

from django.db import migrations, models
import django.db.models.deletion


def cache_cable_peers(apps, schema_editor):
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Cable = apps.get_model('dcim', 'Cable')
    CircuitTermination = apps.get_model('circuits', 'CircuitTermination')

    if 'test' not in sys.argv:
        print(f"\n    Updating circuit termination cable peers...", flush=True)
    ct = ContentType.objects.get_for_model(CircuitTermination)
    for cable in Cable.objects.filter(termination_a_type=ct):
        CircuitTermination.objects.filter(pk=cable.termination_a_id).update(
            _cable_peer_type_id=cable.termination_b_type_id,
            _cable_peer_id=cable.termination_b_id
        )
    for cable in Cable.objects.filter(termination_b_type=ct):
        CircuitTermination.objects.filter(pk=cable.termination_b_id).update(
            _cable_peer_type_id=cable.termination_a_type_id,
            _cable_peer_id=cable.termination_a_id
        )


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('circuits', '0020_custom_field_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='circuittermination',
            name='_cable_peer_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='circuittermination',
            name='_cable_peer_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='contenttypes.contenttype'),
        ),
        migrations.RunPython(
            code=cache_cable_peers,
            reverse_code=migrations.RunPython.noop
        ),
    ]
