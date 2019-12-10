import sys

from django.db import migrations, models
import django.db.models.deletion

import utilities.fields


def console_connections_to_cables(apps, schema_editor):
    """
    Copy all existing console connections as Cables
    """
    ContentType = apps.get_model('contenttypes', 'ContentType')
    ConsolePort = apps.get_model('dcim', 'ConsolePort')
    ConsoleServerPort = apps.get_model('dcim', 'ConsoleServerPort')
    Cable = apps.get_model('dcim', 'Cable')

    # Load content types
    consoleport_type = ContentType.objects.get_for_model(ConsolePort)
    consoleserverport_type = ContentType.objects.get_for_model(ConsoleServerPort)

    # Create a new Cable instance from each console connection
    if 'test' not in sys.argv:
        print("\n    Adding console connections... ", end='', flush=True)
    for consoleport in ConsolePort.objects.filter(connected_endpoint__isnull=False):

        # Create the new Cable
        cable = Cable.objects.create(
            termination_a_type=consoleport_type,
            termination_a_id=consoleport.id,
            termination_b_type=consoleserverport_type,
            termination_b_id=consoleport.connected_endpoint_id,
            status=consoleport.connection_status
        )

        # Cache the Cable on its two termination points
        ConsolePort.objects.filter(pk=consoleport.id).update(
            cable=cable
        )
        ConsoleServerPort.objects.filter(pk=consoleport.connected_endpoint_id).update(
            connection_status=consoleport.connection_status,
            cable=cable
        )

    cable_count = Cable.objects.filter(termination_a_type=consoleport_type).count()
    if 'test' not in sys.argv:
        print("{} cables created".format(cable_count))

    # Normalize connection_status for all non-connected ConsolePorts
    ConsolePort.objects.filter(connected_endpoint__isnull=True).update(connection_status=None)


def power_connections_to_cables(apps, schema_editor):
    """
    Copy all existing power connections as Cables
    """
    ContentType = apps.get_model('contenttypes', 'ContentType')
    PowerPort = apps.get_model('dcim', 'PowerPort')
    PowerOutlet = apps.get_model('dcim', 'PowerOutlet')
    Cable = apps.get_model('dcim', 'Cable')

    # Load content types
    powerport_type = ContentType.objects.get_for_model(PowerPort)
    poweroutlet_type = ContentType.objects.get_for_model(PowerOutlet)

    # Create a new Cable instance from each power connection
    if 'test' not in sys.argv:
        print("    Adding power connections... ", end='', flush=True)
    for powerport in PowerPort.objects.filter(connected_endpoint__isnull=False):

        # Create the new Cable
        cable = Cable.objects.create(
            termination_a_type=powerport_type,
            termination_a_id=powerport.id,
            termination_b_type=poweroutlet_type,
            termination_b_id=powerport.connected_endpoint_id,
            status=powerport.connection_status
        )

        # Cache the Cable on its two termination points
        PowerPort.objects.filter(pk=powerport.id).update(
            cable=cable
        )
        PowerOutlet.objects.filter(pk=powerport.connected_endpoint_id).update(
            connection_status=powerport.connection_status,
            cable=cable
        )

    cable_count = Cable.objects.filter(termination_a_type=powerport_type).count()
    if 'test' not in sys.argv:
        print("{} cables created".format(cable_count))

    # Normalize connection_status for all non-connected PowerPorts
    PowerPort.objects.filter(connected_endpoint__isnull=True).update(connection_status=None)


def interface_connections_to_cables(apps, schema_editor):
    """
    Copy all InterfaceConnections as Cables
    """
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Interface = apps.get_model('dcim', 'Interface')
    InterfaceConnection = apps.get_model('dcim', 'InterfaceConnection')
    Cable = apps.get_model('dcim', 'Cable')

    # Load content types
    interface_type = ContentType.objects.get_for_model(Interface)

    # Create a new Cable instance from each InterfaceConnection
    if 'test' not in sys.argv:
        print("    Adding interface connections... ", end='', flush=True)
    for conn in InterfaceConnection.objects.all():

        # Create the new Cable
        cable = Cable.objects.create(
            termination_a_type=interface_type,
            termination_a_id=conn.interface_a_id,
            termination_b_type=interface_type,
            termination_b_id=conn.interface_b_id,
            status=conn.connection_status
        )

        # Cache the connected Cable on each Interface
        Interface.objects.filter(pk=conn.interface_a_id).update(
            _connected_interface=conn.interface_b,
            connection_status=conn.connection_status,
            cable=cable
        )
        Interface.objects.filter(pk=conn.interface_b_id).update(
            _connected_interface=conn.interface_a,
            connection_status=conn.connection_status,
            cable=cable
        )

    cable_count = Cable.objects.filter(termination_a_type=interface_type).count()
    if 'test' not in sys.argv:
        print("{} cables created".format(cable_count))


