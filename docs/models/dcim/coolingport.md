# Cooling Ports

A cooling port is a device component which represents a coolant intake or outlet on a device, such as a server cold-plate inlet or a coolant distribution unit (CDU) intake. A cooling port can be connected via a cooling hose cable to a [cooling outlet](./coolingoutlet.md) or a [cooling feed](./coolingfeed.md).

!!! tip
    Like most device components, cooling ports are instantiated automatically from [cooling port templates](./coolingporttemplate.md) assigned to the selected device type when a device is created.

## Fields

### Device

The device to which this cooling port belongs.

### Module

The installed module within the assigned device to which this cooling port belongs (optional).

### Name

The name of the cooling port. Must be unique to the parent device.

### Label

An alternative physical label identifying the cooling port.

### Type

Indicates whether the port carries supply (cold) or return (warm) coolant.

### Connector Type

The physical coolant connector type (e.g. UQD, UQDB, QDC, camlock, or threaded NPT/BSP).

### Diameter

The nominal connector diameter.

### Maximum Flow

The maximum coolant flow rate this port supports, in litres per minute (L/min).

### Heat Capacity

The heat-removal capacity of this port, in kilowatts (kW).

### Mark Connected

If selected, this component will be treated as if a cable has been connected.
