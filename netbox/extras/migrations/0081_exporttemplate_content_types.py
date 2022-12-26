from django.db import migrations, models


def copy_content_types(apps, schema_editor):
    ExportTemplate = apps.get_model('extras', 'ExportTemplate')

    for et in ExportTemplate.objects.all():
        et.content_types.set([et.content_type])


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('extras', '0080_customlink_content_types'),
    ]

    operations = [
        migrations.AddField(
            model_name='exporttemplate',
            name='content_types',
            field=models.ManyToManyField(related_name='export_templates', to='contenttypes.contenttype'),
        ),
        migrations.RunPython(
            code=copy_content_types,
            reverse_code=migrations.RunPython.noop
        ),
        migrations.RemoveConstraint(
            model_name='exporttemplate',
            name='extras_exporttemplate_unique_content_type_name',
        ),
        migrations.RemoveField(
            model_name='exporttemplate',
            name='content_type',
        ),
        migrations.AlterModelOptions(
            name='exporttemplate',
            options={'ordering': ('name',)},
        ),
    ]
