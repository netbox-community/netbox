# Power Outlets

Power outlets represent the outlets on a power distribution unit (PDU) or other device that supplies power to dependent devices. Each power port may be assigned a physical type, and may be associated with a specific feed leg (where three-phase power is used) and/or a specific upstream power port. This association can be used to model the distribution of power within a device.

For example, imagine a PDU with one power port which draws from a three-phase feed and 48 power outlets arranged into three banks of 16 outlets each. Outlets 1-16 would be associated with leg A on the port, and outlets 17-32 and 33-48 would be associated with legs B and C, respectively.

!!! tip
    Like most device components, power outlets are instantiated automatically from [power outlet templates](./poweroutlettemplate.md) assigned to the selected device type when a device is created.

## Fields

### Device

The device to which this power outlet belongs.

### Module

The installed module within the assigned device to which this power outlet belongs (optional).

### Name

The name of the power outlet. Must be unique to the parent device.

### Label

An alternative physical label identifying the power outlet.

### Type

The type of power outlet.

### Power Port

When modeling a device which redistributes power from an upstream supply, such as a power distribution unit (PDU), each power outlet should be mapped to the respective [power port](./powerport.md) on the device which supplies power. For example, a 24-outlet PDU may two power ports, each distributing power to 12 of its outlets.

### Feed Leg

This field is used to indicate to which leg of three-phase power circuit the outlet is bound. (This should be left blank for single-phase applications.)

### Mark Connected

If selected, this component will be treated as if a cable has been connected.
