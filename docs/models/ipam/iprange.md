# IP Ranges

This model represents an arbitrary range of individual IPv4 or IPv6 addresses, inclusive of its starting and ending addresses. For instance, the range 192.0.2.10 to 192.0.2.20 has eleven members. (The total member count is available as the `size` property on an IPRange instance.) Like [prefixes](./prefix.md) and [IP addresses](./ipaddress.md), each IP range may optionally be assigned to a [VRF](./vrf.md).

Each IP range can be marked as populated, which instructs NetBox to treat the range as though every IP address within it has been created (even though these individual IP addresses don't actually exist in the database). This can be helpful in scenarios where the management of a subset of IP addresses has been deferred to an external system of record, such as a DHCP server. NetBox will prohibit the creation of individual IP addresses within a range that has been marked as populated.

An IP range can also be marked as utilized. This will cause its utilization to always be reported as 100% when viewing the range or when calculating the utilization of a parent prefix. (If not enabled, a range's utilization is calculated based on the number of IP addresses which have been created within it.)

Typically, IP ranges marked as populated should also be marked as utilized, although there may be scenarios where this is undesirable (e.g. when reclaiming old IP space). An IP range which has been marked as populated but _not_ marked as utilized will always report a utilization of 0%, as it cannot contain child IP addresses.

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

### Mark Populated

!!! note "This field was added in NetBox v4.3."

If enabled, NetBox will treat this IP range as being fully populated when calculating available IP space. It will also prevent the creation of IP addresses which fall within the declared range (and assigned VRF, if any).

### Mark Utilized

If enabled, the IP range will be considered 100% utilized regardless of how many IP addresses are defined within it. This is useful for documenting DHCP ranges, for example.
