# NetBox v4.5

## v4.5.3 (2026-02-17)

### Enhancements

* [#19129](https://github.com/netbox-community/netbox/issues/19129) - Improve display of multiple MAC addresses within interfaces table
* [#20981](https://github.com/netbox-community/netbox/issues/20981) - Enhance JSON rendering for custom validators and protection rules in config revision view
* [#21240](https://github.com/netbox-community/netbox/issues/21240) - Add support for configuring Redis `KWARGS` parameters
* [#21257](https://github.com/netbox-community/netbox/issues/21257) - `ContentTypeFilter` now accepts multiple values
* [#21266](https://github.com/netbox-community/netbox/issues/21266) - Add table columns representing installed devices to the device bays table
* [#21267](https://github.com/netbox-community/netbox/issues/21267) - Normalize device height formatting in rack units (display "0U")
* [#21268](https://github.com/netbox-community/netbox/issues/21268) - Add device type details panel to device view
* [#21337](https://github.com/netbox-community/netbox/issues/21337) - Show the assigned platform's parent on the virtual machine UI view

### Performance Improvements

* [#20211](https://github.com/netbox-community/netbox/issues/20211) - Use thumbnails for image attachment hover previews to improve page load performance
* [#21016](https://github.com/netbox-community/netbox/issues/21016) - Restore missing SQL indexes for MPTT fields
* [#21196](https://github.com/netbox-community/netbox/issues/21196) - `q` filter should match on primary IP only for IP address values when filtering devices/VMs
* [#21420](https://github.com/netbox-community/netbox/issues/21420) - Improve query performance of `ContentTypeFilter`
* [#21421](https://github.com/netbox-community/netbox/issues/21421) - Eliminate extraneous application of `DISTINCT` to queries for `MultipleChoiceFilter`

### Bug Fixes

* [#20435](https://github.com/netbox-community/netbox/issues/20435) - Fix navigation menu margin issue when scrollbar appears
* [#21127](https://github.com/netbox-community/netbox/issues/21127) - Ensure assigned cable paths are cleared when removing terminations from a cable
* [#21277](https://github.com/netbox-community/netbox/issues/21277) - Record pre-change snapshot when adding cluster members via UI
* [#21320](https://github.com/netbox-community/netbox/issues/21320) - Avoid validation failures when site or optional fields are missing during rack import
* [#21354](https://github.com/netbox-community/netbox/issues/21354) - Fix base URL in Swagger when `BASE_PATH` is set
* [#21358](https://github.com/netbox-community/netbox/issues/21358) - Token list in UI cannot be ordered by token value
* [#21371](https://github.com/netbox-community/netbox/issues/21371) - Fix `KeyError` exception when triggering a webhook from an event rule
* [#21375](https://github.com/netbox-community/netbox/issues/21375) - Address failure condition in `ipam.0070_vlangroup_vlan_id_ranges` migration
* [#21390](https://github.com/netbox-community/netbox/issues/21390) - Avoid creating "empty" changelog records for related objects when processing manyo-to-many relations
* [#21397](https://github.com/netbox-community/netbox/issues/21397) - Correct rendering of owner field in CircuitType edit form
* [#21412](https://github.com/netbox-community/netbox/issues/21412) - Avoid `AttributeError` exception on initialization when a plugin has local imports in `__init__.py`

---

## v4.5.2 (2026-02-03)

### Enhancements

* [#15801](https://github.com/netbox-community/netbox/issues/15801) - Add link peer and connection columns to the VLAN device interfaces table
* [#19221](https://github.com/netbox-community/netbox/issues/19221) - Truncate long image attachment filenames in the UI
* [#19869](https://github.com/netbox-community/netbox/issues/19869) - Display peer connections for LAG member interfaces
* [#20052](https://github.com/netbox-community/netbox/issues/20052) - Increase logging level of error message when a custom script fails to load
* [#20172](https://github.com/netbox-community/netbox/issues/20172) - Add `cabled` filter for interfaces in GraphQL API
* [#21081](https://github.com/netbox-community/netbox/issues/21081) - Add owner group table columns & filters across all supported object list views
* [#21088](https://github.com/netbox-community/netbox/issues/21088) - Add max depth and max length dropdowns for child prefix views
* [#21110](https://github.com/netbox-community/netbox/issues/21110) - Support cursor-based pagination in GraphQL API
* [#21201](https://github.com/netbox-community/netbox/issues/21201) - Pre-populate GenericForeignKey form fields when cloning
* [#21209](https://github.com/netbox-community/netbox/issues/21209) - Ignore case sensitivity for configuration parameters which specify an app label and model name
* [#21228](https://github.com/netbox-community/netbox/issues/21228) - Support image attachments for rack types
* [#21244](https://github.com/netbox-community/netbox/issues/21244) - Enable omitting specific fields from REST API responses with `?omit=` parameter

### Performance Improvements

* [#21249](https://github.com/netbox-community/netbox/issues/21249) - Avoid extraneous user query when no event rules are present
* [#21259](https://github.com/netbox-community/netbox/issues/21259) - Cache ObjectType lookups for the duration of a request
* [#21260](https://github.com/netbox-community/netbox/issues/21260) - Defer object serialization for events pipeline processing
* [#21263](https://github.com/netbox-community/netbox/issues/21263) - Prefetch related objects after creating/updating objects via REST API
* [#21300](https://github.com/netbox-community/netbox/issues/21300) - Cache custom field lookups for the duration of a request
* [#21302](https://github.com/netbox-community/netbox/issues/21302) - Avoid redundant uniqueness checks in ValidatedModelSerializer
* [#21303](https://github.com/netbox-community/netbox/issues/21303) - Cache post-change snapshot on each instance after serialization
* [#21327](https://github.com/netbox-community/netbox/issues/21327) - Always leverage `get_by_natural_key()` to resolve ContentTypes

### Bug Fixes

* [#20212](https://github.com/netbox-community/netbox/issues/20212) - Fix support for image attachment thumbnails when using S3 storage
* [#20383](https://github.com/netbox-community/netbox/issues/20383) - When editing a device, clearing the assigned unit should also clear the rack face selection
* [#20902](https://github.com/netbox-community/netbox/issues/20902) - Avoid `SyncError` exception when Git URL contains an embedded username
* [#20977](https://github.com/netbox-community/netbox/issues/20977) - "Run again" button should respect script variable defaults
* [#21115](https://github.com/netbox-community/netbox/issues/21115) - Include `attribute_data` in ModuleType YAML export
* [#21129](https://github.com/netbox-community/netbox/issues/21129) - Store queue name on the Job model to ensure deletion of associated RQ task when a non-default queue is used
* [#21168](https://github.com/netbox-community/netbox/issues/21168) - Fix Application Service cloning to preserve parent object
* [#21173](https://github.com/netbox-community/netbox/issues/21173) - Ensure all plugin menu items are registered regardless of initialization order
* [#21176](https://github.com/netbox-community/netbox/issues/21176) - Remove checkboxes from IP ranges in mixed-type tables
* [#21202](https://github.com/netbox-community/netbox/issues/21202) - Fix scoped form cloning clearing the `scope` field when `scope_type` changes
* [#21214](https://github.com/netbox-community/netbox/issues/21214) - Clean up AutoSyncRecord when detaching from DataSource
* [#21242](https://github.com/netbox-community/netbox/issues/21242) - Navigation menu items for authentication should not require `staff_only` permission
* [#21254](https://github.com/netbox-community/netbox/issues/21254) - Fix `AttributeError` exception when checking for latest release
* [#21262](https://github.com/netbox-community/netbox/issues/21262) - Assigned scope should be replicated when cloning a prefix
* [#21269](https://github.com/netbox-community/netbox/issues/21269) - Fix replication of front/rear port assignments from the module type when installing a module

---

## v4.5.1 (2026-01-20)

### Enhancements

* [#21018](https://github.com/netbox-community/netbox/issues/21018) - Enable filtering prefixes by location/site/site group/region directly via GraphQL API
* [#21142](https://github.com/netbox-community/netbox/issues/21142) - Enable filtering device components by site/location/rack directly via GraphQL API
* [#21144](https://github.com/netbox-community/netbox/issues/21144) - Enable specifying a prefix length for IP addresses when utilizing the `/api/ipam/prefixes/<id>/available-ips/` REST API endpoint
* [#21165](https://github.com/netbox-community/netbox/issues/21165) - VLAN selector should default to group (instead of site)
* [#21178](https://github.com/netbox-community/netbox/issues/21178) - Improve consistency of rack measurements in UI

### Bug Fixes

* [#19901](https://github.com/netbox-community/netbox/issues/19901) - Fix `RelatedObjectDoesNotExist` exception when importing modules into unnamed devices
* [#20239](https://github.com/netbox-community/netbox/issues/20239) - Prevent shared mutable state in PluginMenuItem & PluginMenuButton
* [#20933](https://github.com/netbox-community/netbox/issues/20933) - Fix writable `data_file` assignment for ConfigContext and ConfigContextProfile via the REST API
* [#21039](https://github.com/netbox-community/netbox/issues/21039) - Fix support for AVIF image uploads
* [#21050](https://github.com/netbox-community/netbox/issues/21050) - Clear device OOB IP assignments when reassigning IP addresses
* [#21051](https://github.com/netbox-community/netbox/issues/21051) - Remove irrelevant object types from permissions form
* [#21097](https://github.com/netbox-community/netbox/issues/21097) - Fix comparison lookups for ID filters in GraphQL API
* [#21102](https://github.com/netbox-community/netbox/issues/21102) - Fix GraphiQL explorer UI
* [#21117](https://github.com/netbox-community/netbox/issues/21117) - Avoid `ValueError` exception when `API_TOKEN_PEPPERS` is not defined
* [#21118](https://github.com/netbox-community/netbox/issues/21118) - Address performance issue when saving sites with many assigned objects
* [#21124](https://github.com/netbox-community/netbox/issues/21124) - Fix front/rear port mapping for module types
* [#21134](https://github.com/netbox-community/netbox/issues/21134) - Fix bulk renaming for module types
* [#21139](https://github.com/netbox-community/netbox/issues/21139) - Support `fields` parameter for job, object change, and object type REST API endpoints
* [#21140](https://github.com/netbox-community/netbox/issues/21140) - Restore translation for object attribute labels on several UI views
* [#21160](https://github.com/netbox-community/netbox/issues/21160) - Fix performance issue loading UI views caused by unintended `APISelect` choices resolution
* [#21166](https://github.com/netbox-community/netbox/issues/21166) - Fix support for 32-bit ASN filtering in GraphQL API
* [#21175](https://github.com/netbox-community/netbox/issues/21175) - Fix pending migrations warning when `DEFAULT_LANGUAGE` is set
* [#21181](https://github.com/netbox-community/netbox/issues/21181) - Handle `AuthenticationFailed` exception when using an invalid API token to fetch media files
* [#21213](https://github.com/netbox-community/netbox/issues/21213) - Tag weight field should be marked as required in UI forms
* [#21231](https://github.com/netbox-community/netbox/issues/21231) - Presence of object types table should be checked only during migration (performance improvement)

---

## v4.5.0 (2026-01-06)

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
