from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0214_platform_rebuild'),
    ]

    operations = [
        migrations.AddField(
            model_name='rackreservation',
            name='status',
            field=models.CharField(default='active', max_length=50),
        ),
    ]
