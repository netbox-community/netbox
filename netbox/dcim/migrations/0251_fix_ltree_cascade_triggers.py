"""Reinstall the ltree cascade triggers with a restore-safe WHEN clause.

The cascade triggers installed by 0242_ltree_paths compared two ltree values with
`IS DISTINCT FROM`, which resolves the `ltree = ltree` operator through search_path at
CREATE TRIGGER time. pg_dump emits `set_config('search_path', '', false)`, so restoring a
v4.7.0 dump could not create these triggers — and because psql does not stop on error by
default, the restore reported success with the triggers silently missing. See #23130.

Reinstalling covers both affected databases: one restored from such a dump (the triggers
are absent) and one upgraded in place (they exist with the old definition, which would
fail its own next restore). InstallLtreeTriggers drops before creating, so this applies
cleanly in either state.

This reinstalls triggers only, so it takes ACCESS EXCLUSIVE on each table for the DDL
itself and performs no table scan. Note that this is a stronger lock than the ROW
EXCLUSIVE held by 0242's backfill, and it blocks readers as well as writers: it is brief,
but on a busy table it queues behind any long-running query and holds everything behind
it for that query's duration.

It does not repair path/sort_path values which went stale while the triggers were
missing; see the v4.7.1 release notes for detection and repair.

Reversing this migration is a no-op. Reversing 0242_ltree_paths in turn drops these
triggers rather than recreating them, which is that migration's business; what matters
here is that undoing a corrective reinstall has no target state of its own, since the
definition it replaced is the broken one.
"""
from django.db import migrations

from utilities.ltree import ReinstallLtreeTriggers

# The tables carrying a sort_path column, maintained from `name`.
SORT_TABLES = (
    'dcim_region',
    'dcim_sitegroup',
    'dcim_location',
    'dcim_devicerole',
    'dcim_platform',
    'dcim_modulebay',
)


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0250_cooling_infrastructure'),
    ]

    operations = [
        *[ReinstallLtreeTriggers(t, name_column='name') for t in SORT_TABLES],
        ReinstallLtreeTriggers('dcim_inventoryitem'),
        ReinstallLtreeTriggers('dcim_inventoryitemtemplate'),
    ]
