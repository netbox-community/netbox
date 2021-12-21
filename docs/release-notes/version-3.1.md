# NetBox v3.1

## v3.1.3 (FUTURE)

### Enhancements

* [#8100](https://github.com/netbox-community/netbox/issues/8100) - Add "other" choice for FHRP group protocol

### Bug Fixes

* [#7246](https://github.com/netbox-community/netbox/issues/7246) - Don't attempt to URL-decode NAPALM response payloads
* [#7962](https://github.com/netbox-community/netbox/issues/7962) - Fix user menu under report/script result view
* [#8097](https://github.com/netbox-community/netbox/issues/8097) - Fix styling of Markdown tables
* [#8131](https://github.com/netbox-community/netbox/issues/8131) - Restore annotation of available IPs under prefix IPs view

---

## v3.1.2 (2021-12-20)

### Enhancements

* [#7661](https://github.com/netbox-community/netbox/issues/7661) - Remove forced styling of custom banners
* [#7665](https://github.com/netbox-community/netbox/issues/7665) - Add toggle to show only available child prefixes
* [#7999](https://github.com/netbox-community/netbox/issues/7999) - Add 6 GHz and 60 GHz wireless channels
* [#8057](https://github.com/netbox-community/netbox/issues/8057) - Dynamic object tables using HTMX
* [#8080](https://github.com/netbox-community/netbox/issues/8080) - Link to NAT IPs for device/VM primary IPs
* [#8081](https://github.com/netbox-community/netbox/issues/8081) - Allow creating services directly from navigation menu
* [#8083](https://github.com/netbox-community/netbox/issues/8083) - Removed "related devices" panel from device view
* [#8108](https://github.com/netbox-community/netbox/issues/8108) - Improve breadcrumb links for device/VM components

### Bug Fixes

* [#7674](https://github.com/netbox-community/netbox/issues/7674) - Fix inadvertent application of device type context to virtual machines
* [#8074](https://github.com/netbox-community/netbox/issues/8074) - Ordering VMs by name should reference naturalized value
* [#8077](https://github.com/netbox-community/netbox/issues/8077) - Fix exception when attaching image to location, circuit, or power panel
* [#8078](https://github.com/netbox-community/netbox/issues/8078) - Add missing wireless models to `lsmodels()` in `nbshell`
* [#8079](https://github.com/netbox-community/netbox/issues/8079) - Fix validation of LLDP neighbors when connected device has an asset tag
* [#8088](https://github.com/netbox-community/netbox/issues/8088) - Improve legibility of text in labels with light-colored backgrounds
* [#8092](https://github.com/netbox-community/netbox/issues/8092) - Rack elevations should not include device asset tags
* [#8096](https://github.com/netbox-community/netbox/issues/8096) - Fix DataError during change logging of objects with very long string representations
* [#8101](https://github.com/netbox-community/netbox/issues/8101) - Preserve return URL when using "create and add another" button
* [#8102](https://github.com/netbox-community/netbox/issues/8102) - Raise validation error when attempting to assign an IP address to multiple objects

---

## v3.1.1 (2021-12-13)

### Enhancements

* [#8047](https://github.com/netbox-community/netbox/issues/8047) - Display sorting indicator in table column headers

### Bug Fixes

* [#5869](https://github.com/netbox-community/netbox/issues/5869) - Fix permissions evaluation under available prefix/IP REST API endpoints
* [#7519](https://github.com/netbox-community/netbox/issues/7519) - Return a 409 status for unfulfillable available prefix/IP requests
* [#7690](https://github.com/netbox-community/netbox/issues/7690) - Fix custom field integer support for MultiValueNumberFilter
* [#7990](https://github.com/netbox-community/netbox/issues/7990) - Fix `title` display on contact detail view
* [#7996](https://github.com/netbox-community/netbox/issues/7996) - Show WWN field in interface creation form
* [#8001](https://github.com/netbox-community/netbox/issues/8001) - Correct verbose name for wireless LAN group model
* [#8003](https://github.com/netbox-community/netbox/issues/8003) - Fix cable tracing across bridged interfaces with no cable
* [#8005](https://github.com/netbox-community/netbox/issues/8005) - Fix contact email display
* [#8009](https://github.com/netbox-community/netbox/issues/8009) - Validate IP addresses for uniqueness when creating an FHRP group
* [#8010](https://github.com/netbox-community/netbox/issues/8010) - Allow filtering devices by multiple serial numbers
* [#8019](https://github.com/netbox-community/netbox/issues/8019) - Exclude metrics endpoint when `LOGIN_REQUIRED` is true
* [#8030](https://github.com/netbox-community/netbox/issues/8030) - Validate custom field names
* [#8033](https://github.com/netbox-community/netbox/issues/8033) - Fix display of zero values for custom integer fields in tables
* [#8035](https://github.com/netbox-community/netbox/issues/8035) - Redirect back to parent prefix after creating IP address(es) where applicable
* [#8038](https://github.com/netbox-community/netbox/issues/8038) - Placeholder filter should display zero integer values
* [#8042](https://github.com/netbox-community/netbox/issues/8042) - Fix filtering cables list by site slug or rack name
* [#8051](https://github.com/netbox-community/netbox/issues/8051) - Contact group parent assignment should not be required under REST API

---

## v3.1.0 (2021-12-06)

!!! warning "PostgreSQL 10 Required"
    NetBox v3.1 requires PostgreSQL 10 or later.

### Breaking Changes

* The `tenant` and `tenant_id` filters for the Cable model now filter on the tenant assigned directly to each cable, rather than on the parent object of either termination.
* The `cable_peer` and `cable_peer_type` attributes of cable termination models have been renamed to `link_peer` and `link_peer_type`, respectively, to accommodate wireless links between interfaces.
* Exported webhooks and custom fields now reference associated content types by raw string value (e.g. "dcim.site") rather than by human-friendly name.
* The 128GFC interface type has been corrected from `128gfc-sfp28` to `128gfc-qsfp28`.

### New Features

#### Contact Objects ([#1344](https://github.com/netbox-community/netbox/issues/1344))

A set of new models for tracking contact information has been introduced within the tenancy app. Users may now create individual contact objects to be associated with various models within NetBox. Each contact has a name, title, email address, etc. Contacts can be arranged in hierarchical groups for ease of management.

When assigning a contact to an object, the user must select a predefined role (e.g. "billing" or "technical") and may optionally indicate a priority relative to other contacts associated with the object. There is no limit on how many contacts can be assigned to an object, nor on how many objects to which a contact can be assigned.

#### Wireless Networks ([#3979](https://github.com/netbox-community/netbox/issues/3979))

This release introduces two new models to represent wireless networks:

* Wireless LAN - A multi-access wireless segment to which any number of wireless interfaces may be attached
* Wireless Link - A point-to-point connection between exactly two wireless interfaces

Both types of connection include SSID and authentication attributes. Additionally, the interface model has been extended to include several attributes pertinent to wireless operation:

* Wireless role - Access point or station
* Channel - A predefined channel within a standardized band
* Channel frequency & width - Customizable channel attributes (e.g. for licensed bands)

#### Dynamic Configuration Updates ([#5883](https://github.com/netbox-community/netbox/issues/5883))

Some parameters of NetBox's configuration are now accessible via the admin UI. These parameters can be modified by an administrator and take effect immediately upon application: There is no need to restart NetBox. Additionally, each iteration of the dynamic configuration is preserved in the database, and can be restored by an administrator at any time.

Dynamic configuration parameters may also still be defined within `configuration.py`, and the settings defined here take precedence over those defined via the user interface.

For a complete list of supported parameters, please see the [dynamic configuration documentation](../configuration/dynamic-settings.md). 

#### First Hop Redundancy Protocol (FHRP) Groups ([#6235](https://github.com/netbox-community/netbox/issues/6235))

A new FHRP group model has been introduced to aid in modeling the configurations of protocols such as HSRP, VRRP, and GLBP. Each FHRP group may be assigned one or more virtual IP addresses, as well as an authentication type and key. Member device and VM interfaces may be associated with one or more FHRP groups, with each assignment receiving a numeric priority designation.

#### Conditional Webhooks ([#6238](https://github.com/netbox-community/netbox/issues/6238))

Webhooks now include a `conditions` field, which may be used to specify conditions under which a webhook triggers. For example, you may wish to generate outgoing requests for a device webhook only when its status is "active" or "staged". This can be done by declaring conditional logic in JSON:

```json
{
  "attr": "status.value",
  "op": "in",
  "value": ["active", "staged"]
}
```

Multiple conditions may be nested using AND/OR logic as well. For more information, please see the [conditional logic documentation](../reference/conditions.md). 

#### Interface Bridging ([#6346](https://github.com/netbox-community/netbox/issues/6346))

A `bridge` field has been added to the interface model for devices and virtual machines. This can be set to reference another interface on the same parent device/VM to indicate a direct layer two bridging adjacency. Additionally, "bridge" has been added as an interface type. (However, interfaces of any type may be designated as bridged.)

Multiple interfaces can be bridged to a single virtual interface to effect a bridge group. Alternatively, two physical interfaces can be bridged to one another, to effect an internal cross-connect.

#### Multiple ASNs per Site ([#6732](https://github.com/netbox-community/netbox/issues/6732))

With the introduction of the new ASN model, NetBox now supports the assignment of multiple ASNs per site. Each ASN instance must have a 32-bit AS number, and may optionally be assigned to a RIR and/or Tenant.

The `asn` integer field on the site model has been preserved to maintain backward compatability until a later release.

#### Single Sign-On (SSO) Authentication ([#7649](https://github.com/netbox-community/netbox/issues/7649))

Support for single sign-on (SSO) authentication has been added via the [python-social-auth](https://github.com/python-social-auth) library. NetBox administrators can configure one of the [supported authentication backends](https://python-social-auth.readthedocs.io/en/latest/intro.html#auth-providers) to enable SSO authentication for users.

### Enhancements

* [#1337](https://github.com/netbox-community/netbox/issues/1337) - Add WWN field to interfaces
* [#1943](https://github.com/netbox-community/netbox/issues/1943) - Relax uniqueness constraint on cluster names
* [#3839](https://github.com/netbox-community/netbox/issues/3839) - Add `airflow` field for devices types and devices
* [#5143](https://github.com/netbox-community/netbox/issues/5143) - Include a device's asset tag in its display value
* [#6497](https://github.com/netbox-community/netbox/issues/6497) - Extend tag support to organizational models
* [#6615](https://github.com/netbox-community/netbox/issues/6615) - Add filter lookups for custom fields
* [#6711](https://github.com/netbox-community/netbox/issues/6711) - Add `longtext` custom field type with Markdown support
* [#6715](https://github.com/netbox-community/netbox/issues/6715) - Add tenant assignment for cables
* [#6874](https://github.com/netbox-community/netbox/issues/6874) - Add tenant assignment for locations
* [#7354](https://github.com/netbox-community/netbox/issues/7354) - Relax uniqueness constraints on region, site group, and location names
* [#7452](https://github.com/netbox-community/netbox/issues/7452) - Add `json` custom field type
* [#7530](https://github.com/netbox-community/netbox/issues/7530) - Move device type component lists to separate views
* [#7606](https://github.com/netbox-community/netbox/issues/7606) - Model transmit power for interfaces
* [#7619](https://github.com/netbox-community/netbox/issues/7619) - Permit custom validation rules to be defined as plain data or dotted path to class
* [#7761](https://github.com/netbox-community/netbox/issues/7761) - Extend cable tracing across bridged interfaces
* [#7812](https://github.com/netbox-community/netbox/issues/7812) - Enable change logging for image attachments
* [#7858](https://github.com/netbox-community/netbox/issues/7858) - Standardize the representation of content types across import & export functions

### Bug Fixes

* [#7589](https://github.com/netbox-community/netbox/issues/7589) - Correct 128GFC interface type identifier

### Other Changes

* [#7318](https://github.com/netbox-community/netbox/issues/7318) - Raise minimum required PostgreSQL version from 9.6 to 10

### REST API Changes

* Added the following endpoints for ASNs:
    * `/api/ipam/asn/`
* Added the following endpoints for FHRP groups:
    * `/api/ipam/fhrp-groups/`
    * `/api/ipam/fhrp-group-assignments/`
* Added the following endpoints for contacts:
    * `/api/tenancy/contact-assignments/`
    * `/api/tenancy/contact-groups/`
    * `/api/tenancy/contact-roles/`
    * `/api/tenancy/contacts/`
* Added the following endpoints for wireless networks:
    * `/api/wireless/wireless-lans/`
    * `/api/wireless/wireless-lan-groups/`
    * `/api/wireless/wireless-links/`
* Added `tags` field to the following models:
    * circuits.CircuitType
    * dcim.DeviceRole
    * dcim.Location
    * dcim.Manufacturer
    * dcim.Platform
    * dcim.RackRole
    * dcim.Region
    * dcim.SiteGroup
    * ipam.RIR
    * ipam.Role
    * ipam.VLANGroup
    * tenancy.ContactGroup
    * tenancy.ContactRole
    * tenancy.TenantGroup
    * virtualization.ClusterGroup
    * virtualization.ClusterType
* circuits.CircuitTermination
    * `cable_peer` has been renamed to `link_peer`
    * `cable_peer_type` has been renamed to `link_peer_type`
* dcim.Cable
    * Added `tenant` field
* dcim.ConsolePort
    * `cable_peer` has been renamed to `link_peer`
    * `cable_peer_type` has been renamed to `link_peer_type`
* dcim.ConsoleServerPort
    * `cable_peer` has been renamed to `link_peer`
    * `cable_peer_type` has been renamed to `link_peer_type`
* dcim.Device
    * The `display` field now includes the device's asset tag, if set
    * Added `airflow` field
* dcim.DeviceType
    * Added `airflow` field 
* dcim.FrontPort
    * `cable_peer` has been renamed to `link_peer`
    * `cable_peer_type` has been renamed to `link_peer_type`
* dcim.Interface
    * `cable_peer` has been renamed to `link_peer`
    * `cable_peer_type` has been renamed to `link_peer_type`
    * Added `bridge` field
    * Added `rf_channel` field
    * Added `rf_channel_frequency` field
    * Added `rf_channel_width` field
    * Added `rf_role` field
    * Added `tx_power` field
    * Added `wireless_link` field
    * Added `wwn` field
    * Added `count_fhrp_groups` read-only field
* dcim.Location
    * Added `tenant` field
* dcim.PowerFeed
    * `cable_peer` has been renamed to `link_peer`
    * `cable_peer_type` has been renamed to `link_peer_type`
* dcim.PowerOutlet
    * `cable_peer` has been renamed to `link_peer`
    * `cable_peer_type` has been renamed to `link_peer_type`
* dcim.PowerPort
    * `cable_peer` has been renamed to `link_peer`
    * `cable_peer_type` has been renamed to `link_peer_type`
* dcim.RearPort
    * `cable_peer` has been renamed to `link_peer`
    * `cable_peer_type` has been renamed to `link_peer_type`
* dcim.Site
    * Added `asns` relationship to ipam.ASN
* extras.ImageAttachment
    * Added the `last_updated` field
* extras.Webhook
    * Added the `conditions` field
* virtualization.VMInterface
    * Added `bridge` field
    * Added `count_fhrp_groups` read-only field
