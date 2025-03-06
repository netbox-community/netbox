# VLANs

A Virtual LAN (VLAN) represents an isolated layer two domain, identified by a name and a numeric ID (1-4094) as defined in [IEEE 802.1Q](https://en.wikipedia.org/wiki/IEEE_802.1Q). VLANs are arranged into [VLAN groups](./vlangroup.md) to define scope and to enforce uniqueness.

## Fields

### ID

A 12-bit numeric ID for the VLAN, 1-4094 (inclusive).

### Name

The configured VLAN name.

### Status

The VLAN's operational status.

!!! tip
    Additional statuses may be defined by setting `VLAN.status` under the [`FIELD_CHOICES`](../../configuration/data-validation.md#field_choices) configuration parameter.

### Role

The user-defined functional [role](./role.md) assigned to the VLAN.

### VLAN Group or Site

The [VLAN group](./vlangroup.md) or [site](../dcim/site.md) to which the VLAN is assigned.

### Q-in-Q Role

!!! info "This field was introduced in NetBox v4.2."

For VLANs which comprise a Q-in-Q/IEEE 802.1ad topology, this field indicates whether the VLAN is treated as a service or customer VLAN.

### Q-in-Q Service VLAN

!!! info "This field was introduced in NetBox v4.2."

The designated parent service VLAN for a Q-in-Q customer VLAN. This may be set only for Q-in-Q custom VLANs.
