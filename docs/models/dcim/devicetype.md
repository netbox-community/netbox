# Device Types

A device type represents a particular make and model of hardware that exists in the real world. Device types define the physical attributes of a device (rack height and depth) and its individual components (console, power, and network interfaces).

Device types are instantiated as devices installed within racks. For example, you might define a device type to represent a Juniper EX4300-48T network switch with 48 Ethernet interfaces. You can then create multiple devices of this type named "switch1," "switch2," and so on. Each device will inherit the components (such as interfaces) of its device type at the time of creation. (However, changes made to a device type will **not** apply to instances of that device type retroactively.)

Some devices house child devices which share physical resources, like space and power, but which functional independently from one another. A common example of this is blade server chassis. Each device type is designated as one of the following:

* A parent device (which has device bays)
* A child device (which must be installed in a device bay)
* Neither

!!! note
    This parent/child relationship is **not** suitable for modeling chassis-based devices, wherein child members share a common control plane.

    For that application you should create a single Device for the chassis, and add Interfaces directly to it.  Interfaces can be created in bulk using range patterns, e.g. "Gi1/[1-24]".

    Add Inventory Items if you want to record the line cards themselves as separate entities.  There is no explicit relationship between each interface and its line card, but it may be implied by the naming (e.g. interfaces "Gi1/x" are on line card 1)
