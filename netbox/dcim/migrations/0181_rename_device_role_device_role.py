from django.db import migrations


def update_table_configs(apps, schema_editor):
    """
    Replace the `device_role` column in DeviceTable configs with `role`.
    """
    UserConfig = apps.get_model('users', 'UserConfig')

    for table in ('DeviceTable', 'DeviceBayTable'):
        for config in UserConfig.objects.filter(**{f'data__tables__{table}__columns__contains': 'device_role'}):
            config.data['tables'][table]['columns'] = [
                'role' if x == 'device_role' else x
                for x in config.data['tables'][table]['columns']
            ]
            config.save()


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0180_powerfeed_tenant'),
    ]

    operations = [
        migrations.RenameField(
            model_name='device',
            old_name='device_role',
            new_name='role',
        ),
        migrations.RunPython(
            code=update_table_configs,
            reverse_code=migrations.RunPython.noop
        ),
    ]
