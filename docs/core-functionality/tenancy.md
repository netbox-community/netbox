# Tenants

A tenant represents a discrete entity for administrative purposes. Typically, tenants are used to represent individual customers or internal departments within an organization. The following objects can be assigned to tenants:

* Sites
* Racks
* Rack reservations
* Devices
* VRFs
* Prefixes
* IP addresses
* VLANs
* Circuits
* Virtual machines

If a prefix or IP address is not assigned to a tenant, it will appear to inherit the tenant to which its parent VRF is assigned, if any.

### Tenant Groups

Tenants can be organized by custom groups. For instance, you might create one group called "Customers" and one called "Acquisitions." The assignment of tenants to groups is optional.
