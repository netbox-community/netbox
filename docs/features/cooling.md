# Cooling

As part of its DCIM feature set, NetBox supports modeling data center cooling infrastructure, from facility plant down to the coolant connections on individual devices. This is used to document liquid- and hybrid-cooled environments (chillers, cooling distribution units, manifolds, rear-door heat exchangers, and cold-plate servers) as a source of truth.

## Relationship to Power

The cooling stack deliberately mirrors the [power distribution](./power-tracking.md) model:

| Cooling | Power equivalent | Role |
|---|---|---|
| Cooling Source | Power Panel | Facility plant (the upstream origin) |
| Cooling Feed | Power Feed | A loop delivered to a rack |
| Cooling Intake | Power Port | A device-side consumer (draws coolant) |
| Cooling Outflow | Power Outlet | A device-side supply (feeds downstream equipment) |

There are two intentional differences from the power model:

- **Coolant connections are direct references, not cables.** Hoses are not structured cabling, so an intake references the outflow that supplies it directly, rather than through a cable. Tracing a loop is a walk along these references.
- **A feed represents the entire loop.** A single cooling feed covers both the supply (cold) and return (warm) paths of a loop, rather than modeling each direction separately.

## Cooling Sources

A [cooling source](../models/dcim/coolingsource.md) is the furthest upstream cooling element modeled in NetBox, representing a chiller, cooling tower, dry cooler, or CRAC/CRAH unit. Each source is associated with a site, and may optionally be associated with a particular location within that site. A cooling source is not a device; it represents external facility plant, and records the coolant (fluid type) and total rated cooling capacity for the loops it originates.

## Cooling Feeds

A [cooling feed](../models/dcim/coolingfeed.md) represents a coolant loop originating from a cooling source and serving a particular rack. Each feed records an operational status, a rated cooling capacity, and a rated (design) flow rate.

## Device Components

Devices participate in cooling through two component types, instantiated from templates on the device type just like power ports and outlets:

- A [cooling intake](../models/dcim/coolingintake.md) is a coolant intake on a device, such as a server cold-plate inlet or a CDU facility intake. It records the connector type, diameter, and rated maximum flow, and optionally references the upstream [cooling outflow](../models/dcim/coolingoutflow.md) that supplies it.
- A [cooling outflow](../models/dcim/coolingoutflow.md) is a coolant supply point on a device, such as a CDU or manifold outlet. It optionally references a parent cooling intake on the same device — the device takes coolant in through its intake and passes it back out through its outflow.

!!! tip "In-rack cooling equipment is modeled as a device"
    Coolant distribution units (CDUs), manifolds, and rear-door heat exchangers (RDHx) are modeled as ordinary (typically zero-U) [devices](../models/dcim/device.md) installed in the rack — exactly as a PDU is modeled as a device with power ports and outlets. The device's make and model come from its [device type](../models/dcim/devicetype.md), and its cooling connections are represented by cooling intake and outflow components. There is no dedicated CDU or RDHx model.

## Racks and Devices

Racks and devices carry lightweight cooling attributes independent of the feed/component topology:

- A [rack](../models/dcim/rack.md) records a **cooling capability** (air-only, liquid-capable, or liquid-required) and a **cooling capacity** in kilowatts, typically inherited from its rack type.
- A [device](../models/dcim/device.md) records a **cooling method** (air, liquid, hybrid, or immersion), inherited from its device type and overridable per device.

