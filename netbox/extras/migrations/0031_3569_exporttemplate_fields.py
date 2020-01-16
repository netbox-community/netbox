from django.db import migrations, models


EXPORTTEMPLATE_LANGUAGE_CHOICES = (
    (10, 'django'),
    (20, 'jinja2'),
)


def exporttemplate_language_to_slug(apps, schema_editor):
    ExportTemplate = apps.get_model('extras', 'ExportTemplate')
    for id, slug in EXPORTTEMPLATE_LANGUAGE_CHOICES:
        ExportTemplate.objects.filter(template_language=str(id)).update(template_language=slug)


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('extras', '0030_3569_objectchange_fields'),
    ]

    operations = [

        # ExportTemplate.template_language
        migrations.AlterField(
            model_name='exporttemplate',
            name='template_language',
            field=models.CharField(default='jinja2', max_length=50),
        ),
        migrations.RunPython(
            code=exporttemplate_language_to_slug
        ),

    ]
