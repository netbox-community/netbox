# IP Ranges

This model represents an arbitrary range of individual IPv4 or IPv6 addresses, inclusive of its starting and ending addresses. For instance, the range 192.0.2.10 to 192.0.2.20 has eleven members. (The total member count is available as the `size` property on an IPRange instance.) Like [prefixes](./prefix.md) and [IP addresses](./ipaddress.md), each IP range may optionally be assigned to a [VRF](./vrf.md).

## Fields

### VRF

The [Virtual Routing and Forwarding](./vrf.md) instance in which this IP range exists.

!!! note
    VRF assignment is optional. IP ranges with no VRF assigned are considered to exist in the "global" table.

### Start & End Address

The beginning and ending IP addresses (inclusive) which define the boundaries of the range. Both IP addresses must specify the correct mask.

!!! note
    The maximum supported size of an IP range is 2^32 - 1.

### Role

The user-defined functional [role](./role.md) assigned to the IP range.

### Status

The IP range's operational status. Note that the status of a range does _not_ have any impact on its member IP addresses, which may have their statuses defined independently.

!!! tip
    Additional statuses may be defined by setting `IPRange.status` under the [`FIELD_CHOICES`](../../configuration/data-validation.md#field_choices) configuration parameter.

### Mark Utilized

If enabled, the IP range will be considered 100% utilized regardless of how many IP addresses are defined within it. This is useful for documenting DHCP ranges, for example.
