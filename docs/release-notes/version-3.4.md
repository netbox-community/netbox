# NetBox v3.4

## v3.4.2 (2023-01-03)

### Enhancements

* [#9285](https://github.com/netbox-community/netbox/issues/9285) - Enable specifying assigned component during bulk import of inventory items
* [#10700](https://github.com/netbox-community/netbox/issues/10700) - Match device name when using modules quick search
* [#11121](https://github.com/netbox-community/netbox/issues/11121) - Add VM resource totals to cluster view
* [#11156](https://github.com/netbox-community/netbox/issues/11156) - Enable selecting assigned component when editing inventory item in UI
* [#11223](https://github.com/netbox-community/netbox/issues/11223) - `reindex` management command should accept app label without model name
* [#11244](https://github.com/netbox-community/netbox/issues/11244) - Add controls for saved filters to rack elevations list
* [#11248](https://github.com/netbox-community/netbox/issues/11248) - Fix database migration when plugin with search indexer is enabled
* [#11259](https://github.com/netbox-community/netbox/issues/11259) - Add support for Redis username configuration

### Bug Fixes

* [#11280](https://github.com/netbox-community/netbox/issues/11280) - Fix errant newlines when exporting interfaces with multiple IP addresses assigned
* [#11290](https://github.com/netbox-community/netbox/issues/11290) - Correct reporting of scheduled job duration
* [#11232](https://github.com/netbox-community/netbox/issues/11232) - Enable partial & regular expression matching for non-string types in global search
* [#11342](https://github.com/netbox-community/netbox/issues/11342) - Correct cable trace URL under "connection" tab for device components
* [#11345](https://github.com/netbox-community/netbox/issues/11345) - Fix form validation for bulk import of modules

---

## v3.4.1 (2022-12-16)

### Enhancements

* [#9971](https://github.com/netbox-community/netbox/issues/9971) - Enable ordering of nested group models by name
* [#11214](https://github.com/netbox-community/netbox/issues/11214) - Introduce the `DEFAULT_LANGUAGE` configuration parameter

### Bug Fixes

* [#11175](https://github.com/netbox-community/netbox/issues/11175) - Fix cloning of fields containing special characters
* [#11178](https://github.com/netbox-community/netbox/issues/11178) - Pressing enter in quick search box should not trigger bulk operations
* [#11184](https://github.com/netbox-community/netbox/issues/11184) - Correct visualization of cable path which splits across multiple circuit terminations
* [#11185](https://github.com/netbox-community/netbox/issues/11185) - Fix TemplateSyntaxError when viewing custom script results
* [#11189](https://github.com/netbox-community/netbox/issues/11189) - Fix localization of dates & numbers
* [#11205](https://github.com/netbox-community/netbox/issues/11205) - Correct cloning behavior for recursively-nested models
* [#11206](https://github.com/netbox-community/netbox/issues/11206) - Avoid clearing assigned groups if `REMOTE_AUTH_DEFAULT_GROUPS` is invalid

---

## v3.4.0 (2022-12-14)

!!! warning "PostgreSQL 11 Required"
    NetBox v3.4 requires PostgreSQL 11 or later.

### Breaking Changes

* Device and virtual machine names are no longer case-sensitive. Attempting to create e.g. "device1" and "DEVICE1" within the same site will raise a validation error.
* The `asn`, `noc_contact`, `admin_contact`, and `portal_url` fields have been removed from the provider model. Please replicate any data remaining in these fields to the ASN and contact models introduced in NetBox v3.1 prior to upgrading.
* The `content_type` fields on the CustomLink and ExportTemplate models have been renamed to `content_types` and now support the assignment of multiple content types per object.
* Within the Python API, the `cf` property on an object with custom fields now returns deserialized values. For example, a custom field referencing an object will return the object instance rather than its numeric ID. To access the raw serialized values, reference the object's `custom_field_data` attribute instead.
* The `NetBoxModelCSVForm` class has been renamed to `NetBoxModelImportForm`. Backward compatability with the previous name has been retained for this release, but will be dropped in NetBox v3.5.

### New Features

#### New Global Search ([#10560](https://github.com/netbox-community/netbox/issues/10560))

NetBox's global search functionality has been completely overhauled and replaced by a new cache-based lookup. This new implementation provides a much faster, more intelligent search capability. Results are returned in order of precedence regardless of object type, and matching field values are highlighted in the results. Additionally, custom field values are now included in global search results (where enabled). Plugins can also register their own models with the new global search engine.

#### Virtual Device Contexts ([#7854](https://github.com/netbox-community/netbox/issues/7854))

A new model representing virtual device contexts (VDCs) has been added. VDCs are logical partitions of resources within a device that can be managed independently. A VDC is created within a device and may have device interfaces assigned to it. An interface can be allocated to any number of VDCs on its device.

#### Saved Filters ([#9623](https://github.com/netbox-community/netbox/issues/9623))

Object lists can be filtered by a variety of different fields and characteristics. Applied filters can now be saved for reuse. For example, the query string

```
?status=active&region_id=12&tenant=acme
```

can be saved and applied to future queries as

```
?filter=my-custom-filter
```

Saved filters can be kept private, or shared among NetBox users. They can be applied to both UI and REST API searches.

#### JSON/YAML Bulk Imports ([#4347](https://github.com/netbox-community/netbox/issues/4347))

NetBox's bulk import feature, which was previously limited to CSV-formatted data for most types of objects, has been extended to accept data formatted in JSON or YAML as well. This enables users to directly import objects from a variety of sources without needing to first convert data to CSV. NetBox will attempt to automatically determine the format of import data if not specified by the user.

#### Update Existing Objects via Bulk Import ([#7961](https://github.com/netbox-community/netbox/issues/7961))

NetBox's CSV-based bulk import functionality has been extended to support also modifying existing objects. When an `id` column is present in the import form, it will be used to infer the object to be modified, rather than a new object being created. All fields (columns) are optional when modifying existing objects.

#### Scheduled Reports & Scripts ([#8366](https://github.com/netbox-community/netbox/issues/8366))

Reports and custom scripts can now be scheduled for execution at a desired future time. Background scheduling is handled entirely by the existing RQ workers; there is no need to configure additional tasks to support scheduled jobs. When creating a scheduled job, the user may optionally specify an interval at which the job will run repeatedly (e.g. every 24 hours).

#### API for Staged Changes ([#10851](https://github.com/netbox-community/netbox/issues/10851))

This release introduces a new programmatic API that enables plugins and custom scripts to prepare changes in NetBox without actually committing them to the active database. To stage changes, create and activate a branch using the `checkout()` context manager. Any changes made within this context will be captured, recorded, and rolled back for future use. Once ready, a branch can be applied to the active database by calling `merge()`. 

!!! danger "Experimental Feature"
    This feature is still under active development and considered experimental in nature. Its use in production is strongly discouraged at this time.

### Enhancements

* [#815](https://github.com/netbox-community/netbox/issues/815) - Enable specifying terminations when bulk importing circuits
* [#6003](https://github.com/netbox-community/netbox/issues/6003) - Enable the inclusion of custom field values in global search
* [#7376](https://github.com/netbox-community/netbox/issues/7376) - Enable the assignment of tags during CSV import
* [#8245](https://github.com/netbox-community/netbox/issues/8245) - Enable GraphQL filtering of related objects
* [#8274](https://github.com/netbox-community/netbox/issues/8274) - Enable associating a custom link with multiple object types
* [#8485](https://github.com/netbox-community/netbox/issues/8485) - Enable journaling for all organizational models
* [#8853](https://github.com/netbox-community/netbox/issues/8853) - Introduce the `ALLOW_TOKEN_RETRIEVAL` config parameter to restrict the display of API tokens
* [#9249](https://github.com/netbox-community/netbox/issues/9249) - Device and virtual machine names are no longer case-sensitive
* [#9478](https://github.com/netbox-community/netbox/issues/9478) - Add `link_peers` field to GraphQL types for cabled objects
* [#9654](https://github.com/netbox-community/netbox/issues/9654) - Add `weight` field to racks, device types, and module types
* [#9817](https://github.com/netbox-community/netbox/issues/9817) - Add `assigned_object` field to GraphQL type for IP addresses and L2VPN terminations
* [#9832](https://github.com/netbox-community/netbox/issues/9832) - Add `mounting_depth` field to rack model
* [#9892](https://github.com/netbox-community/netbox/issues/9892) - Add optional `name` field for FHRP groups
* [#10348](https://github.com/netbox-community/netbox/issues/10348) - Add decimal custom field type
* [#10371](https://github.com/netbox-community/netbox/issues/10371) - Add `status` field for modules
* [#10545](https://github.com/netbox-community/netbox/issues/10545) - Standardize the use of `description` and `comments` fields on all primary models
* [#10556](https://github.com/netbox-community/netbox/issues/10556) - Include a `display` field in all GraphQL object types
* [#10595](https://github.com/netbox-community/netbox/issues/10595) - Add GraphQL relationships for additional generic foreign key fields
* [#10675](https://github.com/netbox-community/netbox/issues/10675) - Add `max_weight` field to track maximum load capacity for racks
* [#10698](https://github.com/netbox-community/netbox/issues/10698) - Omit app label from content type in table columns
* [#10710](https://github.com/netbox-community/netbox/issues/10710) - Add `status` field to WirelessLAN
* [#10761](https://github.com/netbox-community/netbox/issues/10761) - Enable associating an export template with multiple object types
* [#10945](https://github.com/netbox-community/netbox/issues/10945) - Enable recurring execution of scheduled reports & scripts
* [#11022](https://github.com/netbox-community/netbox/issues/11022) - Introduce `QUEUE_MAPPINGS` configuration parameter to allow customization of background task prioritization

### Bug Fixes (from v3.4-beta1)

* [#10946](https://github.com/netbox-community/netbox/issues/10946) - Fix AttributeError exception when viewing a device with a primary IP and no platform assigned
* [#10948](https://github.com/netbox-community/netbox/issues/10948) - Linkify primary IPs for VDCs
* [#10950](https://github.com/netbox-community/netbox/issues/10950) - Fix validation of VDC primary IPs
* [#10957](https://github.com/netbox-community/netbox/issues/10957) - Add missing VDCs column to interface tables
* [#10973](https://github.com/netbox-community/netbox/issues/10973) - Fix device links in VDC table
* [#10980](https://github.com/netbox-community/netbox/issues/10980) - Fix view tabs for plugin objects
* [#10982](https://github.com/netbox-community/netbox/issues/10982) - Catch `NoReverseMatch` exception when rendering tabs with no registered URL
* [#10984](https://github.com/netbox-community/netbox/issues/10984) - Fix navigation menu expansion for plugin menus comprising multiple words
* [#11000](https://github.com/netbox-community/netbox/issues/11000) - Improve validation of YAML-formatted import data
* [#11046](https://github.com/netbox-community/netbox/issues/11046) - Fix exception when caching very large field values for search
* [#11154](https://github.com/netbox-community/netbox/issues/11154) - Index VM interface MAC address and MTU for global search
* [#11171](https://github.com/netbox-community/netbox/issues/11171) - Fix querying of related objects under GraphQL API

### Plugins API

* [#4751](https://github.com/netbox-community/netbox/issues/4751) - Enable embedding custom content on core list views via `list_buttons()` method
* [#8927](https://github.com/netbox-community/netbox/issues/8927) - Enable inclusion of plugin models in global search via `SearchIndex`
* [#9071](https://github.com/netbox-community/netbox/issues/9071) - Enable plugins to register top-level navigation menus using PluginMenu
* [#9072](https://github.com/netbox-community/netbox/issues/9072) - Enable registration of tabbed plugin views for core NetBox models
* [#9880](https://github.com/netbox-community/netbox/issues/9880) - Enable plugins to install and register other Django apps via `django_apps` attribute
* [#9887](https://github.com/netbox-community/netbox/issues/9887) - Inspect `docs_url` property to determine link to model documentation
* [#10314](https://github.com/netbox-community/netbox/issues/10314) - Move `clone()` method from NetBoxModel to CloningMixin
* [#10543](https://github.com/netbox-community/netbox/issues/10543) - Introduce `get_plugin_config()` utility function
* [#10739](https://github.com/netbox-community/netbox/issues/10739) - Introduce `get_queryset()` method on generic views

### Other Changes

* [#9045](https://github.com/netbox-community/netbox/issues/9045) - Remove legacy ASN field from provider model
* [#9046](https://github.com/netbox-community/netbox/issues/9046) - Remove legacy contact fields from provider model
* [#10052](https://github.com/netbox-community/netbox/issues/10052) - The `cf` attribute on objects now returns deserialized custom field data
* [#10358](https://github.com/netbox-community/netbox/issues/10358) - Raise minimum required PostgreSQL version from 10 to 11
* [#10694](https://github.com/netbox-community/netbox/issues/10694) - Emit the `post_save` signal when creating device components in bulk
* [#10697](https://github.com/netbox-community/netbox/issues/10697) - Move application registry into core app
* [#10699](https://github.com/netbox-community/netbox/issues/10699) - Remove unused custom `import_object()` function
* [#10781](https://github.com/netbox-community/netbox/issues/10781) - Add support for Python v3.11
* [#10816](https://github.com/netbox-community/netbox/issues/10816) - Pass the current request as context when instantiating a FilterSet within UI views
* [#10820](https://github.com/netbox-community/netbox/issues/10820) - Switch timezone library from pytz to zoneinfo
* [#10821](https://github.com/netbox-community/netbox/issues/10821) - Enable data localization

### REST API Changes

* Added the `/api/dcim/virtual-device-contexts/` endpoint
* circuits.provider
    * Removed the `asn`, `noc_contact`, `admin_contact`, and `portal_url` fields
    * Added a `description` field
* dcim.Cable
    * Added `description` and `comments` fields
* dcim.Device
    * Added a `description` field
* dcim.DeviceType
    * Added `description`, `weight`, and `weight_unit` fields
* dcim.Module
    * Added a `description` field
* dcim.Interface
    * Added the `vdcs` field
* dcim.Module
    * Added a required `status` field
* dcim.ModuleType
    * Added `description`, `weight`, and `weight_unit` fields
* dcim.PowerFeed
    * Added a `description` field
* dcim.PowerPanel
    * Added `description` and `comments` fields
* dcim.Rack
    * Added `description`, `mounting_depth`, `weight`, `max_weight`, and `weight_unit` fields
* dcim.RackReservation
    * Added a `comments` field
* dcim.VirtualChassis
    * Added `description` and `comments` fields
* extras.CustomField
    * Added a `search_weight` field
* extras.CustomLink
    * Renamed `content_type` field to `content_types`
* extras.ExportTemplate
    * Renamed `content_type` field to `content_types`
* extras.JobResult
    * Added `interval`, `scheduled`, and `started` fields
* ipam.Aggregate
    * Added a `comments` field
* ipam.ASN
    * Added a `comments` field
* ipam.FHRPGroup
    * Added `name` and `comments` fields
* ipam.IPAddress
    * Added a `comments` field
* ipam.IPRange
    * Added a `comments` field
* ipam.L2VPN
    * Added a `comments` field
* ipam.Prefix
    * Added a `comments` field
* ipam.RouteTarget
    * Added a `comments` field
* ipam.Service
    * Added a `comments` field
* ipam.ServiceTemplate
    * Added a `comments` field
* ipam.VLAN
    * Added a `comments` field
* ipam.VRF
    * Added a `comments` field
* tenancy.Contact
    * Added a `description` field
* virtualization.Cluster
    * Added a `description` field
* virtualization.VirtualMachine
    * Added a `description` field
* wireless.WirelessLAN
    * Added a required `status` choice field
    * Added a `comments` field
* wireless.WirelessLink
    * Added a `comments` field

### GraphQL API Changes

* All object types now include a `display` field
* All cabled object types now include a `link_peers` field
* Add a `contacts` relationship for all relevant models
* dcim.Cable
    * Add A/B terminations fields
* dcim.CableTermination
    * Add `termination` field
* dcim.InventoryItem
    * Add `component` field
* dcim.InventoryItemTemplate
    * Add `component` field
* dcim.Rack
    * Add `mounting_depth` field
* ipam.FHRPGroupAssignment
    * Add `interface` field
* ipam.IPAddress
    * Add `assigned_object` field
* ipam.L2VPNTermination
    * Add `assigned_object` field
* ipam.VLANGroupType
    * Add `scope` field
