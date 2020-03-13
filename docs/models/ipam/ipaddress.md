# IP Addresses

An IP address comprises a single host address (either IPv4 or IPv6) and its subnet mask. Its mask should match exactly how the IP address is configured on an interface in the real world.

Like prefixes, an IP address can optionally be assigned to a VRF (otherwise, it will appear in the "global" table). IP addresses are automatically organized under parent prefixes within their respective VRFs.

Also like prefixes, each IP address can be assigned a status and a role. Statuses are hard-coded in NetBox and include the following:

* Active
* Reserved
* Deprecated
* DHCP

Each IP address can optionally be assigned a special role. Roles are used to indicate some special attribute of an IP address: for example, it is used as a loopback, or is a virtual IP maintained using VRRP. (Note that this differs in purpose from a _functional_ role, and thus cannot be customized.) Available roles include:

* Loopback
* Secondary
* Anycast
* VIP
* VRRP
* HSRP
* GLBP

An IP address can be assigned to a device or virtual machine interface, and an interface may have multiple IP addresses assigned to it. Further, each device and virtual machine may have one of its interface IPs designated as its primary IP address (one for IPv4 and one for IPv6).

## Network Address Translation (NAT)

An IP address can be designated as the network address translation (NAT) inside IP address for exactly one other IP address. This is useful primarily to denote a translation between public and private IP addresses. This relationship is followed in both directions: For example, if 10.0.0.1 is assigned as the inside IP for 192.0.2.1, 192.0.2.1 will be displayed as the outside IP for 10.0.0.1.

!!! note
    NetBox does not support tracking one-to-many NAT relationships (also called port address translation). This type of policy requires additional logic to model and cannot be fully represented by IP address alone.
