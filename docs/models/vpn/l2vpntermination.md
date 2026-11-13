# L2VPN Termination

A L2VPN termination is the attachment of an [L2VPN](./l2vpn.md) to an [interface](../dcim/interface.md), [VLAN](../ipam/vlan.md), or [IP address](../ipam/ipaddress.md). Note that the L2VPNs of the following types may have only two terminations assigned to them:

* VPWS
* EPL
* EP-LAN
* EP-TREE

## Fields

### L2VPN

The [L2VPN](./l2vpn.md) instance.

### VLAN, Interface, or IP Address

The [VLAN](../ipam/vlan.md), [device interface](../dcim/interface.md), [virtual machine interface](../virtualization/virtualmachine.md), or [IP address](../ipam/ipaddress.md) attached to the L2VPN.

An interface or VLAN can terminate only one L2VPN. An IP address can terminate any number of L2VPNs, but each L2VPN only once. For example, a pseudowire can be terminated to the IP address of its far-end provider edge (PE) device, with the pseudowire ID recorded as the L2VPN's identifier.
