from django.db import migrations
from django.db.models import Q


def delete_obsolete_cablepaths(apps, schema_editor):
    """
    Delete all CablePath instances which originate or terminate at a CircuitTermination.
    """
    ContentType = apps.get_model('contenttypes', 'ContentType')
    CircuitTermination = apps.get_model('circuits', 'CircuitTermination')
    CablePath = apps.get_model('dcim', 'CablePath')

    ct = ContentType.objects.get_for_model(CircuitTermination)
    CablePath.objects.filter(Q(origin_type=ct) | Q(destination_type=ct)).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('circuits', '0028_cache_circuit_terminations'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='circuittermination',
            name='_path',
        ),
        migrations.RunPython(
            code=delete_obsolete_cablepaths,
            reverse_code=migrations.RunPython.noop
        ),
    ]
