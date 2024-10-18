from django.db import migrations, models


def set_null_values(apps, schema_editor):
    """
    Replace empty strings with null values.
    """
    FHRPGroup = apps.get_model('ipam', 'FHRPGroup')
    IPAddress = apps.get_model('ipam', 'IPAddress')

    FHRPGroup.objects.filter(auth_type='').update(auth_type=None)
    IPAddress.objects.filter(role='').update(role=None)


class Migration(migrations.Migration):

    dependencies = [
        ('ipam', '0072_prefix_cached_relations'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fhrpgroup',
            name='auth_type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='ipaddress',
            name='role',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.RunPython(
            code=set_null_values,
            reverse_code=migrations.RunPython.noop
        ),
    ]
