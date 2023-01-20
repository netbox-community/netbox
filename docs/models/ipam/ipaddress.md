# IP Addresses

An IP address object in NetBox comprises a single host address (either IPv4 or IPv6) and its subnet mask, and represents an IP address as configured on a network interface. IP addresses can be assigned to [device](../dcim/device.md) and [virtual machine](../virtualization/virtualmachine.md) interfaces, as well as to [FHRP groups](./fhrpgroup.md). Further, each device and virtual machine may have one of its interface IPs designated as its primary IP per address family (one for IPv4 and one for IPv6).

!!! tip
    When primary IPs are set for both IPv4 and IPv6, NetBox will prefer IPv6. This can be changed by setting the `PREFER_IPV4` configuration parameter.

## Network Address Translation (NAT)

An IP address can be designated as the network address translation (NAT) inside IP address for exactly one other IP address. This is useful primarily to denote a translation between public and private IP addresses. This relationship is followed in both directions: For example, if 10.0.0.1 is assigned as the inside IP for 192.0.2.1, 192.0.2.1 will be displayed as the outside IP for 10.0.0.1.

!!! note
    NetBox does not currently support tracking application-level NAT relationships (also called _port address translation_ or PAT). This type of policy requires additional logic to model and cannot be fully represented by IP address alone.

## Fields

### Address

The IPv4 or IPv6 address and mask, in CIDR notation (e.g. `192.0.2.0/24`).

### Status

The operational status of the IP address.

!!! tip
    Additional statuses may be defined by setting `ipam.IPAddress.status` under the [`FIELD_CHOICES`](../../configuration/data-validation.md#field_choices) configuration parameter.

### Role

The functional role fulfilled by this IP address. Options include:

* **Loopback:** Configured on a loopback interface
* **Secondary:** One of multiple IP addresses configured on an interface
* **Anycast:** Employed for anycast services
* **VIP:** A general-purpose virtual IP address
* **VRRP:** A virtual IP address managed with the VRRP protocol
* **HSRP:** A virtual IP address managed with the HSRP protocol
* **GLBP:** A virtual IP address managed with the GLBP protocol
* **CARP:** A virtual IP address managed with the CARP protocol

!!! tip
    Virtual IP addresses should be assigned to [FHRP groups](./fhrpgroup.md) rather than to actual interfaces to accurately model their shared nature.

### VRF

The [Virtual Routing and Forwarding](./vrf.md) instance in which this IP address exists.

!!! note
    VRF assignment is optional. IP addresses with no VRF assigned are considered to exist in the "global" table.

### DNS Name

A DNS A/AAAA record value associated with this IP address.
