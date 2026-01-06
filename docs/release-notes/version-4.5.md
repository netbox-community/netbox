## v4.5.0 (FUTURE)

### Breaking Changes

* Python 3.10 and 3.11 are no longer supported. NetBox now requires Python 3.12, 3.13, or 3.14.
* GraphQL API queries which filter by object IDs or enums must now specify a filter lookup similar to other fields. For example, `id: 123` becomes `id: {exact: 123 }`.
* Rendering a device or virtual machine configuration is now restricted to users with the `render_config` permission for the applicable object type.
* Retrieval of API token plaintexts is no longer supported. The `ALLOW_TOKEN_RETRIEVAL` config parameter has been removed.
* API tokens can no longer be reassigned from one user to another.
* A config context assigned to a platform will now also apply to any children of that platform. (Although this is typically desired behavior, it may introduce unanticipated changes for existing deployments.)
* The `/api/dcim/cable-terminations/` REST API endpoint is now read-only. Cable terminations must be set on cables directly via the `/api/dcim/cables/` endpoint.
* The UI view dedicated to swapping A/Z circuit terminations has been removed.
* The experimental HTMX navigation feature has been removed.
* The obsolete boolean field `is_staff` has been removed from the `User` model.
* Removal of deprecated behavior
    * The `/api/extras/object-types/` REST API endpoint has been removed. (Use `/api/core/object-types/` instead.)
    * Webhooks no longer specify a `model` in payload data. (Reference `object_type` instead, which includes the parent app label.)
    * The obsolete module `core.models.contenttypes` has been removed (replaced in v4.4 by `core.models.object_types`).
    * The `load_yaml()` and `load_json()` utility methods have been removed from the base class for custom scripts.

### New Features

#### Lookup Modifiers in Filter Forms ([#7604](https://github.com/netbox-community/netbox/issues/7604))

Most object list filters within the UI have been extended to include optional lookup modifiers to support more complex queries. For instance, filters for numeric values now include a dropdown where a user can select "less than," "greater than," or "not" in addition to the default equivalency match. The specific modifiers available depend on the type of each filter. Plugins can register their own filtersets using the `register_filterset()` decorator to enable this new functionality.

(Note that this feature does not introduce any new filters. Rather, it makes available in the UI filters which already exist.)

#### Improved API Authentication Tokens ([#20210](https://github.com/netbox-community/netbox/issues/20210))

This release introduces a new version of API token (v2) which implements several security improvements. HMAC hashing with a cryptographic pepper is used to authenticate these tokens, obviating the need to store plaintexts. The new tokens also employ a non-sensitive key which can be shared to identify tokens without divulging their plaintexts. We've also adopted the standard "bearer" HTTP header format, as shown below.

```
# v1 token header
Authorization: Token <TOKEN>

# v2 token header
Authorization: Bearer nbt_<KEY>.<TOKEN>
```

Note that v2 token keys are prefixed with the fixed string `nbt_`, which can be used to aid in secret detection.

Backward compatibility with legacy (v1) tokens is retained in this release. However, users are strongly encouraged to begin using only v2 tokens, as support for legacy tokens will be removed in NetBox v4.7.

#### Object Ownership ([#20304](https://github.com/netbox-community/netbox/issues/20304))

An optional `owner` foreign key field has been added to most models. This enables the assignment of objects to a new Owner model, which represents a set of users and/or groups. Through this relationship, we can now convey ownership of objects within NetBox natively, without needing to rely on the assignment of tags or custom fields.

(Note that ownership differs significantly in function from tenancy. Ownership determines the parties responsible for the maintenance of an object, whereas as tenancy conveys an operational dependency.)

#### Advanced Port Mappings ([#20564](https://github.com/netbox-community/netbox/issues/20564))

The previous many-to-one mapping of front to rear ports has been expanded to support bidirectional mappings. The `rear_port` and `rear_port_position` fields on the FrontPort model have been replaced with an intermediary PortMapping model, which supports any number of assignments between front port/position pair and a rear port/position pair. This change unlocks the ability to model complex inline devices that swap individual fiber pairs between cables.

#### Cable Profiles ([#20788](https://github.com/netbox-community/netbox/issues/20788))

Cables can now be assigned profiles which determine how they are treated for path tracing. A profile indicates the number of discrete parallel channels or lanes carried by the cable among its endpoints. For example, a 1-to-4 breakout cable has four lanes, shared at one end via a common termination and split out at the other end to four separate terminations. Profiles, when assigned, enable NetBox to more accurately trace a specific connection within a cable, rather than the cable as a whole.

The assignment of cable profiles is optional: Cable tracing will continue to operate as before for cables with no profile assigned.

### Enhancements

* [#16681](https://github.com/netbox-community/netbox/issues/16681) - Introduce a `render_config` permission, which is now required to render a device or virtual machine configuration
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
* [#20929](https://github.com/netbox-community/netbox/issues/20929) - Require the `render_config` permission to view a rendered device/VM configuration in the UI
* [#20936](https://github.com/netbox-community/netbox/issues/20936) - Introduce the `/api/authentication-check/` REST API endpoint for validating authentication tokens
* [#20959](https://github.com/netbox-community/netbox/issues/20959) - Include a count of related module types for a manufacturer in the REST API

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
* [#20295](https://github.com/netbox-community/netbox/issues/20295) - Cable terminations may be modified via the REST API only by modifying the cable itself
* [#20617](https://github.com/netbox-community/netbox/issues/20617) - Introduce `BaseModel` as the global base class for models
* [#20683](https://github.com/netbox-community/netbox/issues/20683) - Remove the UI view dedicated to swapping A/Z circuit terminations
* [#20926](https://github.com/netbox-community/netbox/issues/20926) - Standardize naming of GraphQL filters

### REST API Changes

* Most objects now include an optional `owner` foreign key field.
* The `/api/dcim/cable-terminations` endpoint is now read-only.
* Introduced the `/api/authentication-check/` endpoint to test REST API credentials
* `circuits.CircuitGroup`
    * Add optional `comments` field
* `circuits.CircuitType`
    * Add optional `comments` field
* `circuits.VirtualCircuitType`
    * Add optional `comments` field
* `dcim.Cable`
    * Add the optional `profile` choice field
* `dcim.FrontPort`
    * Removed the `rear_port` and `rear_port_position` fields
    * Add the `positions` integer field
    * Add the `rear_ports` list for port mappings
* `dcim.InventoryItemRole`
    * Add optional `comments` field
* `dcim.Manufacturer`
    * Add optional `comments` field
    * Add read-only `moduletype_count` integer field
* `dcim.ModuleType`
    * Add read-only `module_count` integer field
* `dcim.PowerOutletTemplate`
    * Add optional `color` field
* `dcim.RackRole`
    * Add optional `comments` field
* `dcim.RackType`
    * Add read-only `rack_count` integer field
* `dcim.RearPort`
    * Add the `front_ports` list for port mappings
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
