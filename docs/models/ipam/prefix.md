# Prefixes

A prefix is an IPv4 or IPv6 network and mask expressed in CIDR notation (e.g. 192.0.2.0/24). A prefix entails only the "network portion" of an IP address: All bits in the address not covered by the mask must be zero. (In other words, a prefix cannot be a specific IP address.)

Prefixes are automatically organized by their parent aggregates. Additionally, each prefix can be assigned to a particular site and virtual routing and forwarding instance (VRF). Each VRF represents a separate IP space or routing table. All prefixes not assigned to a VRF are considered to be in the "global" table.

Each prefix can be assigned a status and a role. These terms are often used interchangeably so it's important to recognize the difference between them. The **status** defines a prefix's operational state. Statuses are hard-coded in NetBox and can be one of the following:

* Container - A summary of child prefixes
* Active - Provisioned and in use
* Reserved - Designated for future use
* Deprecated - No longer in use

On the other hand, a prefix's **role** defines its function. Role assignment is optional and roles are fully customizable. For example, you might create roles to differentiate between production and development infrastructure.

A prefix may also be assigned to a VLAN. This association is helpful for associating address space with layer two domains. A VLAN may have multiple prefixes assigned to it.

The prefix model include an "is pool" flag. If enabled, NetBox will treat this prefix as a range (such as a NAT pool) wherein every IP address is valid and assignable. This logic is used when identifying available IP addresses within a prefix. If this flag is disabled, NetBox will assume that the first and last (broadcast) address within an IPv4 prefix are unusable.
