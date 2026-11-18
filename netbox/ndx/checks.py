from django.core.checks import Error, Tags, register
from django.db import connections
from django.db.migrations.recorder import MigrationRecorder

__all__ = (
    'check_plugin_version',
)

PLUGIN_IMPORT_RECORD_TABLE = 'netbox_ndx_ndximportrecord'

# The last migration of the earliest plugin release (v0.11.0) whose data can be imported
PLUGIN_MIN_MIGRATION = ('netbox_ndx', '0005_ndxprovenance_source_charfield')


@register(Tags.database)
def check_plugin_version(app_configs, databases=None, **kwargs):
    """
    Ensure that data left by the netbox_ndx plugin can be imported, by requiring that the plugin was upgraded to its
    minimum supported release beforehand. Evaluated by the migrate command before any migrations are applied.
    """
    errors = []
    for alias in databases or ():
        connection = connections[alias]
        if PLUGIN_IMPORT_RECORD_TABLE not in connection.introspection.table_names():
            continue
        applied = MigrationRecorder(connection).applied_migrations()
        if ('ndx', '0002_import_plugin_data') in applied or PLUGIN_MIN_MIGRATION in applied:
            continue
        errors.append(Error(
            "The netbox_ndx plugin must be upgraded to v0.11.0 or later before upgrading NetBox.",
            hint=(
                "Reinstall the previous NetBox release, upgrade the plugin to v0.11.0 or later, and run its "
                "migrations. Then upgrade NetBox."
            ),
            id='ndx.E001',
        ))
    return errors
