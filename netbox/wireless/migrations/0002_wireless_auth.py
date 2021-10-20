from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wireless', '0001_wireless'),
    ]

    operations = [
        migrations.AddField(
            model_name='wirelesslan',
            name='auth_cipher',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='wirelesslan',
            name='auth_psk',
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name='wirelesslan',
            name='auth_type',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='wirelesslink',
            name='auth_cipher',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='wirelesslink',
            name='auth_psk',
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name='wirelesslink',
            name='auth_type',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
