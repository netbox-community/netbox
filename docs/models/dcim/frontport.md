# Front Ports

Front ports are pass-through ports which represent physical cable connections that comprise part of a longer path. For example, the ports on the front face of a UTP patch panel would be modeled in NetBox as front ports. Each port is assigned a physical type, and must be mapped to a specific [rear port](./rearport.md) on the same device. A single rear port may be mapped to multiple front ports, using numeric positions to annotate the specific alignment of each.

!!! tip
    Like most device components, front ports are instantiated automatically from [front port templates](./frontporttemplate.md) assigned to the selected device type when a device is created.

## Fields

### Device

The device to which this port belongs.

### Module

The installed module within the assigned device to which this port belongs (optional).

### Name

The port's name. Must be unique to the parent device.

### Label

An alternative physical label identifying the port.

### Type

The port's termination type.

### Rear Ports

The rear port and position to which this front port maps.

!!! tip
    When creating multiple front ports using a patterned name (e.g. `Port [1-12]`), you may select the equivalent number of rear port-position mappings from the list.

### Color

The port's color (optional).

### Mark Connected

If selected, this component will be treated as if a cable has been connected.
