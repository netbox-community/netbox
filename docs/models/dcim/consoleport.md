# Console Ports

A console port provides connectivity to the physical console of a device. These are typically used for temporary access by someone who is physically near the device, or for remote out-of-band access provided via a networked console server.

!!! tip
    Like most device components, console ports are instantiated automatically from [console port templates](./consoleporttemplate.md) assigned to the selected device type when a device is created.

## Fields

### Device

The device to which this console port belongs.

### Module

The installed module within the assigned device to which this console port belongs (optional).

### Name

The name of the console port. Must be unique to the parent device.

### Label

An alternative physical label identifying the console port.

### Type

The type of console port.

### Speed

Operating speed, in bits per second (bps).

### Mark Connected

If selected, this component will be treated as if a cable has been connected.
