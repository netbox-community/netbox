# Racks

The rack model represents a physical two- or four-post equipment rack in which [devices](./device.md) can be installed. Each rack must be assigned to a [site](./site.md), and may optionally be assigned to a [location](./location.md) within that site. Racks can also be organized by user-defined functional roles. The name and facility ID of each rack within a location must be unique.

Rack height is measured in *rack units* (U); racks are commonly between 42U and 48U tall, but NetBox allows you to define racks of arbitrary height. A toggle is provided to indicate whether rack units are in ascending (from the ground up) or descending order.

Each rack is assigned a name and (optionally) a separate facility ID. This is helpful when leasing space in a data center your organization does not own: The facility will often assign a seemingly arbitrary ID to a rack (for example, "M204.313") whereas internally you refer to is simply as "R113." A unique serial number and asset tag may also be associated with each rack.

## Fields

### Site

The [site](./site.md) to which the rack is assigned.

### Location

The [location](./location.md) within a site where the rack has been installed (optional).

### Name

The rack's name or identifier. Must be unique to the rack's location, if assigned.

### Rack Type

The [physical type](./racktype.md) of this rack. The rack type defines physical attributes such as height and weight.

### Status

Operational status.

!!! tip
    Additional statuses may be defined by setting `Rack.status` under the [`FIELD_CHOICES`](../../configuration/data-validation.md#field_choices) configuration parameter.

### Role

The functional [role](./rackrole.md) fulfilled by the rack.

### Facility ID

An alternative identifier assigned to the rack e.g. by the facility operator. This is helpful for tracking datacenter rack designations in a colocation facility.

### Serial Number

The unique physical serial number assigned to this rack.

### Asset Tag

A unique, locally-administered label used to identify hardware resources.

!!! note
    Some additional fields pertaining to physical attributes such as height and weight can also be defined on each rack, but should generally be defined instead on the [rack type](./racktype.md).
