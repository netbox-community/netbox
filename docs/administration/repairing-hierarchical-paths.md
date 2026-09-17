# Repairing Hierarchical Paths

NetBox stores each hierarchical object's position in its tree in a PostgreSQL [`ltree`](https://www.postgresql.org/docs/current/ltree.html) column named `path`, and most such models additionally maintain a `sort_path` used to order children by name. Both columns are maintained by database triggers which cascade a change to an object's name or parent down to its descendants.

This page covers detecting and repairing stale values in those columns. It applies to the nested group models (region, site group, location, device role, platform, tenant group, contact group, wireless LAN group) as well as module bays, inventory items, and inventory item templates.

## Databases Restored From a v4.7.0 Dump

In NetBox v4.7.0, the cascade triggers could not be recreated when restoring a `pg_dump` of the database, because `pg_dump` resets the `search_path` and the triggers' `WHEN` clause depended on it. As `psql` does not stop on error by default, such a restore reported success while leaving the database without those triggers. Renaming or moving an affected object therefore did not update its descendants, and the stored paths drifted out of sync with the actual hierarchy. This was corrected in NetBox v4.7.1 ([#23130](https://github.com/netbox-community/netbox/issues/23130)).

Upgrading to v4.7.1 or later reinstalls the triggers, so all subsequent changes are cascaded correctly. It does **not** repair values which have already gone stale — use the checks below to determine whether a repair is needed.

!!! tip
    To avoid this class of failure in general, always restore a dump with `psql -v ON_ERROR_STOP=1` (or `pg_restore --exit-on-error`), as described under [Replicating NetBox](./replicating-netbox.md#load-an-exported-database).

## Checking for Stale Paths

### After Upgrading

The [`rebuild_ltree_paths`](./management-commands.md#rebuild_ltree_paths) management command reports which models are affected without modifying anything or taking any locks:

```no-highlight
python netbox/manage.py rebuild_ltree_paths --check
```

### Before Upgrading

The same test can be run as SQL against a deployment which has not yet been upgraded. Substitute each hierarchical table in turn: `dcim_region`, `dcim_sitegroup`, `dcim_location`, `dcim_devicerole`, `dcim_platform`, `dcim_modulebay`, `dcim_inventoryitem`, `dcim_inventoryitemtemplate`, `tenancy_tenantgroup`, `tenancy_contactgroup`, and `wireless_wirelesslangroup`.

```no-highlight
SELECT count(*) FROM (
    SELECT id FROM dcim_region WHERE parent_id IS NULL
        AND path <> lpad(id::text, 19, '0')::ltree
    UNION ALL
    SELECT c.id FROM dcim_region c JOIN dcim_region p ON c.parent_id = p.id
        WHERE c.path <> p.path || lpad(c.id::text, 19, '0')::ltree
) x;
```

Treat any non-zero result as "this table needs rebuilding" rather than as a count of the damage: an object whose ancestor moved is reported, but its own descendants are consistent with it and so are not, even though they are equally stale.

### Checking `sort_path`

The nine tables which order their children by name additionally maintain a `sort_path`, which can go stale on a rename even when `path` is correct. Every table in the list above except `dcim_inventoryitem` and `dcim_inventoryitemtemplate` carries one, and is checked with:

```no-highlight
SELECT count(*) FROM (
    SELECT id FROM dcim_region WHERE parent_id IS NULL AND sort_path <> name
    UNION ALL
    SELECT c.id FROM dcim_region c JOIN dcim_region p ON c.parent_id = p.id
        WHERE c.sort_path <> p.sort_path || chr(9) || c.name
) x;
```

Stale `sort_path` values affect only the order in which objects are listed. A stale `path`, by contrast, misplaces an object within the hierarchy, so it can be omitted from its ancestor's list of descendants.

## Repairing

Repair an affected table with the [`rebuild_ltree_paths`](./management-commands.md#rebuild_ltree_paths) management command, naming the models the queries above flagged:

```no-highlight
python netbox/manage.py rebuild_ltree_paths dcim.region
```

!!! warning
    A rebuild rewrites every row of the named tables, locking those rows until it commits, so run it during a maintenance window.

Should the command report that a table contains rows unreachable from any root, the parent relationships themselves need correcting first: a rebuild walks down from the roots and would skip those rows.

## Plugins

Plugins which maintain their own `ltree` models via the `InstallLtreeTriggers` migration operation are affected in the same way, and their tables are not touched by NetBox's own corrective migrations. Where such a database was restored from a dump, the plugin's cascade triggers are missing entirely; where it was upgraded in place, they carry the old definition and will be lost by its next dump.

Either way, a new plugin migration applying `ReinstallLtreeTriggers` (passing the same `name_column` as the original) installs the corrected definitions. Use that operation rather than `InstallLtreeTriggers`: both drop each trigger before recreating it, so either works going forwards, but reversing the corrective migration should not undo the original installation. `InstallLtreeTriggers` reverses by dropping both triggers and their functions, which would leave the table with no path maintenance while the migration that first installed them remains applied. `ReinstallLtreeTriggers` reverses to a no-op instead.
