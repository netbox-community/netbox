NetBox supports the concept of individual tenants within its parent organization. Typically, these are used to represent individual customers or internal departments.

# Tenants

A tenant represents a discrete organization. Certain resources within NetBox can be assigned to a tenant. This makes it very convenient to track which resources are assigned to which customers, for instance.

The following objects can be assigned to tenants:

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
