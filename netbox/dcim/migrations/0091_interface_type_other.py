from django.db import migrations


def interface_type_to_slug(apps, schema_editor):
    Interface = apps.get_model('dcim', 'Interface')
    Interface.objects.filter(type=32767).update(type='other')


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0090_cable_termination_models'),
    ]

    operations = [
        # Missed type "other" in the initial migration (see #3967)
        migrations.RunPython(
            code=interface_type_to_slug
        ),
    ]
