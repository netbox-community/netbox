# Power Ports

A power port is a device component which draws power from some external source (e.g. an upstream [power outlet](./poweroutlet.md)), and generally represents a power supply internal to a device.

!!! tip
    Like most device components, power ports are instantiated automatically from [power port templates](./powerporttemplate.md) assigned to the selected device type when a device is created.

## Fields

### Device

The device to which this power port belongs.

### Module

The installed module within the assigned device to which this power port belongs (optional).

### Name

The name of the power port. Must be unique to the parent device.

### Label

An alternative physical label identifying the power port.

### Type

The type of power port.

### Maximum Draw

The maximum amount of power this port consumes (in watts).

!!! info
    When creating a power port on a device which is mapped to outlets and supplies power to downstream devices, the maximum and allocated draw numbers should be left blank. Utilization will be calculated by taking the sum of all power ports of devices connected downstream.

### Allocated Draw

The budgeted amount of power this port consumes (in watts).

### Mark Connected

If selected, this component will be treated as if a cable has been connected.
