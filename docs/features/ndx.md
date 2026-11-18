# NetBox Data Exchange

!!! info "This feature was introduced in NetBox v4.8."

The [NetBox Data Exchange](https://netboxlabs.com/ndx/) (NDX) is a curated catalog of device types, module types, and rack types maintained by NetBox Labs. NetBox can browse the catalog and import its entries directly, removing the need to download and import YAML definitions manually. Each entry includes its full set of component templates (interfaces, power ports, console ports, module bays, etc.).

NDX integration requires an API token, which determines the data available. All tokens can browse and import the full catalog; [enrichment data](../models/ndx/enrichment.md) (lifecycle, thermal, environmental, and operational specifications, platform identification, protocol profiles, and data provenance) is included for entitled tokens only. See the [configuration documentation](../configuration/ndx.md) to enable the integration.

## Browsing the Catalog

Navigate to **Devices > Data Exchange > Catalog** to search and filter the catalog by vendor and entry type. Each entry's detail page summarizes its specifications, components, and the availability of enrichment data, and indicates whether it has already been imported.

## Importing Entries

Click **Import** on an entry, or select several entries in the catalog and click **Import Selected**. Importing an entry creates the corresponding NetBox object along with its component templates:

| Entry type  | NetBox object                          |
|-------------|----------------------------------------|
| Device type | [Device type](../models/dcim/devicetype.md) |
| Module type | [Module type](../models/dcim/moduletype.md) |
| Rack type   | [Rack type](../models/dcim/racktype.md) |

In the UI, a single entry is imported immediately, whereas multiple entries are imported by a [background job](./background-jobs.md). Entries can also be imported via the REST API (`POST /api/ndx/catalog/import/`), which imports up to five entries immediately and queues a background job for more (or when the `background` query parameter is set). Importing an entry requires permission to create (or, when re-importing, to modify) the object and its component templates. All changes are recorded in the [change log](./change-logging.md).

Data is validated just as for a YAML import. Should the catalog provide a value which this release of NetBox doesn't support (such as a newly introduced interface type), the value is replaced and a warning is reported: An unsupported choice for a required field (e.g. interface type) is replaced with "other," and any other unsupported value is left unchanged (or at its default value for a new object).

Where the catalog provides it, an imported type's end of life date is populated from the manufacturer's last date of support, and a pluggable transceiver is assigned the Transceiver [module type profile](../models/dcim/moduletypeprofile.md) with its attributes populated.

### Re-importing

Importing an entry which already exists updates the existing object in place. The object tracked by the entry's import record is updated even if it has since been renamed, as an existing object keeps its manufacturer, model, and slug. Component templates are matched by name: New components are added and existing components are updated, but no components are removed. Fields which the catalog doesn't provide (such as a device type's description) and existing front and rear images are left unchanged.

An entry is skipped if its corresponding object is already tracked by a different catalog entry.

## Tracking Imported Types

Each imported object is tracked by an [import record](../models/ndx/importrecord.md), listed under **Devices > Data Exchange > Imported Types**. A panel on each imported device, module, or rack type links to its import record and summarizes its enrichment data, and the device, module, and rack type lists offer an optional NDX column which marks imported types. Deleting an imported object deletes its import record.

## Keeping Imported Types Current

A system job periodically checks the catalog for changes (daily, by default) and flags imported types for which an update is available. Updates are never applied automatically. The **Sync Status** view shows the result of the most recent check, and offers to sync immediately or to re-import all types with updates available. A check can also be run (and updates optionally applied) using the [`ndx_sync`](../administration/management-commands.md#ndx_sync) management command.

## Network Requirements

NetBox web and worker processes require outbound HTTPS access to the NDX API (`netboxlabs.com` by default). Requests are routed via any configured [HTTP proxies](../configuration/system.md#http_proxies). The integration is disabled when [`ISOLATED_DEPLOYMENT`](../configuration/system.md#isolated_deployment) is enabled.

## Migrating from the NDX Plugin

The NDX plugin (`netbox_ndx`) is superseded by this integration. When upgrading, NetBox copies the plugin's data from its database tables; the plugin itself is not loaded, and its code is not needed.

!!! warning "Do not remove the plugin before upgrading"
    Don't follow the general instructions for [removing a plugin](../plugins/removal.md) until the upgrade has completed. If the plugin's database tables are dropped beforehand, its data is lost: The upgrade completes without error, but nothing is copied.

### Upgrade Checklist

1. **Upgrade the plugin.** On your current NetBox release, upgrade the plugin to v0.11.0 or later and run its database migrations. NetBox can import data only from this release or later, and the upgrade's database migrations will refuse to run otherwise.
2. **Merge or delete open branches.** If [netbox-branching](https://github.com/netboxlabs/netbox-branching) is installed, merge or delete all open branches. A branch may contain changes to the plugin's models, which can't be merged once the plugin has been removed.
3. **Upgrade NetBox.** Install the new release as described in the [upgrade guide](../installation/upgrading.md). Before running the upgrade script (or the `netbox upgrade` command), which applies the database migrations, update the configuration:
    * Remove `netbox_ndx` from [`PLUGINS`](../configuration/plugins.md#plugins) and its settings from `PLUGINS_CONFIG`. (NetBox ignores the plugin if it remains listed.)
    * Remove `netbox-ndx-plugin` from `local_requirements.txt` (if listed), so that it isn't reinstalled.
    * Set [`NDX_API_TOKEN`](../configuration/ndx.md#ndx_api_token) to the token previously configured as the plugin's `api_token`. See [Configuration](#configuration) below for the plugin's other settings.
4. **Apply database migrations and restart.** Complete the upgrade, which applies the database migrations, then restart the NetBox web and worker processes. The migrations:
    * Copy the plugin's import records, enrichment data, and provenance. (Tags, custom field data, and records whose objects no longer exist are not copied.)
    * Extend permissions which apply to the plugin's import record and enrichment models to their replacements. Permissions with constraints are skipped (each is reported in the migration output) and must be updated manually. Synchronizing with the catalog now requires the `sync` action on import records.
    * Delete the plugin's pending and scheduled background jobs.
5. **Verify the integration.** Under **Devices > Data Exchange**, confirm that previously imported types are listed under **Imported Types**. The worker runs a catalog sync when it starts: The **Sync Status** view shows its result, which confirms that the API token is valid. Update any saved filters, export templates, event rules, and other objects which reference the plugin's models.
6. **Remove the plugin.** Once satisfied with the upgrade, uninstall the plugin's Python package (which may be done at any time after step 1):

    ```no-highlight
    pip uninstall netbox-ndx-plugin
    ```

    Then, drop the plugin's database tables and delete its migration records. The tables must be dropped in a single statement, as they reference one another:

    ```no-highlight
    netbox=> DROP TABLE netbox_ndx_ndxenrichment, netbox_ndx_ndximportrecord, netbox_ndx_ndxprovenance, netbox_ndx_ndxsyncstatus;
    netbox=> DELETE FROM django_migrations WHERE app = 'netbox_ndx';
    ```

The upgrade copies the plugin's data rather than moving it. Until the plugin's tables are dropped, it remains possible to roll back to the previous NetBox release with the plugin; however, any changes made since the upgrade will not be reflected in the plugin's data.

!!! note
    The [change log](./change-logging.md) retains records of changes to the plugin's objects, although they can no longer be viewed once the plugin has been removed. The plugin's content types can't be removed while these records exist. They are harmless, and may be left in place.

### Configuration

The plugin's settings (under `PLUGINS_CONFIG['netbox_ndx']`) are not used, with one exception: If `NDX_API_TOKEN` is not set, NetBox uses the plugin's `api_token` (if configured) and warns at startup. Settings map to configuration parameters as follows:

| Plugin setting          | Replacement                                                                  |
|-------------------------|------------------------------------------------------------------------------|
| `api_token`             | [`NDX_API_TOKEN`](../configuration/ndx.md#ndx_api_token)                     |
| `api_url`               | [`NDX_API_URL`](../configuration/ndx.md#ndx_api_url)                         |
| `import_images`         | [`NDX_IMPORT_IMAGES`](../configuration/ndx.md#ndx_import_images)             |
| `sync_interval_minutes` | [`NDX_SYNC_INTERVAL`](../configuration/ndx.md#ndx_sync_interval)             |
| `auto_sync_enabled`     | Periodic checks are enabled by default; set `NDX_SYNC_INTERVAL` to `0` to disable them |
| `web_url`               | Removed (derived from `NDX_API_URL`)                                         |
| `data_url`              | Removed (images are retrieved from the NDX API)                              |
| `cache_timeout`, `error_cache_timeout` | Removed                                                       |
| `populate_core_end_of_life` | Removed (an end of life date set locally is never overwritten)           |

### REST API

The plugin's REST API endpoints have moved from `/api/plugins/ndx/` to `/api/ndx/`, and have changed as follows:

* Catalog entries are imported via `POST /api/ndx/catalog/import/` (formerly `/api/plugins/ndx/import/`). Each entry's result is reported with a `status` of `created`, `updated`, `skipped`, or `failed`, along with any errors and warnings.
* `GET /api/ndx/sync/` reports the status of catalog synchronization.
* Import records and enrichment can no longer be created or modified via the REST API. Import records may be deleted.
* Import records and enrichment no longer support tags or custom fields.

Import record fields have changed as follows:

| Plugin field                    | Replacement                                                                   |
|---------------------------------|-------------------------------------------------------------------------------|
| `ndx_manufacturer`, `ndx_model` | Removed (see the nested `object`)                                             |
| `ndx_vendor_slug`               | `vendor_slug`                                                                 |
| `ndx_version`                   | `checksum`                                                                    |
| `ndx_source`                    | `source` (represented as a value and label)                                   |
| `first_imported`, `last_synced` | `last_imported` (the time of the first import is recorded as `created`)       |
| —                               | `entry_type` (new)                                                            |
| `enrichment`                    | Now a brief representation; complete data is available at `/api/ndx/enrichments/` |

Enrichment fields have changed as follows:

| Plugin field         | Replacement                                    |
|----------------------|------------------------------------------------|
| `extensions_data`    | `extensions`                                   |
| `provenance_entries` | `provenance` (with `provenance_type` renamed to `type`) |
| —                    | `import_record` (new)                          |

Import records are filtered by `vendor_slug` and `source` (formerly `ndx_vendor_slug` and `ndx_source`), and the `q` filter searches NDX IDs and vendor slugs (but not manufacturer or model names).
