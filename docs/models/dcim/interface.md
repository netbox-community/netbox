## Interfaces

Interfaces in NetBox represent network interfaces used to exchange data with connected devices. On modern networks, these are most commonly Ethernet, but other types are supported as well. Each interface must be assigned a type, and may optionally be assigned a MAC address, MTU, and IEEE 802.1Q mode (tagged or access). Each interface can also be enabled or disabled, and optionally designated as management-only (for out-of-band management).

Interfaces may be physical or virtual in nature, but only physical interfaces may be connected via cables. Cables can connect interfaces to pass-through ports, circuit terminations, or other interfaces.

Physical interfaces may be arranged into a link aggregation group (LAG) and associated with a parent LAG (virtual) interface. LAG interfaces can be recursively nested to model bonding of trunk groups. Like all virtual interfaces, LAG interfaces cannot be connected physically.

IP addresses can be assigned to interfaces. VLANs can also be assigned to each interface as either tagged or untagged. (An interface may have only one untagged VLAN.)

!!! note
    Although devices and virtual machines both can have interfaces, a separate model is used for each. Thus, device interfaces have some properties that are not present on virtual machine interfaces and vice versa.
