from django.db import migrations
import mptt
import mptt.managers


def rebuild_mptt(apps, schema_editor):
    manager = mptt.managers.TreeManager()
    DeviceRole = apps.get_model('dcim', 'DeviceRole')
    manager.model = DeviceRole
    mptt.register(DeviceRole)
    manager.contribute_to_class(DeviceRole, 'objects')
    manager.rebuild()


class Migration(migrations.Migration):
    dependencies = [
        ('dcim', '0203_device_role_nested'),
    ]

    operations = [
        migrations.RunPython(code=rebuild_mptt, reverse_code=migrations.RunPython.noop),
    ]
