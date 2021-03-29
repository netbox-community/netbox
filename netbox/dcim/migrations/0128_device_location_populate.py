from django.db import migrations
from django.db.models import Subquery, OuterRef


def populate_device_location(apps, schema_editor):
    Device = apps.get_model('dcim', 'Device')
    Device.objects.filter(rack__isnull=False).update(
        location_id=Subquery(
            Device.objects.filter(pk=OuterRef('pk')).values('rack__location_id')[:1]
        )
    )


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0127_device_location'),
    ]

    operations = [
        migrations.RunPython(
            code=populate_device_location
        ),
    ]
