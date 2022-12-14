# Virtual Device Context

A virtual device context (VDC) represents a logical partition within a physical device, to which interfaces from the parent device can be allocated. Each VDC effectively provides an isolated control plane, but relies on shared resources of the parent device. A VDC is somewhat similar to a virtual machine in that it effects isolation between various components, but stops short of delivering a fully virtualized environment.

Each VDC must be assigned to a device upon creation, after which interfaces belonging to that device can be assigned to one or more of its VDCs. A VDC can have any number of interfaces assigned to it, and an interface can belong to any number of VDCs.

!!! info "A VDC by Any Other Name"
    Network vendors use differing names for this concept. Cisco uses the term VDC, whereas Juniper refers to it as a _Virtual Routing Instance_, and Fortinet uses _Virtual Domain_, for instance. While there may be some nuance among the vendors' unique implementations, the general concept remains the same for each.

## Fields

### Device

The device to which this VDC belongs.

### Name

The VDC's configured name. Must be unique to the assigned device.

### Status

The operational status of the VDC.

### Identifier

A vendor-prescribed unique identifier for the VDC (optional). Must be unique to the assigned device if defined.

### Primary IPv4 & IPv6 Addresses

Each VDC may designate one primary IPv4 address and/or one primary IPv6 address for management purposes.

!!! tip
    NetBox will prefer IPv6 addresses over IPv4 addresses by default. This can be changed by setting the `PREFER_IPV4` configuration parameter.
