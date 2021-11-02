# FHRP Group

A first-hop redundancy protocol (FHRP) enables multiple physical interfaces to present a virtual IP address in a redundant manner. Example of such protocols include:

* Hot Standby Router Protocol (HSRP)
* Virtual Router Redundancy Protocol (VRRP)
* Common Address Redundancy Protocol (CARP)
* Gateway Load Balancing Protocol (GLBP)

NetBox models these redundancy groups by protocol and group ID. Each group may optionally be assigned an authentication type and key. (Note that the authentication key is stored as a plaintext value in NetBox.) Each group may be assigned or more virtual IPv4 and/or IPv6 addresses.

## FHRP Group Assignments

Member device and VM interfaces can be assigned to FHRP groups, along with a numeric priority value. For instance, three interfaces, each belonging to a different router, may each be assigned to the same FHRP group to serve a common virtual IP address. Each of these assignments would typically receive a different priority.
