"""Reinstall the ltree cascade trigger with a restore-safe WHEN clause.

The cascade trigger installed by 0021_ltree_paths compared two ltree values with
`IS DISTINCT FROM`, which resolves the `ltree = ltree` operator through search_path at
CREATE TRIGGER time. pg_dump emits `set_config('search_path', '', false)`, so restoring a
v4.7.0 dump could not create this trigger — and because psql does not stop on error by
default, the restore reported success with the trigger silently missing. See #23130.

Reinstalling covers both affected databases: one restored from such a dump (the trigger is
absent) and one upgraded in place (the trigger exists with the old definition, which would
fail its own next restore). InstallLtreeTriggers drops before creating, so this applies
cleanly in either state.

This does not repair path/sort_path values which went stale while the trigger was missing;
see the v4.7.1 release notes for detection and repair.

Reversing this migration is a no-op: the trigger it replaces belongs to 0021_ltree_paths,
which recreates it (from the corrected template) when reversed in turn.
"""
from django.db import migrations

from utilities.ltree import ReinstallLtreeTriggers

TABLE = 'wireless_wirelesslangroup'


class Migration(migrations.Migration):

    dependencies = [
        ('wireless', '0023_wirelesslangroup_drop_unique_constraint'),
    ]

    operations = [
        ReinstallLtreeTriggers(TABLE, name_column='name'),
    ]
