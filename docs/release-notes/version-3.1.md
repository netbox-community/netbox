## v3.1-beta1 (FUTURE)

!!! warning "PostgreSQL 10 Required"
    NetBox v3.1 requires PostgreSQL 10 or later.

### Breaking Changes

* The `tenant` and `tenant_id` filters for the Cable model now filter on the tenant assigned directly to each cable, rather than on the parent object of either termination.

#### Contacts ([#1344](https://github.com/netbox-community/netbox/issues/1344))

A set of new models for tracking contact information has been introduced within the tenancy app. Users may now create individual contact objects to be associated with various models within NetBox. Each contact has a name, title, email address, etc. Contacts can be arranged in hierarchical groups for ease of management.

When assigning a contact to an object, the user must select a predefined role (e.g. "billing" or "technical") and may optionally indicate a priority relative to other contacts associated with the object. There is no limit on how many contacts can be assigned to an object, nor on how many objects to which a contact can be assigned.

#### 

### Enhancements

* [#1337](https://github.com/netbox-community/netbox/issues/1337) - Add WWN field to interfaces
* [#1943](https://github.com/netbox-community/netbox/issues/1943) - Relax uniqueness constraint on cluster names
* [#3839](https://github.com/netbox-community/netbox/issues/3839) - Add `airflow` field for devices types and devices
* [#6711](https://github.com/netbox-community/netbox/issues/6711) - Add `longtext` custom field type with Markdown support
* [#6715](https://github.com/netbox-community/netbox/issues/6715) - Add tenant assignment for cables
* [#6874](https://github.com/netbox-community/netbox/issues/6874) - Add tenant assignment for locations
* [#7354](https://github.com/netbox-community/netbox/issues/7354) - Relax uniqueness constraints on region, site group, and location names

### Other Changes

* [#7318](https://github.com/netbox-community/netbox/issues/7318) - Raise minimum required PostgreSQL version from 9.6 to 10

### REST API Changes

* Added the following endpoints for contacts:
    * `/api/tenancy/contact-assignments/`
    * `/api/tenancy/contact-groups/`
    * `/api/tenancy/contact-roles/`
    * `/api/tenancy/contacts/`
* dcim.Cable
    * Added `tenant` field
* dcim.Device
    * Added `airflow` field
* dcim.DeviceType
    * Added `airflow` field 
* dcim.Interface
    * Added `wwn` field
* dcim.Location
    * Added `tenant` field
