# Interfaces

Interfaces in NetBox represent network interfaces used to exchange data with connected devices. On modern networks, these are most commonly Ethernet, but other types are supported as well. IP addresses and VLANs can be assigned to interfaces.

!!! tip
    Like most device components, interfaces are instantiated automatically from [interface templates](./interfacetemplate.md) assigned to the selected device type when a device is created.

!!! note
    Although both devices and virtual machines both can have interfaces assigned, a separate model is used for each. Thus, device interfaces have some properties that are not present on virtual machine interfaces and vice versa.

## Fields

### Device

The device to which this interface belongs.

### Module

The installed module within the assigned device to which this interface belongs (optional).

### Name

The name of the interface, as reported by the device's operating system. Must be unique to the parent device.

### Label

An alternative physical label identifying the interface.

### Type

The type of interface. Interfaces may be physical or virtual in nature, but only physical interfaces may be connected via cables.

!!! note
    The interface type refers to the physical termination or port on the device. Interfaces which employ a removable optic or similar transceiver should be defined to represent the type of transceiver in use, irrespective of the physical termination to that transceiver.

### Speed

The operating speed, in kilobits per second (kbps).

### Duplex

The operation duplex (full, half, or auto).

### VRF

The [virtual routing and forwarding](../ipam/vrf.md) instance to which this interface is assigned.

### MAC Address

The 48-bit MAC address (for Ethernet interfaces).

### WWN

The 64-bit world-wide name (for Fibre Channel interfaces).

### MTU

The interface's configured maximum transmissible unit (MTU).

### Transmit Power

The interface's configured output power, in dBm (for optical interfaces).

### Enabled

If not selected, this interface will be treated as disabled/inoperative.

### Management Only

Designates the interface as handling management traffic only (e.g. for out-of-band management connections).

### Mark Connected

If selected, this component will be treated as if a cable has been connected.

### Parent Interface

Virtual interfaces can be bound to a physical parent interface. This is helpful for modeling virtual interfaces which employ encapsulation on a physical interface, such as an 802.1Q VLAN-tagged subinterface.

!!! note
    An interface with one or more child interfaces assigned cannot be deleted until all its child interfaces have been deleted or reassigned.

### Bridged Interface

Interfaces can be bridged to other interfaces on a device in two manners: symmetric or grouped.

* **Symmetric:** For example, eth0 is bridged to eth1, and eth1 is bridged to eth0. This effects a point-to-point bridge between the two interfaces, which NetBox will follow when tracing cable paths.
* **Grouped:** Multiple interfaces are each bridged to a common virtual bridge interface, effecting a multiaccess bridged segment. NetBox cannot follow these relationships when tracing cable paths, because no forwarding information is available.

### LAG Interface

Physical interfaces may be arranged into link aggregation groups (LAGs, also known as "trunks") and associated with a parent LAG (virtual) interface. LAG interfaces can be recursively nested to model bonding of trunk groups. Like all virtual interfaces, LAG interfaces cannot be connected physically.

### PoE Mode

The power over Ethernet (PoE) mode for this interface. (This field must be left empty for interfaces which do not support PoE.) Choices include:

* Powered device (PD)
* Power-supplying equipment (PSE)

### PoE Type

The classification of PoE transmission supported, for PoE-enabled interfaces. This can be one of the listed IEEE 802.3 standards, or a passive setting (24 or 48 volts across two or four pairs).

### 802.1Q Mode

For switched Ethernet interfaces, this identifies the 802.1Q encapsulation strategy in effect. Options include:

* **Access:** All traffic is assigned to a single VLAN, with no tagging.
* **Tagged:** One untagged "native" VLAN is allowed, as well as any number of tagged VLANs.
* **Tagged (all):** Implies that all VLANs are carried by the interface. One untagged VLAN may be designated.

This field must be left blank for routed interfaces which do employ 802.1Q encapsulation.

### Untagged VLAN

The "native" (untagged) VLAN for the interface. Valid only when one of the above 802.1Q mode is selected.

### Tagged VLANs

The tagged VLANs which are configured to be carried by this interface. Valid only for the "tagged" 802.1Q mode above.

### Q-in-Q SVLAN

The assigned service VLAN (for Q-in-Q/802.1ad interfaces).

### Wireless Role

Indicates the configured role for wireless interfaces (access point or station).

### Wireless Channel

The configured channel for wireless interfaces.

!!! tip
    Selecting one of the pre-defined wireless channels will automatically populate the channel frequency and width upon saving the interface.

### Channel Frequency

The configured operation frequency of a wireless interface, in MHz. This is typically inferred by the configured channel above, but may be set manually e.g. to identify a licensed channel not available for general use.

### Channel Width

The configured channel width of a wireless interface, in MHz. This is typically inferred by the configured channel above, but may be set manually e.g. to identify a licensed channel not available for general use.

### Wireless LANs

The [wireless LANs](../wireless/wirelesslan.md) for which this interface carries traffic. (Valid for wireless interfaces only.)

### VLAN Translation Policy

The [VLAN translation policy](../ipam/vlantranslationpolicy.md) that applies to this interface (optional).
