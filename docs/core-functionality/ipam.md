# Aggregates

The first step to documenting your IP space is to define its scope by creating aggregates. Aggregates establish the root of your IP address hierarchy by defining the top-level allocations that you're interested in managing. Most organizations will want to track some commonly-used private IP spaces, such as:

* 10.0.0.0/8 (RFC 1918)
* 100.64.0.0/10 (RFC 6598)
* 172.16.0.0/12 (RFC 1918)
* 192.168.0.0/16 (RFC 1918)
* One or more /48s within fd00::/8 (IPv6 unique local addressing)

In addition to one or more of these, you'll want to create an aggregate for each globally-routable space your organization has been allocated. These aggregates should match the allocations recorded in public WHOIS databases.

Each IP prefix will be automatically arranged under its parent aggregate if one exists. Note that it's advised to create aggregates only for IP ranges actually allocated to your organization (or marked for private use): There is no need to define aggregates for provider-assigned space which is only used on Internet circuits, for example.

Aggregates cannot overlap with one another: They can only exist side-by-side. For instance, you cannot define both 10.0.0.0/8 and 10.16.0.0/16 as aggregates, because they overlap. 10.16.0.0/16 in this example would be created as a prefix and automatically grouped under 10.0.0.0/8. Remember, the purpose of aggregates is to establish the root of your IP addressing hierarchy.

## Regional Internet Registries (RIRs)

[Regional Internet registries](https://en.wikipedia.org/wiki/Regional_Internet_registry) are responsible for the allocation of globally-routable address space. The five RIRs are ARIN, RIPE, APNIC, LACNIC, and AFRINIC. However, some address space has been set aside for internal use, such as defined in RFCs 1918 and 6598. NetBox considers these RFCs as a sort of RIR as well; that is, an authority which "owns" certain address space. There also exist lower-tier registries which serve a particular geographic area.

Each aggregate must be assigned to one RIR. You are free to define whichever RIRs you choose (or create your own). The RIR model includes a boolean flag which indicates whether the RIR allocates only private IP space.

For example, suppose your organization has been allocated 104.131.0.0/16 by ARIN. It also makes use of RFC 1918 addressing internally. You would first create RIRs named ARIN and RFC 1918, then create an aggregate for each of these top-level prefixes, assigning it to its respective RIR.

---

# Prefixes

A prefix is an IPv4 or IPv6 network and mask expressed in CIDR notation (e.g. 192.0.2.0/24). A prefix entails only the "network portion" of an IP address: All bits in the address not covered by the mask must be zero. (In other words, a prefix cannot be a specific IP address.)

Prefixes are automatically arranged by their parent aggregates. Additionally, each prefix can be assigned to a particular site and VRF (routing table). All prefixes not assigned to a VRF will appear in the "global" table.

Each prefix can be assigned a status and a role. These terms are often used interchangeably so it's important to recognize the difference between them. The **status** defines a prefix's operational state. Statuses are hard-coded in NetBox and can be one of the following:

* Container - A summary of child prefixes
* Active - Provisioned and in use
* Reserved - Designated for future use
* Deprecated - No longer in use

On the other hand, a prefix's **role** defines its function. Role assignment is optional and roles are fully customizable. For example, you might create roles to differentiate between production and development infrastructure.

A prefix may also be assigned to a VLAN. This association is helpful for identifying which prefixes are included when reviewing a list of VLANs.

The prefix model include a "pool" flag. If enabled, NetBox will treat this prefix as a range (such as a NAT pool) wherein every IP address is valid and assignable. This logic is used for identifying available IP addresses within a prefix. If this flag is disabled, NetBox will assume that the first and last (broadcast) address within the prefix are unusable.

---

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

---

# Virtual Routing and Forwarding (VRF)

A VRF object in NetBox represents a virtual routing and forwarding (VRF) domain. Each VRF is essentially a separate routing table. VRFs are commonly used to isolate customers or organizations from one another within a network, or to route overlapping address space (e.g. multiple instances of the 10.0.0.0/8 space).

Each VRF is assigned a unique name and route distinguisher (RD). The RD is expected to take one of the forms prescribed in [RFC 4364](https://tools.ietf.org/html/rfc4364#section-4.2), however its formatting is not strictly enforced.

Each prefix and IP address may be assigned to one (and only one) VRF. If you have a prefix or IP address which exists in multiple VRFs, you will need to create a separate instance of it in NetBox for each VRF. Any IP prefix or address not assigned to a VRF is said to belong to the "global" table.

By default, NetBox will allow duplicate prefixes to be assigned to a VRF. This behavior can be disabled by setting the "enforce unique" flag on the VRF model.

!!! note
    Enforcement of unique IP space can be toggled for global table (non-VRF prefixes) using the `ENFORCE_GLOBAL_UNIQUE` configuration setting.
