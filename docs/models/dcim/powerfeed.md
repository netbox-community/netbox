# Power Feed

A power feed represents the distribution of power from a [power panel](./powerpanel.md) to a particular [device](./device.md), typically a power distribution unit (PDU). The [power port](./powerport.md) (inlet) on a device can be connected via a cable to a power feed. A power feed may optionally be assigned to a rack to allow more easily tracking the distribution of power among racks.

## Fields

### Power Panel

The [power panel](./powerpanel.md) which supplies upstream power to this feed.

### Rack

The [rack](./rack.md) within which this feed delivers power (optional).

### Name

The feed's name or other identifier. Must be unique to the assigned power panel.

### Status

The feed's operational status.

!!! tip
    Additional statuses may be defined by setting `PowerFeed.status` under the [`FIELD_CHOICES`](../../configuration/data-validation.md#field_choices) configuration parameter.

### Type

In redundant environments, each power feed can be designated as providing either primary or redundant power. (In environment with only one power source, all power feeds should be designated as primary.)

### Mark Connected

If selected, the power feed will be treated as if a cable has been connected.

### Supply

Electrical current type (AC or DC).

### Voltage

Operating circuit voltage, in volts.

### Amperage

Operation circuit amperage, in amperes.

### Phase

Indicates whether the circuit provides single- or three-phase power.

### Max Utilization

The maximum safe utilization of the feed, expressed as a percentage of the total available power. (Typically this will be set to around 80%, to avoid tripping a breaker during heaving spikes in current draw.)

!!! info
    The power utilization of a rack is calculated when one or more power feeds are assigned to the rack and connected to devices that draw power.
