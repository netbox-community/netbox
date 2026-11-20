from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_populate_job_execution_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='access',
            field=models.CharField(default='shared', max_length=30),
        ),
    ]
