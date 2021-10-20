## Interfaces

Interfaces in NetBox represent network interfaces used to exchange data with connected devices. On modern networks, these are most commonly Ethernet, but other types are supported as well. Each interface must be assigned a type, and may optionally be assigned a MAC address, MTU, and IEEE 802.1Q mode (tagged or access). Each interface can also be enabled or disabled, and optionally designated as management-only (for out-of-band management).

!!! note
    Although devices and virtual machines both can have interfaces, a separate model is used for each. Thus, device interfaces have some properties that are not present on virtual machine interfaces and vice versa.

### Interface Types

Interfaces may be physical or virtual in nature, but only physical interfaces may be connected via cables. Cables can connect interfaces to pass-through ports, circuit terminations, or other interfaces. Virtual interfaces, such as 802.1Q-tagged subinterfaces, may be assigned to physical parent interfaces.

Physical interfaces may be arranged into a link aggregation group (LAG) and associated with a parent LAG (virtual) interface. LAG interfaces can be recursively nested to model bonding of trunk groups. Like all virtual interfaces, LAG interfaces cannot be connected physically.

### Wireless Interfaces

Wireless interfaces may additionally track the following attributes:

* **Role** - AP or station
* **Channel** - One of several standard wireless channels
* **Channel Frequency** - The transmit frequency
* **Channel Width** - Channel bandwidth

If a predefined channel is selected, the frequency and width attributes will be assigned automatically. If no channel is selected, these attributes may be defined manually.

### IP Address Assignment

IP addresses can be assigned to interfaces. VLANs can also be assigned to each interface as either tagged or untagged. (An interface may have only one untagged VLAN.)
