from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0135_location_tenant'),
    ]

    operations = [
        migrations.AddField(
            model_name='interface',
            name='rf_channel',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='interface',
            name='rf_channel_width',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
    ]
