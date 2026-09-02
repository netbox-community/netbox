# NetBox v4.7

## v4.7.0 (2026-09-02)

!!! warning "PostgreSQL 15 or Later Required"
    This release of NetBox drops support for PostgreSQL 14.

!!! warning "PostgreSQL ltree Extension Required"
    The PostgreSQL database must support the [ltree extension](https://www.postgresql.org/docs/current/ltree.html). This trusted module ships with PostgreSQL and does not require superuser permission to activate. NetBox will install it automatically during the upgrade if it is not already present. This requires the NetBox database user to hold the `CREATE` privilege on the database. Installations created using NetBox's standard PostgreSQL setup instructions already satisfy this requirement because the NetBox user owns the database. See [Verify Database Permissions](../installation/upgrading.md#verify-database-permissions) for details.

!!! warning "Redis 6.0 or Later Required"
    This release of NetBox drops support for Redis 5.x.

!!! warning "Extended Upgrade Duration"
    Two steps in this upgrade scale with the size of the database, and may take considerably longer than a typical NetBox upgrade.

    The migration which replaces `django-mptt` with `ltree` adds and alters columns on each hierarchical table before backfilling it in a single statement. The schema changes hold an `ACCESS EXCLUSIVE` lock, which blocks reads as well as writes for their duration; the backfill which follows locks every row it updates, blocking concurrent writes to those rows until it commits. On a large deployment this can last several minutes.

    The upgrade script then runs the `rebuild_config_context_cache` management command, which issues one `UPDATE` per device and virtual machine.

    Plan a maintenance window accordingly, and note that these migrations are not reversible in practice: Reversing them restores the MPTT columns but does not repopulate them.

### Breaking Changes

* PostgreSQL 14 is no longer supported. NetBox now requires PostgreSQL 15 or later: The upgrade script will abort when connected to an earlier release. (NetBox v4.6 reported this as a warning.)
* Redis 5.x is no longer supported. NetBox now requires Redis 6.0 or later.
* Selection and multiple selection custom field values are now returned as objects specifying both the raw value and its human-friendly label (e.g. `{"value": "datacenter", "label": "Data Center"}`) in both the REST and GraphQL APIs. These fields continue to accept the raw value on write.
* The `protocol` and `ports` fields on the `ipam.Service` and `ipam.ServiceTemplate` models have been replaced by a unified `port_mappings` field, which supports multiple protocols per service. The legacy fields are retained (as deprecated) in the REST and GraphQL APIs, but at the ORM level they are now read-only properties derived from `port_mappings`: Passing `protocol` or `ports` to the model raises a `TypeError`, and assigning to `service.ports` raises an `AttributeError`. This restriction applies only at the ORM level: The REST API continues to accept the legacy pair on write, translating it into `port_mappings`.
* Because `protocol` is now filtered against the `port_mappings` array rather than a dedicated model field, the character-based REST filter lookups previously generated for it (`protocol__ic`, `protocol__isw`, `protocol__empty`, etc.) are no longer available. The `port__empty` lookup has been removed as well.
* The GraphQL filters for `ipam.Service` and `ipam.ServiceTemplate` have changed shape: The nested `ports` integer lookup has been replaced by the flat `port`, `port__gt`, `port__gte`, `port__lt`, and `port__lte` parameters (each accepting a list of values), alongside the new `port_mappings` parameter. Additionally, the members of `ServiceProtocolEnum` have been renamed to drop a spurious `ROLE_` prefix (e.g. `ROLE_TCP` is now `TCP`).
* Config context data is now pre-rendered and cached for each device and virtual machine, and is always included in their REST API representations. The `DeviceWithConfigContextSerializer` and `VirtualMachineWithConfigContextSerializer` classes have been removed (merged into the base serializers), and the `?exclude=config_context` query parameter is now silently ignored.
* Failed bulk create and update operations via the REST API now return a structured response of the form `{"detail": ..., "errors": [{"index": N, "errors": {...}}]}`, correlating each error with the index of the offending object in the submitted list. (Bulk operations remain all-or-none.)
* API token plaintexts can no longer be specified by the client when creating a token via the REST API. The `token` field is now read-only, and any value supplied is ignored. (This restriction was already in effect in the web UI.)
* Executing a custom script via the REST API now requires that the calling token have its write ability enabled.
* The `username` argument has been removed from `extras.webhooks.send_webhook()` (the value remains available to webhook templates as `request.user`). Any webhook jobs still enqueued when the workers are restarted will fail with a `TypeError`, so the background queues should be allowed to drain before upgrading.
* Updates to the global search cache are now deferred to a background task. As a result, a newly created or modified object may not appear in search results for a brief period. (When no background worker is running, the index is updated synchronously as before.)
* Hierarchical models are now backed by a PostgreSQL `ltree` column rather than django-mptt. This covers the nested group models (Region, SiteGroup, Location, DeviceRole, Platform, TenantGroup, ContactGroup, WirelessLANGroup, etc.) as well as ModuleBay, InventoryItem, and InventoryItemTemplate. The `lft`, `rght`, `tree_id`, and `level` columns have been dropped from every migrated model: `level` remains available as a Python property, but can no longer be used in a queryset filter or `order_by()` clause. NetBox's `ltree` implementation deliberately covers only the subset of MPTT's API which NetBox itself uses (`get_ancestors()`, `get_descendants()`, `get_children()`, and `add_related_count()`); methods such as `get_root()`, `get_family()`, `is_leaf_node()`, `move_to()`, and `insert_at()` are no longer available. The MPTT-backed `NestedGroupModel` base class is retained for backward compatibility with plugins, but is deprecated: New code should use `NestedLtreeGroupModel` instead.
* django-tables2 has been upgraded to v3.0, which renames its `querystring` template tag to `querystring_replace` and removes the `RelatedLinkColumn` class.
* `social-auth-app-django` and `social-auth-core` have been upgraded to v6.0 and v5.1 respectively, each a major release. Deployments which employ single sign-on should test authentication against a non-production instance before upgrading.
* The `request` object passed to custom link templates is now a sanitized subset of the current request. Only the `id`, `path`, `path_info`, `method`, `GET`, and `user` attributes are available; cookies, headers, and session state are no longer accessible.
* URL custom field values are now validated against the [`ALLOWED_URL_SCHEMES`](../configuration/security.md#allowed_url_schemes) configuration parameter. A value entered without a scheme is assumed to use `https` and stored as an absolute URL.
* Webhooks now support a configurable timeout. If you have lowered `RQ_DEFAULT_TIMEOUT` to 60 seconds or less, you must also set [`WEBHOOK_DEFAULT_TIMEOUT`](../configuration/miscellaneous.md#webhook_default_timeout) to a lower value; NetBox will refuse to start otherwise.
* Specifying an email server under the [`EMAIL`](../configuration/system.md#email) configuration parameter is now mandatory in order to send mail: A deployment which does not define `EMAIL['SERVER']` will raise an `InvalidMailer` exception when attempting to send, rather than failing at the SMTP connection.
* NetBox now populates Django's `MAILERS` setting rather than the individual `EMAIL_*` settings which it supersedes. `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_SSL`, `EMAIL_USE_TLS`, `EMAIL_TIMEOUT`, `EMAIL_SSL_CERTFILE`, and `EMAIL_SSL_KEYFILE` are no longer defined, and `EMAIL_BACKEND` is no longer consulted. Plugin code which reads any of these, or which calls `django.core.mail.get_connection()` with an explicit backend (now raising a `RuntimeError`), must be updated. The `EMAIL` configuration parameter itself is unchanged.
* The upgrade script now runs the `rebuild_config_context_cache` management command to populate the new config context cache. This issues one `UPDATE` per device and virtual machine, and may extend the duration of the upgrade considerably for deployments with a large number of either. The command skips objects whose cache is already populated, so it is safe to interrupt and re-run; it may also be deferred until after NetBox is back online, as any object whose cache is empty falls back to rendering its config context on demand.
* Creating a custom field which has a default value, and deleting a custom field, are now deferred to a background job where the field's assigned object types hold more than [`BULK_UPDATE_CHUNK_SIZE`](../configuration/system.md#bulk_update_chunk_size) objects in total.
* The obsolete `populate_custom_field_defaults()` method has been removed from `CustomFieldsMixin`.
* `CustomField.objects.get_for_model()` and the `custom_fields` property of `CustomFieldsMixin` now return a list rather than a queryset, and `get_for_model()` returns only those fields which are active: Any whose stored data is being updated by a background job is omitted (see [field status](../customization/custom-fields.md#field-status)) unless selected via its `statuses` argument.
* Removal of deprecated behavior
    * The `housekeeping` management command has been removed. (Its constituent tasks are performed by the individual management commands introduced in NetBox v4.6.)
    * NetBox's custom `querystring` template tag has been removed in favor of Django's built-in tag of the same name. The two are not interchangeable: Django's tag reads the current request from the template context, so the `request` argument must be dropped (`{% querystring request page=1 %}` becomes `{% querystring page=1 %}`; passing `request` raises a `TemplateSyntaxError`). It also returns a bare `?` where NetBox's tag returned an empty string.
    * The legacy Sentry configuration parameters `SENTRY_DSN`, `SENTRY_SAMPLE_RATE`, `SENTRY_SEND_DEFAULT_PII`, and `SENTRY_TRACES_SAMPLE_RATE` have been removed. Use `SENTRY_CONFIG` instead.
    * The obsolete `DEFAULT_ACTION_PERMISSIONS` constant has been removed.
    * Support for legacy view action mappings has been dropped, and the `LEGACY_ACTIONS` constant has been removed.
    * Registered models are no longer populated under `registry['models']`. (Use `ObjectType.objects.public()` instead.) The `registry['denormalized_fields']` store has been removed as well.
    * The backward compatibility shims for `OptionalLimitOffsetPagination` (now `NetBoxPagination`), `ExpandableIPAddressField` (now `ExpandableIPNetworkField`), and `expand_ipaddress_pattern()` (now `expand_ipnetwork_pattern()`) have been removed.
    * The `request_id` and `username` keys have been removed from the context available to outgoing webhooks. Use `request.id` and `request.user` instead.
    * The automatic reverse relationship created by `OwnerMixin` (e.g. `site_set`) has been removed.

### New Features

#### Cooling Infrastructure Modeling ([#22447](https://github.com/netbox-community/netbox/issues/22447))

NetBox has long modeled power distribution end to end, but had no equivalent for cooling. This release introduces a cooling data model which deliberately mirrors the power model, so that the concepts and workflows feel familiar.

Two new top-level models parallel PowerPanel and PowerFeed: **CoolingSource** represents facility-level cooling plant (a chiller, cooling tower, dry cooler, or facility water system) scoped to a site or location, and **CoolingFeed** represents a coolant loop delivered from a source to a rack. Two new device components parallel PowerPort and PowerOutlet: **CoolingIntake** represents a coolant intake on a device (e.g. a server cold-plate connection or a CDU's facility water inlet), and **CoolingOutflow** represents a coolant outlet on a CDU or manifold which supplies downstream equipment. Each intake may reference the upstream outflow which serves it, and both components have corresponding device type templates. CDUs and manifolds are modeled as ordinary devices carrying these components.

Lightweight descriptive attributes have also been added for users who want to record cooling characteristics without modeling the full plumbing: a `cooling_method` field (air, liquid, hybrid, or immersion) on the Device, DeviceType, and ModuleType models, and `cooling_capability` (air-only, hybrid, or liquid-only) and `cooling_capacity` fields on the Rack and RackType models.

#### Channelized Subinterfaces ([#20972](https://github.com/netbox-community/netbox/issues/20972))

Channelized (breakout) interfaces can now be modeled natively. A new `channels` field on the Interface model indicates the number of physical channels into which an interface is divided, and each channel is represented by a subinterface of the new generic `channel` type, bound to its parent via the new `channel_id` field. A single cable terminates to the channelized parent interface, and NetBox traces a distinct cable path for each channel subinterface. Both fields are available on interface templates as well.

#### Multi-Protocol Application Services ([#20285](https://github.com/netbox-community/netbox/issues/20285))

Application services and service templates can now expose the same port on multiple protocols — for example, DNS listening on both `tcp/53` and `udp/53`. The single-protocol `protocol` and `ports` fields have been replaced by a unified `port_mappings` field, represented in the APIs as a flat list of `protocol/port` strings (e.g. `["tcp/80", "udp/53"]`). New `port_mappings`, `protocol`, and `port` filters are available in the UI and in both APIs, with the latter two correlated so that they must be satisfied by a single mapping.

#### Module Bay Types ([#19731](https://github.com/netbox-community/netbox/issues/19731))

A new ModuleBayType model has been introduced to convey which kinds of modules a module bay is able to accommodate (e.g. an SFP28 cage or a PCIe x16 slot). Bay types can be assigned to module bays, module bay templates, and module types; where both a bay and a module type declare bay types, NetBox validates that the two sets share at least one type in common before permitting installation. Bay types assigned to a module bay template propagate automatically to each instantiated module bay.

#### Relocating Installed Modules ([#15289](https://github.com/netbox-community/netbox/issues/15289))

An installed module can now be moved to a different module bay, including a bay on a different device, rather than having to be deleted and recreated. A move relocates the module's entire subtree — its components, its own module bays, and any child modules installed within them — and re-resolves any component names, labels, and positions derived from the module type's templates for the destination bay. Cross-device moves are permitted only where the moved components carry no active topology or device-scoped configuration.

#### Background Processing for REST API Requests ([#21992](https://github.com/netbox-community/netbox/issues/21992))

Bulk write operations via the REST API can now be processed as a background job rather than synchronously, avoiding proxy and gateway timeouts on large batches. Appending `?background=true` to a bulk write request enqueues a job and immediately returns an `HTTP 202 Accepted` response containing the job's ID and URL; the job's `data` field records the response the synchronous request would have returned. Note that validation is deferred to the worker, so a `202` response indicates only that the request was accepted, and the job's final status must be inspected to confirm the outcome.

#### Per-Object Errors for Bulk Operations ([#20054](https://github.com/netbox-community/netbox/issues/20054))

When a bulk create or update via the REST API fails validation, the response now identifies each offending object by its index within the submitted list, along with its specific field errors, rather than reporting only the first failure. This enables clients to correct and resubmit only the objects which actually failed.

#### Pre-Rendered Config Context Data ([#21025](https://github.com/netbox-community/netbox/issues/21025))

Rather than compiling config context data on demand from the full set of applicable ConfigContext instances, NetBox now pre-renders each device's and virtual machine's merged context data and caches it on the object itself. The cache is invalidated automatically whenever an upstream change is detected — a config context being created, modified, or deleted, or a change to an attribute which determines which contexts apply — and repopulated by a non-blocking background job. During the brief window between invalidation and re-render, reads fall back to the original on-demand rendering path, so the data returned is always correct rather than stale.

#### Snapshot-Aware Event Rule Conditions ([#18159](https://github.com/netbox-community/netbox/issues/18159))

Event rule conditions can now inspect the pre-change and post-change snapshots captured at the time of an event, rather than only the object's current data. New `changed` and `unchanged` operators compare an attribute's value across the two snapshots, and the `snapshots.prechange.<attr>` and `snapshots.postchange.<attr>` dot-path syntax exposes either snapshot to any standard operator. This makes it possible to express the long-requested "fire only when status changes _to_ active" rule, avoiding webhooks and scripts triggered by unrelated updates. A new `regex` operator has been added as well, and conditions which reference an attribute that cannot be resolved now fail closed and log an error rather than silently disabling the rule.

### Enhancements

* [#15165](https://github.com/netbox-community/netbox/issues/15165) - Re-render only the affected fieldset, rather than the entire form, when an HTMX-driven selection changes
* [#18645](https://github.com/netbox-community/netbox/issues/18645) - Support the bulk import of cables having multiple terminations per side
* [#18821](https://github.com/netbox-community/netbox/issues/18821) - Set or update an interface's primary MAC address in a single operation via the `mac_address` field
* [#20897](https://github.com/netbox-community/netbox/issues/20897) - Include the label alongside the value for selection custom fields in the REST & GraphQL APIs
* [#21367](https://github.com/netbox-community/netbox/issues/21367) - Add a read-only `is_primary` field to the MAC address REST API representation
* [#21712](https://github.com/netbox-community/netbox/issues/21712) - Support description annotations for static choice fields, and permit choices to be declared as dictionaries in `FIELD_CHOICES`
* [#22205](https://github.com/netbox-community/netbox/issues/22205) - Add an `end_of_life` date field to device types and module types to aid in hardware lifecycle planning
* [#22231](https://github.com/netbox-community/netbox/issues/22231) - Introduce a `nulls_first` parameter to control the placement of empty values when ordering by a custom field
* [#22409](https://github.com/netbox-community/netbox/issues/22409) - Disallow client-specified API token plaintexts via the REST API
* [#22411](https://github.com/netbox-community/netbox/issues/22411) - Enforce token write ability when executing a custom script via the REST API
* [#22441](https://github.com/netbox-community/netbox/issues/22441) - Record and display the execution time of each background job
* [#22446](https://github.com/netbox-community/netbox/issues/22446) - Introduce breadcrumbs support for declarative layouts
* [#22486](https://github.com/netbox-community/netbox/issues/22486) - Support a configurable timeout for webhooks, with a new `WEBHOOK_DEFAULT_TIMEOUT` configuration parameter
* [#22563](https://github.com/netbox-community/netbox/issues/22563) - Preserve the scroll position of the sidebar navigation when moving between pages
* [#22595](https://github.com/netbox-community/netbox/issues/22595) - Introduce the [`BULK_UPDATE_CHUNK_SIZE`](../configuration/system.md#bulk_update_chunk_size) configuration parameter to bound the number of rows affected by a single bulk `UPDATE` statement
* [#22604](https://github.com/netbox-community/netbox/issues/22604) - Document the experimental Python package installation and upgrade workflow
* [#22607](https://github.com/netbox-community/netbox/issues/22607) - Sanitize the HTTP request passed to the template context when rendering custom links
* [#22640](https://github.com/netbox-community/netbox/issues/22640) - Enforce `ALLOWED_URL_SCHEMES` when validating URL custom field values
* [#22757](https://github.com/netbox-community/netbox/issues/22757) - Support arbitrary help text on inline form fields
* [#22786](https://github.com/netbox-community/netbox/issues/22786) - Publish NetBox releases to the production Python Package Index (PyPI)
* [#22851](https://github.com/netbox-community/netbox/issues/22851) - Unpin `social-auth-core` to permit the installation of newer PyJWT versions
* [#23010](https://github.com/netbox-community/netbox/issues/23010) - Defer the provisioning of default and purging of stale custom field data to a background job

### Performance Improvements

* [#21326](https://github.com/netbox-community/netbox/issues/21326) - Defer updates to the global search cache to a background job, so that they no longer delay the response
* [#21355](https://github.com/netbox-community/netbox/issues/21355) - Maintain denormalized field data using PostgreSQL triggers rather than Python signal handlers
* [#21418](https://github.com/netbox-community/netbox/issues/21418) - Replace django-mptt with a PostgreSQL `ltree` implementation for hierarchical models

### Plugins

* [#19821](https://github.com/netbox-community/netbox/issues/19821) - Introduce `GenericObjectChoiceField` and `GenericObjectFormMixin` to represent a generic foreign key relation as a single form field
* [#22351](https://github.com/netbox-community/netbox/issues/22351) - Enable plugins to register custom Jinja filters and to inject context variables for config template rendering
* [#22592](https://github.com/netbox-community/netbox/issues/22592) - Enable plugins to add fields and filters to NetBox's existing core GraphQL types
* [#22770](https://github.com/netbox-community/netbox/issues/22770) - Enable plugins to register custom Event Rule action types by subclassing `EventRuleAction`

### Deprecations

* [#22288](https://github.com/netbox-community/netbox/issues/22288) - The `JINJA2_FILTERS` configuration parameter has been renamed to `JINJA_FILTERS`. The old name remains supported, but will be removed in NetBox v5.0.
* [#22593](https://github.com/netbox-community/netbox/issues/22593) - The `form_factor`, `width`, `outer_width`, `outer_height`, `outer_depth`, and `outer_unit` fields on the Rack model have been deprecated, and will be removed in NetBox v5.0. These values will instead be inferred from the rack's assigned rack type, which will become a mandatory assignment.
* [#22935](https://github.com/netbox-community/netbox/issues/22935) - The custom scripts functionality in core NetBox has been deprecated in favor of a dedicated plugin, and will be removed in NetBox v5.0.
* The `protocol` and `ports` fields on application services and service templates have been deprecated in favor of `port_mappings`, and will be removed from the REST & GraphQL APIs in NetBox v5.0.
* The MPTT-backed `NestedGroupModel` base class has been deprecated in favor of `NestedLtreeGroupModel`, and will be removed in a future release.

### Other Changes

* [#19091](https://github.com/netbox-community/netbox/issues/19091) - Remove NetBox's custom `querystring` template tag in favor of Django's built-in tag
* [#20546](https://github.com/netbox-community/netbox/issues/20546) - Raise the minimum required PostgreSQL version from 14 to 15
* [#20547](https://github.com/netbox-community/netbox/issues/20547) - Consolidate paired uniqueness constraints on nullable fields into single constraints using PostgreSQL's `NULLS NOT DISTINCT`
* [#21565](https://github.com/netbox-community/netbox/issues/21565) - Remove the obsolete `housekeeping` management command
* [#21883](https://github.com/netbox-community/netbox/issues/21883) - Drop support for the deprecated Sentry configuration parameters
* [#21886](https://github.com/netbox-community/netbox/issues/21886) - Remove the obsolete `DEFAULT_ACTION_PERMISSIONS` constant
* [#21888](https://github.com/netbox-community/netbox/issues/21888) - Remove support for legacy view actions
* [#21891](https://github.com/netbox-community/netbox/issues/21891) - Remove the `models` key from the application registry
* [#21902](https://github.com/netbox-community/netbox/issues/21902) - Upgrade django-tables2 to v3.0
* [#22052](https://github.com/netbox-community/netbox/issues/22052) - Remove the backward compatibility shim for `OptionalLimitOffsetPagination`
* [#22053](https://github.com/netbox-community/netbox/issues/22053) - Remove the backward compatibility shim for `ExpandableIPAddressField`
* [#22054](https://github.com/netbox-community/netbox/issues/22054) - Remove the backward compatibility shim for `expand_ipaddress_pattern()`
* [#22161](https://github.com/netbox-community/netbox/issues/22161) - Rename the filterset test mixin base classes to use a `*TestMixin` suffix
* [#22300](https://github.com/netbox-community/netbox/issues/22300) - Drop the automatic reverse relationship defined by `OwnerMixin`
* [#22393](https://github.com/netbox-community/netbox/issues/22393) - Drop support for Redis 5.x
* [#22438](https://github.com/netbox-community/netbox/issues/22438) - Omit the "2" suffix from the new Jinja plugin resources (`jinja_filters`, `get_jinja_context()`, `register_jinja_filters()`) for consistency with `JINJA_FILTERS`
* [#22485](https://github.com/netbox-community/netbox/issues/22485) - Move the search subsystem's signal wiring into `AppConfig.ready()` and break its import cycle
* [#22571](https://github.com/netbox-community/netbox/issues/22571) - Migrate from django-pglocks to django-pgware
* [#22615](https://github.com/netbox-community/netbox/issues/22615) - Remove the legacy `request_id` and `username` keys from the webhook context
* [#22942](https://github.com/netbox-community/netbox/issues/22942) - Upgrade to Django 6.1

### REST API Changes

* New features:
    * The `background=true` query parameter requests background processing of a bulk write operation, returning `HTTP 202 Accepted` with the enqueued job's ID and URL
    * Failed bulk create & update operations now return per-object errors correlated by index
    * Selection & multiple selection custom field values are now returned as `{value, label}` objects
    * Config context data is now always included for devices & virtual machines; the `exclude=config_context` query parameter is ignored
* New endpoints:
    * `GET/POST /api/dcim/cooling-feeds/`
    * `GET/PUT/PATCH/DELETE /api/dcim/cooling-feeds/<id>/`
    * `GET/POST /api/dcim/cooling-intakes/`
    * `GET/PUT/PATCH/DELETE /api/dcim/cooling-intakes/<id>/`
    * `GET/POST /api/dcim/cooling-intake-templates/`
    * `GET/PUT/PATCH/DELETE /api/dcim/cooling-intake-templates/<id>/`
    * `GET/POST /api/dcim/cooling-outflows/`
    * `GET/PUT/PATCH/DELETE /api/dcim/cooling-outflows/<id>/`
    * `GET/POST /api/dcim/cooling-outflow-templates/`
    * `GET/PUT/PATCH/DELETE /api/dcim/cooling-outflow-templates/<id>/`
    * `GET/POST /api/dcim/cooling-sources/`
    * `GET/PUT/PATCH/DELETE /api/dcim/cooling-sources/<id>/`
    * `GET/POST /api/dcim/module-bay-types/`
    * `GET/PUT/PATCH/DELETE /api/dcim/module-bay-types/<id>/`
* `core.Job`
    * Add read-only duration field `execution_time`
* `dcim.Device`
    * Add optional choice field `cooling_method`
    * Add read-only JSON field `config_context` (previously available only via `DeviceWithConfigContextSerializer`)
    * Annotate counts of assigned cooling intakes (`cooling_intake_count`) and outflows (`cooling_outflow_count`)
* `dcim.DeviceType`
    * Add optional choice field `cooling_method`
    * Add optional date field `end_of_life`
    * Annotate counts of cooling intake & outflow templates (`cooling_intake_template_count`, `cooling_outflow_template_count`)
* `dcim.Interface`
    * Add optional integer fields `channels` and `channel_id`
    * The `mac_address` field is now writable, and creates or updates the interface's primary MAC address
* `dcim.InterfaceTemplate`
    * Add optional integer fields `channels` and `channel_id`
    * Add optional foreign key field `parent`
* `dcim.MACAddress`
    * Add read-only boolean field `is_primary`
* `dcim.Module`
    * Add read-only boolean field `is_bay_compatible`
    * A module may now be relocated by patching its `module_bay` (the device is derived from the target bay)
* `dcim.ModuleBay`
    * Add many-to-many field `module_bay_types`
    * Add read-only boolean field `is_module_compatible`
* `dcim.ModuleBayTemplate`
    * Add many-to-many field `module_bay_types`
* `dcim.ModuleType`
    * Add optional choice field `cooling_method`
    * Add optional date field `end_of_life`
    * Add many-to-many field `module_bay_types`
    * Annotate counts of cooling intake & outflow templates (`cooling_intake_template_count`, `cooling_outflow_template_count`)
* `dcim.Rack`
    * Add optional choice field `cooling_capability`
    * Add optional decimal field `cooling_capacity`
* `dcim.RackType`
    * Add optional choice field `cooling_capability`
    * Add optional decimal field `cooling_capacity`
* `extras.CustomField`
    * Add boolean field `nulls_first`
    * Add read-only choice field `status`
* `extras.EventRule`
    * Add read-only boolean field `action_is_available`
    * The `action_object_type` field is now optional, and is no longer restricted to object types which support event rules
    * The choices available for `action_type` now include any action types registered by plugins
* `extras.Webhook`
    * Add optional integer field `timeout`
* `ipam.Service`
    * Add the `port_mappings` list field
    * The `protocol` and `ports` fields are deprecated; they are populated only for single-protocol services and return null otherwise. They remain writable: A request may specify either `port_mappings` or the legacy pair, but not both in conflict
    * The brief representation now includes `port_mappings` in place of `protocol` and `ports`
* `ipam.ServiceTemplate`
    * Add the `port_mappings` list field
    * The `protocol` and `ports` fields are deprecated; they are populated only for single-protocol services and return null otherwise. They remain writable: A request may specify either `port_mappings` or the legacy pair, but not both in conflict
    * The brief representation now includes `port_mappings` in place of `protocol` and `ports`
* `users.Token`
    * The `token` field is now read-only; a plaintext value can no longer be specified on creation
* `virtualization.VirtualMachine`
    * Add read-only JSON field `config_context` (previously available only via `VirtualMachineWithConfigContextSerializer`)
* `virtualization.VMInterface`
    * The `mac_address` field is now writable, and creates or updates the interface's primary MAC address

### GraphQL API Changes

* New query fields:
    * `cooling_feed` / `cooling_feed_list`
    * `cooling_intake` / `cooling_intake_list`
    * `cooling_intake_template` / `cooling_intake_template_list`
    * `cooling_outflow` / `cooling_outflow_list`
    * `cooling_outflow_template` / `cooling_outflow_template_list`
    * `cooling_source` / `cooling_source_list`
    * `module_bay_type` / `module_bay_type_list`
* Selection & multiple selection custom field values resolved via `custom_fields` are now returned as `{value, label}` objects
* The `ServiceFilter` and `ServiceTemplateFilter` types now expose the flat `port_mappings`, `protocol`, `port`, `port__gt`, `port__gte`, `port__lt`, and `port__lte` parameters in place of the previous `protocol` and nested `ports` lookups
* The members of `ServiceProtocolEnum` have been renamed from `ROLE_TCP`, `ROLE_UDP`, and `ROLE_SCTP` to `TCP`, `UDP`, and `SCTP`
* Interface & interface template types now expose the `channels` and `channel_id` fields
* Device, device type, module type, rack, and rack type types now expose their new cooling fields, and new enums have been introduced for the cooling choice sets
* The custom field type and filter now expose the new `status` field, with a corresponding `CustomFieldStatusEnum`
* Plugins may now extend core output types and filters (see the [plugin GraphQL API documentation](../plugins/development/graphql-api.md))
