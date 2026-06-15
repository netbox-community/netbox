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

    When rows in `source_table` are updated, the trigger copies the values of the mapped source columns into
    the corresponding denormalized columns on every `dependent_table` row that references them via
    `fk_column`. This replaces the Python `post_save` handlers formerly defined in `netbox.denormalized` and
    `dcim.signals`.

    The trigger is statement-level (`FOR EACH STATEMENT`) and uses transition tables: a single bulk source
    update (`UPDATE ... WHERE ...`, `QuerySet.update()`, `bulk_update()`) fires the trigger once and is
    propagated with a single set-based UPDATE joining the changed rows, rather than once per affected row.

    Args:
        dependent_table: The table carrying the denormalized columns (e.g. 'ipam_prefix').
        source_table: The table whose changes are propagated (e.g. 'dcim_site').
        fk_column: The column on `dependent_table` referencing `source_table` (e.g. '_site_id').
        mappings: A mapping of {dependent_column: source_column}, using actual database column names
            (e.g. {'_region_id': 'region_id', '_site_group_id': 'group_id'}). Each is copied directly
            from the changed source row.
        related_mappings: An optional iterable of related-table lookups for columns that live one hop
            beyond `source_table`. Each entry is a dict with keys `table` (the related table), `source_fk`
            (a column on `source_table` referencing `related_table.id`), and `mappings`
            ({dependent_column: related_column}). Each is resolved by joining the related table once.
            This closes the chain gap when a denormalized column is derived through an intermediate object
            (e.g. a Location's Site change must refresh the dependent's region/site-group, not just its site).

    The trigger fires AFTER UPDATE of the watched source columns (the direct `mappings` sources plus each
    related `source_fk`), and only propagates to rows whose watched column(s) actually changed (the body
    joins the OLD/NEW transition tables and filters with IS DISTINCT FROM). It does not fire on INSERT (a
    newly created source row has no dependents yet) and it does not recurse: the dependent tables carry no
    triggers of their own.
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
        # `n`/`o` are the NEW/OLD transition tables (all rows changed by the source statement). Direct
        # mappings copy from the new source row; related mappings join the related table once.
        set_parts = [f'"{dest}" = n."{src}"' for dest, src in self.mappings.items()]
        watched = list(self.mappings.values())
        related_joins = []
        for i, rel in enumerate(self.related_mappings):
            alias = f'r{i}'
            related_joins.append(f'LEFT JOIN "{rel["table"]}" AS {alias} ON {alias}.id = n."{rel["source_fk"]}"')
            for dest, rel_col in rel['mappings'].items():
                set_parts.append(f'"{dest}" = {alias}."{rel_col}"')
            watched.append(rel['source_fk'])

        # Deduplicate watched columns while preserving order (a direct mapping and a related lookup may
        # both key off the same source column, e.g. site_id).
        watched_columns = list(dict.fromkeys(watched))

        set_clause = ', '.join(set_parts)
        update_of = ', '.join(f'"{col}"' for col in watched_columns)
        change_filter = ' OR '.join(f'o."{col}" IS DISTINCT FROM n."{col}"' for col in watched_columns)
        joins = ('\n              ' + '\n              '.join(related_joins)) if related_joins else ''

        schema_editor.execute(f'''
            CREATE OR REPLACE FUNCTION "{self.function_name}"() RETURNS TRIGGER AS $$
            BEGIN
                UPDATE "{self.dependent_table}" AS dep
                   SET {set_clause}
                  FROM new_rows AS n
                  JOIN old_rows AS o ON o.id = n.id{joins}
                 WHERE dep."{self.fk_column}" = n.id
                   AND ({change_filter});
                RETURN NULL;
            END
            $$ LANGUAGE plpgsql;
        ''')
        schema_editor.execute(f'''
            CREATE TRIGGER "{self.trigger_name}"
                AFTER UPDATE OF {update_of} ON "{self.source_table}"
                REFERENCING OLD TABLE AS old_rows NEW TABLE AS new_rows
                FOR EACH STATEMENT EXECUTE FUNCTION "{self.function_name}"();
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
