from django.db import migrations, models


def copy_content_types(apps, schema_editor):
    CustomLink = apps.get_model('extras', 'CustomLink')

    for customlink in CustomLink.objects.all():
        customlink.content_types.set([customlink.content_type])


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('extras', '0079_scheduled_jobs'),
    ]

    operations = [
        migrations.AddField(
            model_name='customlink',
            name='content_types',
            field=models.ManyToManyField(related_name='custom_links', to='contenttypes.contenttype'),
        ),
        migrations.RunPython(
            code=copy_content_types,
            reverse_code=migrations.RunPython.noop
        ),
        migrations.RemoveField(
            model_name='customlink',
            name='content_type',
        ),
    ]
