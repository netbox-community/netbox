# Virtual Chassis

A virtual chassis represents a set of devices which share a common control plane. A common example of this is a stack of switches which are connected and configured to operate as a single device. A virtual chassis must be assigned a name and may be assigned a domain.

Each device in the virtual chassis is referred to as a VC member, and assigned a position and (optionally) a priority. VC member devices commonly reside within the same rack, though this is not a requirement. One of the devices may be designated as the VC master: This device will typically be assigned a name, services, virtual interfaces, and other attributes related to managing the VC.
If a VC master is defined, interfaces from all VC members are displayed when navigating to its device interfaces view. This does not include other members interfaces declared as management-only.

!!! note
    It's important to recognize the distinction between a virtual chassis and a chassis-based device. A virtual chassis is **not** suitable for modeling a chassis-based switch with removable line cards (such as the Juniper EX9208), as its line cards are _not_ physically autonomous devices.
