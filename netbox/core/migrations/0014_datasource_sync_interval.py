from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_job_data_encoder'),
    ]

    operations = [
        migrations.AddField(
            model_name='datasource',
            name='sync_interval',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
    ]
