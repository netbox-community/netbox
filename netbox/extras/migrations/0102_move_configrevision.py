from django.db import migrations


def update_content_type(apps, schema_editor):
    ContentType = apps.get_model('contenttypes', 'ContentType')

    # Delete the new ContentType effected by the introduction of core.ConfigRevision
    ContentType.objects.filter(app_label='core', model='configrevision').delete()

    # Update the app label of the original ContentType for extras.ConfigRevision to ensure any foreign key
    # references are preserved
    ContentType.objects.filter(app_label='extras', model='configrevision').update(app_label='core')


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0101_eventrule'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.DeleteModel(
                    name='ConfigRevision',
                ),
            ],
            database_operations=[
                migrations.AlterModelTable(
                    name='ConfigRevision',
                    table='core_configrevision',
                ),
            ],
        ),
        migrations.RunPython(
            code=update_content_type,
            reverse_code=migrations.RunPython.noop
        ),
    ]
