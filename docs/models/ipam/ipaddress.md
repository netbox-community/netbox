# IP Addresses

An IP address comprises a single host address (either IPv4 or IPv6) and its subnet mask. Its mask should match exactly how the IP address is configured on an interface in the real world.

Like a prefix, an IP address can optionally be assigned to a VRF (otherwise, it will appear in the "global" table). IP addresses are automatically arranged under parent prefixes within their respective VRFs according to the IP hierarchy.

Each IP address can also be assigned an operational status and a functional role. Statuses are hard-coded in NetBox and include the following:

* Active
* Reserved
* Deprecated
* DHCP
* SLAAC (IPv6 Stateless Address Autoconfiguration)

Roles are used to indicate some special attribute of an IP address; for example, use as a loopback or as the the virtual IP for a VRRP group. (Note that functional roles are conceptual in nature, and thus cannot be customized by the user.) Available roles include:

* Loopback
* Secondary
* Anycast
* VIP
* VRRP
* HSRP
* GLBP

An IP address can be assigned to any device or virtual machine interface, and an interface may have multiple IP addresses assigned to it. Further, each device and virtual machine may have one of its interface IPs designated as its primary IP per address family (one for IPv4 and one for IPv6).

!!! note
    When primary IPs are set for both IPv4 and IPv6, NetBox will prefer IPv6. This can be changed by setting the `PREFER_IPV4` configuration parameter.

## Network Address Translation (NAT)

An IP address can be designated as the network address translation (NAT) inside IP address for exactly one other IP address. This is useful primarily to denote a translation between public and private IP addresses. This relationship is followed in both directions: For example, if 10.0.0.1 is assigned as the inside IP for 192.0.2.1, 192.0.2.1 will be displayed as the outside IP for 10.0.0.1.

!!! note
    NetBox does not support tracking one-to-many NAT relationships (also called port address translation). This type of policy requires additional logic to model and cannot be fully represented by IP address alone.
