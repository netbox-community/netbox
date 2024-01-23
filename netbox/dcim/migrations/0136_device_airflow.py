from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0135_tenancy_extensions'),
    ]

    operations = [
        migrations.AddField(
            model_name='devicetype',
            name='airflow',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='device',
            name='airflow',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
