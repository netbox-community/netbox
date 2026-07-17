# Cooling Feed

A cooling feed represents a coolant loop delivered from a [cooling source](./coolingsource.md) to a particular rack or coolant distribution unit (CDU). It is the cooling equivalent of a [power feed](./powerfeed.md). A [cooling intake](./coolingintake.md) on a device references the feed that supplies it (via the intake's `cooling_feed` field) rather than being cabled.

A single feed represents the entire loop, covering both the supply (cold) and return (warm) paths.

The rated flow rate recorded on a feed is a design specification (the intended operating envelope), not live telemetry; runtime readings belong in an external monitoring system.

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

The rated (design) coolant flow rate, expressed as a numeric value with a selectable unit (L/min, m³/h, or GPM).
