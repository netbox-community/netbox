from django.db import migrations, models


def set_null_values(apps, schema_editor):
    """
    Replace empty strings with null values.
    """
    WirelessLAN = apps.get_model('wireless', 'WirelessLAN')
    WirelessLink = apps.get_model('wireless', 'WirelessLink')

    WirelessLAN.objects.filter(auth_cipher='').update(auth_cipher=None)
    WirelessLAN.objects.filter(auth_type='').update(auth_type=None)
    WirelessLink.objects.filter(auth_cipher='').update(auth_cipher=None)
    WirelessLink.objects.filter(auth_type='').update(auth_type=None)
    WirelessLink.objects.filter(distance_unit='').update(distance_unit=None)


class Migration(migrations.Migration):
    dependencies = [
        ('wireless', '0009_wirelesslink_distance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wirelesslan',
            name='auth_cipher',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='wirelesslan',
            name='auth_type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='wirelesslink',
            name='auth_cipher',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='wirelesslink',
            name='auth_type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='wirelesslink',
            name='distance_unit',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.RunPython(code=set_null_values, reverse_code=migrations.RunPython.noop),
    ]
