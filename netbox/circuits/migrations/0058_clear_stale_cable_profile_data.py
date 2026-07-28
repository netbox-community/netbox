from django.db import migrations
from django.db.models import Q


def clear_stale_cable_profile_data(apps, schema_editor):
    """
    Clear cached cable connector and position data from circuit terminations which no
    longer have a cable attached. Earlier versions failed to clear these values when a
    profiled cable was deleted, causing subsequent validation to fail.
    """
    CircuitTermination = apps.get_model('circuits', 'CircuitTermination')
    db_alias = schema_editor.connection.alias

    CircuitTermination.objects.using(db_alias).filter(
        Q(cable_connector__isnull=False) | Q(cable_positions__isnull=False),
        cable__isnull=True,
    ).update(
        cable_connector=None,
        cable_positions=None,
    )


class Migration(migrations.Migration):
    dependencies = [
        ('circuits', '0057_default_ordering_indexes'),
    ]

    operations = [
        migrations.RunPython(clear_stale_cable_profile_data, migrations.RunPython.noop),
    ]
