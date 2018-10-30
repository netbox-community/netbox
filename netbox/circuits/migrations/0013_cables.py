from django.db import migrations, models
import django.db.models.deletion

from dcim.constants import CONNECTION_STATUS_CONNECTED


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
    print("\n    Adding circuit terminations... ", end='', flush=True)
    for circuittermination in CircuitTermination.objects.filter(interface__isnull=False):
        c = Cable()

        # We have to assign all fields manually because we're inside a migration.
        c.termination_a_type = circuittermination_type
        c.termination_a_id = circuittermination.id
        c.termination_b_type = interface_type
        c.termination_b_id = circuittermination.interface_id
        c.connection_status = CONNECTION_STATUS_CONNECTED
        c.save()

        # Cache the connected Cable on the CircuitTermination
        circuittermination.cable = c
        circuittermination.connected_endpoint = circuittermination.interface
        circuittermination.connection_status = CONNECTION_STATUS_CONNECTED
        circuittermination.save()

        # Cache the connected Cable on the Interface
        interface = circuittermination.interface
        interface.cable = c
        interface._connected_circuittermination = circuittermination
        interface.connection_status = CONNECTION_STATUS_CONNECTED
        interface.save()

    cable_count = Cable.objects.filter(termination_a_type=circuittermination_type).count()
    print("{} cables created".format(cable_count))


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('circuits', '0012_change_logging'),
        ('dcim', '0066_cables'),
    ]

    operations = [

        # Add CircuitTermination.connected_endpoint
        migrations.AddField(
            model_name='circuittermination',
            name='connected_endpoint',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dcim.Interface'),
        ),
        migrations.AddField(
            model_name='circuittermination',
            name='connection_status',
            field=models.NullBooleanField(default=True),
        ),

        # Copy CircuitTermination connections to Interfaces as Cables
        migrations.RunPython(circuit_terminations_to_cables),

        # Model changes
        migrations.RemoveField(
            model_name='circuittermination',
            name='interface',
        ),
    ]
