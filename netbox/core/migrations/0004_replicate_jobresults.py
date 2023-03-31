from django.db import migrations


def replicate_jobresults(apps, schema_editor):
    """
    Replicate existing JobResults to the new Jobs table before deleting the old JobResults table.
    """
    Job = apps.get_model('core', 'Job')
    JobResult = apps.get_model('extras', 'JobResult')

    jobs = []
    for job_result in JobResult.objects.order_by('pk').iterator(chunk_size=100):
        jobs.append(
            Job(
                object_type=job_result.obj_type,
                name=job_result.name,
                created=job_result.created,
                scheduled=job_result.scheduled,
                interval=job_result.interval,
                started=job_result.started,
                completed=job_result.completed,
                user=job_result.user,
                status=job_result.status,
                data=job_result.data,
                job_id=job_result.job_id,
            )
        )
        if len(jobs) == 100:
            Job.objects.bulk_create(jobs)
            jobs = []
    if jobs:
        Job.objects.bulk_create(jobs)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_job'),
    ]

    operations = [
        migrations.RunPython(
            code=replicate_jobresults,
            reverse_code=migrations.RunPython.noop
        ),
    ]
