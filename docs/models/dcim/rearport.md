# Rear Ports

Like [front ports](./frontport.md), rear ports are pass-through ports which represent the continuation of a path from one cable to the next. Each rear port is defined with its physical type and a number of positions: Rear ports with more than one position can be mapped to multiple front ports. This can be useful for modeling instances where multiple paths share a common cable (for example, six discrete two-strand fiber connections sharing a 12-strand MPO cable).

!!! note
    Front and rear ports need not necessarily reside on the actual front or rear device face. This terminology is used primarily to distinguish between the two components in a pass-through port pairing.

!!! tip
    Like most device components, rear ports are instantiated automatically from [rear port templates](./rearporttemplate.md) assigned to the selected device type when a device is created.

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

### Color

The port's color (optional).

### Positions

The number of [front ports](./frontport.md) to which this rear port can be mapped. For example, an MPO fiber termination cassette might have a single 12-strand rear port mapped to 12 discrete front ports, each terminating a single fiber strand. (For rear ports which map directly to a single front port, set this to `1`.)

### Mark Connected

If selected, this component will be treated as if a cable has been connected.
