# Tenancy

Most core objects within NetBox's data model support _tenancy_. This is the association of an object with a particular tenant to convey ownership or dependency. For example, an enterprise might represent its internal business units as tenants, whereas a managed services provider might create a tenant in NetBox to represent each of its customers.

```mermaid
flowchart TD
    TenantGroup --> TenantGroup & Tenant
    Tenant --> Site & Device & Prefix & Circuit & ...
```

## Tenant Groups

Tenants can be grouped by any logic that your use case demands, and groups can nested recursively for maximum flexibility. For example, You might define a parent "Customers" group with child groups "Current" and "Past" within it. A tenant can be assigned to a group at any level within the hierarchy.

## Tenants

Typically, the tenant model is used to represent a customer or internal organization, however it can be used for whatever purpose meets your needs.

Most core objects within NetBox can be assigned to particular tenant, so this model provides a very convenient way to correlate ownership across object types. For example, each of your customers might have its own racks, devices, IP addresses, circuits and so on: These can all be easily tracked via tenant assignment.
