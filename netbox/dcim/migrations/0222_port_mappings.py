from itertools import islice

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


def chunked(iterable, size):
    """
    Yield successive chunks of a given size from an iterator.
    """
    iterator = iter(iterable)
    while chunk := list(islice(iterator, size)):
        yield chunk


def populate_port_template_mappings(apps, schema_editor):
    FrontPortTemplate = apps.get_model('dcim', 'FrontPortTemplate')
    PortTemplateMapping = apps.get_model('dcim', 'PortTemplateMapping')

    front_ports = FrontPortTemplate.objects.iterator(chunk_size=1000)

    def generate_copies():
        for front_port in front_ports:
            yield PortTemplateMapping(
                device_type_id=front_port.device_type_id,
                module_type_id=front_port.module_type_id,
                front_port_id=front_port.pk,
                front_port_position=1,
                rear_port_id=front_port.rear_port_id,
                rear_port_position=front_port.rear_port_position,
            )

    # Bulk insert in streaming batches
    for chunk in chunked(generate_copies(), 1000):
        PortTemplateMapping.objects.bulk_create(chunk, batch_size=1000)


def populate_port_mappings(apps, schema_editor):
    FrontPort = apps.get_model('dcim', 'FrontPort')
    PortMapping = apps.get_model('dcim', 'PortMapping')

    front_ports = FrontPort.objects.iterator(chunk_size=1000)

    def generate_copies():
        for front_port in front_ports:
            yield PortMapping(
                device_id=front_port.device_id,
                front_port_id=front_port.pk,
                front_port_position=1,
                rear_port_id=front_port.rear_port_id,
                rear_port_position=front_port.rear_port_position,
            )

    # Bulk insert in streaming batches
    for chunk in chunked(generate_copies(), 1000):
        PortMapping.objects.bulk_create(chunk, batch_size=1000)


class Migration(migrations.Migration):
    dependencies = [
        ('dcim', '0221_cable_connector_positions'),
    ]

    operations = [
        # Create PortTemplateMapping model (for DeviceTypes)
        migrations.CreateModel(
            name='PortTemplateMapping',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                (
                    'front_port_position',
                    models.PositiveSmallIntegerField(
                        default=1,
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(1024)
                        ]
                    )
                ),
                (
                    'rear_port_position',
                    models.PositiveSmallIntegerField(
                        default=1,
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(1024)
                        ]
                    )
                ),
                (
                    'device_type',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to='dcim.devicetype',
                        related_name='port_mappings',
                        blank=True,
                        null=True
                    )
                ),
                (
                    'module_type',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to='dcim.moduletype',
                        related_name='port_mappings',
                        blank=True,
                        null=True
                    )
                ),
                (
                    'front_port',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to='dcim.frontporttemplate',
                        related_name='mappings'
                    )
                ),
                (
                    'rear_port',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to='dcim.rearporttemplate',
                        related_name='mappings'
                    )
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name='porttemplatemapping',
            constraint=models.UniqueConstraint(
                fields=('front_port', 'front_port_position'),
                name='dcim_porttemplatemapping_unique_front_port_position'
            ),
        ),
        migrations.AddConstraint(
            model_name='porttemplatemapping',
            constraint=models.UniqueConstraint(
                fields=('rear_port', 'rear_port_position'),
                name='dcim_porttemplatemapping_unique_rear_port_position'
            ),
        ),

        # Create PortMapping model (for Devices)
        migrations.CreateModel(
            name='PortMapping',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                (
                    'front_port_position',
                    models.PositiveSmallIntegerField(
                        default=1,
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(1024)
                        ]
                    ),
                ),
                (
                    'rear_port_position',
                    models.PositiveSmallIntegerField(
                        default=1,
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(1024),
                        ]
                    ),
                ),
                (
                    'device',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to='dcim.device',
                        related_name='port_mappings'
                    )
                ),
                (
                    'front_port',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to='dcim.frontport',
                        related_name='mappings'
                    )
                ),
                (
                    'rear_port',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to='dcim.rearport',
                        related_name='mappings'
                    )
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name='portmapping',
            constraint=models.UniqueConstraint(
                fields=('front_port', 'front_port_position'),
                name='dcim_portmapping_unique_front_port_position'
            ),
        ),
        migrations.AddConstraint(
            model_name='portmapping',
            constraint=models.UniqueConstraint(
                fields=('rear_port', 'rear_port_position'),
                name='dcim_portmapping_unique_rear_port_position'
            ),
        ),

        # Data migration
        migrations.RunPython(
            code=populate_port_template_mappings,
            reverse_code=migrations.RunPython.noop
        ),
        migrations.RunPython(
            code=populate_port_mappings,
            reverse_code=migrations.RunPython.noop
        ),
    ]
