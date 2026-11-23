from django.db import migrations
from django.db.models import Q

BATCH_SIZE = 5000


def populate_job_access(apps, schema_editor):
    """
    Assign the "object" access class to existing script and data source jobs (see ScriptJob and SyncDataSourceJob).
    Updates are performed in batches, as installations which retain job history indefinitely can accumulate a very
    large number of rows.
    """
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Job = apps.get_model('core', 'Job')

    object_types = ContentType.objects.filter(
        Q(app_label='extras', model='script') | Q(app_label='core', model='datasource')
    )
    queryset = Job.objects.filter(object_type__in=object_types, object_id__isnull=False, access='shared')

    last_pk = 0
    while True:
        pks = list(
            queryset.filter(pk__gt=last_pk).order_by('pk').values_list('pk', flat=True)[:BATCH_SIZE]
        )
        if not pks:
            break
        Job.objects.filter(pk__in=pks).update(access='object')
        last_pk = pks[-1]


class Migration(migrations.Migration):
    # Kept separate from the migration which adds the column and run without a wrapping transaction, so that each
    # batch commits independently (see 0026_populate_job_execution_time)
    atomic = False

    dependencies = [
        ('core', '0027_job_access'),
    ]

    operations = [
        migrations.RunPython(
            code=populate_job_access,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
