import sys

from django.db import migrations, models


def calculate_downstream_powerports(apps, schema_editor):
    PowerPort = apps.get_model('dcim', 'PowerPort')
    PowerOutlet = apps.get_model('dcim', 'PowerOutlet')

    poweroutlet_count = PowerOutlet.objects.count()

    if 'test' not in sys.argv:
        print("\n    Calculating downstream power ports...")

    for i, poweroutlet in enumerate(PowerOutlet.objects.all(), start=1):
        if not i % 100 and 'test' not in sys.argv:
            print("      [{}/{}]".format(i, poweroutlet_count))

        downstream_powerports = PowerPort.objects.none()

        if hasattr(poweroutlet, 'connected_endpoint'):
            next_powerports = PowerPort.objects.filter(pk=poweroutlet.connected_endpoint.pk)

            while next_powerports:
                downstream_powerports |= next_powerports

                # Prevent loops by excluding those already matched
                next_powerports = PowerPort.objects.exclude(
                    pk__in=downstream_powerports
                ).filter(
                    _connected_poweroutlet__power_port__in=downstream_powerports
                )

        poweroutlet.downstream_powerports.set(downstream_powerports)


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0097_interfacetemplate_type_other'),
    ]

    operations = [
        migrations.AddField(
            model_name='poweroutlet',
            name='downstream_powerports',
            field=models.ManyToManyField(blank=True, related_name='upstream_poweroutlets', to='dcim.PowerPort'),
        ),
        migrations.RunPython(
            code=calculate_downstream_powerports,
            reverse_code=migrations.RunPython.noop
        ),
    ]
