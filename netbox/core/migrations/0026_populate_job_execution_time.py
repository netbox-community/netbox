from django.db import migrations
from django.db.models import DurationField, ExpressionWrapper, F

BATCH_SIZE = 5000


def populate_execution_time(apps, schema_editor):
    """
    Populate execution_time for existing jobs which have both a start and completion time recorded.
    Updates are performed in batches, as installations which retain job history indefinitely can
    accumulate a very large number of rows. Rows which already have a value are skipped, so that an
    interrupted run can simply be resumed.
    """
    Job = apps.get_model("core", "Job")
    queryset = Job.objects.filter(
        started__isnull=False, completed__isnull=False, execution_time__isnull=True
    )
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
    # The backfill is deliberately kept out of the migration which adds the column, so that the
    # ACCESS EXCLUSIVE lock taken by ALTER TABLE is not held for its duration. Running without a
    # wrapping transaction is what allows the batching above to bound the work actually held open.
    atomic = False

    dependencies = [
        ("core", "0025_add_job_execution_time"),
    ]

    operations = [
        migrations.RunPython(
            code=populate_execution_time,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
