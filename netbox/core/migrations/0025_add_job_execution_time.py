from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0024_job_notifications"),
    ]

    operations = [
        migrations.AddField(
            model_name="job",
            name="execution_time",
            field=models.DurationField(blank=True, editable=False, null=True),
        ),
    ]
