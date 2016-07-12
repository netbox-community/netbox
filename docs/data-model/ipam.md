IP address management (IPAM) entails the allocation of IP networks, addresses, and related numeric resources.

# VRFs

A VRF object in NetBox represents a virtual routing and forwarding (VRF) domain within a network. Each VRF is essentially a separate routing table: the same IP prefix or address can exist in multiple VRFs. VRFs are commonly used to isolate customers or organizations from one another within a network.

Each VRF is assigned a name and a unique route distinguisher (RD). VRFs are an optional feature of NetBox: Any IP prefix or address not assigned to a VRF is said to belong to the "global" table.

---

# Aggregates

IPv4 address space is organized as a hierarchy, with more-specific (smaller) prefix arranged as child nodes under less-specific (larger) prefixes. For example:

* 10.0.0.0/8
    * 10.1.0.0/16
        * 10.1.2.0/24

The root of the IPv4 hierarchy is 0.0.0.0/0, which encompasses all possible IPv4 addresses (and similarly, ::/0 for IPv6). However, even the largest organizations use only a small fraction of the global address space. Therefore, it makes sense to track in NetBox only the address space which is of interest to your organization.

Aggregates serve as arbitrary top-level nodes in the IP space hierarchy. They allow you to easily construct your IP scheme without any clutter of unused address space. For instance, most organizations utilize some portion of the RFC 1918 private IPv4 space. So, you might define three aggregates for this space:

* 10.0.0.0/8
* 172.16.0.0/12
* 192.168.0.0/16

Additionally, you might define an aggregate for each large swath of public IPv4 space your organization uses. You'd also create aggregates for both globally routable and unique local IPv6 space.

Any prefixes you create in NetBox (discussed below) will be automatically organized under their respective aggregates. Any space within an aggregate which is not covered by an existing prefix will be annotated as available for allocation.

Aggregates cannot overlap with one another; they can only exist in parallel. For instance, you cannot define both 10.0.0.0/8 and 10.16.0.0/16 as aggregates, because they overlap. 10.16.0.0/16 in this example would be created as a prefix.

### RIRs

Regional Internet Registries (RIRs) are responsible for the allocation of global address space. The five RIRs are ARIN, RIPE, APNIC, LACNIC, and AFRINIC. However, some address space has been set aside for private or internal use only, such as defined in RFCs 1918 and 6598. NetBox considers these RFCs as a sort of RIR as well; that is, an authority which "owns" certain address space.

Each aggregate must be assigned to one RIR. You are free to define whichever RIRs you choose (or create your own).

---

# Prefixes

A prefix is an IPv4 or IPv6 network and mask expressed in CIDR notation (e.g. 192.0.2.0/24). A prefix entails only the "network portion" of an IP address; all bits in the address not covered by the mask must be zero.

Each prefix may be assigned to one VRF; prefixes not assigned to a VRF are assigned to the "global" table. Prefixes are also organized under their respective aggregates, irrespective of VRF assignment.

A prefix may optionally be assigned to one VLAN; a VLAN may have multiple prefixes assigned to it. This can be helpful is replicating real-world IP assignments. Each prefix may also be assigned a short description.

### Statuses

Each prefix is assigned an operational status. This is one of the following:

* Container - A summary of child prefixes
* Active - Provisioned and in use
* Reserved - Earmarked for future use
* Deprecated - No longer in use

### Roles

Whereas a status describes a prefix's operational state, a role describes its function. For example, roles might include:

* Access segment
* Infrastructure
* NAT
* Lab
* Out-of-band

Role assignment is optional and you are free to create as many as you'd like.

---

# IP Addresses

An IP address comprises a single address (either IPv4 or IPv6) and its mask. Its mask should match exactly how the IP address is configured on an interface in the real world.

Like prefixes, an IP address can optionally be assigned to a VRF (or it will appear in the "global" table). IP addresses are automatically organized under parent prefixes within their respective VRFs. Each IP address can also be assigned a short description.

Each IP address can optionally be assigned to a device's interface; an interface may have multiple IP addresses assigned to it. Further, each device may have one of its interface IPs designated as its primary IP address.

One IP address can be designated as the network address translation (NAT) IP address for exactly one other IP address. This is useful primarily is denoting the public address for a private internal IP. Tracking one-to-many NAT (or PAT) assignments is not currently supported.

---

# VLANs

A VLAN represents an isolated layer two domain, identified by a name and a numeric ID (1-4094). Note that while it is good practice, neither VLAN names nor IDs must be unique within a site. This is to accommodate the fact that many real-world network use less-than-optimal VLAN allocations and may have overlapping VLAN ID assignments in practice.

Like prefixes, each VLAN is assigned an operational status and (optionally) a functional role.
