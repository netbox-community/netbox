import uuid

import django.contrib.postgres.fields.jsonb
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import extras.utils
from extras.choices import JobResultStatusChoices


def convert_job_results(apps, schema_editor):
    """
    Convert ReportResult objects to JobResult objects
    """
    Report = apps.get_model('extras', 'Report')
    ReportResult = apps.get_model('extras', 'ReportResult')
    JobResult = apps.get_model('extras', 'JobResult')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    report_content_type = ContentType.objects.get_for_model(Report)

    job_results = []
    for report_result in ReportResult.objects.all():
        if report_result.failed:
            status = JobResultStatusChoices.STATUS_FAILED
        else:
            status = JobResultStatusChoices.STATUS_COMPLETED
        job_results.append(
            JobResult(
                name=report_result.report,
                obj_type=report_content_type,
                created=report_result.created,
                completed=report_result.created,
                user=report_result.user,
                status=status,
                data=report_result.data,
                job_id=uuid.uuid4()
            )
        )
    JobResult.objects.bulk_create(job_results)


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('extras', '0043_report'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('completed', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(default='pending', max_length=30)),
                ('data', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('job_id', models.UUIDField(unique=True)),
                ('obj_type', models.ForeignKey(limit_choices_to=extras.utils.FeatureQuery('job_results'), on_delete=django.db.models.deletion.CASCADE, related_name='job_results', to='contenttypes.ContentType')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['obj_type', 'name', '-created'],
            },
        ),
        migrations.RunPython(
            code=convert_job_results
        ),
        migrations.DeleteModel(
            name='ReportResult'
        )
    ]
