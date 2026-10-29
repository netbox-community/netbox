# Prefixes

A prefix is an IPv4 or IPv6 network and mask expressed in CIDR notation (e.g. 192.0.2.0/24). A prefix entails only the "network portion" of an IP address: All bits in the address not covered by the mask must be zero. (In other words, a prefix cannot be a specific IP address.) Prefixes are automatically organized by their parent [aggregate](./aggregate.md) and assigned [VRF](./vrf.md).

## Fields

### Prefix

The IPv4 or IPv6 network this prefix represents.

### Classification

The kind of address space the prefix covers, derived automatically from the prefix and read-only. A prefix that lies entirely within one class takes that class, and a prefix that spans several is classified as mixed. Public covers all space no other class claims. It describes the address space only, not whether the prefix is allocated to you, announced or reachable.

| Classification  | Address space                                                                                             |
|-----------------|-----------------------------------------------------------------------------------------------------------|
| Public          | All other space, including globally reachable blocks such as 192.0.0.9/32 and 64:ff9b::/96                 |
| Private         | 10.0.0.0/8, 172.16.0.0/12 and 192.168.0.0/16 (RFC 1918), fc00::/7 (RFC 4193)                               |
| Shared          | 100.64.0.0/10 (RFC 6598)                                                                                  |
| Loopback        | 127.0.0.0/8, ::1/128                                                                                      |
| Link-local      | 169.254.0.0/16, fe80::/10                                                                                 |
| Documentation   | 192.0.2.0/24, 198.51.100.0/24, 203.0.113.0/24, 2001:db8::/32, 3fff::/20                                   |
| Multicast       | 224.0.0.0/4, ff00::/8                                                                                     |
| Benchmarking    | 198.18.0.0/15, 2001:2::/48                                                                                |
| Special-purpose | Other blocks of the IANA special-purpose registries which are not marked globally reachable (including deprecated blocks, TEREDO and 6to4), and IPv6 space reserved by the IETF |
| Mixed           | More than one of the above                                                                                |

!!! note "Custom validation"
    The database computes the classification when the prefix is saved. A custom validator therefore cannot read it for a new prefix, and sees the stored classification rather than the edited one for an existing prefix. Validators which check the address space should inspect `prefix` directly.

### Status

The prefix's operational status. Note that the status of a prefix does _not_ have any impact on its member [IP addresses](./ipaddress.md), which may have their statuses defined independently. The "container" status indicates that the prefix exists merely as a container for organizing child prefixes.

!!! tip
    Additional statuses may be defined by setting `Prefix.status` under the [`FIELD_CHOICES`](../../configuration/data-validation.md#field_choices) configuration parameter.

### VRF

The [Virtual Routing and Forwarding](./vrf.md) instance in which this prefix exists.

!!! note
    VRF assignment is optional. Prefixes with no VRF assigned are considered to exist in the "global" table.

### Role

The user-defined functional [role](./role.md) assigned to the prefix.

### Is a Pool

Designates whether the prefix should be treated as a pool. If selected, the first and last IP addresses within the prefix (normally reserved as the network and broadcast addresses, respectively) will be considered usable. This option is ideal for documenting NAT pools.

### Mark Utilized

If selected, this prefix will report 100% utilization regardless of how many child objects have been defined within it.

### Scope

!!! info "This field replaced the `site` field in NetBox v4.2."

The [region](../dcim/region.md), [site](../dcim/site.md), [site group](../dcim/sitegroup.md) or [location](../dcim/location.md) to which the prefix is assigned (optional).

### VLAN

The [VLAN](./vlan.md) to which this prefix is assigned (optional). This mapping is helpful for associating IP space with layer two domains. A VLAN may have multiple prefixes assigned to it.
