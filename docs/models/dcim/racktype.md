# Rack Types

!!! info "This feature was introduced in NetBox v4.1."

A rack type defines the physical characteristics of a particular model of [rack](./rack.md).

## Fields

### Manufacturer

The [manufacturer](./manufacturer.md) which produces this type of rack.

### Model

The model number assigned to this rack type by its manufacturer. Must be unique to the manufacturer.

### Slug

A unique URL-friendly representation of the model identifier. (This value can be used for filtering.)

### Form Factor

A rack can be designated as one of the following form factors:

* 2-post frame
* 4-post frame
* 4-post cabinet
* Wall-mounted frame
* Wall-mounted cabinet

### Width

The canonical distance between the two vertical rails on a face. (This is typically 19 inches, however other standard widths exist.)

### Height

The height of the rack, measured in units.

### Starting Unit

The number of the numerically lowest unit in the rack. This value defaults to one, but may be higher in certain situations. For example, you may want to model only a select range of units within a shared physical rack (e.g. U13 through U24).

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
