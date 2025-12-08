## v4.5.0 (FUTURE)

### Breaking Changes

* Python 3.10 and 3.11 are no longer supported. NetBox now requires Python 3.12 or later.
* GraphQL API queries which filter by object IDs or enums must now specify a filter lookup similar to other fields. (For example, `id: 123` becomes `id: {exact: 123 }`.)
* Rendering a device or virtual machine configuration is now restricted to users with the `render_config` permission for the applicable object type.
* Retrieval of API token plaintexts is no longer supported. The `ALLOW_TOKEN_RETRIEVAL` config parameter has been removed.
* The owner of an API token can no longer be changed once it has been created.
* Config contexts now apply to all child platforms of a parent platform.
* The `/api/extras/object-types/` REST API endpoint has been removed. (Use `/api/core/object-types/` instead.)
* The `/api/dcim/cable-terminations/` REST API endpoint is now read-only. Cable terminations must be set on cables directly.
* The UI view dedicated to swaping A/Z circuit terminations has been removed.
* Webhooks no longer specify a `model` in payload data. (Reference `object_type` instead, which includes the parent app label.)
* The obsolete module `core.models.contenttypes` has been removed (replaced in v4.4 by `core.models.object_types`).
* The `load_yaml()` and `load_json()` utility methods have been removed from the base class for custom scripts.
* The experimental HTMX navigation feature has been removed.
* The obsolete field `is_staff` has been removed from the `User` model.

### New Features

#### Lookup Modifiers in Filter Forms ([#7604](https://github.com/netbox-community/netbox/issues/7604))

#### Improved API Authentication Tokens ([#20210](https://github.com/netbox-community/netbox/issues/20210))

#### Object Ownership ([#20304](https://github.com/netbox-community/netbox/issues/20304))

#### Advanced Port Mappings ([#20564](https://github.com/netbox-community/netbox/issues/20564))

#### Cable Profiles ([#20788](https://github.com/netbox-community/netbox/issues/20788))

### Enhancements

* [#16681](https://github.com/netbox-community/netbox/issues/16681) - Introduce a `render_config` permission, which is noq required to render a device or virtual machine configuration
* [#18658](https://github.com/netbox-community/netbox/issues/18658) - Add a `start_on_boot` choice field for virtual machines
* [#19095](https://github.com/netbox-community/netbox/issues/19095) - Add support for Python 3.13 and 3.14
* [#19338](https://github.com/netbox-community/netbox/issues/19338) - Enable filter lookups for object IDs and enums in GraphQL API queries
* [#19523](https://github.com/netbox-community/netbox/issues/19523) - Cache the number of instances for device, module, and rack types, and enable filtering by these counts
* [#20417](https://github.com/netbox-community/netbox/issues/20417) - Add an optional `color` field for device type power outlets
* [#20476](https://github.com/netbox-community/netbox/issues/20476) - Once provisioned, the owner of an API token cannot be changed
* [#20492](https://github.com/netbox-community/netbox/issues/20492) - Completely disabled the means to retrieve legacy API token plaintexts (removed the `ALLOW_TOKEN_RETRIEVAL` config parameter)
* [#20639](https://github.com/netbox-community/netbox/issues/20639) - Apply config contexts to devices/VMs assigned any child platform of the parent platform
* [#20834](https://github.com/netbox-community/netbox/issues/20834) - Add an `enabled` boolean field to API tokens
* [#20917](https://github.com/netbox-community/netbox/issues/20917) - Include usage reference on API token views
* [#20925](https://github.com/netbox-community/netbox/issues/20925) - Add optional `comments` field to all subclasses of `OrganizationalModel`
* [#20936](https://github.com/netbox-community/netbox/issues/20936) - Introduce the `/api/authentication-check/` REST API endpoint for validating authentication tokens

### Plugins

* [#13182](https://github.com/netbox-community/netbox/issues/13182) - Added `PrimaryModel`, `OrganizationalModel`, and `NestedGroupModel` to the plugins API, as well as their respective base classes for various resources

### Other Changes

* [#16137](https://github.com/netbox-community/netbox/issues/16137) - Remove the obsolete boolean field `is_staff` from the `User` model
* [#17571](https://github.com/netbox-community/netbox/issues/17571) - Remove the experimental HTMX navigation feature
* [#17936](https://github.com/netbox-community/netbox/issues/17936) - Introduce a dedicated `GFKSerializerField` for representing generic foreign keys in API serializers
* [#19889](https://github.com/netbox-community/netbox/issues/19889) - Drop support for Python 3.10 and 3.11
* [#19898](https://github.com/netbox-community/netbox/issues/19898) - Remove the obsolete REST API endpoint `/api/extras/object-types/`
* [#20088](https://github.com/netbox-community/netbox/issues/20088) - Remove the non-deterministic `model` key from webhook payload data
* [#20095](https://github.com/netbox-community/netbox/issues/20095) - Remove the obsolete module `core.models.contenttypes`
* [#20096](https://github.com/netbox-community/netbox/issues/20096) - Remove the `load_yaml()` and `load_json()` utility methods from the `BaseScript` class
* [#20204](https://github.com/netbox-community/netbox/issues/20204) - Started migrating object views from custom HTML templates to declarative layouts
* [#20617](https://github.com/netbox-community/netbox/issues/20617) - Introduce `BaseModel` as the global base class for models
* [#20683](https://github.com/netbox-community/netbox/issues/20683) - Remove the UI view dedicated to swaping A/Z circuit terminations
* [#20926](https://github.com/netbox-community/netbox/issues/20926) - Standardize naming of GraphQL filters

### REST API Changes

* Most objects now include an optional `owner` foreign key field.
* The `/api/dcim/cable-terminations` endpoint is now read-only.
* Introduced the `/api/authentication-check/` endpoint.
* `circuits.CircuitGroup`
  * Add optional `comments` field
* `circuits.CircuitType`
  * Add optional `comments` field
* `circuits.VirtualCircuitType`
  * Add optional `comments` field
* `dcim.Cable`
  * Add the optional `profile` choice field
* `dcim.InventoryItemRole`
  * Add optional `comments` field
* `dcim.Manufacturer`
  * Add optional `comments` field
* `dcim.ModuleType`
  * Add read-only `module_count` integer field
* `dcim.PowerOutletTemplate`
  * Add optional `color` field
* `dcim.RackRole`
  * Add optional `comments` field
* `dcim.RackType`
  * Add read-only `rack_count` integer field
* `ipam.ASNRange`
  * Add optional `comments` field
* `ipam.RIR`
  * Add optional `comments` field
* `ipam.Role`
  * Add optional `comments` field
* `ipam.VLANGroup`
  * Add optional `comments` field
* `tenancy.ContactRole`
  * Add optional `comments` field
* `users.Token`
  * Add `enabled` boolean field
* `virtualization.ClusterGroup`
  * Add optional `comments` field
* `virtualization.ClusterType`
  * Add optional `comments` field
* `virtualization.VirtualMachine`
  * Add optional `start_on_boot` choice field
* `vpn.TunnelGroup`
  * Add optional `comments` field
