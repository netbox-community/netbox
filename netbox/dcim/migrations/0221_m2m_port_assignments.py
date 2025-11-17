import django.core.validators
import django.db.models.deletion
from django.db import migrations
from django.db import models
from itertools import islice


def chunked(iterable, size):
    """Yield successive chunks of a given size from an iterator."""
    iterator = iter(iterable)
    while chunk := list(islice(iterator, size)):
        yield chunk


def populate_port_assignments(apps, schema_editor):
    FrontPort = apps.get_model('dcim', 'FrontPort')
    PortAssignment = apps.get_model('dcim', 'PortAssignment')

    front_ports = FrontPort.objects.iterator(chunk_size=1000)

    def generate_copies():
        for front_port in front_ports:
            yield PortAssignment(
                front_port_id=front_port.pk,
                front_port_position=1,
                rear_port_id=front_port.rear_port_id,
                rear_port_position=front_port.rear_port_position,
            )

    # Bulk insert in streaming batches
    for chunk in chunked(generate_copies(), 1000):
        PortAssignment.objects.bulk_create(chunk, batch_size=1000)


class Migration(migrations.Migration):
    dependencies = [
        ('dcim', '0220_cable_position'),
    ]

    operations = [
        migrations.CreateModel(
            name='PortAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                (
                    'front_port_position',
                    models.PositiveSmallIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(1024),
                        ]
                    ),
                ),
                (
                    'rear_port_position',
                    models.PositiveSmallIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(1024),
                        ]
                    ),
                ),
                ('front_port', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dcim.frontport')),
                ('rear_port', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dcim.rearport')),
            ],
        ),
        migrations.AddField(
            model_name='frontport',
            name='rear_ports',
            field=models.ManyToManyField(related_name='front_ports', through='dcim.PortAssignment', to='dcim.rearport'),
        ),
        migrations.AddConstraint(
            model_name='portassignment',
            constraint=models.UniqueConstraint(
                fields=('front_port', 'front_port_position'), name='dcim_portassignment_unique_front_port_position'
            ),
        ),
        migrations.AddConstraint(
            model_name='portassignment',
            constraint=models.UniqueConstraint(
                fields=('rear_port', 'rear_port_position'), name='dcim_portassignment_unique_rear_port_position'
            ),
        ),
        migrations.RunPython(code=populate_port_assignments, reverse_code=migrations.RunPython.noop),
    ]
