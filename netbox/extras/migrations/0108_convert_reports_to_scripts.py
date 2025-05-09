from django.db import migrations


def convert_reportmodule_jobs(apps, schema_editor):
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Job = apps.get_model('core', 'Job')
    db_alias = schema_editor.connection.alias

    # Convert all ReportModule jobs to ScriptModule jobs
    if reportmodule_ct := ContentType.objects.using(db_alias).filter(app_label='extras', model='reportmodule').first():
        scriptmodule_ct = ContentType.objects.using(db_alias).get(app_label='extras', model='scriptmodule')
        Job.objects.using(db_alias).filter(object_type_id=reportmodule_ct.id).update(object_type_id=scriptmodule_ct.id)


class Migration(migrations.Migration):
    dependencies = [
        ('extras', '0107_cachedvalue_extras_cachedvalue_object'),
    ]

    operations = [
        migrations.RunPython(code=convert_reportmodule_jobs, reverse_code=migrations.RunPython.noop),
        migrations.DeleteModel(
            name='Report',
        ),
    ]
