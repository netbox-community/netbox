## Interfaces

[Virtual machine](./virtualmachine.md) interfaces behave similarly to device [interfaces](../dcim/interface.md): They can be assigned to VRFs, may have IP addresses, VLANs, and services attached to them, and so on. However, given their virtual nature, they lack properties pertaining to physical attributes. For example, VM interfaces do not have a physical type and cannot have cables attached to them.

## Fields

### Virtual Machine

The [virtual machine](./virtualmachine.md) to which this interface is assigned.

### Name

The interface's name. Must be unique to the assigned VM.

### Parent Interface

Identifies the parent interface of a subinterface (e.g. used to employ encapsulation).

!!! note
    An interface with one or more child interfaces assigned cannot be deleted until all its child interfaces have been deleted or reassigned.

### Bridged Interface

An interface on the same VM with which this interface is bridged.

### Enabled

If not selected, this interface will be treated as disabled/inoperative.

### MAC Address

The 48-bit MAC address (for Ethernet interfaces).

### MTU

The interface's configured maximum transmissible unit (MTU).

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

### VRF

The [virtual routing and forwarding](../ipam/vrf.md) instance to which this interface is assigned.

### VLAN Translation Policy

The [VLAN translation policy](../ipam/vlantranslationpolicy.md) that applies to this interface (optional).
