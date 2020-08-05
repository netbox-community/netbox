## Device Bays

Device bays represent a space or slot within a parent device in which a child device may be installed. For example, a 2U parent chassis might house four individual blade servers. The chassis would appear in the rack elevation as a 2U device with four device bays, and each server within it would be defined as a 0U device installed in one of the device bays. Child devices do not appear within rack elevations or count as consuming rack units.

Child devices are first-class Devices in their own right: That is, they are fully independent managed entities which don't share any control plane with the parent.  Just like normal devices, child devices have their own platform (OS), role, tags, and components.  LAG interfaces may not group interfaces belonging to different child devices.

!!! note
    Device bays are **not** suitable for modeling line cards (such as those commonly found in chassis-based routers and switches), as these components depend on the control plane of the parent device to operate. Instead, line cards and similarly non-autonomous hardware should be modeled as inventory items within a device, with any associated interfaces or other components assigned directly to the device.
