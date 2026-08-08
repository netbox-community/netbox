from django.db import migrations


def nullify_empty_cable_end(apps, schema_editor):
    """
    Replace empty strings with null values on cached cable end data. Earlier versions
    wrote an empty string when a cable termination was deleted, leaving disconnected
    terminations inconsistent with those which have never been cabled.
    """
    CircuitTermination = apps.get_model('circuits', 'CircuitTermination')
    db_alias = schema_editor.connection.alias

    CircuitTermination.objects.using(db_alias).filter(cable_end='').update(cable_end=None)


class Migration(migrations.Migration):
    dependencies = [
        ('circuits', '0058_clear_stale_cable_profile_data'),
    ]

    operations = [
        migrations.RunPython(nullify_empty_cable_end, migrations.RunPython.noop),
    ]
