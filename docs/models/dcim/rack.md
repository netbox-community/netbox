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

### Type

A rack can be designated as one of the following types:

* 2-post frame
* 4-post frame
* 4-post cabinet
* Wall-mounted frame
* Wall-mounted cabinet

### Width

The canonical distance between the two vertical rails on a face. (This is typically 19 inches, however other standard widths exist.)

### Height

The height of the rack, measured in units.

### Outer Dimensions

The external width and depth of the rack can be tracked to aid in floorplan calculations. These measurements must be designated in either millimeters or inches.

### Mounting Depth

The maximum depth of a mounted device that the rack can accommodate, in millimeters. For four-post frames or cabinets, this is the horizontal distance between the front and rear vertical rails. (Note that this measurement does _not_ include space between the rails and the cabinet doors.)

### Weight

The numeric weight of the rack, including a unit designation (e.g. 10 kilograms or 20 pounds).

### Maximum Weight

The maximum total weight capacity for all installed devices, inclusive of the rack itself.

### Descending Units

If selected, the rack's elevation will display unit 1 at the top of the rack. (Most racks use ascending numbering, with unit 1 assigned to the bottommost position.)