def delete_interfaceconnection_content_type(apps, schema_editor):
    """
    Delete the ContentType for the InterfaceConnection model. (This is not done automatically upon model deletion.)
    """
    ContentType = apps.get_model('contenttypes', 'ContentType')
    InterfaceConnection = apps.get_model('dcim', 'InterfaceConnection')
    ContentType.objects.get_for_model(InterfaceConnection).delete()


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('circuits', '0006_terminations'),
        ('dcim', '0065_front_rear_ports'),
    ]

    operations = [

        # Create the Cable model
        migrations.CreateModel(
            name='Cable',
            options={'ordering': ['pk']},
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('termination_a_id', models.PositiveIntegerField()),
                ('termination_b_id', models.PositiveIntegerField()),
                ('type', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('status', models.BooleanField(default=True)),
                ('label', models.CharField(blank=True, max_length=100)),
                ('color', utilities.fields.ColorField(blank=True, max_length=6)),
                ('length', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('length_unit', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('_abs_length', models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True)),
                ('termination_a_type', models.ForeignKey(limit_choices_to={'model__in': ['consoleport', 'consoleserverport', 'interface', 'poweroutlet', 'powerport', 'frontport', 'rearport', 'circuittermination', 'powerfeed']}, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='contenttypes.ContentType')),
                ('termination_b_type', models.ForeignKey(limit_choices_to={'model__in': ['consoleport', 'consoleserverport', 'interface', 'poweroutlet', 'powerport', 'frontport', 'rearport', 'circuittermination', 'powerfeed']}, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='contenttypes.ContentType')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='cable',
            unique_together={('termination_b_type', 'termination_b_id'), ('termination_a_type', 'termination_a_id')},
        ),

        # Alter console port models
        migrations.RenameField(
            model_name='consoleport',
            old_name='cs_port',
            new_name='connected_endpoint'
        ),
        migrations.AlterField(
            model_name='consoleport',
            name='device',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='consoleports', to='dcim.Device'),
        ),
        migrations.AlterField(
            model_name='consoleport',
            name='connected_endpoint',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='connected_endpoint', to='dcim.ConsoleServerPort'),
        ),
        migrations.AlterField(
            model_name='consoleport',
            name='connection_status',
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name='consoleport',
            name='cable',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dcim.Cable'),
        ),
        migrations.AlterField(
            model_name='consoleserverport',
            name='device',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='consoleserverports', to='dcim.Device'),
        ),
        migrations.AddField(
            model_name='consoleserverport',
            name='cable',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dcim.Cable'),
        ),
        migrations.AddField(
            model_name='consoleserverport',
            name='connection_status',
            field=models.NullBooleanField(),
        ),

        # Alter power port models
        migrations.RenameField(
            model_name='powerport',
            old_name='power_outlet',
            new_name='connected_endpoint'
        ),
        migrations.AlterField(
            model_name='powerport',
            name='device',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='powerports', to='dcim.Device'),
        ),
        migrations.AlterField(
            model_name='powerport',
            name='connected_endpoint',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='connected_endpoint', to='dcim.PowerOutlet'),
        ),
        migrations.AlterField(
            model_name='powerport',
            name='connection_status',
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name='powerport',
            name='cable',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dcim.Cable'),
        ),
        migrations.AlterField(
            model_name='poweroutlet',
            name='device',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='poweroutlets', to='dcim.Device'),
        ),
        migrations.AddField(
            model_name='poweroutlet',
            name='cable',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dcim.Cable'),
        ),
        migrations.AddField(
            model_name='poweroutlet',
            name='connection_status',
            field=models.NullBooleanField(),
        ),

        # Alter the Interface model
        migrations.AddField(
            model_name='interface',
            name='_connected_circuittermination',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='circuits.CircuitTermination'),
        ),
        migrations.AddField(
            model_name='interface',
            name='_connected_interface',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dcim.Interface'),
        ),
        migrations.AddField(
            model_name='interface',
            name='connection_status',
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name='interface',
            name='cable',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dcim.Cable'),
        ),

        # Alter front/rear port models
        migrations.AddField(
            model_name='frontport',
            name='cable',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dcim.Cable'),
        ),
        migrations.AddField(
            model_name='rearport',
            name='cable',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dcim.Cable'),
        ),

        # Copy console/power/interface connections as Cables
        migrations.RunPython(console_connections_to_cables),
        migrations.RunPython(power_connections_to_cables),
        migrations.RunPython(interface_connections_to_cables),

        # Delete the InterfaceConnection model and its ContentType
        migrations.RunPython(delete_interfaceconnection_content_type),
        migrations.RemoveField(
            model_name='interfaceconnection',
            name='interface_a',
        ),
        migrations.RemoveField(
            model_name='interfaceconnection',
            name='interface_b',
        ),
        migrations.DeleteModel(
            name='InterfaceConnection',
        ),
    ]
