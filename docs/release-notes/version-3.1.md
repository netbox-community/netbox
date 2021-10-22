## v3.1-beta1 (FUTURE)

!!! warning "PostgreSQL 10 Required"
    NetBox v3.1 requires PostgreSQL 10 or later.

### Breaking Changes

* The `tenant` and `tenant_id` filters for the Cable model now filter on the tenant assigned directly to each cable, rather than on the parent object of either termination.

### New Features

#### Contacts ([#1344](https://github.com/netbox-community/netbox/issues/1344))

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

#### Interface Bridging ([#6346](https://github.com/netbox-community/netbox/issues/6346))

A `bridge` field has been added to the interface model for devices and virtual machines. This can be set to reference another interface on the same parent device/VM to indicate a direct layer two bridging adjacency.

Multiple interfaces can be bridged to a single virtual interface to effect a bridge group. Alternatively, two physical interfaces can be bridged to one another, to effect an internal cross-connect.

### Enhancements

* [#1337](https://github.com/netbox-community/netbox/issues/1337) - Add WWN field to interfaces
* [#1943](https://github.com/netbox-community/netbox/issues/1943) - Relax uniqueness constraint on cluster names
* [#3839](https://github.com/netbox-community/netbox/issues/3839) - Add `airflow` field for devices types and devices
* [#6497](https://github.com/netbox-community/netbox/issues/6497) - Extend tag support to organizational models
* [#6711](https://github.com/netbox-community/netbox/issues/6711) - Add `longtext` custom field type with Markdown support
* [#6715](https://github.com/netbox-community/netbox/issues/6715) - Add tenant assignment for cables
* [#6874](https://github.com/netbox-community/netbox/issues/6874) - Add tenant assignment for locations
* [#7354](https://github.com/netbox-community/netbox/issues/7354) - Relax uniqueness constraints on region, site group, and location names
* [#7530](https://github.com/netbox-community/netbox/issues/7530) - Move device type component lists to separate views

### Other Changes

* [#7318](https://github.com/netbox-community/netbox/issues/7318) - Raise minimum required PostgreSQL version from 9.6 to 10

### REST API Changes

* Added the following endpoints for contacts:
    * `/api/tenancy/contact-assignments/`
    * `/api/tenancy/contact-groups/`
    * `/api/tenancy/contact-roles/`
    * `/api/tenancy/contacts/`
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
* dcim.Cable
    * Added `tenant` field
* dcim.Device
    * Added `airflow` field
* dcim.DeviceType
    * Added `airflow` field 
* dcim.Interface
    * Added `bridge` field
    * Added `wwn` field
* dcim.Location
    * Added `tenant` field
* virtualization.VMInterface
    * Added `bridge` field
