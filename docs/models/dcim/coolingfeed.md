# Cooling Feed

A cooling feed represents a coolant loop delivered from a [cooling source](./coolingsource.md) to a particular rack or coolant distribution unit (CDU). It is the cooling equivalent of a [power feed](./powerfeed.md). A [cooling port](./coolingport.md) on a device can be connected via a cooling hose cable to a cooling feed.

Because a coolant loop has both a cold (supply) and a warm (return) side, supply and return are represented as separate feeds so that each path can be traced independently.

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

### Type

Indicates whether the feed carries supply (cold) or return (warm) coolant.

### Fluid Type

The coolant used in the loop (e.g. water, water/glycol, dielectric fluid, or refrigerant).

### Cooling Capacity

The heat-removal capacity of the feed, in kilowatts (kW).

### Flow Rate

The coolant flow rate, in litres per minute (L/min).

### Pressure

The operating pressure of the loop, in kilopascals (kPa).

### Supply / Return Temperature

The supply and return coolant temperatures, in degrees Celsius (°C).

### Mark Connected

If selected, the cooling feed will be treated as if a cable has been connected.
