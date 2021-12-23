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

#### Automatic Provisioning of Next Available VLANs ([#2658](https://github.com/netbox-community/netbox/issues/2658))

A new REST API endpoint has been added at `/api/ipam/vlan-groups/<pk>/available-vlans/`. A GET request to this endpoint will return a list of available VLANs within the group. A POST request can be made to this endpoint specifying the name(s) of one or more VLANs to create within the group, and their VLAN IDs will be assigned automatically.

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

### Enhancements

* [#7650](https://github.com/netbox-community/netbox/issues/7650) - Add support for local account password validation
* [#7759](https://github.com/netbox-community/netbox/issues/7759) - Improved the user preferences form
* [#8168](https://github.com/netbox-community/netbox/issues/8168) - Add `min_vid` and `max_vid` fields to VLAN group

### Other Changes

* [#7731](https://github.com/netbox-community/netbox/issues/7731) - Require Python 3.8 or later
* [#7743](https://github.com/netbox-community/netbox/issues/7743) - Remove legacy ASN field from site model
* [#7748](https://github.com/netbox-community/netbox/issues/7748) - Remove legacy contact fields from site model
* [#8031](https://github.com/netbox-community/netbox/issues/8031) - Remove automatic redirection of legacy slug-based URLs

### REST API Changes

* Added the following endpoints for modules & module types:
    * `/api/dcim/modules/`
    * `/api/dcim/module-bays/`
    * `/api/dcim/module-bay-templates/`
    * `/api/dcim/module-types/`
* dcim.ConsolePort
    * Added `module` field
* dcim.ConsoleServerPort
    * Added `module` field
* dcim.FrontPort
    * Added `module` field
* dcim.Interface
    * Added `module` field
* dcim.PowerPort
    * Added `module` field
* dcim.PowerOutlet
    * Added `module` field
* dcim.RearPort
    * Added `module` field
* dcim.Site
    * Removed the `asn`, `contact_name`, `contact_phone`, and `contact_email` fields
* ipam.VLANGroup
    * Added the `/availables-vlans/` endpoint
    * Added the `min_vid` and `max_vid` fields
