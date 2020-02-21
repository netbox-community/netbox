import sys

from django.db import migrations, models


def update_related_powerports(apps, schema_editor):
    PowerPort = apps.get_model('dcim', 'PowerPort')
    PowerOutlet = apps.get_model('dcim', 'PowerOutlet')

    poweroutlet_count = PowerOutlet.objects.count()

    if 'test' not in sys.argv:
        print("\n    Updating power outlets with related power ports...")

    for i, poweroutlet in enumerate(PowerOutlet.objects.all(), start=1):
        if not i % 100 and 'test' not in sys.argv:
            print("      [{}/{}]".format(i, poweroutlet_count))

        # Copy of PowerOutlet.calculate_upstream_powerports
        upstream_powerports = PowerPort.objects.none()

        if poweroutlet.power_port:
            next_powerports = PowerPort.objects.filter(pk=poweroutlet.power_port.pk)

            while next_powerports.exists():
                upstream_powerports |= next_powerports

                # Prevent loops by excluding those already matched
                next_powerports = PowerPort.objects.exclude(
                    pk__in=upstream_powerports,
                ).filter(
                    poweroutlets__connected_endpoint__in=upstream_powerports,
                )

        # Copy of PowerOutlet.calculate_downstream_powerports
        downstream_powerports = PowerPort.objects.none()

        if hasattr(poweroutlet, 'connected_endpoint'):
            next_powerports = PowerPort.objects.filter(pk=poweroutlet.connected_endpoint.pk)

            while next_powerports.exists():
                downstream_powerports |= next_powerports

                # Prevent loops by excluding those already matched
                next_powerports = PowerPort.objects.exclude(
                    pk__in=downstream_powerports,
                ).filter(
                    _connected_poweroutlet__power_port__in=downstream_powerports,
                )

        poweroutlet._upstream_powerports.set(upstream_powerports)
        poweroutlet._downstream_powerports.set(downstream_powerports)


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0098_devicetype_images'),
    ]

    operations = [
        migrations.AddField(
            model_name='poweroutlet',
            name='_downstream_powerports',
            field=models.ManyToManyField(blank=True, related_name='_upstream_poweroutlets', to='dcim.PowerPort'),
        ),
        migrations.AddField(
            model_name='poweroutlet',
            name='_upstream_powerports',
            field=models.ManyToManyField(blank=True, related_name='_downstream_poweroutlets', to='dcim.PowerPort'),
        ),
        migrations.RunPython(
            code=update_related_powerports,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
