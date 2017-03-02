NetBox supports the assignment of resources to tenant organizations. Typically, these are used to represent individual customers of or internal departments within the organization using NetBox.

# Tenants

A tenant represents a discrete organization. The following objects can be assigned to tenants:

* Sites
* Racks
* Devices
* VRFs
* Prefixes
* IP addresses
* VLANs
* Circuits

If a prefix or IP address is not assigned to a tenant, it will appear to inherit the tenant to which its parent VRF is assigned, if any.

### Tenant Groups

Tenants can be grouped by type. For instance, you might create one group called "Customers" and one called "Acquisitions." The assignment of tenants to groups is optional.
