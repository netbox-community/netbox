from django.db import migrations
from django.db.models import OuterRef, Subquery


def populate_circuit_termination_site_cache(apps, schema_editor):
    """
    Populate the cached _site and _location fields on CableTermination records whose
    termination is a CircuitTermination. Earlier versions failed to cache these values,
    causing site/location filters on cables to omit such terminations.
    """
    ContentType = apps.get_model('contenttypes', 'ContentType')
    CableTermination = apps.get_model('dcim', 'CableTermination')
    CircuitTermination = apps.get_model('circuits', 'CircuitTermination')

    try:
        ct = ContentType.objects.get_by_natural_key('circuits', 'circuittermination')
    except ContentType.DoesNotExist:
        return

    circuit_terminations = CircuitTermination.objects.filter(pk=OuterRef('termination_id'))
    CableTermination.objects.filter(termination_type=ct).update(
        _site=Subquery(circuit_terminations.values('_site_id')[:1]),
        _location=Subquery(circuit_terminations.values('_location_id')[:1]),
    )


class Migration(migrations.Migration):
    dependencies = [
        ('dcim', '0234_cablepath_nodes_index'),
        ('circuits', '0057_default_ordering_indexes'),
    ]

    operations = [
        migrations.RunPython(populate_circuit_termination_site_cache, migrations.RunPython.noop),
    ]
