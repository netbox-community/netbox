# NetBox v3.2

## v3.2.0 (FUTURE)

!!! warning "Python 3.8 or Later Required"
    NetBox v3.2 requires Python 3.8 or later.

### Breaking Changes

* Automatic redirection of legacy slug-based URL paths has been removed.
* The `asn` field has been removed from the site model. Please use the ASN model introduced in NetBox v3.1 to track ASN assignments for sites.
* The `asn` query filter for sites now matches against the AS number of assigned ASNs.
* The `contact_name`, `contact_phone`, and `contact_email` fields have been removed from the site model. Please use the new contact model introduced in NetBox v3.1 to store contact information for sites.

### New Features

#### Service Templates ([#1591](https://github.com/netbox-community/netbox/issues/1591))

A new service template model has been introduced to assist in standardizing the definition and application of layer four services to devices and virtual machines. As an alternative to manually defining a name, protocol, and port(s) each time a service is created, a user now has the option of selecting a pre-defined template from which these values will be populated.

#### Automatic Provisioning of Next Available VLANs ([#2658](https://github.com/netbox-community/netbox/issues/2658))

A new REST API endpoint has been added at `/api/ipam/vlan-groups/<pk>/available-vlans/`. A GET request to this endpoint will return a list of available VLANs within the group. A POST request can be made to this endpoint specifying the name(s) of one or more VLANs to create within the group, and their VLAN IDs will be assigned automatically.

#### Inventory Item Roles ([#3087](https://github.com/netbox-community/netbox/issues/3087))

A new model has been introduced to represent function roles for inventory items, similar to device roles. The assignment of roles to inventory items is optional.

#### Custom Object Fields ([#7006](https://github.com/netbox-community/netbox/issues/7006))

Two new types of custom field have been added: object and multi-object. These can be used to associate objects with other objects in NetBox. For example, you might create a custom field named `primary_site` on the tenant model so that a particular site can be associated with each tenant as its primary. The multi-object custom field type allows for the assignment of one or more objects of the same type.

Custom field object assignment is fully supported in the REST API, and functions similarly to normal foreign key relations. Nested representations are provided for each custom field object.

#### Modules & Module Types ([#7844](https://github.com/netbox-community/netbox/issues/7844))

Several new models have been added to support field-replaceable device modules, such as those within a chassis-based switch or router. Similar to devices, each module is instantiated from a user-defined module type, and can have components associated with it. These components become available to the parent device once the module has been installed within a module bay. This makes it very convenient to replicate the addition and deletion of device components as modules are installed and removed. 

Automatic renaming of module components is also supported. When a new module is created, any occurrence of the string `{module}` in a component name will be replaced with the position of the module bay into which the module is being installed.

#### Custom Status Choices ([#8054](https://github.com/netbox-community/netbox/issues/8054))

Custom choices can be now added to most status fields in NetBox. This is done by defining the `FIELD_CHOICES` configuration parameter to map field identifiers to an iterable of custom choices. These choices are populated automatically when NetBox initializes. For example, the following will add three custom choices for the site status field:

```python
FIELD_CHOICES = {
    'dcim.Site.status': (
        ('foo', 'Foo'),
        ('bar', 'Bar'),
        ('baz', 'Baz'),
    )
}
```

#### Inventory Item Templates ([#8118](https://github.com/netbox-community/netbox/issues/8118))

Inventory items can now be templatized on a device type similar to the other component types. This enables users to better pre-model fixed hardware components.

Inventory item templates can be arranged hierarchically within a device type, and may be assigned to other components. These relationships will be mirrored when instantiating inventory items on a newly-created device.

### Enhancements

* [#5429](https://github.com/netbox-community/netbox/issues/5429) - Enable toggling the placement of table paginators
* [#6954](https://github.com/netbox-community/netbox/issues/6954) - Remember users' table ordering preferences
* [#7650](https://github.com/netbox-community/netbox/issues/7650) - Add support for local account password validation
* [#7679](https://github.com/netbox-community/netbox/issues/7679) - Add actions menu to all object tables
* [#7681](https://github.com/netbox-community/netbox/issues/7681) - Add `service_id` field for provider networks
* [#7759](https://github.com/netbox-community/netbox/issues/7759) - Improved the user preferences form
* [#7784](https://github.com/netbox-community/netbox/issues/7784) - Support cluster type assignment for config contexts
* [#7846](https://github.com/netbox-community/netbox/issues/7846) - Enable associating inventory items with device components
* [#7852](https://github.com/netbox-community/netbox/issues/7852) - Enable assigning interfaces to VRFs
* [#8168](https://github.com/netbox-community/netbox/issues/8168) - Add `min_vid` and `max_vid` fields to VLAN group
* [#8295](https://github.com/netbox-community/netbox/issues/8295) - Webhook URLs can now be templatized
* [#8296](https://github.com/netbox-community/netbox/issues/8296) - Allow disabling custom links
* [#8307](https://github.com/netbox-community/netbox/issues/8307) - Add `data_type` indicator to REST API serializer for custom fields

### Other Changes

* [#7731](https://github.com/netbox-community/netbox/issues/7731) - Require Python 3.8 or later
* [#7743](https://github.com/netbox-community/netbox/issues/7743) - Remove legacy ASN field from site model
* [#7748](https://github.com/netbox-community/netbox/issues/7748) - Remove legacy contact fields from site model
* [#8031](https://github.com/netbox-community/netbox/issues/8031) - Remove automatic redirection of legacy slug-based URLs

### REST API Changes

* Added the following endpoints:
    * `/api/dcim/inventory-item-roles/`
    * `/api/dcim/inventory-item-templates/`
    * `/api/dcim/modules/`
    * `/api/dcim/module-bays/`
    * `/api/dcim/module-bay-templates/`
    * `/api/dcim/module-types/`
    * `/api/extras/service-templates/`
* circuits.ProviderNetwork
    * Added `service_id` field
* dcim.ConsolePort
    * Added `module` field
* dcim.ConsoleServerPort
    * Added `module` field
* dcim.FrontPort
    * Added `module` field
* dcim.Interface
    * Added `module` and `vrf` fields
* dcim.InventoryItem
    * Added `component_type`, `component_id`, and `role` fields
    * Added read-only `component` field
* dcim.PowerPort
    * Added `module` field
* dcim.PowerOutlet
    * Added `module` field
* dcim.RearPort
    * Added `module` field
* dcim.Site
    * Removed the `asn`, `contact_name`, `contact_phone`, and `contact_email` fields
* extras.ConfigContext
    * Add `cluster_types` field
* extras.CustomField
    * Added `object_type` field
* extras.CustomLink
    * Added `enabled` field
* ipam.VLANGroup
    * Added the `/availables-vlans/` endpoint
    * Added the `min_vid` and `max_vid` fields
