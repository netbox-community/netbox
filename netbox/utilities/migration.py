from django.db import migrations, models

from netbox.config import ConfigItem

__all__ = (
    'InstallDenormalizationTrigger',
    'cached_scope_triggers',
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
    This replaces the Python `post_save` handlers formerly defined in `netbox.denormalized` and `dcim.signals`.

    Args:
        dependent_table: The table carrying the denormalized columns (e.g. 'ipam_prefix').
        source_table: The table whose changes are propagated (e.g. 'dcim_site').
        fk_column: The column on `dependent_table` referencing `source_table` (e.g. '_site_id').
        mappings: A mapping of {dependent_column: source_column}, using actual database column names
            (e.g. {'_region_id': 'region_id', '_site_group_id': 'group_id'}). Each is copied directly:
            `dependent_column = NEW.source_column`.
        related_mappings: An optional iterable of related-table lookups for columns that live one hop
            beyond `source_table`. Each entry is a dict with keys `table` (the related table), `source_fk`
            (a column on `source_table` referencing `related_table.id`), and `mappings`
            ({dependent_column: related_column}). Each is resolved with a single multi-column subquery
            (`(cols) = (SELECT cols FROM table WHERE id = NEW.source_fk)`), so the related row is read once.
            This closes the chain gap when a denormalized column is derived through an intermediate object
            (e.g. a Location's Site change must refresh the dependent's region/site-group, not just its site).

    The trigger fires AFTER UPDATE of the watched source columns (the direct `mappings` sources plus each
    related `source_fk`), and only when at least one of them actually changed. It does not fire on INSERT (a
    newly created source row has no dependents yet) and it does not recurse: the dependent tables carry no
    triggers of their own.

    Note: this is a row-level trigger, so a bulk source update of N rows fires it N times. A statement-level
    trigger with transition tables would batch this, but PostgreSQL forbids transition tables on a trigger
    with an `UPDATE OF <columns>` list, and dropping that column list would fire the trigger on every source
    update (including unrelated columns) — a worse trade on hot-write tables like dcim_device.
    """
    reversible = True

    def __init__(self, dependent_table, source_table, fk_column, mappings, related_mappings=()):
        self.dependent_table = dependent_table
        self.source_table = source_table
        self.fk_column = fk_column
        self.mappings = mappings
        self.related_mappings = list(related_mappings)

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
        # Direct column copies from the changed source row.
        set_parts = [f'"{dest}" = NEW."{src}"' for dest, src in self.mappings.items()]
        watched = list(self.mappings.values())
        # One-hop lookups: a single multi-column subquery per related table reads its row only once.
        for rel in self.related_mappings:
            dests = ', '.join(f'"{d}"' for d in rel['mappings'].keys())
            cols = ', '.join(f'"{c}"' for c in rel['mappings'].values())
            set_parts.append(f'({dests}) = (SELECT {cols} FROM "{rel["table"]}" WHERE id = NEW."{rel["source_fk"]}")')
            watched.append(rel['source_fk'])

        # Deduplicate watched columns while preserving order (a direct mapping and a related lookup may
        # both key off the same source column, e.g. site_id).
        watched_columns = list(dict.fromkeys(watched))

        set_clause = ', '.join(set_parts)
        update_of = ', '.join(f'"{col}"' for col in watched_columns)
        when_clause = ' OR '.join(f'OLD."{col}" IS DISTINCT FROM NEW."{col}"' for col in watched_columns)

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


# Site/region/site-group lookup shared by every CachedScopeMixin-style dependent (see cached_scope_triggers).
SITE_SCOPE_RELATED_MAPPINGS = (
    {
        'table': 'dcim_site',
        'source_fk': 'site_id',
        'mappings': {'_region_id': 'region_id', '_site_group_id': 'group_id'},
    },
)


def cached_scope_triggers(dependent_table):
    """
    Return the Site + Location `InstallDenormalizationTrigger` pair for a dependent table carrying the
    standard cached-scope columns (_site/_location/_region/_site_group) — i.e. any CachedScopeMixin model
    (Prefix, Cluster, WirelessLAN) plus CircuitTermination, which share the same denormalization shape.

    Region- and SiteGroup-scoped rows need no trigger: their cached FK is the scoped object itself and
    never changes underneath them. So two triggers fully cover the cache:
      - dcim_site: region/group changed  -> refresh _region/_site_group on rows scoped to that site
      - dcim_location: site changed       -> refresh _site (and the new site's region/group)
    """
    return [
        InstallDenormalizationTrigger(
            dependent_table=dependent_table,
            source_table='dcim_site',
            fk_column='_site_id',
            mappings={'_region_id': 'region_id', '_site_group_id': 'group_id'},
        ),
        InstallDenormalizationTrigger(
            dependent_table=dependent_table,
            source_table='dcim_location',
            fk_column='_location_id',
            mappings={'_site_id': 'site_id'},
            related_mappings=SITE_SCOPE_RELATED_MAPPINGS,
        ),
    ]
