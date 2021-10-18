# Contacts

A contact represent an individual or group that has been associated with an object in NetBox for administrative reasons. For example, you might assign one or more operational contacts to each site. Contacts can be arranged within nested contact groups.

Each contact must include a name, which is unique to its parent group (if any). The following optional descriptors are also available:

* Title
* Phone
* Email
* Address

## Contact Assignment

Each contact can be assigned to one or more objects, allowing for the efficient reuse of contact information. When assigning a contact to an object, the user may optionally specify a role and/or priority (primary, secondary, tertiary, or inactive) to better convey the nature of the contact's relationship to the assigned object.

The following models support the assignment of contacts:

* circuits.Circuit
* circuits.Provider
* dcim.Device
* dcim.Location
* dcim.Manufacturer
* dcim.PowerPanel
* dcim.Rack
* dcim.Region
* dcim.Site
* dcim.SiteGroup
* tenancy.Tenant
* virtualization.Cluster
* virtualization.ClusterGroup
* virtualization.VirtualMachine
