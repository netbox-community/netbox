## Device Bays

Device bays represent the ability of a device to house child devices. For example, you might install four blade servers into a 2U chassis. The chassis would appear in the rack elevation as a 2U device with four device bays. Each server within it would be defined as a 0U device installed in one of the device bays. Child devices do not appear within rack elevations or the "Non-Racked Devices" list within the rack view.

Child devices are first-class Devices in their own right: that is, fully independent managed entities which don't share any control plane with the parent.  Just like normal devices, child devices have their own platform (OS), role, tags, and interfaces.  You cannot create a LAG between interfaces in different child devices.

Therefore, Device bays are **not** suitable for modeling chassis-based switches and routers.  These should instead be modeled as a single Device, with the line cards as Inventory Items.
