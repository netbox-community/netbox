from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_job_created_auto_now'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datasource',
            name='type',
            field=models.CharField(max_length=50),
        ),
    ]
