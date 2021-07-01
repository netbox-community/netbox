# NetBox v2.11

## v2.11.8 (FUTURE)

### Enhancements

* [#6138](https://github.com/netbox-community/netbox/issues/6138) - Add an `empty` filter modifier for character fields
* [#6368](https://github.com/netbox-community/netbox/issues/6368) - Enable virtual chassis assignment during bulk import of devices
* [#6620](https://github.com/netbox-community/netbox/issues/6620) - Show assigned VMs count under device role view
* [#6666](https://github.com/netbox-community/netbox/issues/6666) - Show management-only status under interface detail view
* [#6667](https://github.com/netbox-community/netbox/issues/6667) - Display VM memory as GB/TB as appropriate

### Bug Fixes

* [#6626](https://github.com/netbox-community/netbox/issues/6626) - Fix site field on VM search form; add site group
* [#6637](https://github.com/netbox-community/netbox/issues/6637) - Fix group assignment in "available VLANs" link under VLAN group view
* [#6640](https://github.com/netbox-community/netbox/issues/6640) - Disallow numeric values in custom text fields
* [#6652](https://github.com/netbox-community/netbox/issues/6652) - Fix exception when adding components in bulk to multiple devices
* [#6676](https://github.com/netbox-community/netbox/issues/6676) - Fix device/VM counts per cluster under cluster type/group views
* [#6680](https://github.com/netbox-community/netbox/issues/6680) - Allow setting custom field values for VM interfaces on intial creation

---

## v2.11.7 (2021-06-16)

### Enhancements

* [#6455](https://github.com/netbox-community/netbox/issues/6455) - Permit /32 IPv4 and /128 IPv6 prefixes
* [#6493](https://github.com/netbox-community/netbox/issues/6493) - Show change log diff for non-atomic (pre-2.11) changes
* [#6564](https://github.com/netbox-community/netbox/issues/6564) - Add N connector type for pass-through ports
* [#6588](https://github.com/netbox-community/netbox/issues/6588) - Add support for webp files as front/rear device type images
* [#6589](https://github.com/netbox-community/netbox/issues/6589) - Standardize breadcrumb navigation for power panels and feeds

### Bug Fixes

* [#6553](https://github.com/netbox-community/netbox/issues/6553) - ProviderNetwork search should match on name
* [#6562](https://github.com/netbox-community/netbox/issues/6562) - Disable ordering of secrets by assigned object
* [#6563](https://github.com/netbox-community/netbox/issues/6563) - Fix filtering by location for cable connection forms
* [#6584](https://github.com/netbox-community/netbox/issues/6584) - Fix ordering of nested inventory items
* [#6602](https://github.com/netbox-community/netbox/issues/6602) - Fix deletion of devices with cables attached

---

## v2.11.6 (2021-06-04)

### Bug Fixes

* [#6544](https://github.com/netbox-community/netbox/issues/6544) - Fix migration error when upgrading with VRF(s) defined

---

## v2.11.5 (2021-06-04)

**NOTE:** This release includes a database migration that calculates and annotates prefix depth. It may impose a noticeable delay on the upgrade process: Users should anticipate roughly one minute of delay per 100 thousand prefixes being updated.

### Enhancements

* [#6087](https://github.com/netbox-community/netbox/issues/6087) - Improved prefix hierarchy rendering
* [#6487](https://github.com/netbox-community/netbox/issues/6487) - Add location filter to cable connection form
* [#6501](https://github.com/netbox-community/netbox/issues/6501) - Expose prefix depth and children on REST API serializer
* [#6527](https://github.com/netbox-community/netbox/issues/6527) - Support Markdown for report descriptions
* [#6540](https://github.com/netbox-community/netbox/issues/6540) - Add a "flat" column to the prefix table

### Bug Fixes

* [#6064](https://github.com/netbox-community/netbox/issues/6064) - Fix object permission assignments for user and group models
* [#6217](https://github.com/netbox-community/netbox/issues/6217) - Disallow passing of string values for integer custom fields
* [#6284](https://github.com/netbox-community/netbox/issues/6284) - Avoid sending redundant webhooks when adding/removing tags
* [#6492](https://github.com/netbox-community/netbox/issues/6492) - Correct tag population in post-change data resulting from REST API changes
* [#6496](https://github.com/netbox-community/netbox/issues/6496) - Fix upgrade script when Python installed in nonstandard path
* [#6502](https://github.com/netbox-community/netbox/issues/6502) - Correct permissions evaluation for running a report via the REST API
* [#6517](https://github.com/netbox-community/netbox/issues/6517) - Fix assignment of user when creating rack reservations via REST API
* [#6525](https://github.com/netbox-community/netbox/issues/6525) - Paginate related IPs table under IP address view

---

## v2.11.4 (2021-05-25)

### Enhancements

* [#5121](https://github.com/netbox-community/netbox/issues/5121) - Add content type filters for tags
* [#6358](https://github.com/netbox-community/netbox/issues/6358) - Add search field for VLAN groups
* [#6393](https://github.com/netbox-community/netbox/issues/6393) - Add `description` filter for IP addresses
* [#6400](https://github.com/netbox-community/netbox/issues/6400) - Add cyan color choice for plugin buttons
* [#6422](https://github.com/netbox-community/netbox/issues/6422) - Enable filtering users by group under admin UI
* [#6441](https://github.com/netbox-community/netbox/issues/6441) - Improve UI paginator to optimize page object count

### Bug Fixes

* [#6376](https://github.com/netbox-community/netbox/issues/6376) - Fix assignment of VLAN groups to clusters, cluster groups via REST API
* [#6398](https://github.com/netbox-community/netbox/issues/6398) - Avoid exception when deleting device connected to self via circuit
* [#6426](https://github.com/netbox-community/netbox/issues/6426) - Allow assigning virtual chassis member interfaces to LAG on VC master
* [#6438](https://github.com/netbox-community/netbox/issues/6438) - Fix missing descriptions and label for device type imports and exports
* [#6465](https://github.com/netbox-community/netbox/issues/6465) - Fix typo in installed plugins REST API endpoint
* [#6467](https://github.com/netbox-community/netbox/issues/6467) - Fix access to metrics on custom `BASE_PATH` when login is required
* [#6468](https://github.com/netbox-community/netbox/issues/6468) - Disable ordering VLAN groups list by scope object

---

## v2.11.3 (2021-05-07)

### Enhancements

* [#6197](https://github.com/netbox-community/netbox/issues/6197) - Introduced `SESSION_COOKIE_NAME` config parameter
* [#6318](https://github.com/netbox-community/netbox/issues/6318) - Add OM5 MMF cable type
* [#6351](https://github.com/netbox-community/netbox/issues/6351) - Add aggregates count to tenant view
* [#6359](https://github.com/netbox-community/netbox/issues/6359) - Enable custom links for organizational and nested group models

### Bug Fixes

* [#6240](https://github.com/netbox-community/netbox/issues/6240) - Fix display of available VLAN ranges under VLAN group view
* [#6308](https://github.com/netbox-community/netbox/issues/6308) - Fix linking of available VLANs in VLAN group view
* [#6309](https://github.com/netbox-community/netbox/issues/6309) - Restrict parent VM interface assignment to the parent VM
* [#6312](https://github.com/netbox-community/netbox/issues/6312) - Interface device filter should return all virtual chassis interfaces only if device is master
* [#6313](https://github.com/netbox-community/netbox/issues/6313) - Fix device type instance count under manufacturer view
* [#6321](https://github.com/netbox-community/netbox/issues/6321) - Restore "add an IP" button under prefix IPs view
* [#6333](https://github.com/netbox-community/netbox/issues/6333) - Fix filtering of circuit terminations by primary key
* [#6339](https://github.com/netbox-community/netbox/issues/6339) - Improve ordering of interfaces when viewing virtual chassis master
* [#6350](https://github.com/netbox-community/netbox/issues/6350) - Include first & last IP addresses when allocating available IPv6 addresses via the REST API
* [#6355](https://github.com/netbox-community/netbox/issues/6355) - Fix caching error when swapping A/Z circuit terminations
* [#6357](https://github.com/netbox-community/netbox/issues/6357) - Fix ProviderNetwork nested API serializer
* [#6363](https://github.com/netbox-community/netbox/issues/6363) - Correct pre-population of cluster group when creating a cluster
* [#6369](https://github.com/netbox-community/netbox/issues/6369) - Fix interface assignment for VLANs in non-scoped groups

---

## v2.11.2 (2021-04-27)

### Enhancements

* [#6275](https://github.com/netbox-community/netbox/issues/6275) - Linkify rack, device counts on locations list
* [#6278](https://github.com/netbox-community/netbox/issues/6278) - Note device locations on cable traces
* [#6287](https://github.com/netbox-community/netbox/issues/6287) - Add option to clear assigned max length filter on prefixes list

### Bug Fixes

* [#6236](https://github.com/netbox-community/netbox/issues/6236) - Journal entry title should account for configured timezone
* [#6246](https://github.com/netbox-community/netbox/issues/6246) - Permit full-length descriptions when creating device components and VM interfaces
* [#6248](https://github.com/netbox-community/netbox/issues/6248) - Fix table column reconfiguration under Chrome
* [#6252](https://github.com/netbox-community/netbox/issues/6252) - Fix assignment of console port speed values above 19.2kbps
* [#6254](https://github.com/netbox-community/netbox/issues/6254) - Disable ordering of space column in racks table
* [#6258](https://github.com/netbox-community/netbox/issues/6258) - Fix parent assignment for SiteGroup API serializer
* [#6262](https://github.com/netbox-community/netbox/issues/6262) - Support filtering by created/updated time for all relevant objects
* [#6267](https://github.com/netbox-community/netbox/issues/6267) - Fix cable tracing API endpoint for circuit terminations
* [#6289](https://github.com/netbox-community/netbox/issues/6289) - Fix assignment of VC member interfaces to LAG interfaces

---

## v2.11.1 (2021-04-21)

### Enhancements

* [#6161](https://github.com/netbox-community/netbox/issues/6161) - Enable ordering of device component tables
* [#6179](https://github.com/netbox-community/netbox/issues/6179) - Enable natural ordering for virtual machines
* [#6189](https://github.com/netbox-community/netbox/issues/6189) - Add ability to search for locations by name or description
* [#6190](https://github.com/netbox-community/netbox/issues/6190) - Allow filtering devices with no location assigned
* [#6210](https://github.com/netbox-community/netbox/issues/6210) - Include child locations on location view

### Bug Fixes

* [#6184](https://github.com/netbox-community/netbox/issues/6184) - Fix parent object table column in prefix IP addresses list
* [#6188](https://github.com/netbox-community/netbox/issues/6188) - Support custom field filtering for regions, site groups, and locations
* [#6196](https://github.com/netbox-community/netbox/issues/6196) - Fix object list display for users with read-only permissions
* [#6215](https://github.com/netbox-community/netbox/issues/6215) - Restore tenancy section in virtual machine form

---

## v2.11.0 (2021-04-16)

**Note:** NetBox v2.11 is the last major release that will support Python 3.6. Beginning with NetBox v3.0, Python 3.7 or later will be required.

### Breaking Changes

* All objects now use numeric IDs in their UI view URLs instead of slugs. You may need to update external references to NetBox objects. (Note that this does _not_ affect the REST API.)
* The UI now uses numeric IDs when filtering object lists. You may need to update external links to filtered object lists. (Note that the slug- and name-based filters will continue to work, however the filter selection fields within the UI will not be automatically populated.)
* The RackGroup model has been renamed to Location (see [#4971](https://github.com/netbox-community/netbox/issues/4971)). Its REST API endpoint has changed from `/api/dcim/rack-groups/` to `/api/dcim/locations/`.
* The foreign key field `group` on dcim.Rack has been renamed to `location`.
* The foreign key field `site` on ipam.VLANGroup has been replaced with the `scope` generic foreign key (see [#5284](https://github.com/netbox-community/netbox/issues/5284)).
* Custom script ObjectVars no longer support the `queryset` parameter: Use `model` instead (see [#5995](https://github.com/netbox-community/netbox/issues/5995)).

### New Features

#### Journaling Support ([#151](https://github.com/netbox-community/netbox/issues/151))

NetBox now supports journaling for all primary objects. The journal is a collection of human-generated notes and comments about an object maintained for historical context. It supplements NetBox's change log to provide additional information about why changes have been made or to convey events which occur outside NetBox. Unlike the change log, in which records typically expire after some time, journal entries persist for the life of the associated object.

#### Parent Interface Assignments ([#1519](https://github.com/netbox-community/netbox/issues/1519))

Virtual device and VM interfaces can now be assigned to a "parent" interface by setting the `parent` field on the interface object. This is helpful for associating subinterfaces with their physical counterpart. For example, you might assign virtual interfaces Gi0/0.100 and Gi0/0.200 as children of the physical interface Gi0/0.

#### Pre- and Post-Change Snapshots in Webhooks ([#3451](https://github.com/netbox-community/netbox/issues/3451))

In conjunction with the newly improved change logging functionality ([#5913](https://github.com/netbox-community/netbox/issues/5913)), outgoing webhooks now include both pre- and post-change representations of the modified object. These are available in the rendering context as a dictionary named `snapshots` with keys `prechange` and `postchange`. For example, here are the abridged snapshots resulting from renaming a site and changing its status:

```json
"snapshots": {
    "prechange": {
        "name": "Site 1",
        "slug": "site-1",
        "status": "active",
        ...
    },
    "postchange": {
        "name": "Site 2",
        "slug": "site-2",
        "status": "planned",
        ...
    }
}
```

Note: The pre-change snapshot for a newly created will always be null, as will the post-change snapshot for a deleted object.

#### Mark as Connected Without a Cable ([#3648](https://github.com/netbox-community/netbox/issues/3648))

Cable termination objects (circuit terminations, power feeds, and most device components) can now be marked as "connected" without actually attaching a cable. This helps simplify the process of modeling an infrastructure boundary where we don't necessarily know or care what is connected to an attachment point, but still need to reflect the termination as being occupied.

In addition to the new `mark_connected` boolean field, the REST API representation of these objects now also includes a read-only boolean field named `_occupied`. This conveniently returns true if either a cable is attached or `mark_connected` is true.

#### Allow Assigning Devices to Locations ([#4971](https://github.com/netbox-community/netbox/issues/4971))

Devices can now be assigned to locations (formerly known as rack groups) within a site without needing to be assigned to a particular rack. This is handy for assigning devices to rooms or floors within a building where racks are not used. The `location` foreign key field has been added to the Device model to support this.

#### Dynamic Object Exports ([#4999](https://github.com/netbox-community/netbox/issues/4999))

When exporting a list of objects in NetBox, users now have the option of selecting the "current view". This will render CSV output matching the current configuration of the table being viewed. For example, if you modify the sites list to display only the site name, tenant, and status, the rendered CSV will include only these columns, and they will appear in the order chosen.

The legacy static export behavior has been retained to ensure backward compatibility for dependent integrations. However, users are strongly encouraged to adapt custom export templates where needed as this functionality will be removed in v3.0.

#### Variable Scope Support for VLAN Groups ([#5284](https://github.com/netbox-community/netbox/issues/5284))

In previous releases, VLAN groups could be assigned only to a site. To afford more flexibility in conveying the true scope of an L2 domain, a VLAN group can now be assigned to a region, site group (new in v2.11), site, location, or rack. VLANs assigned to a group will be available only to devices and virtual machines which exist within its scope.

For example, a VLAN within a group assigned to a location will be available only to devices assigned to that location (or one of its child locations), or to a rack within that location.

#### New Site Group Model ([#5892](https://github.com/netbox-community/netbox/issues/5892))

This release introduces the new SiteGroup model, which can be used to organize sites similar to the existing Region model. Whereas regions are intended for geographically arranging sites into countries, states, and so on, the new site group model can be used to organize sites by functional role or other arbitrary classification. Using regions and site groups in conjunction provides two dimensions along which sites can be organized, offering greater flexibility to the user.

#### Improved Change Logging ([#5913](https://github.com/netbox-community/netbox/issues/5913))

The ObjectChange model (which is used to record the creation, modification, and deletion of NetBox objects) now explicitly records the pre-change and post-change state of each object, rather than only the post-change state. This was done to present a more clear depiction of each change being made, and to prevent the erroneous association of a previous unlogged change with its successor.

#### Provider Network Modeling ([#5986](https://github.com/netbox-community/netbox/issues/5986))

A new provider network model has been introduced to represent the boundary of a network that exists outside the scope of NetBox. Each instance of this model must be assigned to a provider, and circuits can now terminate to either provider networks or to sites. The use of this model will likely be extended by future releases to support overlay and virtual circuit modeling.

### Enhancements

* [#4833](https://github.com/netbox-community/netbox/issues/4833) - Allow assigning config contexts by device type
* [#5344](https://github.com/netbox-community/netbox/issues/5344) - Add support for custom fields in tables
* [#5370](https://github.com/netbox-community/netbox/issues/5370) - Extend custom field support to organizational models
* [#5375](https://github.com/netbox-community/netbox/issues/5375) - Add `speed` attribute to console port models
* [#5401](https://github.com/netbox-community/netbox/issues/5401) - Extend custom field support to device component models
* [#5425](https://github.com/netbox-community/netbox/issues/5425) - Create separate tabs for VMs and devices under the cluster view
* [#5451](https://github.com/netbox-community/netbox/issues/5451) - Add support for multiple-selection custom fields
* [#5608](https://github.com/netbox-community/netbox/issues/5608) - Add REST API endpoint for custom links
* [#5610](https://github.com/netbox-community/netbox/issues/5610) - Add REST API endpoint for webhooks
* [#5757](https://github.com/netbox-community/netbox/issues/5757) - Add unique identifier to every object view
* [#5830](https://github.com/netbox-community/netbox/issues/5830) - Add `as_attachment` to ExportTemplate to control download behavior
* [#5848](https://github.com/netbox-community/netbox/issues/5848) - Filter custom fields by content type in format `<app_label>.<model>`
* [#5891](https://github.com/netbox-community/netbox/issues/5891) - Add `display` field to all REST API serializers
* [#5894](https://github.com/netbox-community/netbox/issues/5894) - Use primary keys when filtering object lists by related objects in the UI
* [#5895](https://github.com/netbox-community/netbox/issues/5895) - Rename RackGroup to Location
* [#5901](https://github.com/netbox-community/netbox/issues/5901) - Add `created` and `last_updated` fields to device component models
* [#5971](https://github.com/netbox-community/netbox/issues/5971) - Add dedicated views for organizational models
* [#5972](https://github.com/netbox-community/netbox/issues/5972) - Enable bulk editing for organizational models
* [#5975](https://github.com/netbox-community/netbox/issues/5975) - Allow partial (decimal) vCPU allocations for virtual machines
* [#6001](https://github.com/netbox-community/netbox/issues/6001) - Paginate component tables under device views
* [#6038](https://github.com/netbox-community/netbox/issues/6038) - Include tagged objects list on tag view
* [#6088](https://github.com/netbox-community/netbox/issues/6088) - Improved table configuration form
* [#6097](https://github.com/netbox-community/netbox/issues/6097) - Redirect old slug-based object views
* [#6125](https://github.com/netbox-community/netbox/issues/6125) - Add locations count to home page
* [#6146](https://github.com/netbox-community/netbox/issues/6146) - Add bulk disconnect support for power feeds
* [#6149](https://github.com/netbox-community/netbox/issues/6149) - Support image attachments for locations

### Bug Fixes (from v2.11-beta1)

* [#5583](https://github.com/netbox-community/netbox/issues/5583) - Eliminate redundant change records when adding/removing tags
* [#6100](https://github.com/netbox-community/netbox/issues/6100) - Fix VM interfaces table "add interfaces" link
* [#6104](https://github.com/netbox-community/netbox/issues/6104) - Fix location column on racks table
* [#6105](https://github.com/netbox-community/netbox/issues/6105) - Hide checkboxes for VMs under cluster VMs view
* [#6106](https://github.com/netbox-community/netbox/issues/6106) - Allow assigning a virtual interface as the parent of an existing interface
* [#6107](https://github.com/netbox-community/netbox/issues/6107) - Fix rack selection field on device form
* [#6110](https://github.com/netbox-community/netbox/issues/6110) - Fix handling of TemplateColumn values for table export
* [#6123](https://github.com/netbox-community/netbox/issues/6123) - Prevent device from being assigned to mismatched site and location
* [#6124](https://github.com/netbox-community/netbox/issues/6124) - Location `parent` filter should return all child locations (not just those directly assigned)
* [#6130](https://github.com/netbox-community/netbox/issues/6130) - Improve display of assigned models in custom fields list
* [#6155](https://github.com/netbox-community/netbox/issues/6155) - Fix admin links for plugins, background tasks
* [#6171](https://github.com/netbox-community/netbox/issues/6171) - Fix display of horizontally-scrolling object lists
* [#6173](https://github.com/netbox-community/netbox/issues/6173) - Fix assigned device/VM count when bulk editing/deleting device roles
* [#6176](https://github.com/netbox-community/netbox/issues/6176) - Correct position of MAC address field when creating VM interfaces
* [#6177](https://github.com/netbox-community/netbox/issues/6177) - Prevent VM interface from being assigned as its own parent

### Other Changes

* [#1638](https://github.com/netbox-community/netbox/issues/1638) - Migrate all primary keys to 64-bit integers
* [#5873](https://github.com/netbox-community/netbox/issues/5873) - Use numeric IDs in all object URLs
* [#5938](https://github.com/netbox-community/netbox/issues/5938) - Deprecated support for Python 3.6
* [#5990](https://github.com/netbox-community/netbox/issues/5990) - Deprecated `display_field` parameter for custom script ObjectVar and MultiObjectVar fields
* [#5995](https://github.com/netbox-community/netbox/issues/5995) - Dropped backward compatibility for `queryset` parameter on ObjectVar and MultiObjectVar (use `model` instead)
* [#6014](https://github.com/netbox-community/netbox/issues/6014) - Moved the virtual machine interfaces list to a separate view
* [#6071](https://github.com/netbox-community/netbox/issues/6071) - Cable traces now traverse circuits

### REST API Changes

* All primary keys are now 64-bit integers
* All model serializers now include a `display` field to be used for the presentation of an object to a human user
* All device components
    * Added support for custom fields
    * Added `created` and `last_updated` fields to track object creation and modification
* All device component templates
    * Added `created` and `last_updated` fields to track object creation and modification
* All organizational models
    * Added support for custom fields
* All cable termination models (cabled device components, power feeds, and circuit terminations)
    * Added `mark_connected` boolean field to force connection status
    * Added `_occupied` read-only boolean field as common attribute for determining whether an object is occupied
* Renamed RackGroup to Location
    * The `/dcim/rack-groups/` endpoint is now `/dcim/locations/`
* circuits.CircuitTermination
    * Added the `provider_network` field
    * Removed the `connected_endpoint`, `connected_endpoint_type`, and `connected_endpoint_reachable` fields
    * The `trace/` endpoint has been replaced with `paths/`
* circuits.ProviderNetwork
    * Added the `/api/circuits/provider-networks/` endpoint
* dcim.Device
    * Added the `location` field
* dcim.Interface
    * Added the `parent` field
* dcim.PowerPanel
    * Renamed `rack_group` field to `location`
* dcim.Rack
    * Renamed `group` field to `location`
* dcim.Site
    * Added the `group` foreign key field to SiteGroup
* dcim.SiteGroup
    * Added the `/api/dcim/site-groups/` endpoint
* extras.ConfigContext
    * Added the `site_groups` many-to-many field to track the assignment of ConfigContexts to SiteGroups
* extras.CustomField
    * Added new custom field type: `multi-select`
* extras.CustomLink
    * Added the `/api/extras/custom-links/` endpoint
* extras.ExportTemplate
    * Added the `as_attachment` boolean field
* extras.ObjectChange
    * Added the `prechange_data` field
    * Renamed `object_data` to `postchange_data`
* extras.Webhook
    * Added the `/api/extras/webhooks/` endpoint
* ipam.VLANGroup
    * Added the `scope_type`, `scope_id`, and `scope` fields (`scope` is a generic foreign key)
    * Dropped the `site` foreign key field
* virtualization.VirtualMachine
    * `vcpus` has been changed from an integer to a decimal value
* virtualization.VMInterface
    * Added the `parent` field
