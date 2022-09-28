# FHRP Group

A first-hop redundancy protocol (FHRP) enables multiple physical interfaces to present a virtual [IP address](./ipaddress.md) (VIP) in a redundant manner. Examples of such protocols include:

* [Hot Standby Router Protocol](https://en.wikipedia.org/wiki/Hot_Standby_Router_Protocol) (HSRP)
* [Virtual Router Redundancy Protocol](https://en.wikipedia.org/wiki/Virtual_Router_Redundancy_Protocol) (VRRP)
* [Common Address Redundancy Protocol](https://en.wikipedia.org/wiki/Common_Address_Redundancy_Protocol) (CARP)
* [Gateway Load Balancing Protocol](https://en.wikipedia.org/wiki/Gateway_Load_Balancing_Protocol) (GLBP)

When creating a new FHRP group, the user may optionally create a VIP as well. This IP address will be automatically assigned to the new group. (Virtual IP addresses can also be assigned after the group has been created.)

## Fields

### Protocol

The wire protocol employed by cooperating servers to maintain the virtual [IP address(es)](./ipaddress.md) for the group.

### Group ID

The group's numeric identifier.

### Name

An optional name for the FHRP group.

### Authentication Type

The type of authentication employed by group nodes, if any.

### Authentication Key

The shared key used for group authentication, if any.

!!! warning
    The authentication key value is stored in plaintext in NetBox's database. Do not utilize this field if you require encryption at rest for shared keys.
