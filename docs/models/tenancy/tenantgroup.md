# Tenant Groups

[Tenants](./tenant.md) can be organized by custom groups. For instance, you might create one group called "Customers" and one called "Departments." The assignment of a tenant to a group is optional.

Tenant groups may be nested recursively to achieve a multi-level hierarchy. For example, you might have a group called "Customers" containing subgroups of individual tenants grouped by product or account team.

A tenant group cannot be deleted if ungrouping its tenants, including those of any nested groups, would result in duplicate tenant names or slugs among ungrouped tenants.

## Fields

### Parent

The parent tenant group (if any).

### Name

A unique human-friendly name.

### Slug

A unique URL-friendly identifier. (This value can be used for filtering.)
