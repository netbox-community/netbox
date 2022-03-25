# FHRP Group

A first-hop redundancy protocol (FHRP) enables multiple physical interfaces to present a virtual IP address in a redundant manner. Example of such protocols include:

* Hot Standby Router Protocol (HSRP)
* Virtual Router Redundancy Protocol (VRRP)
* Common Address Redundancy Protocol (CARP)
* Gateway Load Balancing Protocol (GLBP)

NetBox models these redundancy groups by protocol and group ID. Each group may optionally be assigned an authentication type and key. (Note that the authentication key is stored as a plaintext value in NetBox.) Each group may be assigned or more virtual IPv4 and/or IPv6 addresses.
