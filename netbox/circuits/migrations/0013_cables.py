import sys

from django.db import migrations, models
import django.db.models.deletion

CONNECTION_STATUS_CONNECTED = True


def circuit_terminations_to_cables(apps, schema_editor):
    """
    Copy all existing CircuitTermination Interface associations as Cables
    """
    ContentType = apps.get_model('contenttypes', 'ContentType')
    CircuitTermination = apps.get_model('circuits', 'CircuitTermination')
    Interface = apps.get_model('dcim', 'Interface')
    Cable = apps.get_model('dcim', 'Cable')

    # Load content types
    circuittermination_type = ContentType.objects.get_for_model(CircuitTermination)
    interface_type = ContentType.objects.get_for_model(Interface)

    # Create a new Cable instance from each console connection
    if 'test' not in sys.argv:
        print("\n    Adding circuit terminations... ", end='', flush=True)
    for circuittermination in CircuitTermination.objects.filter(interface__isnull=False):

        # Create the new Cable
        cable = Cable.objects.create(
            termination_a_type=circuittermination_type,
            termination_a_id=circuittermination.id,
            termination_b_type=interface_type,
            termination_b_id=circuittermination.interface_id,
            status=CONNECTION_STATUS_CONNECTED
        )

        # Cache the Cable on its two termination points
        CircuitTermination.objects.filter(pk=circuittermination.pk).update(
            cable=cable,
            connected_endpoint=circuittermination.interface,
            connection_status=CONNECTION_STATUS_CONNECTED
        )
        # Cache the connected Cable on the Interface
        Interface.objects.filter(pk=circuittermination.interface_id).update(
            cable=cable,
            _connected_circuittermination=circuittermination,
            connection_status=CONNECTION_STATUS_CONNECTED
        )

    cable_count = Cable.objects.filter(termination_a_type=circuittermination_type).count()
    if 'test' not in sys.argv:
        print("{} cables created".format(cable_count))


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('circuits', '0012_change_logging'),
        ('dcim', '0066_cables'),
    ]

    operations = [

        # Add new CircuitTermination fields
        migrations.AddField(
            model_name='circuittermination',
            name='connected_endpoint',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dcim.Interface'),
        ),
        migrations.AddField(
            model_name='circuittermination',
            name='connection_status',
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name='circuittermination',
            name='cable',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dcim.Cable'),
        ),

        # Copy CircuitTermination connections to Interfaces as Cables
        migrations.RunPython(circuit_terminations_to_cables),

        # Remove interface field from CircuitTermination
        migrations.RemoveField(
            model_name='circuittermination',
            name='interface',
        ),
    ]
