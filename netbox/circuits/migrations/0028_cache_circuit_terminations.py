import sys

from django.db import migrations


def cache_circuit_terminations(apps, schema_editor):
    Circuit = apps.get_model('circuits', 'Circuit')
    CircuitTermination = apps.get_model('circuits', 'CircuitTermination')

    if 'test' not in sys.argv:
        print(f"\n    Caching circuit terminations...", flush=True)

    a_terminations = {
        ct.circuit_id: ct.pk for ct in CircuitTermination.objects.filter(term_side='A')
    }
    z_terminations = {
        ct.circuit_id: ct.pk for ct in CircuitTermination.objects.filter(term_side='Z')
    }
    for circuit in Circuit.objects.all():
        Circuit.objects.filter(pk=circuit.pk).update(
            termination_a_id=a_terminations.get(circuit.pk),
            termination_z_id=z_terminations.get(circuit.pk),
        )


class Migration(migrations.Migration):

    dependencies = [
        ('circuits', '0027_providernetwork'),
    ]

    operations = [
        migrations.RunPython(
            code=cache_circuit_terminations,
            reverse_code=migrations.RunPython.noop
        ),
    ]
