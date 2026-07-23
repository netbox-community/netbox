# Cooling Source

A cooling source represents a facility-level source of cooling, such as a chiller, cooling tower, or dry cooler. It serves as the upstream origin for one or more [cooling feeds](./coolingfeed.md) which distribute coolant to racks and devices. A cooling source is not modeled as a device; it represents external facility plant.

## Fields

### Site

The [site](../../models/dcim/site.md) at which the cooling source is located.

### Location

The [location](./location.md) within the site where the cooling source resides (optional).

### Name

The cooling source's name or identifier. Must be unique to the assigned site.

### Type

The type of cooling plant (e.g. chiller, cooling tower, dry cooler, CRAC, or CRAH).

### Status

The operational status of the cooling source.

!!! tip
    Additional statuses may be defined by setting `CoolingSource.status` under the [`FIELD_CHOICES`](../../configuration/data-validation.md#field_choices) configuration parameter.

### Fluid Type

The coolant used by the source (e.g. water, water/glycol, dielectric fluid, or refrigerant).

### Cooling Capacity

The total heat-removal capacity of the source, expressed in kilowatts (kW).
