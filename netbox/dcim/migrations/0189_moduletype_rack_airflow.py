from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0188_racktype'),
    ]

    operations = [
        migrations.AddField(
            model_name='moduletype',
            name='airflow',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='rack',
            name='airflow',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
