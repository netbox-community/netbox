## v4.3.0-beta2 (2025-04-23)

### Breaking Changes

* The GraphQL API Now uses an advanced syntax for filtering, to enable e.g. logical AND/OR filtering and custom field lookups.
* PostgreSQL 13 is no longer supported. NetBox v4.3 requires PostgreSQL 14.0 or later.
* The `ALLOW_TOKEN_RETRIEVAL` configuration parameter now defaults to False.
* The `device` and `virtual_machine` foreign keys on the Service model have been replaced with a generic `parent` relationship to support the assignment of services to FHRP groups as well.
* The `group` foreign key on the Contact model has been replaced with a many-to-many `groups` field.
* PluginTemplateExtension no longer supports registration via the singular `model` attribute (use `models` instead).
* The legacy staged changes functionality has been removed.

### New Features

#### Module Type Profiles & Custom Attributes ([#19002](https://github.com/netbox-community/netbox/issues/19002))

The new [module type profile](../models/dcim/moduletypeprofile.md) model enables users to declare custom profiles for module types, with the ability to define custom attributes for each profile according to its functional role. For example, a CPU module type might declare architecture and clock speed attributes; a hard disk profile might declare attributes for type and speed.

Attributes can be declared on each profile using [JSON schema](https://json-schema.org/), which allows for attributes to be declared as strings (text), integers, decimals, booleans, or choice fields. Profile attributes render as individual form fields when modifying a module type. Several profiles have been included by default to serve as examples, however these may be modified or removed.

#### Reusable Table Configurations ([#14591](https://github.com/netbox-community/netbox/issues/14591))

After modifying the displayed columns and/or ordering for a specific object table in the user interface, users now have the option to save that configuration so that it can be reused in the future. Similar to saved filters, table configs can be shared with other users to easily replicate table layouts crafted to serve specific use cases.

#### Option to Treat IP Ranges as Fully Populated ([#9763](https://github.com/netbox-community/netbox/issues/9763))

A new `mark_populated` boolean field has been added to the IPRange model. If set to true, NetBox will consider the IP range to be fully populated, and will not permit the creation of individual IP addresses within the range. For example, you might defer the management of an IP range to an external DHCP server, and wish for NetBox to treat the range as a opaque monolithic block for planning and allocation purposes.

#### Hierarchical Device Roles ([#18245](https://github.com/netbox-community/netbox/issues/18245))

Device roles can now be arranged hierarchically, with one role optionally serving as a parent to one or more child roles. For example, you might wish to create a generic "Server" role for devices with "Application Server" and "Database Server" roles beneath it. A device could then be assigned to any of these three roles.

#### Periodic Synchronization of Data Sources ([#18287](https://github.com/netbox-community/netbox/issues/18287))

Data sources can now be configured to synchronize automatically at a specified interval, as indicated by the new `sync_interval` field. No additional system configuration is necessary to support this functionality; background jobs will be scheduled automatically by the RQ worker process.

#### Proxy Routing ([#18627](https://github.com/netbox-community/netbox/issues/18627))

User can now declare one or more proxy routers via the `PROXY_ROUTERS` configuration parameter to control the use of specific proxy servers for various outbound connections. For example, it is now possible to configure NetBox to use different proxies based on the type of outbound traffic or its destination.

### Enhancements

* [#7598](https://github.com/netbox-community/netbox/issues/7598) - Adopt advanced query filtering in GraphQL API to support filtering by custom fields
* [#8423](https://github.com/netbox-community/netbox/issues/8423) - Enable assigning services to FHRP groups
* [#15842](https://github.com/netbox-community/netbox/issues/15842) - Introduce the `LOGIN_FORM_HIDDEN` configuration parameter
* [#16224](https://github.com/netbox-community/netbox/issues/16224) - Implement pagination support for the GraphQL API
* [#17170](https://github.com/netbox-community/netbox/issues/17170) - Enable the assignment of a contact to multiple contact groups
* [#17443](https://github.com/netbox-community/netbox/issues/17443) - Add a `file_name` field to the export template model
* [#17602](https://github.com/netbox-community/netbox/issues/17602) - Add a `comments` field to all nested group models (Region, SiteGroup, Location, ContactGroup, TenantGroup, and WirelessLANGroup)
* [#17608](https://github.com/netbox-community/netbox/issues/17608) - Add a `status` field to the L2VPN model
* [#17653](https://github.com/netbox-community/netbox/issues/17653) - Enable declaring Jinja environment parameters on export templates (similar to config templates)
* [#17793](https://github.com/netbox-community/netbox/issues/17793) - Introduce a REST API endpoint for tagged objects (`/api/extras/tagged-objects/`)
* [#17841](https://github.com/netbox-community/netbox/issues/17841) - Add a `weight` field to the Tag model to influence ordering
* [#18296](https://github.com/netbox-community/netbox/issues/18296) - Add a `tenant` field to the VLAN group model
* [#18352](https://github.com/netbox-community/netbox/issues/18352) - Add a `status` field to the power outlet model
* [#18417](https://github.com/netbox-community/netbox/issues/18417) - Add an `outer_height` field to the rack & rack type models
* [#18535](https://github.com/netbox-community/netbox/issues/18535) - The presence of incompatible plugins will no longer prevent NetBox from starting
* [#18780](https://github.com/netbox-community/netbox/issues/18780) - Introduce `DATABASES` and `DATABASE_ROUTERS` configuration parameters to enable defining connections to external databases (e.g. for plugins)
* [#18783](https://github.com/netbox-community/netbox/issues/18783) - Enable filtering all applicable models by tag ID
* [#18785](https://github.com/netbox-community/netbox/issues/18785) - Enable custom choices for rack, device, and module airflow

### Plugins

* [#16630](https://github.com/netbox-community/netbox/issues/16630) - Plugins can now inject content within the HTML `<head>` block via the new `plugin_head()` method on PluginTemplateExtension
* [#17424](https://github.com/netbox-community/netbox/issues/17424) - Extend ViewTab with a `visible` argument to control tab rendering
* [#17857](https://github.com/netbox-community/netbox/issues/17857) - Added a `release_track` attribute to PluginConfig
* [#18305](https://github.com/netbox-community/netbox/issues/18305) - Introduce plugin support for ContactsMixin
* [#19073](https://github.com/netbox-community/netbox/issues/19073) - Allow installed plugins to be omitted from the plugins list

### Bug Fixes (From beta1)

* [#19213](https://github.com/netbox-community/netbox/issues/19213) - Fix rendering of dropdown selection form fields
* [#19224](https://github.com/netbox-community/netbox/issues/19224) - Fix GraphQL API support for custom field choices
* [#19225](https://github.com/netbox-community/netbox/issues/19225) - Restore missing GraphQL API filters
* [#19263](https://github.com/netbox-community/netbox/issues/19263) - Render action buttons only if the record model matches the table model
* [#19264](https://github.com/netbox-community/netbox/issues/19264) - Support table configs on child object list views
* [#19266](https://github.com/netbox-community/netbox/issues/19266) - Fix copy-to-clipboard button for IP addresses

### Other Changes

* [#18071](https://github.com/netbox-community/netbox/issues/18071) - Removed legacy staged changed functionality in favor of the [netbox-branching](https://github.com/netboxlabs/netbox-branching) plugin
* [#18072](https://github.com/netbox-community/netbox/issues/18072) - Drop support for the singular `model` attribute on PluginTemplateExtension (use `models` instead)
* [#18191](https://github.com/netbox-community/netbox/issues/18191) - Remove redundant PostgreSQL indexes
* [#18236](https://github.com/netbox-community/netbox/issues/18236) - Upgrade the HTMX library to v2.0
* [#18540](https://github.com/netbox-community/netbox/issues/18540) - Operational plugins are now recorded in the application registry
* [#18623](https://github.com/netbox-community/netbox/issues/18623) - Upgrade the Tabler CSS theme to v1.0
* [#18743](https://github.com/netbox-community/netbox/issues/18743) - Upgrade Django to v5.2
* [#18751](https://github.com/netbox-community/netbox/issues/18751) - Change the default value for `ALLOW_TOKEN_RETRIEVAL` to False
* [#18808](https://github.com/netbox-community/netbox/issues/18808) - Squashed migration dependencies have been altered to rectify an issue with Django's `sqlmigrate` management command
* [#18820](https://github.com/netbox-community/netbox/issues/18820) - PostgreSQL 13 is no longer supported
* [#19004](https://github.com/netbox-community/netbox/issues/19004) - The use of inventory items has been deprecated in favor of modules. Inventory items and roles may be removed in a future NetBox release.

### REST API Changes

* Added the following endpoints:
    * `/api/extras/table-configs/`
    * `/api/extras/tagged-objects/`
    * `/api/dcim/module-type-profiles/`
* core.DataSource
    * Added the optional `sync_interval` field
* dcim.DeviceRole
    * Added the optional `parent` recursive foreign key field to effect hierarchical ordering
    * Added a `comments` field
* dcim.Location
    * Added a `comments` field
* dcim.ModuleType
    * Added the optional `profile` foreign key to the new ModuleTypeProfile model
* dcim.PowerOutlet
    * Added a `status` field
* dcim.Rack
    * Added the optional `outer_height` field
* dcim.RackType
    * Added the optional `outer_height` field
* dcim.Region
    * Added a `comments` field
* dcim.SiteGroup
    * Added a `comments` field
* extras.ConfigTemplate
    * Added optional fields `mime_type`, `file_name`, `file_extension` and `as_attachment`
* extras.ExportTemplate
    * Added optional fields `file_name` and `environment_params` (JSON)
* extras.Tag
    * Added a `weight` field
* ipam.IPRange
    * Added a `mark_populaed` boolean field
* ipam.L2VPN
    * Added a `status` field
* ipam.Service
    * Removed the `device` and `virtual_machine` foreign key fields
    * Added the `parent_object_type`, `parent_object_id`, and (read-only) `parent` fields
* ipam.VLANGroup
    * Added the optional `tenant` foreign key field
* tenancy.Contact
    * Removed the `group` foreign key field
    * Added the `groups` many-to-many field
* tenancy.ContactGroup
    * Added a `comments` field
* tenancy.TenantGroup
    * Added a `comments` field
* wireless.WirelessLANGroup
    * Added a `comments` field
