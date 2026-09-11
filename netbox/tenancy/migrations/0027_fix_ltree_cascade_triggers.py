"""Reinstall the ltree cascade triggers with a restore-safe WHEN clause.

The cascade triggers installed by 0025_ltree_paths compared two ltree values with
`IS DISTINCT FROM`, which resolves the `ltree = ltree` operator through search_path at
CREATE TRIGGER time. pg_dump emits `set_config('search_path', '', false)`, so restoring a
v4.7.0 dump could not create these triggers — and because psql does not stop on error by
default, the restore reported success with the triggers silently missing. See #23130.

Reinstalling covers both affected databases: one restored from such a dump (the triggers
are absent) and one upgraded in place (they exist with the old definition, which would
fail its own next restore). InstallLtreeTriggers drops before creating, so this applies
cleanly in either state.

This does not repair path/sort_path values which went stale while the triggers were
missing; see the v4.7.1 release notes for detection and repair.

Reversing this migration is a no-op: the triggers it replaces belong to 0025_ltree_paths,
which recreates them (from the corrected template) when reversed in turn.
"""
from django.db import migrations

from utilities.ltree import ReinstallLtreeTriggers

TABLES = ('tenancy_tenantgroup', 'tenancy_contactgroup')


class Migration(migrations.Migration):

    dependencies = [
        ('tenancy', '0026_consolidate_unique_constraints'),
    ]

    operations = [
        *[ReinstallLtreeTriggers(t, name_column='name') for t in TABLES],
    ]
