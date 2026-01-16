from django.db import migrations, models
from django.db.models import Q

import ipam.fields


def backfill_denormalized_fields(apps, schema_editor):
    Device = apps.get_model('dcim', 'Device')

    # TODO: Optimize for bulk operations
    for device in Device.objects.filter(
        Q(virtual_chassis__isnull=False) | Q(primary_ip4__isnull=False) | Q(primary_ip6__isnull=False)
    ):
        device._virtual_chassis_name = device.virtual_chassis.name if device.virtual_chassis else ''
        device._primary_ip4_address = device.primary_ip4.address if device.primary_ip4 else None
        device._primary_ip6_address = device.primary_ip6.address if device.primary_ip6 else None
        device.save()


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0225_gfk_indexes'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='_primary_ip4_address',
            field=ipam.fields.IPAddressField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='device',
            name='_primary_ip6_address',
            field=ipam.fields.IPAddressField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='device',
            name='_virtual_chassis_name',
            field=models.CharField(blank=True),
        ),
        migrations.RunPython(
            code=backfill_denormalized_fields,
            reverse_code=migrations.RunPython.noop
        ),
    ]
