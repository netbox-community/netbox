# Cooling Feed

A cooling feed represents a coolant loop delivered from a [cooling source](./coolingsource.md) to a particular rack or coolant distribution unit (CDU). It is the cooling equivalent of a [power feed](./powerfeed.md). A [cooling port](./coolingport.md) on a device references the feed that supplies it (via the port's `cooling_feed` field) rather than being cabled.

Because a coolant loop has both a cold (supply) and a warm (return) side, supply and return are represented as separate feeds so that each path can be traced independently.

Flow rate and temperatures recorded on a feed are design specifications (the intended operating envelope), not live telemetry; runtime readings belong in an external monitoring system.

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

### Flow Direction

Indicates whether the feed carries supply (cold) or return (warm) coolant.

### Fluid Type

The coolant used in the loop (e.g. water, water/glycol, dielectric fluid, or refrigerant).

### Cooling Capacity

The heat-removal capacity of the feed, in kilowatts (kW).

### Rated Flow Rate

The rated (design) coolant flow rate, expressed as a numeric value with a selectable unit (L/min, m³/h, or GPM).

### Supply / Return Temperature

The design supply and return coolant temperatures, each expressed in the selected temperature unit.

### Temperature Unit

The unit (Celsius or Fahrenheit) in which the supply and return temperatures are expressed.
