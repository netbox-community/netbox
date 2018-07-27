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

Tenant assignment is used to signify ownership of an object in NetBox. As such, each object may only be owned by a single tenant. For example, if you have a firewall dedicated to a particular customer, you would assign it to the tenant which represents that customer. However, if the firewall serves multiple customers, it doesn't *belong* to any particular customer, so tenant assignment would not be appropriate.

### Tenant Groups

Tenants can be organized by custom groups. For instance, you might create one group called "Customers" and one called "Acquisitions." The assignment of tenants to groups is optional.
