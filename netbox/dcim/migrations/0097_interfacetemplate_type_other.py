from django.db import migrations


def interfacetemplate_type_to_slug(apps, schema_editor):
    InterfaceTemplate = apps.get_model('dcim', 'InterfaceTemplate')
    InterfaceTemplate.objects.filter(type=32767).update(type='other')


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0096_interface_ordering'),
    ]

    operations = [
        # Missed type "other" in the initial migration (see #3967)
        migrations.RunPython(
            code=interfacetemplate_type_to_slug
        ),
    ]
