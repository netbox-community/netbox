from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_job_log_entries'),
    ]

    operations = [
        migrations.AddField(
            model_name='objectchange',
            name='message',
            field=models.CharField(blank=True, editable=False, max_length=200),
        ),
    ]
