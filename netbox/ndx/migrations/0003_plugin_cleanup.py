import logging

from django.db import migrations

logger = logging.getLogger('netbox.ndx.migrations')

# Plugin models mapped to their replacements
PLUGIN_MODELS = {
    'ndximportrecord': 'importrecord',
    'ndxenrichment': 'enrichment',
}

# Names of the plugin's background jobs
PLUGIN_JOB_NAMES = ('NDX Sync Check', 'NDX Bulk Import')


def migrate_permissions(apps, schema_editor):
    """
    Extend permissions which apply to the plugin's models to the corresponding models. Permissions with constraints
    are skipped, as their constraints may not be valid for the new models.
    """
    ContentType = apps.get_model('contenttypes', 'ContentType')
    ObjectPermission = apps.get_model('users', 'ObjectPermission')
    db_alias = schema_editor.connection.alias

    for plugin_model, model in PLUGIN_MODELS.items():
        plugin_ct = ContentType.objects.using(db_alias).filter(app_label='netbox_ndx', model=plugin_model).first()
        if plugin_ct is None:
            continue
        permissions = ObjectPermission.objects.using(db_alias).filter(object_types=plugin_ct)
        if not permissions.exists():
            continue
        # The content type for a new model is not created until migrations have completed
        content_type, _ = ContentType.objects.using(db_alias).get_or_create(app_label='ndx', model=model)
        for permission in permissions:
            if permission.constraints:
                logger.warning(
                    f"Permission {permission.name} (ID {permission.pk}) has constraints and has not been extended to "
                    f"ndx.{model}; update it manually."
                )
                continue
            permission.object_types.add(content_type)


def delete_plugin_jobs(apps, schema_editor):
    """
    Delete the plugin's pending and scheduled jobs, which can no longer run.
    """
    Job = apps.get_model('core', 'Job')
    db_alias = schema_editor.connection.alias

    jobs = Job.objects.using(db_alias).filter(name__in=PLUGIN_JOB_NAMES, status__in=('pending', 'scheduled'))
    for job in jobs:
        # Cancel the queued RQ job (if reachable)
        try:
            import django_rq

            if rq_job := django_rq.get_queue(job.queue_name or 'default').fetch_job(str(job.job_id)):
                rq_job.delete()
        except Exception as e:
            logger.warning(f"Unable to remove RQ job {job.job_id}: {e}")
        job.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('core', '0026_populate_job_execution_time'),
        ('ndx', '0002_import_plugin_data'),
        ('users', '0016_default_ordering_indexes'),
    ]

    operations = [
        migrations.RunPython(
            code=migrate_permissions,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.RunPython(
            code=delete_plugin_jobs,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
