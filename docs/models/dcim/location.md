# Locations

[Racks](./rack.md) and [devices](./device.md) can be grouped by location within a [site](./site.md). A location may represent a floor, room, cage, or similar organizational unit. Locations can be nested to form a hierarchy. For example, you may have floors within a site, and rooms within a floor.

## Fields

### Site

The parent [site](./site.md) to which this location belongs.

### Parent

The parent location of which this location is a child (optional).

### Name

A unique human-friendly name.

### Slug

A unique URL-friendly identifier. (This value can be used for filtering.)

### Status

The location's operational status.

!!! tip
    Additional statuses may be defined by setting `Location.status` under the [`FIELD_CHOICES`](../../configuration/data-validation.md#field_choices) configuration parameter.
