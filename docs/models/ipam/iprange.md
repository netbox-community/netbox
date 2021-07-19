# IP Ranges

This model represents an arbitrary range of individual IPv4 or IPv6 addresses, inclusive of its starting and ending addresses. For instance, the range 192.0.2.10 to 192.0.2.20 has eleven members. (The total member count is available as the `size` property on an IPRange instance.) Like prefixes and IP addresses, each IP range may optionally be assigned to a VRF and/or tenant.

IP also ranges share the same [functional roles](role.md) as prefixes and VLANs, although the assignment of a role is optional. Each IP range must be assigned an operational status, which is one of the following:

* Active - Provisioned and in use
* Reserved - Designated for future use
* Deprecated - No longer in use

The status of a range does _not_ have any impact on its member IP addresses, which may have their statuses modified separately.
