from django.db import migrations

CABLED_MODELS = (
    'ConsolePort',
    'ConsoleServerPort',
    'FrontPort',
    'Interface',
    'PowerFeed',
    'PowerOutlet',
    'PowerPort',
    'RearPort',
)


def nullify_empty_cable_end(apps, schema_editor):
    """
    Replace empty strings with null values on cached cable end data. Earlier versions
    wrote an empty string when a cable termination was deleted, leaving disconnected
    endpoints inconsistent with those which have never been cabled.
    """
    db_alias = schema_editor.connection.alias

    for model_name in CABLED_MODELS:
        model = apps.get_model('dcim', model_name)
        model.objects.using(db_alias).filter(cable_end='').update(cable_end=None)


class Migration(migrations.Migration):
    dependencies = [
        ('dcim', '0240_clear_stale_cable_profile_data'),
    ]

    operations = [
        migrations.RunPython(nullify_empty_cable_end, migrations.RunPython.noop),
    ]
