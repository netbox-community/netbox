from django.db import migrations


def clear_secrets_changelog(apps, schema_editor):
    """
    Delete all ObjectChange records referencing a model within the old secrets app (pre-v3.0).
    """
    ContentType = apps.get_model('contenttypes', 'ContentType')
    ObjectChange = apps.get_model('extras', 'ObjectChange')

    content_type_ids = ContentType.objects.filter(app_label='secrets').values_list('id', flat=True)
    ObjectChange.objects.filter(changed_object_type__in=content_type_ids).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0061_extras_change_logging'),
    ]

    operations = [
        migrations.RunPython(
            code=clear_secrets_changelog,
            reverse_code=migrations.RunPython.noop
        ),
    ]
