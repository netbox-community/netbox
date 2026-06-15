from django.db import migrations, models

from netbox.config import ConfigItem

__all__ = (
    'InstallDenormalizationTrigger',
    'custom_deconstruct',
)


EXEMPT_ATTRS = (
    'choices',
    'help_text',
    'verbose_name',
)

_deconstruct = models.Field.deconstruct


def custom_deconstruct(field):
    """
    Imitate the behavior of the stock deconstruct() method, but ignore the field attributes listed above.
    """
    name, path, args, kwargs = _deconstruct(field)

    # Remove any ignored attributes
    for attr in EXEMPT_ATTRS:
        kwargs.pop(attr, None)

    # Ignore any field defaults which reference a ConfigItem
    kwargs = {
        k: v for k, v in kwargs.items() if not isinstance(v, ConfigItem)
    }

    return name, path, args, kwargs


class InstallDenormalizationTrigger(migrations.operations.base.Operation):
    """
    Install a PostgreSQL trigger that keeps denormalized columns on a dependent table in sync with their
    source object.

    When a row in `source_table` is updated, the trigger copies the values of the mapped source columns into
    the corresponding denormalized columns on every `dependent_table` row that references it via `fk_column`.
    This replaces the Python `post_save` handler formerly defined in `netbox.denormalized`.

    Args:
        dependent_table: The table carrying the denormalized columns (e.g. 'ipam_prefix').
        source_table: The table whose changes are propagated (e.g. 'dcim_site').
        fk_column: The column on `dependent_table` referencing `source_table` (e.g. '_site_id').
        mappings: A mapping of {dependent_column: source_column}, using actual database column names
            (e.g. {'_region_id': 'region_id', '_site_group_id': 'group_id'}).

    The trigger fires AFTER UPDATE of the source columns, and only when at least one of them actually changed.
    Like the handler it replaces, it does not fire on INSERT (a newly created source row has no dependents
    yet) and it does not cascade: updating the denormalized columns does not itself trigger further
    denormalization.
    """
    reversible = True

    def __init__(self, dependent_table, source_table, fk_column, mappings):
        self.dependent_table = dependent_table
        self.source_table = source_table
        self.fk_column = fk_column
        self.mappings = mappings

    @property
    def function_name(self):
        return f'{self.dependent_table}_denorm_from_{self.source_table}_fn'

    @property
    def trigger_name(self):
        return f'{self.dependent_table}_denorm_from_{self.source_table}'

    def state_forwards(self, app_label, state):
        # Triggers are not part of Django's model state.
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        source_columns = list(self.mappings.values())
        set_clause = ', '.join(f'"{dest}" = NEW."{src}"' for dest, src in self.mappings.items())
        update_of = ', '.join(f'"{col}"' for col in source_columns)
        when_clause = ' OR '.join(f'OLD."{col}" IS DISTINCT FROM NEW."{col}"' for col in source_columns)

        schema_editor.execute(f'''
            CREATE OR REPLACE FUNCTION "{self.function_name}"() RETURNS TRIGGER AS $$
            BEGIN
                UPDATE "{self.dependent_table}"
                   SET {set_clause}
                 WHERE "{self.fk_column}" = NEW.id;
                RETURN NULL;
            END
            $$ LANGUAGE plpgsql;
        ''')
        schema_editor.execute(f'''
            CREATE TRIGGER "{self.trigger_name}"
                AFTER UPDATE OF {update_of} ON "{self.source_table}"
                FOR EACH ROW WHEN ({when_clause})
                EXECUTE FUNCTION "{self.function_name}"();
        ''')

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        schema_editor.execute(f'DROP TRIGGER IF EXISTS "{self.trigger_name}" ON "{self.source_table}";')
        schema_editor.execute(f'DROP FUNCTION IF EXISTS "{self.function_name}"();')

    def describe(self):
        return f'Install denormalization trigger on {self.source_table} updating {self.dependent_table}'
