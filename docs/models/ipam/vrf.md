# Virtual Routing and Forwarding (VRF)

A VRF object in NetBox represents a Virtual Routing and Forwarding (VRF) domain. Each VRF is essentially an independent routing table. VRFs are commonly used to isolate customers or organizations from one another within a network, or to route overlapping address space (e.g. multiple instances of the 10.0.0.0/8 space). Each VRF may be assigned to a specific tenant to aid in organizing the available IP space by customer or internal user.

Each [prefix](./prefix.md), [IP range](./iprange.md), and [IP address](./ipaddress.md) may be assigned to one (and only one) VRF. If you have a prefix or IP address which exists in multiple VRFs, you will need to create a separate instance of it in NetBox for each VRF. Any such object not assigned to a VRF is said to belong to the "global" table.

## Fields

### Name

The configured or administrative name for the VRF instance.

### Route Distinguisher

A route distinguisher is used to map routes to VRFs within a device's routing table e.g. for MPLS/VPN. The assignment of a route distinguisher is optional. If defined, the RD is expected to take one of the forms prescribed in [RFC 4364](https://tools.ietf.org/html/rfc4364#section-4.2), however its formatting is not strictly enforced.

### Enforce Unique Space

By default, NetBox will permit duplicate prefixes to be assigned to a VRF. This behavior can be toggled by setting the "enforce unique" flag on the VRF model.

!!! note
    Enforcement of unique IP space can be toggled for global table (non-VRF prefixes) using the `ENFORCE_GLOBAL_UNIQUE` configuration setting.

### Import & Export Targets

Each VRF may have one or more import and/or export [route targets](./routetarget.md) applied to it. Route targets are used to control the exchange of routes (prefixes) among VRFs in L3VPNs.
