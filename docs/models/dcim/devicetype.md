# Device Types

A device type represents a particular make and model of hardware that exists in the real world. Device types define the physical attributes of a device (rack height and depth) and its individual components (console, power, network interfaces, and so on).

Device types are instantiated as devices installed within sites and/or equipment racks. For example, you might define a device type to represent a Juniper EX4300-48T network switch with 48 Ethernet interfaces. You can then create multiple _instances_ of this type named "switch1," "switch2," and so on. Each device will automatically inherit the components (such as interfaces) of its device type at the time of creation. However, changes made to a device type will **not** apply to instances of that device type retroactively.

Some devices house child devices which share physical resources, like space and power, but which functional independently from one another. A common example of this is blade server chassis. Each device type is designated as one of the following:

* A parent device (which has device bays)
* A child device (which must be installed within a device bay)
* Neither

!!! note
    This parent/child relationship is **not** suitable for modeling chassis-based devices, wherein child members share a common control plane. Instead, line cards and similarly non-autonomous hardware should be modeled as inventory items within a device, with any associated interfaces or other components assigned directly to the device.
