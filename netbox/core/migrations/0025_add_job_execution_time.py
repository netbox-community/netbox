from django.db import migrations, models
from django.db.models import DurationField, ExpressionWrapper, F

BATCH_SIZE = 5000


def populate_execution_time(apps, schema_editor):
    """
    Populate execution_time for existing jobs which have both a start and completion time recorded.
    Updates are performed in batches, as installations which retain job history indefinitely can
    accumulate a very large number of rows.
    """
    Job = apps.get_model("core", "Job")
    queryset = Job.objects.filter(started__isnull=False, completed__isnull=False)
    execution_time = ExpressionWrapper(F("completed") - F("started"), output_field=DurationField())

    last_pk = 0
    while True:
        pks = list(
            queryset.filter(pk__gt=last_pk).order_by("pk").values_list("pk", flat=True)[:BATCH_SIZE]
        )
        if not pks:
            break
        Job.objects.filter(pk__in=pks).update(execution_time=execution_time)
        last_pk = pks[-1]


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
