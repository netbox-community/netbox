# Virtual Routing and Forwarding (VRF)

A VRF object in NetBox represents a virtual routing and forwarding (VRF) domain. Each VRF is essentially a separate routing table. VRFs are commonly used to isolate customers or organizations from one another within a network, or to route overlapping address space (e.g. multiple instances of the 10.0.0.0/8 space). Each VRF may be assigned to a specific tenant to aid in organizing the available IP space by customer or internal user.

Each VRF is assigned a unique name and an optional route distinguisher (RD). The RD is expected to take one of the forms prescribed in [RFC 4364](https://tools.ietf.org/html/rfc4364#section-4.2), however its formatting is not strictly enforced.

Each prefix and IP address may be assigned to one (and only one) VRF. If you have a prefix or IP address which exists in multiple VRFs, you will need to create a separate instance of it in NetBox for each VRF. Any prefix or IP address not assigned to a VRF is said to belong to the "global" table.

By default, NetBox will allow duplicate prefixes to be assigned to a VRF. This behavior can be toggled by setting the "enforce unique" flag on the VRF model.

!!! note
    Enforcement of unique IP space can be toggled for global table (non-VRF prefixes) using the `ENFORCE_GLOBAL_UNIQUE` configuration setting.

Each VRF may have one or more import and/or export route targets applied to it. Route targets are used to control the exchange of routes (prefixes) among VRFs in L3VPNs.
