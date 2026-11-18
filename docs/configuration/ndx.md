# NetBox Data Exchange Parameters

These parameters configure NetBox's integration with the [NetBox Data Exchange](../features/ndx.md) (NDX) catalog.

## NDX_API_TOKEN

Default: `None`

The API token used to authenticate to the NDX catalog. The NDX integration is enabled only when this parameter is set (and [`ISOLATED_DEPLOYMENT`](./system.md#isolated_deployment) is not enabled). The token's entitlement determines whether enrichment data is available.

If this parameter is not set, NetBox uses the `api_token` configured for the legacy NDX plugin under [`PLUGINS_CONFIG`](./plugins.md#plugins_config) (if any), and warns at startup. See [Migrating from the NDX Plugin](../features/ndx.md#migrating-from-the-ndx-plugin).

---

## NDX_API_URL

Default: `'https://netboxlabs.com/ndx/api/v1'`

The base URL of the NDX catalog API. This should be changed only when directed by NetBox Labs.

---

## NDX_IMPORT_IMAGES

Default: `True`

When enabled, front and rear images are downloaded and attached to device types imported from the catalog. An image which is already present (including one uploaded locally) is never replaced.

---

## NDX_SYNC_INTERVAL

Default: `1440` (24 hours)

The interval, in minutes, at which NetBox checks the catalog for updates to imported types. Set this to `0` to disable periodic checks. (Checks can still be run on demand.)
