from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0200_populate_mac_addresses'),
    ]

    operations = [
        migrations.AddField(
            model_name='poweroutlet',
            name='status',
            field=models.CharField(default='enabled', max_length=50),
        ),
    ]
