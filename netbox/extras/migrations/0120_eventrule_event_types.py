import django.contrib.postgres.fields
from django.db import migrations, models

from core.events import *


def set_event_types(apps, schema_editor):
    EventRule = apps.get_model('extras', 'EventRule')
    event_rules = EventRule.objects.all()

    for event_rule in event_rules:
        event_rule.event_types = []
        if event_rule.type_create:
            event_rule.event_types.append(OBJECT_CREATED)
        if event_rule.type_update:
            event_rule.event_types.append(OBJECT_UPDATED)
        if event_rule.type_delete:
            event_rule.event_types.append(OBJECT_DELETED)
        if event_rule.type_job_start:
            event_rule.event_types.append(JOB_STARTED)
        if event_rule.type_job_end:
            # Map type_job_end to all job termination events
            event_rule.event_types.extend([JOB_COMPLETED, JOB_ERRORED, JOB_FAILED])

    EventRule.objects.bulk_update(event_rules, ['event_types'])


class Migration(migrations.Migration):
    dependencies = [
        ('extras', '0119_notifications'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventrule',
            name='event_types',
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=50), blank=True, null=True, size=None
            ),
        ),
        migrations.RunPython(code=set_event_types, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='eventrule',
            name='event_types',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=50), size=None),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name='eventrule',
            name='type_create',
        ),
        migrations.RemoveField(
            model_name='eventrule',
            name='type_delete',
        ),
        migrations.RemoveField(
            model_name='eventrule',
            name='type_job_end',
        ),
        migrations.RemoveField(
            model_name='eventrule',
            name='type_job_start',
        ),
        migrations.RemoveField(
            model_name='eventrule',
            name='type_update',
        ),
    ]
