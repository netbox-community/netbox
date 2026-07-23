# Cooling Feed

A cooling feed represents a coolant loop delivered from a [cooling source](./coolingsource.md) to a particular rack or coolant distribution unit (CDU). The [cooling intakes](./coolingintake.md) a feed supplies are derived from the devices installed in the rack it serves, rather than referenced explicitly.

A single feed represents the entire loop, covering both the supply (cold) and return (warm) paths.

!!! tip
    In-rack cooling equipment — coolant distribution units (CDUs), manifolds, and rear-door heat exchangers (RDHx) — is modeled as an ordinary (typically zero-U) [device](./device.md) installed in the rack. The device's make and model come from its [device type](./devicetype.md), and a [cooling intake](./coolingintake.md) component connects it to cooling. The feed serving such a device is derived from its rack.

## Fields

### Cooling Source

The [cooling source](./coolingsource.md) which supplies this feed.

### Rack

The [rack](./rack.md) which this feed serves (optional).

### Name

The feed's name or identifier. Must be unique to the assigned cooling source.

### Status

The feed's operational status.

!!! tip
    Additional statuses may be defined by setting `CoolingFeed.status` under the [`FIELD_CHOICES`](../../configuration/data-validation.md#field_choices) configuration parameter.

### Cooling Capacity

The heat-removal capacity of the feed, in kilowatts (kW).

### Rated Flow Rate

The rate of coolant flow supported by the feed, expressed as a numeric value with a selectable unit (L/min, m³/h, or GPM).
