from django.db import migrations
from django.db.models import Q

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


def clear_stale_cable_profile_data(apps, schema_editor):
    """
    Clear cached cable connector and position data from endpoints which no longer have
    a cable attached. Earlier versions failed to clear these values when a profiled
    cable was deleted, causing subsequent validation of the endpoint to fail.
    """
    db_alias = schema_editor.connection.alias

    for model_name in CABLED_MODELS:
        model = apps.get_model('dcim', model_name)
        model.objects.using(db_alias).filter(
            Q(cable_connector__isnull=False) | Q(cable_positions__isnull=False),
            cable__isnull=True,
        ).update(
            cable_connector=None,
            cable_positions=None,
        )


class Migration(migrations.Migration):
    dependencies = [
        ('dcim', '0239_add_portmapping_objectchange'),
    ]

    operations = [
        migrations.RunPython(clear_stale_cable_profile_data, migrations.RunPython.noop),
    ]
