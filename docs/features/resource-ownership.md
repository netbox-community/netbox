# Resource Ownership

!!! info "This feature was introduced in NetBox v4.5."

Most objects in NetBox can be assigned an owner. An owner is a set of users and/or groups who are responsible for the administration of associated objects. For example, you might designate the operations team at a site as the owner for all prefixes and VLANs deployed at that site. The users and groups assigned to an owner are referred to as its members.

!!! note
    Ownership of an object should not be confused with the concept of [tenancy](./tenancy.md), which indicates the dedication of an object to a specific tenant. For instance, a tenant might represent a customer served by the object, whereas an owner typically represents a set of internal users responsible for the management of the object.

Owners can be organized into groups for easier management.
