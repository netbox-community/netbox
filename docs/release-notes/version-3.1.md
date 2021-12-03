## v3.1-beta2 (FUTURE)

### Breaking Changes

* Exported webhooks and custom fields now reference associated content types by raw string value (e.g. "dcim.site") rather than by human-friendly name.
* The 128GFC interface type has been corrected from `128gfc-sfp28` to `128gfc-qsfp28`.

### Enhancements

* [#5143](https://github.com/netbox-community/netbox/issues/5143) - Include a device's asset tag in its display value
* [#7619](https://github.com/netbox-community/netbox/issues/7619) - Permit custom validation rules to be defined as plain data or dotted path to class
* [#7761](https://github.com/netbox-community/netbox/issues/7761) - Extend cable tracing across bridged interfaces
* [#7769](https://github.com/netbox-community/netbox/issues/7769) - Enable assignment of IP addresses to an existing FHRP group
* [#7775](https://github.com/netbox-community/netbox/issues/7775) - Enable dynamic config for `CHANGELOG_RETENTION`, `CUSTOM_VALIDATORS`, and `GRAPHQL_ENABLED`
* [#7812](https://github.com/netbox-community/netbox/issues/7812) - Enable change logging for image attachments
* [#7858](https://github.com/netbox-community/netbox/issues/7858) - Standardize the representation of content types across import & export functions
* [#7884](https://github.com/netbox-community/netbox/issues/7884) - Add FHRP groups column to interface tables
* [#7924](https://github.com/netbox-community/netbox/issues/7924) - Include child groups on contact group view
* [#7925](https://github.com/netbox-community/netbox/issues/7925) - Linkify contact phone and email attributes

### Bug Fixes

* [#7589](https://github.com/netbox-community/netbox/issues/7589) - Correct 128GFC interface type identifier
* [#7756](https://github.com/netbox-community/netbox/issues/7756) - Fix AttributeError exception when editing an IP address assigned to a FHRPGroup
* [#7757](https://github.com/netbox-community/netbox/issues/7757) - Fix 404 when assigning multiple contacts/FHRP groups in succession
* [#7768](https://github.com/netbox-community/netbox/issues/7768) - Validate IP address status when creating a new FHRP group
* [#7771](https://github.com/netbox-community/netbox/issues/7771) - Group assignment should be optional when creating contacts via REST API
* [#7849](https://github.com/netbox-community/netbox/issues/7849) - Fix exception when creating an FHRPGroup with an invalid IP address
* [#7880](https://github.com/netbox-community/netbox/issues/7880) - Include assigned IP addresses in FHRP group object representation
* [#7960](https://github.com/netbox-community/netbox/issues/7960) - Prevent creation of regions/site groups/locations with duplicate names (see #7354)

### REST API Changes

* dcim.Device
    * The `display` field now includes the device's asset tag, if set
* extras.ImageAttachment
    * Added the `last_updated` field

---

## v3.1-beta1 (2021-11-05)

!!! warning "PostgreSQL 10 Required"
    NetBox v3.1 requires PostgreSQL 10 or later.

### Breaking Changes

* The `tenant` and `tenant_id` filters for the Cable model now filter on the tenant assigned directly to each cable, rather than on the parent object of either termination.
* The `cable_peer` and `cable_peer_type` attributes of cable termination models have been renamed to `link_peer` and `link_peer_type`, respectively, to accommodate wireless links between interfaces.

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
* [#6497](https://github.com/netbox-community/netbox/issues/6497) - Extend tag support to organizational models
* [#6615](https://github.com/netbox-community/netbox/issues/6615) - Add filter lookups for custom fields
* [#6711](https://github.com/netbox-community/netbox/issues/6711) - Add `longtext` custom field type with Markdown support
* [#6715](https://github.com/netbox-community/netbox/issues/6715) - Add tenant assignment for cables
* [#6874](https://github.com/netbox-community/netbox/issues/6874) - Add tenant assignment for locations
* [#7354](https://github.com/netbox-community/netbox/issues/7354) - Relax uniqueness constraints on region, site group, and location names
* [#7452](https://github.com/netbox-community/netbox/issues/7452) - Add `json` custom field type
* [#7530](https://github.com/netbox-community/netbox/issues/7530) - Move device type component lists to separate views
* [#7606](https://github.com/netbox-community/netbox/issues/7606) - Model transmit power for interfaces

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
* extras.Webhook
    * Added the `conditions` field
* virtualization.VMInterface
    * Added `bridge` field
    * Added `count_fhrp_groups` read-only field
