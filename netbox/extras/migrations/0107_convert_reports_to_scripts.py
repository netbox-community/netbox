from django.db import migrations


def convert_reportmodule_jobs(apps, schema_editor):
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Job = apps.get_model('core', 'Job')

    # Convert all ReportModule jobs to ScriptModule jobs
    if reportmodule_ct := ContentType.objects.filter(app_label='extras', model='reportmodule').first():
        scriptmodule_ct = ContentType.objects.get(app_label='extras', model='scriptmodule')
        Job.objects.filter(object_type_id=reportmodule_ct.id).update(object_type_id=scriptmodule_ct.id)


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0106_bookmark_user_cascade_deletion'),
    ]

    operations = [
        migrations.RunPython(
            code=convert_reportmodule_jobs,
            reverse_code=migrations.RunPython.noop
        ),
        migrations.DeleteModel(
            name='Report',
        ),
        migrations.DeleteModel(
            name='ReportModule',
        ),
    ]
