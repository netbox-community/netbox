# Tenants

A tenant represents a discrete grouping of resources used for administrative purposes. Typically, tenants are used to represent individual customers or internal departments within an organization. The following objects can be assigned to tenants:

* Sites
* Racks
* Rack reservations
* Devices
* VRFs
* Prefixes
* IP addresses
* VLANs
* Circuits
* Clusters
* Virtual machines

Tenant assignment is used to signify the ownership of an object in NetBox. As such, each object may only be owned by a single tenant. For example, if you have a firewall dedicated to a particular customer, you would assign it to the tenant which represents that customer. However, if the firewall serves multiple customers, it doesn't *belong* to any particular customer, so tenant assignment would not be appropriate.
