# Console Server Ports

A console server is a device which provides remote access to the local consoles of connected devices. They are typically used to provide remote out-of-band access to network devices, and generally connect to [console ports](./consoleport.md).

!!! tip
    Like most device components, console server ports are instantiated automatically from [console server port templates](./consoleserverporttemplate.md) assigned to the selected device type when a device is created.

## Fields

### Device

The device to which this console server port belongs.

### Module

The installed module within the assigned device to which this console server port belongs (optional).

### Name

The name of the console server port. Must be unique to the parent device.

### Label

An alternative physical label identifying the console server port.

### Type

The type of console server port.

### Speed

Operating speed, in bits per second (bps).

### Mark Connected

If selected, this component will be treated as if a cable has been connected.
