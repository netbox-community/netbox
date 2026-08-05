from django.db import migrations, models
from django.db.models import DurationField, ExpressionWrapper, F


def populate_execution_time(apps, schema_editor):
    """
    Populate execution_time for existing jobs which have both a start and completion time recorded.
    """
    Job = apps.get_model("core", "Job")
    Job.objects.filter(started__isnull=False, completed__isnull=False).update(
        execution_time=ExpressionWrapper(F("completed") - F("started"), output_field=DurationField())
    )


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
        migrations.RunPython(
            code=populate_execution_time,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
